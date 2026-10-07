from math import isfinite
from typing import Any

from app.utils.calculations import safe_divide as _safe_divide


def _number(value: Any) -> float:
    if value is None:
        return 0.0
    try:
        result = float(value)
    except (TypeError, ValueError):
        return 0.0
    return result if isfinite(result) else 0.0


def safe_divide(numerator: Any, denominator: Any) -> float | None:
    return _safe_divide(numerator, denominator)


def ctr(clicks: Any, impressions: Any) -> float:
    return (safe_divide(clicks, impressions) or 0.0) * 100


def cpc(spend: Any, clicks: Any) -> float | None:
    return safe_divide(spend, clicks)


def conversion_rate(conversions: Any, clicks: Any) -> float:
    return (safe_divide(conversions, clicks) or 0.0) * 100


def cac(spend: Any, conversions: Any) -> float | None:
    return safe_divide(spend, conversions)


def aov(revenue: Any, conversions: Any) -> float | None:
    return safe_divide(revenue, conversions)


def roas(attributed_revenue: Any, spend: Any) -> float | None:
    return safe_divide(attributed_revenue, spend)


def roi(attributed_revenue: Any, spend: Any) -> float | None:
    ratio = safe_divide(_number(attributed_revenue) - _number(spend), spend)
    return None if ratio is None else ratio * 100


def calculate_metrics(
    *,
    spend: Any = 0,
    impressions: Any = 0,
    clicks: Any = 0,
    conversions: Any = 0,
    revenue: Any = 0,
    attributed_revenue: Any | None = None,
) -> dict[str, float | None]:
    attribution_value = revenue if attributed_revenue is None else attributed_revenue
    return {
        "ctr": ctr(clicks, impressions),
        "cpc": cpc(spend, clicks),
        "conversion_rate": conversion_rate(conversions, clicks),
        "cac": cac(spend, conversions),
        "aov": aov(revenue, conversions),
        "roas": roas(attribution_value, spend),
        "roi": roi(attribution_value, spend),
    }
