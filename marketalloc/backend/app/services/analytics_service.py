from datetime import date, datetime, time, timedelta, timezone
from decimal import Decimal
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models import AttributionResult, Campaign, Channel, Conversion, Touchpoint
from app.services.attribution_engine import (
    MODEL_LABELS,
    SUPPORTED_MODELS,
    attribute_conversion,
    normalize_model,
)
from app.services.journey_builder import conversion_journey


def dataset_metadata(campaigns: list[Any]) -> dict[str, Any]:
    is_demo = bool(campaigns) and all(
        campaign.get("is_demo", False) if isinstance(campaign, dict) else campaign.is_demo
        for campaign in campaigns
    )
    label = "DEMO DATASET" if is_demo else "MARKETING DATASET" if campaigns else "NO DATASET"
    return {"dataset_label": label, "is_demo_dataset": is_demo}


def date_bounds(date_from: date | None, date_to: date | None) -> tuple[datetime | None, datetime | None]:
    if date_from and date_to and date_from > date_to:
        raise ValueError("date_from must be on or before date_to.")
    start = datetime.combine(date_from, time.min, tzinfo=timezone.utc) if date_from else None
    end = datetime.combine(date_to + timedelta(days=1), time.min, tzinfo=timezone.utc) if date_to else None
    return start, end


def load_campaigns(
    db: Session,
    *,
    date_from: date | None = None,
    date_to: date | None = None,
    channel_id: int | None = None,
    campaign_id: str | int | None = None,
) -> list[Campaign]:
    if date_from and date_to and date_from > date_to:
        raise ValueError("date_from must be on or before date_to.")
    query = select(Campaign).options(joinedload(Campaign.channel))
    if date_from:
        query = query.where(Campaign.end_date >= date_from)
    if date_to:
        query = query.where(Campaign.start_date <= date_to)
    if channel_id:
        query = query.where(Campaign.channel_id == channel_id)
    if campaign_id is not None:
        campaign_pk = resolve_campaign_pk(db, campaign_id)
        query = query.where(Campaign.id == campaign_pk if campaign_pk is not None else Campaign.id == -1)
    return list(db.scalars(query.order_by(Campaign.name)).unique().all())


def resolve_campaign_pk(db: Session, campaign_id: str | int | None) -> int | None:
    if campaign_id is None:
        return None
    if isinstance(campaign_id, int):
        return campaign_id
    internal_id = db.scalar(select(Campaign.id).where(Campaign.campaign_id == campaign_id))
    if internal_id is not None:
        return internal_id
    return int(campaign_id) if campaign_id.isdecimal() else None


def calculate_dataset_attribution(
    db: Session,
    model: str = "linear",
    *,
    date_from: date | None = None,
    date_to: date | None = None,
    channel_id: int | None = None,
    campaign_id: str | int | None = None,
    decay_parameter: float = 0.7,
    first_weight: float = 0.4,
    middle_weight: float = 0.2,
    last_weight: float = 0.4,
) -> list[dict[str, Any]]:
    model_key = normalize_model(model)
    campaign_pk = resolve_campaign_pk(db, campaign_id)
    if campaign_id is not None and campaign_pk is None:
        return []
    start, end = date_bounds(date_from, date_to)
    query = select(Conversion).options(joinedload(Conversion.customer), joinedload(Conversion.touchpoint))
    if start:
        query = query.where(Conversion.conversion_date >= start)
    if end:
        query = query.where(Conversion.conversion_date < end)
    conversions = list(db.scalars(query.order_by(Conversion.conversion_date, Conversion.id)).unique().all())

    if not conversions:
        return []
    customer_ids = {conversion.customer_id for conversion in conversions}
    points_query = (
        select(Touchpoint)
        .where(Touchpoint.customer_id.in_(customer_ids))
        .options(joinedload(Touchpoint.channel), joinedload(Touchpoint.campaign))
        .order_by(Touchpoint.timestamp, Touchpoint.id)
    )
    if channel_id:
        points_query = points_query.where(Touchpoint.channel_id == channel_id)
    if campaign_pk is not None:
        points_query = points_query.where(Touchpoint.campaign_id == campaign_pk)
    touchpoints = list(db.scalars(points_query).unique().all())
    by_customer: dict[int, list[Touchpoint]] = {}
    for point in touchpoints:
        by_customer.setdefault(point.customer_id, []).append(point)

    result = []
    for conversion in conversions:
        journey = conversion_journey(conversion, by_customer.get(conversion.customer_id, []))
        if (channel_id is not None or campaign_pk is not None) and not journey:
            continue
        credits = attribute_conversion(
            journey,
            float(conversion.revenue),
            model_key,
            decay_parameter=decay_parameter,
            first_weight=first_weight,
            middle_weight=middle_weight,
            last_weight=last_weight,
        )
        for credit in credits:
            result.append(
                {
                    "conversion_id": conversion.id,
                    "order_id": conversion.order_id,
                    "conversion_date": conversion.conversion_date,
                    "model": model_key,
                    "model_label": MODEL_LABELS[model_key],
                    "customer_id": conversion.customer.customer_id,
                    "channel_id": credit.get("channel_id"),
                    "channel": credit.get("channel"),
                    "campaign_id": credit.get("campaign_id"),
                    "campaign": credit.get("campaign"),
                    "touchpoint_id": credit.get("id"),
                    "credit_share": credit["credit_share"],
                    "attributed_revenue": credit["attributed_revenue"],
                }
            )
    return result


