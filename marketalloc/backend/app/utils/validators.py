from math import isfinite
from typing import Any


def non_negative_number(value: Any, field_name: str) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError) as error:
        raise ValueError(f"{field_name} must be a number.") from error
    if not isfinite(number) or number < 0:
        raise ValueError(f"{field_name} must be a finite non-negative number.")
    return number


def require_text(value: Any, field_name: str) -> str:
    text = "" if value is None else str(value).strip()
    if not text:
        raise ValueError(f"{field_name} is required.")
    return text
