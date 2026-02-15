from typing import Dict, Any, List
from backend.services.scoring.metrics import SkinMetrics

def build_profile(metrics: SkinMetrics, quiz: Dict[str, Any], priority: str) -> Dict[str, Any]:
    sensitivity = bool(quiz.get("sensitivity", False))
    tight_after_wash = quiz.get("tight_after_wash", "no")  # yes/no
    breakout_freq = quiz.get("breakout_frequency", "sometimes")  # never/sometimes/often

    concerns: List[str] = []

    # skin type
    if metrics.oiliness >= 60 and metrics.dryness < 50:
        skin_type = "oily"
    elif metrics.dryness >= 60 and metrics.oiliness < 50:
        skin_type = "dry"
    elif metrics.oiliness >= 55 and metrics.dryness >= 55:
        skin_type = "combination"
    else:
        skin_type = "normal"

    if metrics.acne >= 55 or breakout_freq == "often":
        concerns.append("acne")
    if metrics.redness >= 55:
        concerns.append("redness")
    if metrics.dryness >= 55 or tight_after_wash == "yes":
        concerns.append("barrier")
    if metrics.texture >= 55:
        concerns.append("texture")

    # irritation risk
    irritation_risk = "low"
    if sensitivity or metrics.redness >= 60:
        irritation_risk = "medium"
    if sensitivity and (metrics.redness >= 60 or metrics.dryness >= 60):
        irritation_risk = "high"

    # prioritize user's insecurity by putting it first if present
    if priority and priority not in concerns:
        concerns.insert(0, priority)
    elif priority in concerns:
        concerns.remove(priority)
        concerns.insert(0, priority)

    return {
        "skin_type": skin_type,
        "irritation_risk": irritation_risk,
        "concerns": concerns[:4],  # keep tight for hackathon
        "priority": priority,
    }
