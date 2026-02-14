"""
NanoBanana AI Vision Service
Integrates with NanoBanana API for facial skin analysis
"""
import httpx
import logging
from typing import Dict, List, Optional, Tuple
import asyncio
from datetime import datetime

from app.core.config import settings

logger = logging.getLogger(__name__)


class NanoBananaService:
    """Service for NanoBanana AI vision analysis"""
    
    def __init__(self):
        """Initialize NanoBanana client"""
        self.base_url = settings.NANOBANANA_BASE_URL
        self.api_key = settings.NANOBANANA_API_KEY
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    async def analyze_images(
        self,
        image_urls: Dict[str, str]
    ) -> Dict[str, any]:
        """
        Analyze facial images using NanoBanana API
        
        Args:
            image_urls: Dict with keys 'front', 'left', 'right' and image URLs
        
        Returns:
            Analysis results with scores
        """
        start_time = datetime.utcnow()
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                # Prepare request payload
                payload = {
                    "images": {
                        "front": image_urls.get("front"),
                        "left": image_urls.get("left"),
                        "right": image_urls.get("right")
                    },
                    "analysis_types": [
                        "acne",
                        "redness",
                        "oiliness",
                        "dryness",
                        "texture",
                        "pores",
                        "dark_spots"
                    ]
                }
                
                # Make API request
                response = await client.post(
                    f"{self.base_url}/analyze",
                    json=payload,
                    headers=self.headers
                )
                
                response.raise_for_status()
                data = response.json()
                
                # Calculate processing time
                processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
                
                # Normalize and structure results
                normalized_results = self._normalize_scores(data)
                normalized_results["processing_time_ms"] = int(processing_time)
                
                return normalized_results
                
        except httpx.HTTPError as e:
            logger.error(f"NanoBanana API error: {e}")
            raise Exception(f"Failed to analyze images: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in image analysis: {e}")
            raise
    
    def _normalize_scores(self, raw_response: Dict) -> Dict:
        """
        Normalize NanoBanana response to standard score format
        
        Args:
            raw_response: Raw API response
        
        Returns:
            Normalized scores (0-100 scale)
        """
        # Extract scores from API response
        # Note: This is a placeholder - actual structure depends on NanoBanana API
        scores = raw_response.get("analysis", {})
        
        normalized = {
            "acne_score": self._normalize_value(scores.get("acne", {}).get("score")),
            "redness_score": self._normalize_value(scores.get("redness", {}).get("score")),
            "oiliness_score": self._normalize_value(scores.get("oiliness", {}).get("score")),
            "dryness_score": self._normalize_value(scores.get("dryness", {}).get("score")),
            "texture_score": self._normalize_value(scores.get("texture", {}).get("score")),
            "pore_size_score": self._normalize_value(scores.get("pores", {}).get("score")),
            "dark_spots_score": self._normalize_value(scores.get("dark_spots", {}).get("score")),
            "confidence_score": raw_response.get("confidence", 0.95),
            "model_version": raw_response.get("model_version", "1.0"),
            "raw_analysis": raw_response
        }
        
        # Calculate overall score (weighted average)
        normalized["overall_score"] = self._calculate_overall_score(normalized)
        
        return normalized
    
    def _normalize_value(self, value: Optional[float]) -> Optional[float]:
        """
        Normalize a score value to 0-100 scale
        
        Args:
            value: Raw score value
        
        Returns:
            Normalized score (0-100)
        """
        if value is None:
            return None
        
        # Ensure value is between 0 and 100
        return max(0.0, min(100.0, float(value)))
    
    def _calculate_overall_score(self, scores: Dict) -> float:
        """
        Calculate weighted overall skin score
        
        Args:
            scores: Dict of individual scores
        
        Returns:
            Overall score (0-100)
        """
        # Define weights for each metric
        weights = {
            "acne_score": 0.25,
            "redness_score": 0.20,
            "oiliness_score": 0.15,
            "dryness_score": 0.15,
            "texture_score": 0.15,
            "pore_size_score": 0.05,
            "dark_spots_score": 0.05
        }
        
        total_score = 0.0
        total_weight = 0.0
        
        for metric, weight in weights.items():
            score = scores.get(metric)
            if score is not None:
                total_score += score * weight
                total_weight += weight
        
        if total_weight == 0:
            return 0.0
        
        return round(total_score / total_weight, 2)
    
    async def validate_image_quality(self, image_url: str) -> Tuple[bool, Optional[str]]:
        """
        Validate image quality before analysis
        
        Args:
            image_url: URL of the image to validate
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/validate",
                    json={"image_url": image_url},
                    headers=self.headers
                )
                
                response.raise_for_status()
                data = response.json()
                
                is_valid = data.get("valid", False)
                error_message = data.get("error") if not is_valid else None
                
                return is_valid, error_message
                
        except Exception as e:
            logger.error(f"Image validation error: {e}")
            return False, f"Failed to validate image: {str(e)}"


# Singleton instance
nanobanana_service = NanoBananaService()
