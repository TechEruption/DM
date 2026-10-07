from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db_session
from app.schemas.channel import ChannelDetailResponse, ChannelListResponse
from app.services.analytics_service import dataset_metadata, load_campaigns
from app.services.attribution_engine import normalize_model
from app.services.performance_service import channel_rows

router = APIRouter(prefix="/api/channels", tags=["channels"])


@router.get("", summary="List channel performance", response_model=ChannelListResponse)
def list_channels(
    attribution_model: str = Query("linear"),
    date_from: date | None = None,
    date_to: date | None = None,
    campaign_id: str | None = None,
    db: Session = Depends(get_db_session),
):
    try:
        model = normalize_model(attribution_model)
        return {
            "attribution_model": model,
            **dataset_metadata(
                load_campaigns(
                    db,
                    date_from=date_from,
                    date_to=date_to,
                    campaign_id=campaign_id,
                )
            ),
            "channels": channel_rows(
                db,
                model=model,
                date_from=date_from,
                date_to=date_to,
                campaign_id=campaign_id,
            ),
        }
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@router.get("/{channel_id}", summary="Get channel performance", response_model=ChannelDetailResponse)
def get_channel(
    channel_id: int,
    attribution_model: str = Query("linear"),
    date_from: date | None = None,
    date_to: date | None = None,
    campaign_id: str | None = None,
    db: Session = Depends(get_db_session),
):
    try:
        model = normalize_model(attribution_model)
        rows = channel_rows(
            db,
            model=model,
            date_from=date_from,
            date_to=date_to,
            channel_id=channel_id,
            campaign_id=campaign_id,
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    if not rows:
        raise HTTPException(status_code=404, detail="Channel not found.")
    return {"attribution_model": model, **rows[0]}
