from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.core.database import get_db_session
from app.models import Conversion
from app.schemas.dashboard import DashboardSummary, DashboardTrendResponse
from app.services.analytics_service import (
    calculate_dataset_attribution,
    dataset_metadata,
    date_bounds,
    load_campaigns,
    resolve_campaign_pk,
)
from app.services.attribution_engine import normalize_model
from app.services.marketing_metrics import calculate_metrics
from app.services.performance_service import conversion_totals

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/summary", summary="Get executive dashboard KPIs", response_model=DashboardSummary)
def dashboard_summary(
    date_from: date | None = None,
    date_to: date | None = None,
    attribution_model: str = "linear",
    channel_id: int | None = Query(default=None, gt=0),
    campaign_id: str | None = None,
    db: Session = Depends(get_db_session),
):
    attribution_model = normalize_model(attribution_model)
    campaigns = load_campaigns(
        db,
        date_from=date_from,
        date_to=date_to,
        channel_id=channel_id,
        campaign_id=campaign_id,
    )
    spend = sum(float(item.spend) for item in campaigns)
    impressions = sum(item.impressions for item in campaigns)
    clicks = sum(item.clicks for item in campaigns)
    conversions, revenue = conversion_totals(
        db,
        date_from=date_from,
        date_to=date_to,
        channel_id=channel_id,
        campaign_id=campaign_id,
    )
    credits = calculate_dataset_attribution(
        db,
        attribution_model,
        date_from=date_from,
        date_to=date_to,
        channel_id=channel_id,
        campaign_id=campaign_id,
    )
    attributed_revenue = sum(float(item["attributed_revenue"]) for item in credits)
    metrics = calculate_metrics(
        spend=spend,
        impressions=impressions,
        clicks=clicks,
        conversions=conversions,
        revenue=revenue,
        attributed_revenue=attributed_revenue,
    )
    return {
        **dataset_metadata(campaigns),
        "currency": "INR",
        "attribution_model": attribution_model,
        "total_spend": round(spend, 2),
        "total_revenue": revenue,
        "total_attributed_revenue": round(attributed_revenue, 2),
        "total_conversions": conversions,
        "impressions": impressions,
        "clicks": clicks,
        **metrics,
    }


@router.get("/trends", summary="Get marketing performance time series", response_model=DashboardTrendResponse)
def dashboard_trends(
    date_from: date | None = None,
    date_to: date | None = None,
    attribution_model: str = "linear",
    channel_id: int | None = Query(default=None, gt=0),
    campaign_id: str | None = None,
    db: Session = Depends(get_db_session),
):
    attribution_model = normalize_model(attribution_model)
    campaigns = load_campaigns(
        db,
        date_from=date_from,
        date_to=date_to,
        channel_id=channel_id,
        campaign_id=campaign_id,
    )
    credits = calculate_dataset_attribution(
        db,
        attribution_model,
        date_from=date_from,
        date_to=date_to,
        channel_id=channel_id,
        campaign_id=campaign_id,
    )
    periods: dict[str, dict[str, float]] = {}
    for campaign in campaigns:
        period = campaign.start_date.strftime("%Y-%m")
        bucket = periods.setdefault(period, {"spend": 0.0, "revenue": 0.0, "attributed_revenue": 0.0, "conversions": 0})
        bucket["spend"] += float(campaign.spend)
    for credit in credits:
        period = credit["conversion_date"].strftime("%Y-%m")
        bucket = periods.setdefault(period, {"spend": 0.0, "revenue": 0.0, "attributed_revenue": 0.0, "conversions": 0})
        bucket["attributed_revenue"] += float(credit["attributed_revenue"])
    start, end = date_bounds(date_from, date_to)
    query = select(Conversion).options(joinedload(Conversion.touchpoint))
    if start:
        query = query.where(Conversion.conversion_date >= start)
    if end:
        query = query.where(Conversion.conversion_date < end)
    conversions = list(db.scalars(query).all())
    campaign_pk = resolve_campaign_pk(db, campaign_id)
    if campaign_id is not None and campaign_pk is None:
        conversions = []
    elif channel_id or campaign_id:
        qualifying_ids = set()
        for conversion in conversions:
            point = conversion.touchpoint
            if point and (channel_id is None or point.channel_id == channel_id) and (
                campaign_pk is None or point.campaign_id == campaign_pk
            ):
                qualifying_ids.add(conversion.id)
        conversions = [conversion for conversion in conversions if conversion.id in qualifying_ids]
    for conversion in conversions:
        period = conversion.conversion_date.strftime("%Y-%m")
        bucket = periods.setdefault(period, {"spend": 0.0, "revenue": 0.0, "attributed_revenue": 0.0, "conversions": 0})
        bucket["revenue"] += float(conversion.revenue)
        bucket["conversions"] += 1
    return {
        **dataset_metadata(campaigns),
        "attribution_model": attribution_model,
        "trends": [
            {
                "period": period,
                "spend": round(values["spend"], 2),
                "revenue": round(values["revenue"], 2),
                "attributed_revenue": round(values["attributed_revenue"], 2),
                "conversions": int(values["conversions"]),
            }
            for period, values in sorted(periods.items())
        ],
    }
