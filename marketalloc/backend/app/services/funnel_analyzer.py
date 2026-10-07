from typing import Any


FUNNEL_ORDER = (
    ("impressions", "Impressions"),
    ("clicks", "Clicks"),
    ("sessions", "Website Sessions"),
    ("product_views", "Product / Service Views"),
    ("leads", "Leads / Add to Cart"),
    ("conversions", "Conversions"),
)


def analyze_funnel(
    *,
    impressions: int = 0,
    clicks: int = 0,
    sessions: int = 0,
    product_views: int = 0,
    leads: int = 0,
    conversions: int = 0,
    revenue: float = 0.0,
) -> dict[str, Any]:
    values = [max(int(value or 0), 0) for value in (impressions, clicks, sessions, product_views, leads, conversions)]
    stages = []
    largest = None
    largest_drop = -1.0
    for index, (key, label) in enumerate(FUNNEL_ORDER):
        count = values[index]
        previous = values[index - 1] if index else None
        stage_rate = (count / previous * 100) if previous else None
        drop = (max(previous - count, 0) / previous * 100) if previous else None
        if drop is not None and drop > largest_drop:
            largest = {"from_stage": FUNNEL_ORDER[index - 1][1], "to_stage": label, "drop_off_rate": round(drop, 2)}
            largest_drop = drop
        stages.append(
            {
                "key": key,
                "stage": label,
                "count": count,
                "conversion_rate_from_previous": round(stage_rate, 2) if stage_rate is not None else None,
                "drop_off_rate": round(drop, 2) if drop is not None else None,
            }
        )
    stages.append(
        {
            "key": "revenue",
            "stage": "Revenue",
            "count": round(float(revenue or 0), 2),
            "unit": "INR",
            "conversion_rate_from_previous": None,
            "drop_off_rate": None,
        }
    )
    return {"stages": stages, "largest_leakage": largest}
