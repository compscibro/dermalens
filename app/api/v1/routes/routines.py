"""
Treatment Plans router
Handles routine generation, plan management, and adjustments
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc
from datetime import date, timedelta

from app.db.session import get_db
from app.models.user import User
from app.models.scan import Scan, ScanStatus
from app.models.treatment_plan import TreatmentPlan, PlanStatus, AdjustmentReason
from app.schemas.treatment_plan import (
    TreatmentPlanCreate,
    TreatmentPlanResponse,
    TreatmentPlanUpdate,
    ProductRecommendation
)
from app.core.security import get_current_active_user
from app.services.routine_engine.routine_generator import routine_engine
from app.core.config import settings

router = APIRouter(prefix="/routines", tags=["Treatment Plans"])


@router.post("/", response_model=TreatmentPlanResponse, status_code=status.HTTP_201_CREATED)
async def create_treatment_plan(
    plan_data: TreatmentPlanCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create new treatment plan based on baseline scan
    
    Args:
        plan_data: Treatment plan creation data
        current_user: Authenticated user
        db: Database session
    
    Returns:
        Created treatment plan
    """
    # Check if user already has active plan
    active_plan_result = await db.execute(
        select(TreatmentPlan).where(
            and_(
                TreatmentPlan.user_id == current_user.id,
                TreatmentPlan.status == PlanStatus.ACTIVE
            )
        )
    )
    active_plan = active_plan_result.scalar_one_or_none()
    
    if active_plan:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You already have an active treatment plan"
        )
    
    # Verify baseline scan exists and belongs to user
    scan_result = await db.execute(
        select(Scan).where(
            and_(
                Scan.id == plan_data.baseline_scan_id,
                Scan.user_id == current_user.id,
                Scan.status == ScanStatus.COMPLETED
            )
        )
    )
    baseline_scan = scan_result.scalar_one_or_none()
    
    if not baseline_scan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Baseline scan not found or not completed"
        )
    
    # Generate routine using AI engine
    scores = baseline_scan.all_scores
    routine = routine_engine.generate_routine(
        primary_concern=plan_data.primary_concern,
        scores=scores,
        skin_type=current_user.skin_type
    )
    
    # Get product recommendations
    recommendations = routine_engine.get_product_recommendations(plan_data.primary_concern)
    
    # Calculate dates
    start_date = date.today()
    planned_end_date = start_date + timedelta(days=plan_data.lock_duration_days)
    
    # Create treatment plan
    new_plan = TreatmentPlan(
        user_id=current_user.id,
        status=PlanStatus.ACTIVE,
        version=1,
        primary_concern=plan_data.primary_concern,
        start_date=start_date,
        planned_end_date=planned_end_date,
        lock_duration_days=plan_data.lock_duration_days,
        baseline_scan_id=baseline_scan.id,
        am_routine=routine["am_routine"],
        pm_routine=routine["pm_routine"],
        recommended_products=recommendations,
        instructions=f"Follow this routine consistently for {plan_data.lock_duration_days} days. Scan weekly to track progress.",
        warnings="Discontinue if you experience severe irritation or allergic reactions."
    )
    
    # Mark baseline scan
    baseline_scan.is_baseline = True
    
    db.add(new_plan)
    await db.commit()
    await db.refresh(new_plan)
    
    return TreatmentPlanResponse.model_validate(new_plan)


