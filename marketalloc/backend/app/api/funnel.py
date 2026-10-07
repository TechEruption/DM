from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db_session
from app.schemas.funnel import FunnelResponse
from app.services.analytics_service import load_campaigns
from app.services.funnel_analyzer import analyze_funnel
from app.services.performance_service import conversion_totals

router = APIRouter(prefix="/api/funnel", tags=["funnel"])


@router.get("", summary="Analyze marketing funnel stages and leakage", response_model=FunnelResponse)
def funnel_overview(
    date_from: date | None = None,
    date_to: date | None = None,
    channel_id: int | None = Query(default=None, gt=0),
    campaign_id: str | None = None,
    db: Session = Depends(get_db_session),
):
    campaigns = load_campaigns(
        db,
        date_from=date_from,
        date_to=date_to,
        channel_id=channel_id,
        campaign_id=campaign_id,
    )
    conversions, revenue = conversion_totals(
        db,
        date_from=date_from,
        date_to=date_to,
        channel_id=channel_id,
        campaign_id=campaign_id,
    )
    result = analyze_funnel(
        impressions=sum(row.impressions for row in campaigns),
        clicks=sum(row.clicks for row in campaigns),
        sessions=sum(row.sessions for row in campaigns),
        product_views=sum(row.product_views for row in campaigns),
        leads=sum(row.leads for row in campaigns),
        conversions=conversions,
        revenue=revenue,
    )
    return {"currency": "INR", **result}
