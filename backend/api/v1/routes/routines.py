"""
Routines router — read routine plans from S3.
Routines are generated during scan upload.
"""
from fastapi import APIRouter, Query, HTTPException

from backend.schemas.routine import RoutinePlanSchema
from backend.services.storage.s3_service import s3_service

router = APIRouter(prefix="/routines", tags=["Routines"])


@router.get("/{scan_id}", response_model=RoutinePlanSchema)
def get_routine(
    scan_id: str,
    email: str = Query(..., description="User email"),
):
    """Get the routine plan associated with a specific scan."""
    data = s3_service.get_json(s3_service.routine_key(email, scan_id))
    if data is None:
        raise HTTPException(status_code=404, detail="Routine not found for this scan")
    return RoutinePlanSchema(**data)


@router.get("/latest/plan", response_model=RoutinePlanSchema)
def get_latest_routine(
    email: str = Query(..., description="User email"),
):
    """Get the most recent routine plan for a user."""
    prefixes = s3_service.list_prefixes(s3_service.scans_prefix(email))

    if not prefixes:
        raise HTTPException(status_code=404, detail="No scans found")

    # Find the most recent scan that has a routine
    # Collect all scan analyses to sort by date
    scans_with_dates = []
    for prefix in prefixes:
        parts = prefix.rstrip("/").split("/")
        scan_id = parts[-1]
        analysis = s3_service.get_json(s3_service.analysis_key(email, scan_id))
        if analysis:
            scans_with_dates.append((scan_id, analysis.get("date", "")))

    # Sort by date descending
    scans_with_dates.sort(key=lambda x: x[1], reverse=True)

    # Return the first routine found
    for scan_id, _ in scans_with_dates:
        data = s3_service.get_json(s3_service.routine_key(email, scan_id))
        if data:
            return RoutinePlanSchema(**data)

    raise HTTPException(status_code=404, detail="No routines found")
