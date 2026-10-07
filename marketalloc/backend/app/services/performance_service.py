from datetime import date
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Campaign, Channel, Conversion, Touchpoint
from app.services.analytics_service import (
    calculate_dataset_attribution,
    campaign_conversion_stats,
    load_campaigns,
    resolve_campaign_pk,
)
from app.services.attribution_engine import normalize_model
from app.services.marketing_metrics import calculate_metrics


def campaign_rows(
    db: Session,
    *,
    model: str = "linear",
    date_from: date | None = None,
    date_to: date | None = None,
    channel_id: int | None = None,
    campaign_id: str | int | None = None,
) -> list[dict[str, Any]]:
    model_key = normalize_model(model)
    campaigns = load_campaigns(
        db,
        date_from=date_from,
        date_to=date_to,
        channel_id=channel_id,
        campaign_id=campaign_id,
    )
    conversion_stats = campaign_conversion_stats(db, campaigns, date_from=date_from, date_to=date_to)
    credits = calculate_dataset_attribution(
        db,
        model_key,
        date_from=date_from,
        date_to=date_to,
        channel_id=channel_id,
        campaign_id=campaign_id,
    )
    credited: dict[int, float] = {}
    for credit in credits:
        if credit["campaign_id"] is not None:
            credited[credit["campaign_id"]] = credited.get(credit["campaign_id"], 0.0) + credit["attributed_revenue"]

    rows = []
    for campaign in campaigns:
        stats = conversion_stats.get(campaign.id, {"conversions": 0, "revenue": 0.0})
        revenue = float(stats["revenue"])
        attributed_revenue = credited.get(campaign.id, 0.0)
        spend = float(campaign.spend)
        metrics = calculate_metrics(
            spend=spend,
            impressions=campaign.impressions,
            clicks=campaign.clicks,
            conversions=stats["conversions"],
            revenue=revenue,
            attributed_revenue=attributed_revenue,
        )
        rows.append(
            {
                "campaign_id": campaign.campaign_id,
                "campaign_name": campaign.name,
                "channel": campaign.channel.name,
                "channel_id": campaign.channel_id,
                "objective": campaign.objective,
                "spend": spend,
                "impressions": campaign.impressions,
                "clicks": campaign.clicks,
                "sessions": campaign.sessions,
                "product_views": campaign.product_views,
                "leads": campaign.leads,
                "conversions": stats["conversions"],
                "revenue": round(revenue, 2),
                "attributed_revenue": round(attributed_revenue, 2),
                "start_date": campaign.start_date,
                "end_date": campaign.end_date,
                "is_demo": campaign.is_demo,
                **metrics,
            }
        )
    return rows


def channel_rows(
    db: Session,
    *,
    model: str = "linear",
    date_from: date | None = None,
    date_to: date | None = None,
    channel_id: int | None = None,
    campaign_id: str | int | None = None,
) -> list[dict[str, Any]]:
    channels_query = select(Channel).order_by(Channel.name)
    if channel_id:
        channels_query = channels_query.where(Channel.id == channel_id)
    channels = list(db.scalars(channels_query).unique().all())
    campaigns = load_campaigns(
        db,
        date_from=date_from,
        date_to=date_to,
        channel_id=channel_id,
        campaign_id=campaign_id,
    )
    metrics_by_campaign = campaign_rows(
        db,
        model=model,
        date_from=date_from,
        date_to=date_to,
        channel_id=channel_id,
        campaign_id=campaign_id,
    )
    campaigns_by_channel: dict[int, list[dict[str, Any]]] = {}
    for row in metrics_by_campaign:
        campaigns_by_channel.setdefault(row["channel_id"], []).append(row)

    rows = []
    for channel in channels:
        items = campaigns_by_channel.get(channel.id, [])
        spend = sum(row["spend"] for row in items)
        impressions = sum(row["impressions"] for row in items)
        clicks = sum(row["clicks"] for row in items)
        conversions = sum(row["conversions"] for row in items)
        revenue = sum(row["revenue"] for row in items)
        attributed_revenue = sum(row["attributed_revenue"] for row in items)
        metrics = calculate_metrics(
            spend=spend,
            impressions=impressions,
            clicks=clicks,
            conversions=conversions,
            revenue=revenue,
            attributed_revenue=attributed_revenue,
        )
        rows.append(
            {
                "channel_id": channel.id,
                "channel": channel.name,
                "description": channel.description,
                "is_demo": channel.is_demo or (bool(items) and all(row["is_demo"] for row in items)),
                "spend": round(spend, 2),
                "impressions": impressions,
                "clicks": clicks,
                "sessions": sum(row["sessions"] for row in items),
                "product_views": sum(row["product_views"] for row in items),
                "leads": sum(row["leads"] for row in items),
                "conversions": conversions,
                "revenue": round(revenue, 2),
                "attributed_revenue": round(attributed_revenue, 2),
                **metrics,
            }
        )
    return rows


def conversion_totals(
    db: Session,
    *,
    date_from: date | None = None,
    date_to: date | None = None,
    channel_id: int | None = None,
    campaign_id: str | int | None = None,
) -> tuple[int, float]:
    query = (
        select(Conversion)
        .options(joinedload(Conversion.touchpoint))
        .order_by(Conversion.conversion_date)
    )
    if date_from:
        from datetime import datetime, time, timezone

        query = query.where(
            Conversion.conversion_date >= datetime.combine(date_from, time.min, tzinfo=timezone.utc)
        )
    if date_to:
        from datetime import datetime, time, timedelta, timezone

        query = query.where(
            Conversion.conversion_date
            < datetime.combine(date_to + timedelta(days=1), time.min, tzinfo=timezone.utc)
        )
    conversions = list(db.scalars(query).unique().all())
    campaign_pk = resolve_campaign_pk(db, campaign_id)
    if campaign_id is not None and campaign_pk is None:
        return 0, 0.0
    if channel_id or campaign_id:
        conversions = [
            conversion
            for conversion in conversions
            if conversion.touchpoint
            and (channel_id is None or conversion.touchpoint.channel_id == channel_id)
            and (campaign_pk is None or conversion.touchpoint.campaign_id == campaign_pk)
        ]
    return len(conversions), round(sum(float(conversion.revenue) for conversion in conversions), 2)
