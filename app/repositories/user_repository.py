"""
User Repository
Handles all user data operations with DynamoDB
"""
from typing import Optional, Dict, Any
from datetime import datetime
import uuid
import logging
from boto3.dynamodb.conditions import Key, Attr

from app.db.dynamodb import dynamodb_client
from app.core.security import get_password_hash, verify_password

logger = logging.getLogger(__name__)


class UserRepository:
    """Repository for user data operations"""
    
    def __init__(self):
        self.table = dynamodb_client.users_table
    
    async def create_user(
        self,
        email: str,
        password: str,
        full_name: Optional[str] = None,
        skin_type: Optional[str] = None,
        primary_concern: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new user"""
        
        # Check if email exists
        existing = await self.get_user_by_email(email)
        if existing:
            raise ValueError("Email already registered")
        
        user_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        
        user_data = {
            'user_id': user_id,
            'email': email,
            'hashed_password': get_password_hash(password),
            'full_name': full_name,
            'skin_type': skin_type,
            'primary_concern': primary_concern,
            'is_active': True,
            'is_verified': False,
            'created_at': now,
            'updated_at': now,
            'last_login': None
        }
        
        self.table.put_item(Item=user_data)
        logger.info(f"✅ Created user: {email}")
        
        # Don't return password hash
        user_data.pop('hashed_password')
        return user_data
    
    async def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email"""
        try:
            response = self.table.query(
                IndexName='email-index',
                KeyConditionExpression=Key('email').eq(email)
            )
            
            items = response.get('Items', [])
            return items[0] if items else None
        except Exception as e:
            logger.error(f"Error getting user by email: {e}")
            return None
    
    async def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        try:
            response = self.table.get_item(Key={'user_id': user_id})
            return response.get('Item')
        except Exception as e:
            logger.error(f"Error getting user by ID: {e}")
            return None
    
    async def authenticate_user(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate user and return user data"""
        user = await self.get_user_by_email(email)
        
        if not user:
            return None
        
        if not verify_password(password, user.get('hashed_password', '')):
            return None
        
        if not user.get('is_active', False):
            return None
        
        # Update last login
        await self.update_last_login(user['user_id'])
        
        # Remove password hash before returning
        user.pop('hashed_password', None)
        return user
    
    async def update_last_login(self, user_id: str):
        """Update last login timestamp"""
        try:
            self.table.update_item(
                Key={'user_id': user_id},
                UpdateExpression='SET last_login = :now',
                ExpressionAttributeValues={':now': datetime.utcnow().isoformat()}
            )
        except Exception as e:
            logger.error(f"Error updating last login: {e}")
    
    async def update_user(
        self,
        user_id: str,
        full_name: Optional[str] = None,
        skin_type: Optional[str] = None,
        primary_concern: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Update user profile"""
        
        update_expr = []
        expr_values = {}
        
        if full_name is not None:
            update_expr.append('full_name = :name')
            expr_values[':name'] = full_name
        
        if skin_type is not None:
            update_expr.append('skin_type = :skin')
            expr_values[':skin'] = skin_type
        
        if primary_concern is not None:
            update_expr.append('primary_concern = :concern')
            expr_values[':concern'] = primary_concern
        
        if update_expr:
            update_expr.append('updated_at = :now')
            expr_values[':now'] = datetime.utcnow().isoformat()
            
            try:
                response = self.table.update_item(
                    Key={'user_id': user_id},
                    UpdateExpression='SET ' + ', '.join(update_expr),
                    ExpressionAttributeValues=expr_values,
                    ReturnValues='ALL_NEW'
                )
                
                updated_user = response.get('Attributes')
                updated_user.pop('hashed_password', None)
                return updated_user
            except Exception as e:
                logger.error(f"Error updating user: {e}")
                return None
        
        return await self.get_user_by_id(user_id)
    
    async def change_password(self, user_id: str, current_password: str, new_password: str) -> bool:
        """Change user password"""
        user = await self.get_user_by_id(user_id)
        
        if not user:
            return False
        
        if not verify_password(current_password, user.get('hashed_password', '')):
            return False
        
        try:
            self.table.update_item(
                Key={'user_id': user_id},
                UpdateExpression='SET hashed_password = :pwd, updated_at = :now',
                ExpressionAttributeValues={
                    ':pwd': get_password_hash(new_password),
                    ':now': datetime.utcnow().isoformat()
                }
            )
            logger.info(f"✅ Password changed for user: {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error changing password: {e}")
            return False


# Singleton instance
user_repository = UserRepository()