def persist_attribution(db: Session, credits: list[dict[str, Any]], model: str) -> None:
    if not credits:
        return
    conversion_ids = {row["conversion_id"] for row in credits}
    existing = db.scalars(
        select(AttributionResult).where(
            AttributionResult.model_name == model,
            AttributionResult.conversion_id.in_(conversion_ids),
        )
    ).all()
    for row in existing:
        db.delete(row)
    db.flush()
    db.add_all(
        [
            AttributionResult(
                conversion_id=row["conversion_id"],
                model_name=model,
                touchpoint_id=row["touchpoint_id"],
                channel_id=row["channel_id"],
                campaign_id=row["campaign_id"],
                credit_share=Decimal(str(row["credit_share"])),
                attributed_revenue=Decimal(str(row["attributed_revenue"])).quantize(Decimal("0.000001")),
            )
            for row in credits
        ]
    )
    db.commit()


def read_cached_attribution(db: Session, model: str) -> list[dict[str, Any]] | None:
    cached = db.scalars(
        select(AttributionResult)
        .where(AttributionResult.model_name == model)
        .options(
            joinedload(AttributionResult.conversion),
            joinedload(AttributionResult.channel),
            joinedload(AttributionResult.campaign),
        )
    ).unique().all()
    if not cached:
        return None
    return [
        {
            "conversion_id": row.conversion_id,
            "conversion_date": row.conversion.conversion_date,
            "channel": row.channel.name if row.channel else "Unknown",
            "campaign": row.campaign.name if row.campaign else "Unassigned",
            "credit_share": float(row.credit_share),
            "attributed_revenue": float(row.attributed_revenue),
        }
        for row in cached
    ]


def aggregate_credits(
    credits: list[dict[str, Any]],
    group_by: str = "channel",
) -> list[dict[str, Any]]:
    field_map = {"channel": "channel", "campaign": "campaign", "date": "conversion_date"}
    if group_by not in field_map:
        raise ValueError("group_by must be one of channel, campaign, or date.")
    grouped: dict[str, dict[str, Any]] = {}
    for row in credits:
        value = row[field_map[group_by]]
        if group_by == "date":
            key = value.date().isoformat()
        else:
            key = value or ("Unassigned" if group_by == "campaign" else "Unknown")
        bucket = grouped.setdefault(
            key,
            {"attributed_revenue": 0.0, "credit_share": 0.0, "_conversion_ids": set()},
        )
        bucket["attributed_revenue"] += float(row["attributed_revenue"])
        bucket["credit_share"] += float(row["credit_share"])
        bucket["_conversion_ids"].add(row["conversion_id"])
    return [
        {
            "key": key,
            "attributed_revenue": value["attributed_revenue"],
            "credit_share": value["credit_share"],
            "conversions": len(value["_conversion_ids"]),
        }
        for key, value in sorted(grouped.items())
    ]


def campaign_conversion_stats(
    db: Session,
    campaigns: list[Campaign],
    *,
    date_from: date | None = None,
    date_to: date | None = None,
) -> dict[int, dict[str, Any]]:
    campaign_ids = {campaign.id for campaign in campaigns}
    if not campaign_ids:
        return {}
    query = (
        select(Conversion, Touchpoint.campaign_id)
        .join(Touchpoint, Conversion.touchpoint_id == Touchpoint.id)
        .where(Touchpoint.campaign_id.in_(campaign_ids))
    )
    start, end = date_bounds(date_from, date_to)
    if start:
        query = query.where(Conversion.conversion_date >= start)
    if end:
        query = query.where(Conversion.conversion_date < end)
    stats: dict[int, dict[str, Any]] = {}
    for conversion, campaign_key in db.execute(query):
        if campaign_key is None:
            continue
        data = stats.setdefault(campaign_key, {"conversions": 0, "revenue": 0.0})
        data["conversions"] += 1
        data["revenue"] += float(conversion.revenue)
    return stats


def channel_maps(db: Session) -> tuple[dict[int, str], dict[int, str]]:
    channels = list(db.scalars(select(Channel)).all())
    return ({item.id: item.name for item in channels}, {item.id: item.name for item in channels})


def attributed_revenue_by_channel(
    credits: list[dict[str, Any]], channel_name: str | None = None
) -> dict[str, float]:
    totals: dict[str, float] = {}
    for row in credits:
        name = row["channel"] or "Unknown"
        if channel_name and name != channel_name:
            continue
        totals[name] = totals.get(name, 0.0) + float(row["attributed_revenue"])
    return totals
