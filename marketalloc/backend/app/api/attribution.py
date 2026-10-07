from datetime import date
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db_session
from app.schemas.attribution import (
    AttributionCalculateRequest,
    AttributionCalculateResponse,
    AttributionComparisonResponse,
    AttributionResultsResponse,
)
from app.services.analytics_service import (
    aggregate_credits,
    calculate_dataset_attribution,
    persist_attribution,
    read_cached_attribution,
)
from app.services.attribution_engine import MODEL_LABELS, SUPPORTED_MODELS, normalize_model

router = APIRouter(prefix="/api/attribution", tags=["attribution"])


def _calculate(db: Session, payload: AttributionCalculateRequest):
    try:
        model = normalize_model(payload.attribution_model)
        rows = calculate_dataset_attribution(
            db,
            model,
            date_from=payload.date_from,
            date_to=payload.date_to,
            channel_id=payload.channel_id,
            campaign_id=payload.campaign_id,
            decay_parameter=payload.decay_parameter,
            first_weight=payload.first_weight,
            middle_weight=payload.middle_weight,
            last_weight=payload.last_weight,
        )
        return model, rows
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@router.post("/calculate", summary="Calculate and persist attribution credits", response_model=AttributionCalculateResponse)
def calculate_attribution(payload: AttributionCalculateRequest, db: Session = Depends(get_db_session)):
    model, rows = _calculate(db, payload)
    # Persist only the unfiltered standard configuration; custom runs remain reproducible in the response.
    if (
        payload.date_from is None
        and payload.date_to is None
        and payload.channel_id is None
        and payload.campaign_id is None
        and payload.decay_parameter == 0.7
        and (payload.first_weight, payload.middle_weight, payload.last_weight) == (0.4, 0.2, 0.4)
    ):
        persist_attribution(db, rows, model)
    group_by = "channel"
    return {
        "attribution_model": model,
        "model_label": MODEL_LABELS[model],
        "conversion_count": len({row["conversion_id"] for row in rows}),
        "touchpoint_credit_count": len(rows),
        "total_attributed_revenue": round(sum(row["attributed_revenue"] for row in rows), 2),
        "results": aggregate_credits(rows, group_by),
    }


@router.get("/results", summary="Get persisted or calculated attribution results", response_model=AttributionResultsResponse)
def attribution_results(
    attribution_model: str = Query("linear"),
    group_by: str = Query("channel", pattern="^(channel|campaign|date)$"),
    date_from: date | None = None,
    date_to: date | None = None,
    channel_id: int | None = Query(default=None, gt=0),
    campaign_id: str | None = None,
    db: Session = Depends(get_db_session),
):
    try:
        model = normalize_model(attribution_model)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

    rows = []
    if not any((date_from, date_to, channel_id, campaign_id)):
        rows = read_cached_attribution(db, model) or []
    if not rows:
        rows = calculate_dataset_attribution(
            db,
            model,
            date_from=date_from,
            date_to=date_to,
            channel_id=channel_id,
            campaign_id=campaign_id,
        )
        if not any((date_from, date_to, channel_id, campaign_id)):
            persist_attribution(db, rows, model)
    return {
        "attribution_model": model,
        "group_by": group_by,
        "conversion_count": len({row["conversion_id"] for row in rows}),
        "results": aggregate_credits(rows, group_by),
    }


@router.get("/compare", summary="Compare all supported attribution models side by side", response_model=AttributionComparisonResponse)
def attribution_compare(
    date_from: date | None = None,
    date_to: date | None = None,
    group_by: str = Query("channel", pattern="^(channel|campaign|date)$"),
    channel_id: int | None = Query(default=None, gt=0),
    campaign_id: str | None = None,
    db: Session = Depends(get_db_session),
):
    comparison = []
    for model in SUPPORTED_MODELS:
        unfiltered = not any((date_from, date_to, channel_id, campaign_id))
        rows = read_cached_attribution(db, model) if unfiltered else None
        if rows is None:
            rows = calculate_dataset_attribution(
                db,
                model,
                date_from=date_from,
                date_to=date_to,
                channel_id=channel_id,
                campaign_id=campaign_id,
            )
            if unfiltered:
                persist_attribution(db, rows, model)
        for aggregate in aggregate_credits(rows, group_by):
            comparison.append(
                {
                    "model": model,
                    "model_label": MODEL_LABELS[model],
                    "key": aggregate["key"],
                    "channel": aggregate["key"] if group_by == "channel" else None,
                    "attributed_revenue": round(aggregate["attributed_revenue"], 2),
                    "credit_share": round(aggregate["credit_share"], 10),
                    "conversion_count": aggregate["conversions"],
                }
            )
    return {"group_by": group_by, "models": list(SUPPORTED_MODELS), "results": comparison}
