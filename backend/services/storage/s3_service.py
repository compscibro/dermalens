"""
AWS S3 storage service
Primary data store — all user data lives as JSON files and images in S3.
"""
import boto3
import json
from botocore.exceptions import ClientError
from typing import Optional, List
import logging

from backend.core.config import settings

logger = logging.getLogger(__name__)


class S3Service:
    """Service for all S3 operations — JSON storage, image upload, listing."""

    def __init__(self):
        self.s3_client = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION,
        )
        self.bucket = settings.S3_BUCKET_NAME

    # --- JSON operations ---

    def put_json(self, key: str, data: dict) -> None:
        """Upload a JSON object to S3."""
        self.s3_client.put_object(
            Bucket=self.bucket,
            Key=key,
            Body=json.dumps(data, default=str),
            ContentType="application/json",
        )

    def get_json(self, key: str) -> Optional[dict]:
        """Download and parse a JSON object from S3. Returns None if not found."""
        try:
            response = self.s3_client.get_object(Bucket=self.bucket, Key=key)
            return json.loads(response["Body"].read().decode("utf-8"))
        except ClientError as e:
            if e.response["Error"]["Code"] == "NoSuchKey":
                return None
            raise

    # --- Image operations ---

    def upload_image(self, key: str, image_data: bytes, content_type: str = "image/jpeg") -> str:
        """Upload image bytes directly to S3. Returns the S3 key."""
        self.s3_client.put_object(
            Bucket=self.bucket,
            Key=key,
            Body=image_data,
            ContentType=content_type,
        )
        return key

    def get_image_bytes(self, key: str) -> Optional[bytes]:
        """Download image bytes from S3."""
        try:
            response = self.s3_client.get_object(Bucket=self.bucket, Key=key)
            return response["Body"].read()
        except ClientError:
            return None

    def generate_presigned_download_url(self, key: str, expires_in: int = 3600) -> Optional[str]:
        """Generate a presigned URL for downloading/viewing."""
        try:
            return self.s3_client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket, "Key": key},
                ExpiresIn=expires_in,
            )
        except ClientError as e:
            logger.error(f"Error generating presigned download URL: {e}")
            return None

    # --- Listing ---

    def list_prefixes(self, prefix: str) -> List[str]:
        """List sub-folders (common prefixes) under a given prefix."""
        response = self.s3_client.list_objects_v2(
            Bucket=self.bucket, Prefix=prefix, Delimiter="/"
        )
        return [cp["Prefix"] for cp in response.get("CommonPrefixes", [])]

    def list_keys(self, prefix: str) -> List[str]:
        """List all object keys under a given prefix."""
        response = self.s3_client.list_objects_v2(Bucket=self.bucket, Prefix=prefix)
        return [obj["Key"] for obj in response.get("Contents", [])]

    # --- Path helpers ---

    @staticmethod
    def user_prefix(email: str) -> str:
        return f"users/{email}/"

    @staticmethod
    def profile_key(email: str) -> str:
        return f"users/{email}/profile.json"

    @staticmethod
    def scan_prefix(email: str, scan_id: str) -> str:
        return f"users/{email}/scans/{scan_id}/"

    @staticmethod
    def scans_prefix(email: str) -> str:
        return f"users/{email}/scans/"

    @staticmethod
    def scan_image_key(email: str, scan_id: str, angle: str) -> str:
        return f"users/{email}/scans/{scan_id}/{angle}.jpg"

    @staticmethod
    def concerns_key(email: str, scan_id: str) -> str:
        return f"users/{email}/scans/{scan_id}/concerns.json"

    @staticmethod
    def analysis_key(email: str, scan_id: str) -> str:
        return f"users/{email}/scans/{scan_id}/analysis.json"

    @staticmethod
    def routine_key(email: str, scan_id: str) -> str:
        return f"users/{email}/scans/{scan_id}/routine.json"

    @staticmethod
    def chat_key(email: str, session_id: str) -> str:
        return f"users/{email}/chat/{session_id}.json"

    @staticmethod
    def chat_prefix(email: str) -> str:
        return f"users/{email}/chat/"


# Singleton instance
s3_service = S3Service()
