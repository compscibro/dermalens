"""
Treatment Routine Engine
Generates personalized skincare routines based on skin analysis
"""
import logging
from typing import Dict, List, Optional
from datetime import date, timedelta

from app.core.config import settings

logger = logging.getLogger(__name__)


class RoutineEngine:
    """Service for generating treatment routines"""
    
    def __init__(self):
        """Initialize routine engine with ingredient database"""
        self.ingredient_database = self._load_ingredient_database()
        self.conflict_rules = self._load_conflict_rules()
    
    def _load_ingredient_database(self) -> Dict:
        """
        Load ingredient recommendations database
        
        Returns:
            Dict mapping concerns to ingredients
        """
        return {
            "acne": {
                "actives": [
                    {"name": "Salicylic Acid", "concentration": "0.5-2%", "benefits": "Exfoliates, unclogs pores"},
                    {"name": "Benzoyl Peroxide", "concentration": "2.5-5%", "benefits": "Kills acne bacteria"},
                    {"name": "Niacinamide", "concentration": "5-10%", "benefits": "Reduces inflammation"},
                    {"name": "Retinol", "concentration": "0.25-1%", "benefits": "Cell turnover, prevents clogs"}
                ],
                "supportive": [
                    {"name": "Hyaluronic Acid", "benefits": "Hydration without oil"},
                    {"name": "Centella Asiatica", "benefits": "Calms inflammation"},
                    {"name": "Tea Tree Oil", "benefits": "Natural antibacterial"}
                ]
            },
            "redness": {
                "actives": [
                    {"name": "Niacinamide", "concentration": "5-10%", "benefits": "Reduces redness"},
                    {"name": "Azelaic Acid", "concentration": "10-20%", "benefits": "Anti-inflammatory"},
                    {"name": "Centella Asiatica", "benefits": "Calming, healing"},
                    {"name": "Green Tea Extract", "benefits": "Antioxidant, soothing"}
                ],
                "supportive": [
                    {"name": "Ceramides", "benefits": "Barrier repair"},
                    {"name": "Colloidal Oatmeal", "benefits": "Anti-inflammatory"},
                    {"name": "Allantoin", "benefits": "Soothing"}
                ]
            },
            "dryness": {
                "actives": [
                    {"name": "Hyaluronic Acid", "benefits": "Deep hydration"},
                    {"name": "Ceramides", "benefits": "Barrier repair"},
                    {"name": "Glycerin", "benefits": "Moisture retention"},
                    {"name": "Urea", "concentration": "5-10%", "benefits": "Hydration, exfoliation"}
                ],
                "supportive": [
                    {"name": "Squalane", "benefits": "Moisture lock"},
                    {"name": "Shea Butter", "benefits": "Rich moisturization"},
                    {"name": "Panthenol", "benefits": "Healing, hydration"}
                ]
            },
            "oiliness": {
                "actives": [
                    {"name": "Niacinamide", "concentration": "5-10%", "benefits": "Regulates oil"},
                    {"name": "Salicylic Acid", "concentration": "0.5-2%", "benefits": "Controls oil"},
                    {"name": "Zinc", "benefits": "Oil regulation"},
                    {"name": "Retinol", "concentration": "0.25-0.5%", "benefits": "Normalizes oil"}
                ],
                "supportive": [
                    {"name": "Clay", "benefits": "Absorbs excess oil"},
                    {"name": "Witch Hazel", "benefits": "Astringent"},
                    {"name": "Tea Tree Oil", "benefits": "Controls sebum"}
                ]
            }
        }
    
    def _load_conflict_rules(self) -> Dict:
        """
        Load ingredient conflict rules
        
        Returns:
            Dict of ingredients that shouldn't be combined
        """
        return {
            "Retinol": ["Vitamin C", "AHA", "BHA", "Benzoyl Peroxide"],
            "Vitamin C": ["Retinol", "AHA", "Niacinamide (in high concentrations)"],
            "AHA": ["Retinol", "BHA", "Vitamin C"],
            "BHA": ["Retinol", "AHA", "Vitamin C"],
            "Benzoyl Peroxide": ["Retinol", "Vitamin C"]
        }
    
    def generate_routine(
        self,
        primary_concern: str,
        scores: Dict[str, float],
        skin_type: Optional[str] = None
    ) -> Dict[str, List[Dict]]:
        """
        Generate AM and PM skincare routine
        
        Args:
            primary_concern: Main skin concern to address
            scores: Current skin scores
            skin_type: Optional skin type info
        
        Returns:
            Dict with 'am_routine' and 'pm_routine' lists
        """
        am_routine = self._build_am_routine(primary_concern, scores, skin_type)
        pm_routine = self._build_pm_routine(primary_concern, scores, skin_type)
        
        return {
            "am_routine": am_routine,
            "pm_routine": pm_routine
        }
    
    def _build_am_routine(
        self,
        concern: str,
        scores: Dict[str, float],
        skin_type: Optional[str]
    ) -> List[Dict]:
        """Build morning routine"""
        routine = []
        
        # Step 1: Cleanser
        routine.append({
            "step_number": 1,
            "product_type": "cleanser",
            "instructions": self._get_cleanser_instructions(concern, "am"),
            "wait_time_minutes": 0
        })
        
        # Step 2: Toner (optional, for certain concerns)
        if concern in ["acne", "oiliness"]:
            routine.append({
                "step_number": 2,
                "product_type": "toner",
                "instructions": "Apply hydrating or balancing toner to clean skin",
                "wait_time_minutes": 1
            })
        
        # Step 3: Treatment serum
        routine.append({
            "step_number": len(routine) + 1,
            "product_type": "serum",
            "instructions": self._get_serum_instructions(concern, "am"),
            "wait_time_minutes": 2
        })
        
        # Step 4: Moisturizer
        routine.append({
            "step_number": len(routine) + 1,
            "product_type": "moisturizer",
            "instructions": self._get_moisturizer_instructions(concern, skin_type, "am"),
            "wait_time_minutes": 2
        })
        
        # Step 5: Sunscreen (ALWAYS in AM)
        routine.append({
            "step_number": len(routine) + 1,
            "product_type": "sunscreen",
            "instructions": "Apply broad-spectrum SPF 30+ sunscreen. Reapply every 2 hours if outdoors.",
            "wait_time_minutes": 0
        })
        
        return routine
    
    def _build_pm_routine(
        self,
        concern: str,
        scores: Dict[str, float],
        skin_type: Optional[str]
    ) -> List[Dict]:
        """Build evening routine"""
        routine = []
        
        # Step 1: Cleanser (double cleanse if wearing makeup)
        routine.append({
            "step_number": 1,
            "product_type": "cleanser",
            "instructions": self._get_cleanser_instructions(concern, "pm"),
            "wait_time_minutes": 0
        })
        
        # Step 2: Toner
        if concern in ["acne", "oiliness", "redness"]:
            routine.append({
                "step_number": 2,
                "product_type": "toner",
                "instructions": "Apply toner to balance and prep skin",
                "wait_time_minutes": 1
            })
        
        # Step 3: Active treatment
        routine.append({
            "step_number": len(routine) + 1,
            "product_type": "treatment",
            "instructions": self._get_treatment_instructions(concern),
            "wait_time_minutes": 5
        })
        
        # Step 4: Serum (supporting)
        routine.append({
            "step_number": len(routine) + 1,
            "product_type": "serum",
            "instructions": self._get_serum_instructions(concern, "pm"),
            "wait_time_minutes": 2
        })
        
        # Step 5: Moisturizer
        routine.append({
            "step_number": len(routine) + 1,
            "product_type": "moisturizer",
            "instructions": self._get_moisturizer_instructions(concern, skin_type, "pm"),
            "wait_time_minutes": 0
        })
        
        return routine
    
    def _get_cleanser_instructions(self, concern: str, time: str) -> str:
        """Get cleanser instructions based on concern"""
        if concern == "acne":
            return "Use gentle salicylic acid cleanser. Massage for 30 seconds, rinse with lukewarm water."
        elif concern == "redness":
            return "Use gentle, fragrance-free cream cleanser. Avoid hot water and harsh scrubbing."
        elif concern == "dryness":
            return "Use hydrating, non-foaming cleanser. Pat skin instead of rubbing."
        else:  # oiliness
            return "Use gel-based or foaming cleanser to remove excess oil without stripping."
    
    def _get_treatment_instructions(self, concern: str) -> str:
        """Get treatment product instructions"""
        treatments = {
            "acne": "Apply retinol or adapalene (start 2-3x/week, build up slowly). Pea-sized amount for entire face.",
            "redness": "Apply azelaic acid or niacinamide serum to affected areas.",
            "dryness": "Apply hydrating treatment with ceramides and peptides.",
            "oiliness": "Apply oil-control serum with niacinamide and zinc."
        }
        return treatments.get(concern, "Apply targeted treatment product.")
    
    def _get_serum_instructions(self, concern: str, time: str) -> str:
        """Get serum instructions"""
        if time == "am":
            return "Apply antioxidant serum (Vitamin C or niacinamide) to protect against environmental damage."
        else:
            return "Apply hydrating or repairing serum based on your skin's needs."
    
    def _get_moisturizer_instructions(
        self,
        concern: str,
        skin_type: Optional[str],
        time: str
    ) -> str:
        """Get moisturizer instructions"""
        if concern == "dryness":
            return "Apply rich, emollient moisturizer. Use more generous amount for PM."
        elif concern == "oiliness":
            return "Apply lightweight, oil-free gel moisturizer."
        else:
            return "Apply moisturizer appropriate for your skin type."
    
    def get_product_recommendations(self, concern: str) -> List[Dict]:
        """
        Get product recommendations for concern
        
        Args:
            concern: Primary skin concern
        
        Returns:
            List of recommended product types and ingredients
        """
        concern_ingredients = self.ingredient_database.get(concern, {})
        
        recommendations = []
        for ingredient in concern_ingredients.get("actives", []):
            recommendations.append({
                "ingredient": ingredient["name"],
                "concentration": ingredient.get("concentration", "As directed"),
                "benefits": ingredient["benefits"],
                "application": "PM" if "Retinol" in ingredient["name"] else "AM/PM"
            })
        
        return recommendations
    
    def check_routine_conflicts(self, routine: Dict) -> List[str]:
        """
        Check for ingredient conflicts in routine
        
        Args:
            routine: Routine dict with AM and PM steps
        
        Returns:
            List of conflict warnings
        """
        warnings = []
        
        # Extract ingredients from routine (simplified - would need more sophisticated parsing)
        # This is a placeholder for actual conflict checking logic
        
        return warnings


# Singleton instance
routine_engine = RoutineEngine()
