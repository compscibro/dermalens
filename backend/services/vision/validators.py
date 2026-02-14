from services.scoring.metrics import SkinMetrics

def needs_retake(m: SkinMetrics) -> bool:
    if m.retake_required:
        return True
    if m.confidence < 45:
        return True
    return False
