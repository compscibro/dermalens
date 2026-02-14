CONFLICTS = [
    ("retinoid", "strong_acid"),
    ("retinoid", "benzoyl_peroxide"),
    ("strong_acid", "strong_acid"),
]

def has_conflict(a: str, b: str) -> bool:
    return (a, b) in CONFLICTS or (b, a) in CONFLICTS
