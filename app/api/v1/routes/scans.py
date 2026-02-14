"""
Scans router
Handles facial image uploads, analysis, and scan history
"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, and_
from typing import List
from datetime import datetime, timedelta

from app.db.session import get_db
from app.models.user import User
from app.models.scan import Scan, ScanStatus
from app.models.score_delta import ScoreDelta
from app.models.treatment_plan import TreatmentPlan, PlanStatus
from app.schemas.scan import (
    PresignRequest,
    PresignResponse,
    ScanSubmitRequest,
    ScanResponse,
    ScanHistoryResponse,
    ScoreDeltaResponse
)
from app.core.security import get_current_active_user
from app.services.storage.s3_service import s3_service
from app.services.vision.nanobanana_service import nanobanana_service
from app.core.config import settings

router = APIRouter(prefix="/scans", tags=["Scans"])


@router.post("/presign", response_model=PresignResponse)
async def generate_presigned_url(
    request: PresignRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    Generate presigned URL for image upload
    
    Args:
        request: Presign request with angle and file info
        current_user: Authenticated user
    
    Returns:
        Presigned upload URL and image key
    """
    # Validate file size
    max_size_bytes = settings.MAX_IMAGE_SIZE_MB * 1024 * 1024
    if request.file_size > max_size_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File size exceeds maximum of {settings.MAX_IMAGE_SIZE_MB}MB"
        )
    
    # Generate image key
    image_key = s3_service.generate_image_key(current_user.id, request.angle.value)
    
    # Generate presigned URL
    presigned_data = s3_service.generate_presigned_upload_url(
        image_key=image_key,
        content_type=request.content_type
    )
    
    return PresignResponse(
        upload_url=presigned_data["upload_url"],
        image_key=image_key,
        expires_in=settings.S3_PRESIGNED_URL_EXPIRATION
    )


