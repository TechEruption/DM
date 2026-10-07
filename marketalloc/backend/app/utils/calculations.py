"""Safe mathematical helpers for metrics and attribution calculations."""

from math import isfinite
from typing import Any


def safe_divide(numerator: Any, denominator: Any, default: float | None = None) -> float | None:
    try:
        dividend = float(numerator or 0)
        divisor = float(denominator or 0)
    except (TypeError, ValueError):
        return default
    if not isfinite(dividend) or not isfinite(divisor) or divisor == 0:
        return default
    return dividend / divisor
