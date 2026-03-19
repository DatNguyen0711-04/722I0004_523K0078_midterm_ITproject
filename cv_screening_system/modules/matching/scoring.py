import numpy as np


def calculate_match_percentage(similarities: list[float]) -> float:
    """Overall match = average of all per-skill similarity scores × 100."""
    if not similarities:
        return 0.0
    return float(np.mean(similarities) * 100)


def get_match_status(match_percentage: float) -> str:
    if match_percentage >= 80:
        return "STRONG MATCH"
    elif match_percentage >= 65:
        return "GOOD MATCH"
    elif match_percentage >= 50:
        return "POSSIBLE MATCH"
    return "WEAK MATCH"
