from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db_session
from app.schemas.campaign import CampaignListResponse, CampaignSummary
from app.services.analytics_service import dataset_metadata
from app.services.attribution_engine import normalize_model
from app.services.performance_service import campaign_rows

router = APIRouter(prefix="/api/campaigns", tags=["campaigns"])


@router.get("", summary="Search and list campaign performance", response_model=CampaignListResponse)
def list_campaigns(
    search: str | None = None,
    channel_id: int | None = Query(default=None, gt=0),
    campaign_id: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    attribution_model: str = Query("linear"),
    sort_by: str = Query("spend", pattern="^(campaign_name|spend|revenue|attributed_revenue|conversions|roas|cac|ctr)$"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$"),
    db: Session = Depends(get_db_session),
):
    try:
        model = normalize_model(attribution_model)
        rows = campaign_rows(
            db,
            model=model,
            date_from=date_from,
            date_to=date_to,
            channel_id=channel_id,
            campaign_id=campaign_id,
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    if search:
        needle = search.strip().casefold()
        rows = [
            row for row in rows
            if needle in row["campaign_name"].casefold()
            or needle in row["campaign_id"].casefold()
            or needle in row["channel"].casefold()
        ]
    rows.sort(key=lambda row: row.get(sort_by) or 0, reverse=sort_order == "desc")
    rows.sort(key=lambda row: row.get(sort_by) is None)
    return {
        "attribution_model": model,
        **dataset_metadata(rows),
        "count": len(rows),
        "campaigns": rows,
    }


@router.get("/{campaign_id}", summary="Get campaign performance", response_model=CampaignSummary)
def get_campaign(
    campaign_id: str,
    attribution_model: str = Query("linear"),
    db: Session = Depends(get_db_session),
):
    try:
        rows = campaign_rows(db, model=normalize_model(attribution_model), campaign_id=campaign_id)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    if not rows:
        raise HTTPException(status_code=404, detail="Campaign not found.")
    return rows[0]
