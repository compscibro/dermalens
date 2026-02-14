from services.scoring.metrics import SkinMetrics

def should_back_off_actives(prev: SkinMetrics, cur: SkinMetrics) -> bool:
    # if redness/dryness worsen a lot, reduce irritation risk
    return (cur.redness - prev.redness) >= 15 or (cur.dryness - prev.dryness) >= 15
