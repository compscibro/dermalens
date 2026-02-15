"""Plan lock policy — prevent plan changes too early."""


def can_change_plan(weeks_on_plan: int) -> bool:
    """Users should stick to a plan for at least 2 weeks before changing."""
    return weeks_on_plan >= 2
