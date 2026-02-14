from typing import Dict, Any, List
from services.scoring.metrics import SkinMetrics

def build_plan(metrics: SkinMetrics, profile: Dict[str, Any]) -> Dict[str, Any]:
    concerns: List[str] = profile["concerns"]
    irritation = profile["irritation_risk"]

    am = [
        {"step_name": "cleanser", "ingredient_focus": ["gentle cleanser"], "frequency": "daily",
         "why": "Maintain clean skin without stripping the barrier."},
        {"step_name": "moisturizer", "ingredient_focus": ["ceramides"], "frequency": "daily",
         "why": "Support skin barrier and reduce irritation risk."},
        {"step_name": "sunscreen", "ingredient_focus": ["broad spectrum SPF 30+"], "frequency": "daily",
         "why": "Protect skin and prevent worsening of discoloration/irritation."},
    ]

    pm = [
        {"step_name": "cleanser", "ingredient_focus": ["gentle cleanser"], "frequency": "daily",
         "why": "Remove sunscreen/oil buildup."},
        {"step_name": "moisturizer", "ingredient_focus": ["ceramides"], "frequency": "daily",
         "why": "Repair and hydrate overnight."},
    ]

    # one active max in MVP
    active = None
    if "acne" in concerns and metrics.acne >= 50:
        active = {"step_name": "active", "ingredient_focus": ["salicylic acid (BHA)"], "frequency": "2-3x/week",
                  "why": "Acne/oiliness elevated; BHA can help unclog pores."}
    elif "redness" in concerns and metrics.redness >= 50:
        active = {"step_name": "active", "ingredient_focus": ["niacinamide"], "frequency": "daily",
                  "why": "Visible redness detected; niacinamide is generally gentle and supportive."}
    elif "barrier" in concerns and metrics.dryness >= 50:
        active = {"step_name": "treatment", "ingredient_focus": ["hyaluronic acid"], "frequency": "daily",
                  "why": "Dryness/barrier concern; focus on hydration first."}

    if active:
        # insert before moisturizer
        pm.insert(1, active)

    # ramp schedule (simple)
    ramp = {
        "week_1": "Stick to gentle cleanser + moisturizer + sunscreen. If active exists, use 2 nights only.",
        "week_2": "If no irritation, increase active to 3 nights/week.",
        "week_3": "Maintain schedule. Do not add new actives yet.",
        "week_4": "Re-scan and adjust only if metrics improved or irritation present.",
    }

    avoid = [
        {"combo": "stacking multiple strong actives", "why": "Increases irritation risk, especially early."},
        {"combo": "introducing new products every few days", "why": "Hard to identify what causes irritation."},
    ]
    if irritation in ("medium", "high"):
        avoid.append({"combo": "retinoids/strong acids early", "why": "Higher sensitivity signals detected."})

    return {
        "profile": profile,
        "am_steps": am,
        "pm_steps": pm,
        "ramp_schedule": ramp,
        "avoid": avoid,
        "disclaimer": "Not medical advice. If severe, painful, or worsening symptoms occur, consult a dermatologist.",
    }
