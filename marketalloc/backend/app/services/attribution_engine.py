from collections import defaultdict
from datetime import date, datetime
from math import isfinite
from typing import Any, Mapping, Sequence


SUPPORTED_MODELS = ("first_touch", "last_touch", "linear", "time_decay", "position_based")
MODEL_LABELS = {
    "first_touch": "First Touch",
    "last_touch": "Last Touch",
    "linear": "Linear",
    "time_decay": "Time Decay",
    "position_based": "Position Based",
}


def normalize_model(model: str) -> str:
    normalized = model.strip().lower().replace("-", "_").replace(" ", "_").replace("/", "_")
    aliases = {"u_shaped": "position_based", "position": "position_based"}
    normalized = aliases.get(normalized, normalized)
    if normalized not in SUPPORTED_MODELS:
        raise ValueError(f"Unsupported attribution model '{model}'. Choose from: {', '.join(SUPPORTED_MODELS)}.")
    return normalized


def _channel(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text if text else None


def calculate_touchpoint_credits(
    touchpoints: Sequence[Mapping[str, Any]],
    model: str = "linear",
    *,
    decay_parameter: float = 0.7,
    first_weight: float = 0.4,
    middle_weight: float = 0.2,
    last_weight: float = 0.4,
) -> list[dict[str, Any]]:
    """Return touchpoint credit shares; unidentifiable channels receive no credit."""
    model_key = normalize_model(model)
    eligible = []
    for point in touchpoints:
        if not isinstance(point, Mapping):
            raise ValueError("Each journey touchpoint must be a mapping.")
        eligible.append(dict(point))
    for point in eligible:
        point["channel"] = _channel(point.get("channel")) or "Unknown"
    eligible.sort(
        key=lambda point: (
            point["timestamp"].isoformat()
            if isinstance(point.get("timestamp"), (datetime, date))
            else str(point.get("timestamp") or ""),
            str(point.get("id", "")),
        )
    )
    count = len(eligible)
    if count == 0:
        return []

    if not isfinite(decay_parameter) or not 0 < decay_parameter <= 1:
        raise ValueError("decay_parameter must be greater than 0 and at most 1.")
    weights = (first_weight, middle_weight, last_weight)
    if any(not isfinite(weight) or weight < 0 for weight in weights) or sum(weights) <= 0:
        raise ValueError("Position-based weights must be non-negative and have a positive total.")
    if count >= 2 and first_weight + last_weight == 0:
        raise ValueError("Position-based first and last weights must have a positive total for multi-touch journeys.")

    if model_key == "first_touch":
        shares = [1.0] + [0.0] * (count - 1)
    elif model_key == "last_touch":
        shares = [0.0] * (count - 1) + [1.0]
    elif model_key == "linear":
        shares = [1.0 / count] * count
    elif model_key == "time_decay":
        raw = [decay_parameter ** (count - index - 1) for index in range(count)]
        total = sum(raw)
        shares = [value / total for value in raw]
    elif count == 1:
        shares = [1.0]
    elif count == 2:
        pair_total = first_weight + last_weight
        shares = [first_weight / pair_total, last_weight / pair_total] if pair_total else [0.5, 0.5]
    else:
        middle_count = count - 2
        base = [first_weight] + [middle_weight / middle_count] * middle_count + [last_weight]
        total = sum(base)
        shares = [value / total for value in base]

    # Assign floating-point residue to the final point so the total is exactly one.
    if shares:
        shares[-1] = 1.0 - sum(shares[:-1])
    return [{**point, "credit_share": shares[index]} for index, point in enumerate(eligible)]


def attribute_conversion(
    touchpoints: Sequence[Mapping[str, Any]],
    revenue: float,
    model: str = "linear",
    **parameters: Any,
) -> list[dict[str, Any]]:
    try:
        revenue_value = float(revenue)
    except (TypeError, ValueError) as error:
        raise ValueError("Conversion revenue must be a finite non-negative number.") from error
    if not isfinite(revenue_value) or revenue_value < 0:
        raise ValueError("Conversion revenue must be a finite non-negative number.")
    credits = calculate_touchpoint_credits(touchpoints, model, **parameters)
    if not credits:
        return [
            {
                "id": None,
                "channel": "Unknown",
                "campaign": None,
                "credit_share": 1.0,
                "attributed_revenue": revenue_value,
            }
        ]
    result = []
    for touchpoint in credits:
        result.append(
            {
                **touchpoint,
                "attributed_revenue": revenue_value * touchpoint["credit_share"],
            }
        )
    return result


def aggregate_attribution(
    credited_touchpoints: Sequence[Mapping[str, Any]],
    group_by: str = "channel",
) -> list[dict[str, Any]]:
    if group_by not in {"channel", "campaign", "date"}:
        raise ValueError("group_by must be one of: channel, campaign, date.")
    totals: dict[str, dict[str, Any]] = defaultdict(lambda: {"credit_share": 0.0, "attributed_revenue": 0.0})
    for point in credited_touchpoints:
        if group_by == "channel":
            key = str(point.get("channel") or "Unknown")
        elif group_by == "campaign":
            key = str(point.get("campaign") or "Unassigned")
        else:
            timestamp = point.get("timestamp")
            key = str(timestamp)[:10] if timestamp else "Unknown"
        totals[key]["credit_share"] += float(point.get("credit_share", 0.0))
        totals[key]["attributed_revenue"] += float(point.get("attributed_revenue", 0.0))
    return [{"key": key, **value} for key, value in sorted(totals.items())]
