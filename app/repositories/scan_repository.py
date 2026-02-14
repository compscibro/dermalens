"""
Scan Repository
Handles all scan data operations with DynamoDB
"""
from typing import Optional, Dict, Any, List
from datetime import datetime
import uuid
import logging
from boto3.dynamodb.conditions import Key, Attr
from decimal import Decimal

from app.db.dynamodb import dynamodb_client

logger = logging.getLogger(__name__)


class ScanRepository:
    """Repository for scan data operations"""
    
    def __init__(self):
        self.table = dynamodb_client.scans_table
    
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
        """Convert Decimal to float for JSON serialization"""
        if isinstance(obj, Decimal):
            return float(obj)
        elif isinstance(obj, dict):
            return {k: self._convert_decimal_to_float(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_decimal_to_float(item) for item in obj]
        return obj
    
    async def create_scan(
        self,
        user_id: str,
        front_image_key: str,
        left_image_key: str,
        right_image_key: str,
        is_baseline: bool = False,
        week_number: Optional[int] = None
    ) -> Dict[str, Any]:
        """Create a new scan"""
        
        scan_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        
        scan_data = {
            'user_id': user_id,
            'scan_id': scan_id,
            'status': 'pending',
            'scan_date': now,
            'front_image_key': front_image_key,
            'left_image_key': left_image_key,
            'right_image_key': right_image_key,
            'front_image_url': None,
            'left_image_url': None,
            'right_image_url': None,
            'acne_score': None,
            'redness_score': None,
            'oiliness_score': None,
            'dryness_score': None,
            'texture_score': None,
            'pore_size_score': None,
            'dark_spots_score': None,
            'overall_score': None,
            'confidence_score': None,
            'analysis_model_version': None,
            'processing_time_ms': None,
            'raw_analysis': None,
            'error_message': None,
            'is_baseline': is_baseline,
            'week_number': week_number,
            'created_at': now,
            'updated_at': now
        }
        
        self.table.put_item(Item=scan_data)
        logger.info(f"✅ Created scan: {scan_id} for user: {user_id}")
        
        return self._convert_decimal_to_float(scan_data)
    
    async def get_scan(self, user_id: str, scan_id: str) -> Optional[Dict[str, Any]]:
        """Get scan by ID"""
        try:
            response = self.table.get_item(
                Key={'user_id': user_id, 'scan_id': scan_id}
            )
            item = response.get('Item')
            return self._convert_decimal_to_float(item) if item else None
        except Exception as e:
            logger.error(f"Error getting scan: {e}")
            return None
    
    async def get_user_scans(
        self,
        user_id: str,
        limit: int = 50,
        last_evaluated_key: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Get all scans for a user, sorted by date (newest first)"""
        try:
            query_params = {
                'IndexName': 'scan-date-index',
                'KeyConditionExpression': Key('user_id').eq(user_id),
                'ScanIndexForward': False,  # Descending order (newest first)
                'Limit': limit
            }
            
            if last_evaluated_key:
                query_params['ExclusiveStartKey'] = last_evaluated_key
            
            response = self.table.query(**query_params)
            
            return {
                'items': [self._convert_decimal_to_float(item) for item in response.get('Items', [])],
                'last_evaluated_key': response.get('LastEvaluatedKey'),
                'count': len(response.get('Items', []))
            }
        except Exception as e:
            logger.error(f"Error getting user scans: {e}")
            return {'items': [], 'last_evaluated_key': None, 'count': 0}
    
    async def update_scan_analysis(
        self,
        user_id: str,
        scan_id: str,
        analysis_results: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Update scan with AI analysis results"""
        
        # Convert floats to Decimal for DynamoDB
        analysis_results = self._convert_floats_to_decimal(analysis_results)
        
        update_expr = []
        expr_values = {}
        
        # Build update expression dynamically
        field_mapping = {
            'acne_score': ':acne',
            'redness_score': ':redness',
            'oiliness_score': ':oiliness',
            'dryness_score': ':dryness',
            'texture_score': ':texture',
            'pore_size_score': ':pore',
            'dark_spots_score': ':spots',
            'overall_score': ':overall',
            'confidence_score': ':confidence',
            'analysis_model_version': ':version',
            'processing_time_ms': ':time',
            'raw_analysis': ':raw',
            'front_image_url': ':front_url',
            'left_image_url': ':left_url',
            'right_image_url': ':right_url'
        }
        
        for field, placeholder in field_mapping.items():
            if field in analysis_results:
                update_expr.append(f'{field} = {placeholder}')
                expr_values[placeholder] = analysis_results[field]
        
        # Always update status and timestamp
        update_expr.extend(['#status = :status', 'updated_at = :now'])
        expr_values[':status'] = 'completed'
        expr_values[':now'] = datetime.utcnow().isoformat()
        
        try:
            response = self.table.update_item(
                Key={'user_id': user_id, 'scan_id': scan_id},
                UpdateExpression='SET ' + ', '.join(update_expr),
                ExpressionAttributeNames={'#status': 'status'},
                ExpressionAttributeValues=expr_values,
                ReturnValues='ALL_NEW'
            )
            
            updated_scan = response.get('Attributes')
            logger.info(f"✅ Updated scan analysis: {scan_id}")
            return self._convert_decimal_to_float(updated_scan)
        except Exception as e:
            logger.error(f"Error updating scan analysis: {e}")
            return None
    
    async def mark_scan_failed(
        self,
        user_id: str,
        scan_id: str,
        error_message: str
    ) -> bool:
        """Mark scan as failed"""
        try:
            self.table.update_item(
                Key={'user_id': user_id, 'scan_id': scan_id},
                UpdateExpression='SET #status = :status, error_message = :error, updated_at = :now',
                ExpressionAttributeNames={'#status': 'status'},
                ExpressionAttributeValues={
                    ':status': 'failed',
                    ':error': error_message,
                    ':now': datetime.utcnow().isoformat()
                }
            )
            logger.warning(f"⚠️ Marked scan as failed: {scan_id} - {error_message}")
            return True
        except Exception as e:
            logger.error(f"Error marking scan as failed: {e}")
            return False
    
    async def get_latest_scan(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user's most recent scan"""
        result = await self.get_user_scans(user_id, limit=1)
        items = result.get('items', [])
        return items[0] if items else None
    
    async def get_baseline_scan(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user's most recent baseline scan"""
        try:
            response = self.table.query(
                IndexName='scan-date-index',
                KeyConditionExpression=Key('user_id').eq(user_id),
                FilterExpression=Attr('is_baseline').eq(True),
                ScanIndexForward=False,
                Limit=1
            )
            
            items = response.get('Items', [])
            return self._convert_decimal_to_float(items[0]) if items else None
        except Exception as e:
            logger.error(f"Error getting baseline scan: {e}")
            return None
    
    async def calculate_score_deltas(
        self,
        user_id: str,
        current_scan_id: str,
        previous_scan_id: str
    ) -> List[Dict[str, Any]]:
        """Calculate score deltas between two scans"""
        
        current = await self.get_scan(user_id, current_scan_id)
        previous = await self.get_scan(user_id, previous_scan_id)
        
        if not current or not previous:
            return []
        
        deltas = []
        metrics = [
            'acne_score', 'redness_score', 'oiliness_score', 'dryness_score',
            'texture_score', 'pore_size_score', 'dark_spots_score', 'overall_score'
        ]
        
        for metric in metrics:
            curr_value = current.get(metric)
            prev_value = previous.get(metric)
            
            if curr_value is not None and prev_value is not None:
                delta = curr_value - prev_value
                percent_change = (delta / prev_value * 100) if prev_value > 0 else 0
                
                # Lower scores are better
                improvement = delta < 0
                is_significant = abs(percent_change) >= 10.0
                
                deltas.append({
                    'metric_name': metric.replace('_score', ''),
                    'previous_score': prev_value,
                    'current_score': curr_value,
                    'delta': round(delta, 2),
                    'percent_change': round(percent_change, 2),
                    'improvement': improvement,
                    'is_significant': is_significant
                })
        
        return deltas


# Singleton instance
scan_repository = ScanRepository()
