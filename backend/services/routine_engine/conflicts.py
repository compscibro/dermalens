"""Ingredient conflict pairs — used to prevent unsafe combinations."""

CONFLICTS = [
    ("retinoid", "strong_acid"),
    ("retinoid", "benzoyl_peroxide"),
    ("strong_acid", "strong_acid"),
]


def has_conflict(a: str, b: str) -> bool:
    """Return True if two ingredient categories conflict."""
    return (a, b) in CONFLICTS or (b, a) in CONFLICTS