@router.post("/submit", response_model=ScanResponse, status_code=status.HTTP_201_CREATED)
async def submit_scan(
    request: ScanSubmitRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Submit scan for processing after images are uploaded
    
    Args:
        request: Scan submission with image keys
        background_tasks: FastAPI background tasks
        current_user: Authenticated user
        db: Database session
    
    Returns:
        Created scan with pending status
    """
    # Check minimum scan interval
    result = await db.execute(
        select(Scan)
        .where(Scan.user_id == current_user.id)
        .order_by(desc(Scan.scan_date))
        .limit(1)
    )
    last_scan = result.scalar_one_or_none()
    
    if last_scan:
        days_since_last = (datetime.utcnow() - last_scan.scan_date).days
        if days_since_last < settings.MIN_SCAN_INTERVAL_DAYS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Please wait {settings.MIN_SCAN_INTERVAL_DAYS - days_since_last} more days before next scan"
            )
    
    # Verify images exist in S3
    for key in [request.front_image_key, request.left_image_key, request.right_image_key]:
        if not s3_service.check_image_exists(key):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Image not found: {key}"
            )
    
    # Determine if this is a baseline scan
    active_plan_result = await db.execute(
        select(TreatmentPlan)
        .where(
            and_(
                TreatmentPlan.user_id == current_user.id,
                TreatmentPlan.status == PlanStatus.ACTIVE
            )
        )
    )
    active_plan = active_plan_result.scalar_one_or_none()
    is_baseline = active_plan is None
    
    # Calculate week number if in treatment cycle
    week_number = None
    if active_plan and active_plan.baseline_scan_id:
        days_since_baseline = (datetime.utcnow().date() - active_plan.start_date).days
        week_number = (days_since_baseline // 7) + 1
    
    # Create scan record
    new_scan = Scan(
        user_id=current_user.id,
        status=ScanStatus.PENDING,
        front_image_key=request.front_image_key,
        left_image_key=request.left_image_key,
        right_image_key=request.right_image_key,
        is_baseline=is_baseline,
        week_number=week_number
    )
    
    db.add(new_scan)
    await db.commit()
    await db.refresh(new_scan)
    
    # Process scan in background
    background_tasks.add_task(process_scan, new_scan.id, db)
    
    return ScanResponse.from_orm_with_scores(new_scan)


async def process_scan(scan_id: int, db: AsyncSession):
    """
    Background task to process scan with AI
    
    Args:
        scan_id: Scan ID to process
        db: Database session
    """
    # Fetch scan
    result = await db.execute(
        select(Scan).where(Scan.id == scan_id)
    )
    scan = result.scalar_one_or_none()
    
    if not scan:
        return
    
    try:
        # Update status
        scan.status = ScanStatus.PROCESSING
        await db.commit()
        
        # Generate presigned URLs for AI service
        image_urls = {
            "front": s3_service.generate_presigned_download_url(scan.front_image_key),
            "left": s3_service.generate_presigned_download_url(scan.left_image_key),
            "right": s3_service.generate_presigned_download_url(scan.right_image_key)
        }
        
        # Analyze with NanoBanana
        analysis_results = await nanobanana_service.analyze_images(image_urls)
        
        # Update scan with results
        scan.acne_score = analysis_results.get("acne_score")
        scan.redness_score = analysis_results.get("redness_score")
        scan.oiliness_score = analysis_results.get("oiliness_score")
        scan.dryness_score = analysis_results.get("dryness_score")
        scan.texture_score = analysis_results.get("texture_score")
        scan.pore_size_score = analysis_results.get("pore_size_score")
        scan.dark_spots_score = analysis_results.get("dark_spots_score")
        scan.overall_score = analysis_results.get("overall_score")
        scan.confidence_score = analysis_results.get("confidence_score")
        scan.analysis_model_version = analysis_results.get("model_version")
        scan.processing_time_ms = analysis_results.get("processing_time_ms")
        scan.raw_analysis = analysis_results.get("raw_analysis")
        scan.status = ScanStatus.COMPLETED
        
        # Generate download URLs
        scan.front_image_url = image_urls["front"]
        scan.left_image_url = image_urls["left"]
        scan.right_image_url = image_urls["right"]
        
        await db.commit()
        
        # Calculate score deltas if not baseline
        if not scan.is_baseline:
            await calculate_score_deltas(scan, db)
        
    except Exception as e:
        scan.status = ScanStatus.FAILED
        scan.error_message = str(e)
        await db.commit()


async def calculate_score_deltas(current_scan: Scan, db: AsyncSession):
    """
    Calculate score deltas compared to previous scan
    
    Args:
        current_scan: Current scan
        db: Database session
    """
    # Find previous scan
    result = await db.execute(
        select(Scan)
        .where(
            and_(
                Scan.user_id == current_scan.user_id,
                Scan.id < current_scan.id,
                Scan.status == ScanStatus.COMPLETED
            )
        )
        .order_by(desc(Scan.scan_date))
        .limit(1)
    )
    previous_scan = result.scalar_one_or_none()
    
    if not previous_scan:
        return
    
    # Calculate days between scans
    days_between = (current_scan.scan_date - previous_scan.scan_date).days
    
    # Metrics to compare
    metrics = ["acne", "redness", "oiliness", "dryness", "texture", "pore_size", "dark_spots", "overall"]
    
    for metric in metrics:
        prev_value = getattr(previous_scan, f"{metric}_score")
        curr_value = getattr(current_scan, f"{metric}_score")
        
        if prev_value is None or curr_value is None:
            continue
        
        # Calculate delta
        delta = curr_value - prev_value
        percent_change = (delta / prev_value * 100) if prev_value > 0 else 0
        
        # Lower scores are better, so improvement means negative delta
        improvement = delta < 0
        is_significant = abs(percent_change) >= settings.SCORE_DECLINE_THRESHOLD
        
        # Create delta record
        score_delta = ScoreDelta(
            current_scan_id=current_scan.id,
            previous_scan_id=previous_scan.id,
            metric_name=metric,
            previous_score=prev_value,
            current_score=curr_value,
            delta=delta,
            percent_change=percent_change,
            improvement=improvement,
            is_significant=is_significant,
            days_between_scans=days_between
        )
        
        db.add(score_delta)
    
    await db.commit()


@router.get("/history", response_model=ScanHistoryResponse)
async def get_scan_history(
    page: int = 1,
    page_size: int = 10,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get user's scan history
    
    Args:
        page: Page number
        page_size: Items per page
        current_user: Authenticated user
        db: Database session
    
    Returns:
        Paginated scan history
    """
    offset = (page - 1) * page_size
    
    # Get total count
    count_result = await db.execute(
        select(Scan).where(Scan.user_id == current_user.id)
    )
    total = len(count_result.scalars().all())
    
    # Get paginated scans
    result = await db.execute(
        select(Scan)
        .where(Scan.user_id == current_user.id)
        .order_by(desc(Scan.scan_date))
        .offset(offset)
        .limit(page_size)
    )
    scans = result.scalars().all()
    
    scan_responses = [ScanResponse.from_orm_with_scores(scan) for scan in scans]
    
    return ScanHistoryResponse(
        scans=scan_responses,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/{scan_id}", response_model=ScanResponse)
async def get_scan(
    scan_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get specific scan details
    
    Args:
        scan_id: Scan ID
        current_user: Authenticated user
        db: Database session
    
    Returns:
        Scan details
    """
    result = await db.execute(
        select(Scan).where(
            and_(
                Scan.id == scan_id,
                Scan.user_id == current_user.id
            )
        )
    )
    scan = result.scalar_one_or_none()
    
    if not scan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scan not found"
        )
    
    return ScanResponse.from_orm_with_scores(scan)


@router.get("/{scan_id}/deltas", response_model=List[ScoreDeltaResponse])
async def get_scan_deltas(
    scan_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get score deltas for a scan
    
    Args:
        scan_id: Scan ID
        current_user: Authenticated user
        db: Database session
    
    Returns:
        List of score deltas
    """
    # Verify scan belongs to user
    scan_result = await db.execute(
        select(Scan).where(
            and_(
                Scan.id == scan_id,
                Scan.user_id == current_user.id
            )
        )
    )
    scan = scan_result.scalar_one_or_none()
    
    if not scan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scan not found"
        )
    
    # Get deltas
    result = await db.execute(
        select(ScoreDelta).where(ScoreDelta.current_scan_id == scan_id)
    )
    deltas = result.scalars().all()
    
    return [ScoreDeltaResponse.model_validate(delta) for delta in deltas]
