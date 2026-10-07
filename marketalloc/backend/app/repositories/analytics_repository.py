from datetime import date, datetime, time, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models import AttributionResult, Conversion


class AnalyticsRepository:
    def __init__(self, db: Session):
        self.db = db

    def attribution_results(
        self,
        model_name: str,
        *,
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> list[AttributionResult]:
        query = (
            select(AttributionResult)
            .join(Conversion, AttributionResult.conversion_id == Conversion.id)
            .options(joinedload(AttributionResult.conversion))
            .where(AttributionResult.model_name == model_name)
        )
        if date_from is not None:
            query = query.where(
                Conversion.conversion_date >= datetime.combine(date_from, time.min, tzinfo=timezone.utc)
            )
        if date_to is not None:
            query = query.where(
                Conversion.conversion_date
                < datetime.combine(date_to + timedelta(days=1), time.min, tzinfo=timezone.utc)
            )
        return list(self.db.scalars(query.order_by(AttributionResult.id)).unique().all())
