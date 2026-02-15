"""
Routine generation — delegates to Gemini Vision service.
Kept as a thin wrapper for import compatibility.
"""
from backend.services.vision.gemini_vision_service import gemini_vision_service


def generate_routine(analysis: dict, concerns: dict) -> dict:
    """
    Generate a personalized skincare routine using Gemini.

    Args:
        analysis: SkinScan analysis results (scores, overallScore, summary)
        concerns: SkinConcernsForm data

    Returns:
        Dict with morningSteps, eveningSteps, weeklySteps — each step has
        id, order, name, description, productSuggestion, icon.
    """
    return gemini_vision_service.generate_routine(analysis, concerns)
