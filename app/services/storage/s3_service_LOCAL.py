"""
AWS S3 Storage Service - LOCAL TEST MODE
Stores images locally instead of S3 for testing
"""
import os
import logging
from typing import Dict, Optional
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)

class S3Service:
    """Mock S3 service - stores files locally"""
    
    def __init__(self):
        self.local_storage_path = "/tmp/dermalens_local_images"
        os.makedirs(self.local_storage_path, exist_ok=True)
        logger.info(f"🧪 S3 in TEST MODE - storing locally at {self.local_storage_path}")
    
    def generate_image_key(self, user_id: int, angle: str) -> str:
        """Generate unique key for image"""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        return f"users/{user_id}/scans/{timestamp}_{angle}_{unique_id}.jpg"
    
    def generate_presigned_upload_url(
        self,
        image_key: str,
        content_type: str,
        expires_in: int = 3600
    ) -> Dict[str, str]:
        """Generate mock presigned URL"""
        # In local mode, return a mock URL
        # Frontend can still "upload" to this URL (we'll handle it in the API)
        mock_url = f"http://localhost:8000/api/v1/local-upload/{image_key}"
        
        return {
            "upload_url": mock_url,
            "fields": {"Content-Type": content_type},
            "image_key": image_key
        }
    
    def generate_presigned_download_url(
        self,
        image_key: str,
        expires_in: int = 3600
    ) -> Optional[str]:
        """Generate mock download URL"""
        # Return local file path as URL
        local_path = os.path.join(self.local_storage_path, image_key)
        
        # For testing, return a mock URL
        return f"http://localhost:8000/api/v1/local-images/{image_key}"
    
    def check_image_exists(self, image_key: str) -> bool:
        """Check if image exists locally"""
        # For testing, always return True (assume upload succeeded)
        return True
    
    def delete_image(self, image_key: str) -> bool:
        """Delete local image"""
        try:
            local_path = os.path.join(self.local_storage_path, image_key)
            if os.path.exists(local_path):
                os.remove(local_path)
            return True
        except Exception as e:
            logger.error(f"Error deleting local image: {e}")
            return False
    
    def get_image_metadata(self, image_key: str) -> Optional[Dict]:
        """Get image metadata"""
        return {
            "size": 1024000,  # Mock 1MB
            "content_type": "image/jpeg",
            "last_modified": datetime.utcnow()
        }
    
    def save_local_file(self, image_key: str, file_data: bytes) -> bool:
        """Save uploaded file locally"""
        try:
            local_path = os.path.join(self.local_storage_path, image_key)
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            
            with open(local_path, 'wb') as f:
                f.write(file_data)
            
            logger.info(f"💾 Saved image locally: {local_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving local file: {e}")
            return False

# Singleton instance
s3_service = S3Service()
