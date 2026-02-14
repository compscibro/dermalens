from typing import Dict, Any, List, Optional
from services.scoring.metrics import SkinMetrics


def build_plan(metrics: SkinMetrics, profile: Dict[str, Any]) -> Dict[str, Any]:
    concerns: List[str] = profile.get("concerns", [])
    irritation: str = profile.get("irritation_risk", "low")
    priority: Optional[str] = profile.get("priority")

    am = [
        {
            "step_name": "cleanser",
            "ingredient_focus": ["gentle cleanser"],
            "frequency": "daily",
            "why": "Maintain clean skin without stripping the barrier."
        },
        {
            "step_name": "moisturizer",
            "ingredient_focus": ["ceramides"],
            "frequency": "daily",
            "why": "Support skin barrier and reduce irritation risk."
        },
        {
            "step_name": "sunscreen",
            "ingredient_focus": ["broad spectrum SPF 30+"],
            "frequency": "daily",
            "why": "Protect skin and prevent worsening of discoloration/irritation."
        },
    ]

    pm = [
        {
            "step_name": "cleanser",
            "ingredient_focus": ["gentle cleanser"],
            "frequency": "daily",
            "why": "Remove sunscreen/oil buildup."
        },
        {
            "step_name": "moisturizer",
            "ingredient_focus": ["ceramides"],
            "frequency": "daily",
            "why": "Repair and hydrate overnight."
        },
    ]

    # ---- ACTIVE PICKING LOGIC (Priority-first, one active max) ----
    active = None

    # 1) PRIORITY FIRST (user-selected focus)
    if priority == "redness":
        active = {
            "step_name": "active",
            "ingredient_focus": ["niacinamide (2–5%)"],
            "frequency": "daily",
            "why": "You selected redness as top priority; niacinamide is generally gentle and barrier-supportive."
        }

    elif priority == "texture":
        # keep it conservative for MVP; start slow
        active = {
            "step_name": "active",
            "ingredient_focus": ["lactic acid (AHA) low strength"],
            "frequency": "1-2x/week",
            "why": "You selected texture as top priority; a low-strength AHA can help with texture when introduced slowly."
        }

    elif priority == "acne":
        # only choose BHA if acne or oiliness is elevated
        if metrics.acne >= 45 or metrics.oiliness >= 60:
            active = {
                "step_name": "active",
                "ingredient_focus": ["salicylic acid (BHA)"],
                "frequency": "2-3x/week",
                "why": "You selected acne as top priority; acne/oiliness is elevated and BHA can help unclog pores."
            }

    elif priority == "barrier" or priority == "dryness":
        active = {
            "step_name": "treatment",
            "ingredient_focus": ["hyaluronic acid", "ceramides"],
            "frequency": "daily",
            "why": "You selected barrier/dryness as top priority; hydration and barrier support come first."
        }

    # 2) FALLBACK (if priority didn't set an active)
    if active is None:
        if "acne" in concerns and metrics.acne >= 50:
            active = {
                "step_name": "active",
                "ingredient_focus": ["salicylic acid (BHA)"],
                "frequency": "2-3x/week",
                "why": "Acne/oiliness elevated; BHA can help unclog pores."
            }
        elif "redness" in concerns and metrics.redness >= 50:
            active = {
                "step_name": "active",
                "ingredient_focus": ["niacinamide (2–5%)"],
                "frequency": "daily",
                "why": "Visible redness detected; niacinamide is generally gentle and supportive."
            }
        elif "barrier" in concerns and metrics.dryness >= 50:
            active = {
                "step_name": "treatment",
                "ingredient_focus": ["hyaluronic acid", "ceramides"],
                "frequency": "daily",
                "why": "Dryness/barrier concern; focus on hydration and barrier support first."
            }

    # Safety tweak: if irritation risk is high, reduce frequency of acids
    if active is not None and irritation == "high":
        ing = " ".join(active.get("ingredient_focus", [])).lower()
        if "acid" in ing or "bha" in ing or "aha" in ing:
            active["frequency"] = "1x/week"
            active["why"] += " (Irritation risk is high, so frequency is reduced to start more safely.)"

    # insert active before moisturizer in PM
    if active:
        pm.insert(1, active)

    # ramp schedule (simple)
    ramp = {
        "week_1": "Stick to gentle cleanser + moisturizer + sunscreen. If an active is included, use it only 1–2 nights this week.",
        "week_2": "If no irritation (burning, peeling, stinging), increase active frequency slightly (e.g., 2–3 nights/week depending on the active).",
        "week_3": "Maintain schedule. Avoid adding new actives—consistency matters more than stacking products.",
        "week_4": "Re-scan and adjust only if metrics improved or irritation is present."
    }

    avoid = [
        {"combo": "stacking multiple strong actives", "why": "Increases irritation risk, especially early."},
        {"combo": "introducing new products every few days", "why": "Hard to identify what causes irritation."},
    ]
    if irritation in ("medium", "high"):
        avoid.append({"combo": "retinoids/strong acids early", "why": "Higher sensitivity signals detected; start gentler and slower."})

    return {
        "profile": profile,
        "am_steps": am,
        "pm_steps": pm,
        "ramp_schedule": ramp,
        "avoid": avoid,
        "disclaimer": "Not medical advice. If severe, painful, or worsening symptoms occur, consult a dermatologist.",
    }
