"""Clamp all metric scores to 0-100."""
from backend.services.scoring.metrics import SkinMetrics


def clamp_metrics(m: SkinMetrics) -> SkinMetrics:
    def c(x):
        return max(0, min(100, int(x)))

    m.acne = c(m.acne)
    m.redness = c(m.redness)
    m.oiliness = c(m.oiliness)
    m.dryness = c(m.dryness)
    m.texture = c(m.texture)
    m.confidence = c(m.confidence)
    return m
