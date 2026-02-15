"""Image quality / retake validators."""
from backend.services.scoring.metrics import SkinMetrics


def needs_retake(m: SkinMetrics) -> bool:
    """Return True if the user should be asked to retake their photos."""
    if m.retake_required:
        return True
    if m.confidence < 45:
        return True
    return False
