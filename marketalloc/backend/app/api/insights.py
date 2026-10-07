from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db_session
from app.schemas.insights import InsightsResponse
from app.services.analytics_service import calculate_dataset_attribution, load_campaigns
from app.services.attribution_engine import normalize_model
from app.services.funnel_analyzer import analyze_funnel
from app.services.insight_engine import generate_insights
from app.services.budget_optimizer import optimize_budget
from app.services.performance_service import campaign_rows, channel_rows, conversion_totals

router = APIRouter(prefix="/api/insights", tags=["insights"])


@router.get("", summary="Generate deterministic marketing insights", response_model=InsightsResponse)
def list_insights(
    attribution_model: str = "linear",
    date_from: date | None = None,
    date_to: date | None = None,
    channel_id: int | None = Query(default=None, gt=0),
    campaign_id: str | None = None,
    db: Session = Depends(get_db_session),
):
    model = normalize_model(attribution_model)
    performance = channel_rows(
        db,
        model=model,
        date_from=date_from,
        date_to=date_to,
        channel_id=channel_id,
        campaign_id=campaign_id,
    )
    campaigns_performance = campaign_rows(
        db,
        model=model,
        date_from=date_from,
        date_to=date_to,
        channel_id=channel_id,
        campaign_id=campaign_id,
    )
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
    funnel = analyze_funnel(
        impressions=sum(row.impressions for row in campaigns),
        clicks=sum(row.clicks for row in campaigns),
        sessions=sum(row.sessions for row in campaigns),
        product_views=sum(row.product_views for row in campaigns),
        leads=sum(row.leads for row in campaigns),
        conversions=conversions,
        revenue=revenue,
    )
    comparison = []
    for candidate in ("first_touch", "last_touch"):
        credits = calculate_dataset_attribution(
            db,
            candidate,
            date_from=date_from,
            date_to=date_to,
            channel_id=channel_id,
            campaign_id=campaign_id,
        )
        totals = {}
        for credit in credits:
            channel = credit["channel"] or "Unknown"
            totals[channel] = totals.get(channel, 0.0) + credit["attributed_revenue"]
        comparison.extend(
            {"model": candidate, "channel": channel, "attributed_revenue": amount}
            for channel, amount in totals.items()
        )
    budget_result = None
    current_spend = sum(row["spend"] for row in performance)
    if current_spend > 0:
        budget_result = optimize_budget(performance, current_spend)
    insights = generate_insights(
        performance,
        funnel,
        comparison,
        budget_result=budget_result,
        campaign_metrics=campaigns_performance,
    )
    return {"attribution_model": model, "count": len(insights), "insights": insights}
