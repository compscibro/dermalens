"""
Routine generation — now uses the local rule-based engine
instead of delegating to Gemini.
Kept for import compatibility.
"""
from backend.services.routine_engine.engine import build_plan


def generate_routine_from_plan(plan: dict) -> dict:
    """
    Convert the engine's plan dict into the legacy RoutinePlanSchema shape
    (morningSteps, eveningSteps, weeklySteps) expected by the iOS client.
    """
    import uuid

    def _step(order: int, raw: dict) -> dict:
        """Convert an engine step dict to RoutineStepSchema-compatible dict."""
        ingredients = ", ".join(raw.get("ingredient_focus", []))
        return {
            "id": str(uuid.uuid4()),
            "order": order,
            "name": raw.get("step_name", "step"),
            "description": raw.get("why", ""),
            "productSuggestion": ingredients,
            "icon": _icon_for_step(raw.get("step_name", "")),
        }

    morning = [_step(i + 1, s) for i, s in enumerate(plan.get("am_steps", []))]
    evening = [_step(i + 1, s) for i, s in enumerate(plan.get("pm_steps", []))]

    # The engine doesn't produce weekly steps, so we leave it empty
    weekly = []

    return {
        "morningSteps": morning,
        "eveningSteps": evening,
        "weeklySteps": weekly,
    }


def _icon_for_step(step_name: str) -> str:
    """Map engine step names to SF Symbol icons for the iOS client."""
    icons = {
        "cleanser": "drop.fill",
        "moisturizer": "humidity.fill",
        "sunscreen": "sun.max.trianglebadge.exclamationmark.fill",
        "active": "testtube.2",
        "treatment": "testtube.2",
        "serum": "testtube.2",
    }
    return icons.get(step_name.lower(), "sparkles")
