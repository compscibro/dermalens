"""
Scans router — upload photos, run Gemini Vision analysis, generate routine.
All data stored in S3.
"""
from fastapi import APIRouter, Query, HTTPException, UploadFile, File, Form
from typing import List
from datetime import datetime, timezone
import uuid
import json

from backend.schemas.scan import SkinScanSchema, ScanRecordSchema
from backend.schemas.routine import RoutinePlanSchema
from backend.services.storage.s3_service import s3_service
from backend.services.vision.gemini_vision_service import gemini_vision_service

router = APIRouter(prefix="/scans", tags=["Scans"])


@router.post("/upload", response_model=SkinScanSchema)
async def upload_and_analyze(
    front: UploadFile = File(...),
    left: UploadFile = File(...),
    right: UploadFile = File(...),
    concerns: str = Form(...),
    email: str = Query(..., description="User email"),
):
    """
    Upload 3 face photos + concerns, run AI analysis, generate routine.
    Returns the scan analysis. The routine is stored and can be fetched separately.
    """
    if not email or "@" not in email:
        raise HTTPException(status_code=400, detail="Valid email required")

    # Parse concerns JSON
    try:
        concerns_data = json.loads(concerns)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid concerns JSON")

    scan_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()

    # Read image bytes
    front_bytes = await front.read()
    left_bytes = await left.read()
    right_bytes = await right.read()

    # Upload images to S3
    s3_service.upload_image(
        s3_service.scan_image_key(email, scan_id, "front"), front_bytes
    )
    s3_service.upload_image(
        s3_service.scan_image_key(email, scan_id, "left"), left_bytes
    )
    s3_service.upload_image(
        s3_service.scan_image_key(email, scan_id, "right"), right_bytes
    )

    # Save concerns
    s3_service.put_json(s3_service.concerns_key(email, scan_id), concerns_data)

    # Run Gemini Vision analysis
    analysis = gemini_vision_service.analyze_skin(
        front_image=front_bytes,
        left_image=left_bytes,
        right_image=right_bytes,
        concerns=concerns_data,
    )

    # Build full scan record
    scan_data = {
        "id": scan_id,
        "date": now,
        "frontImageName": s3_service.scan_image_key(email, scan_id, "front"),
        "leftImageName": s3_service.scan_image_key(email, scan_id, "left"),
        "rightImageName": s3_service.scan_image_key(email, scan_id, "right"),
        "scores": analysis["scores"],
        "overallScore": analysis["overallScore"],
        "summary": analysis["summary"],
    }

    # Save analysis to S3
    s3_service.put_json(s3_service.analysis_key(email, scan_id), scan_data)

    # Generate routine using Gemini
    routine_raw = gemini_vision_service.generate_routine(analysis, concerns_data)
    routine_data = {
        "id": str(uuid.uuid4()),
        "date": now,
        "morningSteps": routine_raw.get("morningSteps", []),
        "eveningSteps": routine_raw.get("eveningSteps", []),
        "weeklySteps": routine_raw.get("weeklySteps", []),
    }

    # Save routine to S3
    s3_service.put_json(s3_service.routine_key(email, scan_id), routine_data)

    return SkinScanSchema(**scan_data)


@router.get("/{scan_id}", response_model=SkinScanSchema)
def get_scan(
    scan_id: str,
    email: str = Query(..., description="User email"),
):
    """Get a specific scan's analysis results."""
    data = s3_service.get_json(s3_service.analysis_key(email, scan_id))
    if data is None:
        raise HTTPException(status_code=404, detail="Scan not found")
    return SkinScanSchema(**data)


@router.get("/history/list", response_model=List[ScanRecordSchema])
def get_scan_history(
    email: str = Query(..., description="User email"),
):
    """List all scans for a user as summary records."""
    prefixes = s3_service.list_prefixes(s3_service.scans_prefix(email))
    records: List[dict] = []

    for prefix in prefixes:
        # Extract scan_id from prefix like "users/email/scans/{scan_id}/"
        parts = prefix.rstrip("/").split("/")
        scan_id = parts[-1]

        analysis = s3_service.get_json(s3_service.analysis_key(email, scan_id))
        if analysis is None:
            continue

        # Pick top 3 concerns (highest scoring metrics)
        scores = analysis.get("scores", [])
        sorted_scores = sorted(scores, key=lambda s: s.get("score", 0), reverse=True)
        top_concerns = [s["name"] for s in sorted_scores[:3]]

        records.append({
            "id": scan_id,
            "date": analysis.get("date", ""),
            "overallScore": analysis.get("overallScore", 0),
            "thumbnailSystemName": "face.smiling",
            "concerns": top_concerns,
        })

    # Sort by date descending
    records.sort(key=lambda r: r["date"], reverse=True)
    return [ScanRecordSchema(**r) for r in records]
