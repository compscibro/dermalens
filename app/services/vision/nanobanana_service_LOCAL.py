"""
NanoBanana AI Vision Service - LOCAL TEST MODE
Returns mock data for testing without real API
"""
import logging
from typing import Dict
import random
from datetime import datetime
import asyncio

logger = logging.getLogger(__name__)

class NanoBananaService:
    """Mock service for local testing"""
    
    def __init__(self):
        logger.info("🧪 NanoBanana in TEST MODE - using mock data")
    
    async def analyze_images(self, image_urls: Dict[str, str]) -> Dict:
        """Return mock skin analysis scores"""
        logger.info("🎲 Generating mock skin analysis...")
        
        # Simulate API delay
        await asyncio.sleep(0.5)
        
        # Generate realistic random scores
        acne = round(random.uniform(30, 70), 2)
        redness = round(random.uniform(25, 60), 2)
        oiliness = round(random.uniform(35, 75), 2)
        dryness = round(max(0, min(100, 100 - oiliness + random.uniform(-10, 10))), 2)
        
        return {
            "acne_score": acne,
            "redness_score": redness,
            "oiliness_score": oiliness,
            "dryness_score": dryness,
            "texture_score": round(random.uniform(40, 80), 2),
            "pore_size_score": round(random.uniform(35, 75), 2),
            "dark_spots_score": round(random.uniform(20, 60), 2),
            "overall_score": round((acne + redness + oiliness + dryness) / 4, 2),
            "confidence_score": round(random.uniform(0.85, 0.98), 2),
            "model_version": "mock-1.0",
            "processing_time_ms": 500,
            "raw_analysis": {"status": "mock", "images_analyzed": 3}
        }
    
    async def validate_image_quality(self, image_url: str):
        """Mock validation - always returns valid"""
        await asyncio.sleep(0.1)
        return True, None

# Singleton instance
nanobanana_service = NanoBananaService()
