"""
Treatment Plan Repository
Handles all treatment plan operations with DynamoDB
"""
from typing import Optional, Dict, Any, List
from datetime import datetime, date, timedelta
import uuid
import logging
from boto3.dynamodb.conditions import Key, Attr
from decimal import Decimal

from app.db.dynamodb import dynamodb_client

logger = logging.getLogger(__name__)


class TreatmentPlanRepository:
    """Repository for treatment plan operations"""
    
    def __init__(self):
        self.table = dynamodb_client.plans_table
    
    def _convert_floats_to_decimal(self, obj):
        """Convert floats to Decimal for DynamoDB"""
        if isinstance(obj, float):
            return Decimal(str(obj))
        elif isinstance(obj, dict):
            return {k: self._convert_floats_to_decimal(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_floats_to_decimal(item) for item in obj]
        return obj
    
    def _convert_decimal_to_float(self, obj):
        """Convert Decimal to float for JSON"""
        if isinstance(obj, Decimal):
            return float(obj)
        elif isinstance(obj, dict):
            return {k: self._convert_decimal_to_float(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_decimal_to_float(item) for item in obj]
        return obj
    
    async def create_plan(
        self,
        user_id: str,
        primary_concern: str,
        am_routine: List[Dict],
        pm_routine: List[Dict],
        baseline_scan_id: str,
        lock_duration_days: int = 14,
        recommended_products: Optional[List[Dict]] = None,
        instructions: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create new treatment plan"""
        
        plan_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        start_date = date.today().isoformat()
        planned_end_date = (date.today() + timedelta(days=lock_duration_days)).isoformat()
        
        plan_data = {
            'user_id': user_id,
            'plan_id': plan_id,
            'status': 'active',
            'version': 1,
            'primary_concern': primary_concern,
            'start_date': start_date,
            'planned_end_date': planned_end_date,
            'actual_end_date': None,
            'lock_duration_days': lock_duration_days,
            'baseline_scan_id': baseline_scan_id,
            'am_routine': am_routine,
            'pm_routine': pm_routine,
            'recommended_products': recommended_products or [],
            'instructions': instructions,
            'warnings': 'Discontinue if you experience severe irritation or allergic reactions.',
            'can_adjust': False,
            'adjustment_reason': None,
            'adjustment_notes': None,
            'previous_plan_id': None,
            'created_at': now,
            'updated_at': now
        }
        
        # Convert floats to Decimal
        plan_data = self._convert_floats_to_decimal(plan_data)
        
        self.table.put_item(Item=plan_data)
        logger.info(f"✅ Created treatment plan: {plan_id} for user: {user_id}")
        
        return self._convert_decimal_to_float(plan_data)
    
    async def get_plan(self, user_id: str, plan_id: str) -> Optional[Dict[str, Any]]:
        """Get plan by ID"""
        try:
            response = self.table.get_item(
                Key={'user_id': user_id, 'plan_id': plan_id}
            )
            item = response.get('Item')
            return self._convert_decimal_to_float(item) if item else None
        except Exception as e:
            logger.error(f"Error getting plan: {e}")
            return None
    
    async def get_active_plan(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user's active treatment plan"""
        try:
            response = self.table.query(
                KeyConditionExpression=Key('user_id').eq(user_id),
                FilterExpression=Attr('status').eq('active'),
                ScanIndexForward=False,  # Get newest first
                Limit=1
            )
            
            items = response.get('Items', [])
            if not items:
                return None
            
            plan = self._convert_decimal_to_float(items[0])
            
            # Calculate dynamic properties
            plan['is_locked'] = self._is_locked(plan)
            plan['days_remaining'] = self._days_remaining(plan)
            plan['days_elapsed'] = self._days_elapsed(plan)
            
            return plan
        except Exception as e:
            logger.error(f"Error getting active plan: {e}")
            return None
    
    async def get_user_plans(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get all plans for a user"""
        try:
            response = self.table.query(
                KeyConditionExpression=Key('user_id').eq(user_id),
                ScanIndexForward=False,
                Limit=limit
            )
            
            plans = [self._convert_decimal_to_float(item) for item in response.get('Items', [])]
            
            # Add dynamic properties
            for plan in plans:
                plan['is_locked'] = self._is_locked(plan)
                plan['days_remaining'] = self._days_remaining(plan)
                plan['days_elapsed'] = self._days_elapsed(plan)
            
            return plans
        except Exception as e:
            logger.error(f"Error getting user plans: {e}")
            return []
    
    async def update_plan_status(
        self,
        user_id: str,
        plan_id: str,
        status: str,
        adjustment_reason: Optional[str] = None,
        adjustment_notes: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Update plan status"""
        
        update_expr = ['#status = :status', 'updated_at = :now']
        expr_values = {
            ':status': status,
            ':now': datetime.utcnow().isoformat()
        }
        expr_names = {'#status': 'status'}
        
        if status in ['adjusted', 'cancelled', 'completed']:
            update_expr.append('actual_end_date = :end_date')
            expr_values[':end_date'] = date.today().isoformat()
        
        if adjustment_reason:
            update_expr.append('adjustment_reason = :reason')
            expr_values[':reason'] = adjustment_reason
        
        if adjustment_notes:
            update_expr.append('adjustment_notes = :notes')
            expr_values[':notes'] = adjustment_notes
        
        try:
            response = self.table.update_item(
                Key={'user_id': user_id, 'plan_id': plan_id},
                UpdateExpression='SET ' + ', '.join(update_expr),
                ExpressionAttributeNames=expr_names,
                ExpressionAttributeValues=expr_values,
                ReturnValues='ALL_NEW'
            )
            
            updated_plan = response.get('Attributes')
            logger.info(f"✅ Updated plan status: {plan_id} -> {status}")
            return self._convert_decimal_to_float(updated_plan)
        except Exception as e:
            logger.error(f"Error updating plan status: {e}")
            return None
    
    def _is_locked(self, plan: Dict[str, Any]) -> bool:
        """Check if plan is locked"""
        if plan.get('status') != 'active':
            return False
        
        planned_end = date.fromisoformat(plan['planned_end_date'])
        return date.today() < planned_end
    
    def _days_remaining(self, plan: Dict[str, Any]) -> int:
        """Calculate days remaining in lock period"""
        if plan.get('status') != 'active':
            return 0
        
        planned_end = date.fromisoformat(plan['planned_end_date'])
        delta = planned_end - date.today()
        return max(0, delta.days)
    
    def _days_elapsed(self, plan: Dict[str, Any]) -> int:
        """Calculate days elapsed since plan start"""
        start = date.fromisoformat(plan['start_date'])
        delta = date.today() - start
        return delta.days


# Singleton instance
treatment_plan_repository = TreatmentPlanRepository()
