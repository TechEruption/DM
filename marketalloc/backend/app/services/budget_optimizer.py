from math import exp, isfinite
from typing import Any

import numpy as np

from app.services.marketing_metrics import calculate_metrics


def _positive(value: Any) -> float:
    try:
        number = float(value or 0)
        return max(number, 0.0) if isfinite(number) else 0.0
    except (TypeError, ValueError):
        return 0.0


def optimize_budget(
    channels: list[dict[str, Any]],
    total_budget: float,
    *,
    min_allocations: dict[str, float] | None = None,
    max_allocations: dict[str, float] | None = None,
) -> dict[str, Any]:
    """Allocate in deterministic increments using a diminishing marginal-return curve."""
    budget = float(total_budget)
    if not np.isfinite(budget) or budget <= 0:
        raise ValueError("total_budget must be a finite amount greater than zero.")
    if not channels:
        raise ValueError("At least one channel with performance data is required.")
    min_allocations = min_allocations or {}
    max_allocations = max_allocations or {}
    names = [str(item["channel"]) for item in channels]
    if len(set(names)) != len(names):
        raise ValueError("Channel names must be unique.")
    unknown_constraints = (min_allocations.keys() | max_allocations.keys()) - set(names)
    if unknown_constraints:
        raise ValueError(f"Unknown channel constraint(s): {', '.join(sorted(unknown_constraints))}.")

    bases = []
    total_attributed_revenue = sum(
        _positive(item.get("attributed_revenue", item.get("revenue")))
        for item in channels
    )
    for item in channels:
        spend = _positive(item.get("spend"))
        conversions = _positive(item.get("conversions"))
        revenue = _positive(item.get("attributed_revenue", item.get("revenue")))
        metrics = calculate_metrics(
            spend=spend,
            impressions=item.get("impressions"),
            clicks=item.get("clicks"),
            conversions=conversions,
            revenue=item.get("revenue", revenue),
            attributed_revenue=revenue,
        )
        historical_roas = metrics["roas"] or 0.0
        historical_cac = metrics["cac"]
        cvr = (metrics["conversion_rate"] or 0.0) / 100
        bases.append(
            {
                **item,
                "channel": str(item["channel"]),
                "spend": spend,
                "conversions": conversions,
                "revenue": _positive(item.get("revenue", revenue)),
                "attributed_revenue": revenue,
                "historical_roas": historical_roas,
                "historical_cac": historical_cac,
                "conversion_rate": metrics["conversion_rate"] or 0.0,
                "revenue_contribution": revenue / total_attributed_revenue if total_attributed_revenue else 0.0,
                "minimum": _positive(min_allocations.get(str(item["channel"]), 0)),
                "maximum": _positive(
                    max_allocations.get(
                        str(item["channel"]),
                        budget if len(channels) == 1 else budget / 2 if len(channels) == 2 else budget * 0.4,
                    )
                ),
            }
        )
    raw_scores = np.array(
        [
            [
                np.log1p(max(item["historical_roas"], 0.0)),
                np.log1p(1 / max(item["historical_cac"], 1.0)) if item["historical_cac"] else 0.0,
                np.log1p(max(item["conversion_rate"], 0.0) / 100),
                item["revenue_contribution"],
            ]
            for item in bases
        ],
        dtype=float,
    )
    minima = raw_scores.min(axis=0)
    spans = raw_scores.max(axis=0) - minima
    normalized_scores = np.divide(
        raw_scores - minima,
        spans,
        out=np.full_like(raw_scores, 0.5),
        where=spans > 1e-12,
    )
    for item, normalized in zip(bases, normalized_scores, strict=True):
        item["efficiency"] = 0.5 + float(np.mean(normalized))
    minimum_total = sum(item["minimum"] for item in bases)
    maximum_total = sum(item["maximum"] for item in bases)
    for item in bases:
        if item["minimum"] > item["maximum"]:
            raise ValueError(
                f"Minimum allocation exceeds maximum allocation for channel '{item['channel']}'."
            )
    if minimum_total > budget + 1e-8:
        raise ValueError("The sum of minimum allocations cannot exceed total_budget.")
    if maximum_total < budget - 1e-8:
        raise ValueError("The sum of maximum allocations must be at least total_budget.")

    allocations = np.array([item["minimum"] for item in bases], dtype=float)
    remaining = budget - float(allocations.sum())
    steps = min(1000, max(100, len(bases) * 100))
    increment = budget / steps
    while remaining > 1e-7:
        step = min(increment, remaining)
        marginal_scores = []
        for index, item in enumerate(bases):
            if allocations[index] + 1e-8 >= item["maximum"]:
                marginal_scores.append(-1.0)
                continue
            saturation_scale = max(item["spend"], budget / len(bases), 1.0)
            marginal = item["efficiency"] * exp(-allocations[index] / saturation_scale)
            marginal_scores.append(marginal)
        eligible = [index for index, score in enumerate(marginal_scores) if score >= 0]
        if not eligible:
            raise ValueError("Budget could not be allocated within the supplied maximum constraints.")
        selected = max(eligible, key=lambda index: (marginal_scores[index], -index))
        actual_step = min(step, bases[selected]["maximum"] - allocations[selected])
        allocations[selected] += actual_step
        remaining -= actual_step

    # The forecast response curve integrates a decaying marginal return.
    channel_results = []
    for item, allocation in zip(bases, allocations, strict=True):
        current = item["spend"]
        scale = max(current, budget / len(bases), 1.0)
        base_roas = max(item["historical_roas"], 0.05)
        projected_revenue = base_roas * scale * (
            1 - exp(-float(allocation) / scale)
        )
        current_revenue = base_roas * scale * (1 - exp(-current / scale))
        projected_conversions = (
            float(allocation) / item["historical_cac"]
            if item["historical_cac"] and item["historical_cac"] > 0
            else float(allocation) * max(item["conversion_rate"] / 100, 0.001)
        )
        change = float(allocation) - current
        direction = "increase" if change > 0.01 else "decrease" if change < -0.01 else "maintain"
        channel_results.append(
            {
                "channel": item["channel"],
                "current_allocation": round(current, 2),
                "recommended_allocation": round(float(allocation), 2),
                "allocation_change": round(change, 2),
                "historical_roas": round(item["historical_roas"], 4),
                "projected_revenue": round(projected_revenue, 2),
                "projected_conversions": round(projected_conversions, 2),
                "projected_roas": round(projected_revenue / allocation, 4) if allocation else None,
                "projected_roi": round(((projected_revenue - allocation) / allocation) * 100, 2)
                if allocation
                else None,
                "projected_cac": round(float(allocation) / projected_conversions, 2)
                if projected_conversions
                else None,
                "estimated_current_revenue": round(current_revenue, 2),
                "explanation": (
                    f"Recommend to {direction} this channel based on historical ROAS "
                    f"({item['historical_roas']:.2f}x), CAC, conversion rate, and a "
                    "diminishing-return curve; allocation constraints were respected."
                ),
            }
        )
    projected_revenue_total = sum(row["projected_revenue"] for row in channel_results)
    projected_conversions_total = sum(row["projected_conversions"] for row in channel_results)
    projected_roas = projected_revenue_total / budget if budget else None
    return {
        "forecast_label": "Projected / Estimated",
        "total_budget": round(budget, 2),
        "current_allocation": round(sum(item["spend"] for item in bases), 2),
        "recommended_allocation": round(sum(row["recommended_allocation"] for row in channel_results), 2),
        "projected_revenue": round(projected_revenue_total, 2),
        "projected_conversions": round(projected_conversions_total, 2),
        "projected_roas": round(projected_roas, 4) if projected_roas is not None else None,
        "projected_roi": round(((projected_revenue_total - budget) / budget) * 100, 2),
        "projected_cac": round(budget / projected_conversions_total, 2) if projected_conversions_total else None,
        "channels": channel_results,
        "method": (
            "A deterministic marginal-return allocator starts at channel minimums, then distributes "
            "budget in small increments to the channel with the highest current marginal score. "
            "The normalized score combines historical ROAS, CAC, conversion rate, and revenue contribution, "
            "and decays exponentially "
            "as allocation grows. Maximum constraints are enforced at every step. Unless overridden by "
            "a user constraint, each channel is capped at 40% of the total for portfolios with three or "
            "more channels (50% for two channels) to prevent a single-channel concentration outcome."
        ),
    }
