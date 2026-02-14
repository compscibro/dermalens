"""
AWS S3 storage service
Handles image upload, presigned URLs, and retrieval
"""
import boto3
from botocore.exceptions import ClientError
from typing import Optional, Dict
import logging
from datetime import datetime, timedelta
import uuid

from app.core.config import settings

logger = logging.getLogger(__name__)


class S3Service:
    """Service for AWS S3 operations"""
    
    def __init__(self):
        """Initialize S3 client"""
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )
        self.bucket_name = settings.S3_BUCKET_NAME
    
    def generate_image_key(self, user_id: int, angle: str) -> str:
        """
        Generate unique S3 key for image
        
        Args:
            user_id: User ID
            angle: Image angle (front, left, right)
        
        Returns:
            S3 object key
        """
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        return f"users/{user_id}/scans/{timestamp}_{angle}_{unique_id}.jpg"
    
    def generate_presigned_upload_url(
        self,
        image_key: str,
        content_type: str,
        expires_in: int = None
    ) -> Dict[str, str]:
        """
        Generate presigned URL for uploading image
        
        Args:
            image_key: S3 object key
            content_type: MIME type of the file
            expires_in: URL expiration in seconds
        
        Returns:
            Dict with upload_url and fields
        """
        if expires_in is None:
            expires_in = settings.S3_PRESIGNED_URL_EXPIRATION
        
        try:
            presigned_post = self.s3_client.generate_presigned_post(
                Bucket=self.bucket_name,
                Key=image_key,
                Fields={"Content-Type": content_type},
                Conditions=[
                    {"Content-Type": content_type},
                    ["content-length-range", 1, settings.MAX_IMAGE_SIZE_MB * 1024 * 1024]
                ],
                ExpiresIn=expires_in
            )
            
            return {
                "upload_url": presigned_post["url"],
                "fields": presigned_post["fields"],
                "image_key": image_key
            }
            
        except ClientError as e:
            logger.error(f"Error generating presigned URL: {e}")
            raise Exception(f"Failed to generate upload URL: {str(e)}")
    
    def generate_presigned_download_url(
        self,
        image_key: str,
        expires_in: int = 3600
    ) -> Optional[str]:
        """
        Generate presigned URL for downloading/viewing image
        
        Args:
            image_key: S3 object key
            expires_in: URL expiration in seconds
        
        Returns:
            Presigned download URL
        """
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': image_key
                },
                ExpiresIn=expires_in
            )
            return url
            
        except ClientError as e:
            logger.error(f"Error generating presigned download URL: {e}")
            return None
    
    def check_image_exists(self, image_key: str) -> bool:
        """
        Check if image exists in S3
        
        Args:
            image_key: S3 object key
        
        Returns:
            True if image exists, False otherwise
        """
        try:
            self.s3_client.head_object(
                Bucket=self.bucket_name,
                Key=image_key
            )
            return True
        except ClientError:
            return False
    
    def delete_image(self, image_key: str) -> bool:
        """
        Delete image from S3
        
        Args:
            image_key: S3 object key
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=image_key
            )
            logger.info(f"Deleted image: {image_key}")
            return True
        except ClientError as e:
            logger.error(f"Error deleting image: {e}")
            return False
    
    def get_image_metadata(self, image_key: str) -> Optional[Dict]:
        """
        Get image metadata from S3
        
        Args:
            image_key: S3 object key
        
        Returns:
            Image metadata dict
        """
        try:
            response = self.s3_client.head_object(
                Bucket=self.bucket_name,
                Key=image_key
            )
            return {
                "size": response.get("ContentLength"),
                "content_type": response.get("ContentType"),
                "last_modified": response.get("LastModified")
            }
        except ClientError as e:
            logger.error(f"Error getting image metadata: {e}")
            return None


# Singleton instance
s3_service = S3Service()