@router.get("/current", response_model=TreatmentPlanResponse)
async def get_current_plan(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get user's current active treatment plan
    
    Args:
        current_user: Authenticated user
        db: Database session
    
    Returns:
        Current treatment plan
    """
    result = await db.execute(
        select(TreatmentPlan).where(
            and_(
                TreatmentPlan.user_id == current_user.id,
                TreatmentPlan.status == PlanStatus.ACTIVE
            )
        )
    )
    plan = result.scalar_one_or_none()
    
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active treatment plan found"
        )
    
    return TreatmentPlanResponse.model_validate(plan)


@router.patch("/current", response_model=TreatmentPlanResponse)
async def adjust_treatment_plan(
    update_data: TreatmentPlanUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Request adjustment to current treatment plan
    
    Args:
        update_data: Adjustment request data
        current_user: Authenticated user
        db: Database session
    
    Returns:
        Updated/new treatment plan
    """
    # Get current plan
    plan_result = await db.execute(
        select(TreatmentPlan).where(
            and_(
                TreatmentPlan.user_id == current_user.id,
                TreatmentPlan.status == PlanStatus.ACTIVE
            )
        )
    )
    current_plan = plan_result.scalar_one_or_none()
    
    if not current_plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active treatment plan found"
        )
    
    # Check if adjustment is allowed
    adjustment_reason = AdjustmentReason(update_data.adjustment_reason)
    
    # Severe irritation always allows adjustment
    if adjustment_reason == AdjustmentReason.SEVERE_IRRITATION:
        allow_adjustment = True
    # Score decline allows adjustment
    elif adjustment_reason == AdjustmentReason.SCORE_DECLINE:
        # Verify score decline through latest scan
        allow_adjustment = await check_score_decline(current_user.id, db)
    # User request only allowed if plan can be adjusted
    elif adjustment_reason == AdjustmentReason.USER_REQUEST:
        allow_adjustment = current_plan.can_adjust
    else:
        allow_adjustment = False
    
    if not allow_adjustment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Treatment plan adjustment not allowed at this time"
        )
    
    # Mark current plan as adjusted
    current_plan.status = PlanStatus.ADJUSTED
    current_plan.adjustment_reason = adjustment_reason
    current_plan.adjustment_notes = update_data.adjustment_notes
    current_plan.actual_end_date = date.today()
    
    # Get latest scan for new baseline
    latest_scan_result = await db.execute(
        select(Scan).where(
            and_(
                Scan.user_id == current_user.id,
                Scan.status == ScanStatus.COMPLETED
            )
        )
        .order_by(desc(Scan.scan_date))
        .limit(1)
    )
    latest_scan = latest_scan_result.scalar_one_or_none()
    
    if not latest_scan:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No completed scan available for new plan"
        )
    
    # Generate new routine
    scores = latest_scan.all_scores
    routine = routine_engine.generate_routine(
        primary_concern=current_plan.primary_concern,
        scores=scores,
        skin_type=current_user.skin_type
    )
    
    recommendations = routine_engine.get_product_recommendations(current_plan.primary_concern)
    
    # Create new plan
    new_plan = TreatmentPlan(
        user_id=current_user.id,
        status=PlanStatus.ACTIVE,
        version=current_plan.version + 1,
        primary_concern=current_plan.primary_concern,
        start_date=date.today(),
        planned_end_date=date.today() + timedelta(days=current_plan.lock_duration_days),
        lock_duration_days=current_plan.lock_duration_days,
        baseline_scan_id=latest_scan.id,
        am_routine=routine["am_routine"],
        pm_routine=routine["pm_routine"],
        recommended_products=recommendations,
        previous_plan_id=current_plan.id,
        instructions=f"Adjusted routine. Follow consistently for {current_plan.lock_duration_days} days.",
        warnings="Discontinue if you experience severe irritation or allergic reactions."
    )
    
    latest_scan.is_baseline = True
    
    db.add(new_plan)
    await db.commit()
    await db.refresh(new_plan)
    
    return TreatmentPlanResponse.model_validate(new_plan)


async def check_score_decline(user_id: int, db: AsyncSession) -> bool:
    """
    Check if recent scans show significant score decline
    
    Args:
        user_id: User ID
        db: Database session
    
    Returns:
        True if significant decline detected
    """
    # Get last 2 scans
    result = await db.execute(
        select(Scan).where(
            and_(
                Scan.user_id == user_id,
                Scan.status == ScanStatus.COMPLETED
            )
        )
        .order_by(desc(Scan.scan_date))
        .limit(2)
    )
    scans = result.scalars().all()
    
    if len(scans) < 2:
        return False
    
    current, previous = scans[0], scans[1]
    
    # Check primary metrics for decline
    for metric in ["acne_score", "redness_score", "oiliness_score", "dryness_score"]:
        curr_val = getattr(current, metric)
        prev_val = getattr(previous, metric)
        
        if curr_val and prev_val:
            percent_change = ((curr_val - prev_val) / prev_val) * 100
            # Lower is better, so positive change is bad
            if percent_change >= settings.SCORE_DECLINE_THRESHOLD:
                return True
    
    return False


@router.get("/history")
async def get_plan_history(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get user's treatment plan history
    
    Args:
        current_user: Authenticated user
        db: Database session
    
    Returns:
        List of all treatment plans
    """
    result = await db.execute(
        select(TreatmentPlan)
        .where(TreatmentPlan.user_id == current_user.id)
        .order_by(desc(TreatmentPlan.created_at))
    )
    plans = result.scalars().all()
    
    return [TreatmentPlanResponse.model_validate(plan) for plan in plans]


@router.get("/recommendations/{concern}")
async def get_recommendations(
    concern: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Get product recommendations for a specific concern
    
    Args:
        concern: Skin concern (acne, redness, dryness, oiliness)
        current_user: Authenticated user
    
    Returns:
        List of product recommendations
    """
    if concern not in ["acne", "redness", "dryness", "oiliness"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid concern. Must be one of: acne, redness, dryness, oiliness"
        )
    
    recommendations = routine_engine.get_product_recommendations(concern)
    return {"concern": concern, "recommendations": recommendations}
