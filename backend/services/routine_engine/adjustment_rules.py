"""Adjustment rules — detect when actives should be backed off."""
from backend.services.scoring.metrics import SkinMetrics


def should_back_off_actives(prev: SkinMetrics, cur: SkinMetrics) -> bool:
    """Return True if redness/dryness worsened enough to warrant reducing actives."""
    return (cur.redness - prev.redness) >= 15 or (cur.dryness - prev.dryness) >= 15
