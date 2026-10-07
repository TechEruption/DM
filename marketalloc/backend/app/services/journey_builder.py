from datetime import datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models import Conversion, Customer, Touchpoint


def build_customer_journey(db: Session, customer_id: str) -> dict[str, Any] | None:
    customer = db.scalar(select(Customer).where(Customer.customer_id == customer_id))
    if customer is None:
        return None
    points = db.scalars(
        select(Touchpoint)
        .where(Touchpoint.customer_id == customer.id)
        .options(joinedload(Touchpoint.channel), joinedload(Touchpoint.campaign))
        .order_by(Touchpoint.timestamp, Touchpoint.id)
    ).all()
    conversions = db.scalars(
        select(Conversion)
        .where(Conversion.customer_id == customer.id)
        .order_by(Conversion.conversion_date, Conversion.id)
    ).all()
    by_session: dict[str, list[Touchpoint]] = {}
    for point in points:
        by_session.setdefault(point.session_id, []).append(point)
    journeys = []
    for session_id, session_points in sorted(
        by_session.items(), key=lambda entry: (entry[1][0].timestamp, entry[0])
    ):
        session_conversions = [conversion for conversion in conversions if conversion.session_id == session_id]
        journeys.append(
            {
                "session_id": session_id,
                "touchpoints": [
                    {
                        "id": point.external_id,
                        "timestamp": point.timestamp,
                        "channel": point.channel.name if point.channel else None,
                        "campaign": point.campaign.name if point.campaign else None,
                        "campaign_id": point.campaign.campaign_id if point.campaign else None,
                        "touchpoint_type": point.touchpoint_type,
                    }
                    for point in session_points
                ],
                "conversions": [
                    {
                        "order_id": conversion.order_id,
                        "timestamp": conversion.conversion_date,
                        "revenue": float(conversion.revenue),
                        "touchpoint_id": conversion.touchpoint.external_id if conversion.touchpoint else None,
                    }
                    for conversion in session_conversions
                ],
                "converted": bool(session_conversions),
            }
        )
    return {
        "customer_id": customer.customer_id,
        "segment": customer.segment,
        "is_demo": customer.is_demo,
        "journeys": journeys,
        "conversion_count": len(conversions),
        "total_revenue": sum(float(conversion.revenue) for conversion in conversions),
    }


def conversion_journey(
    conversion: Conversion,
    touchpoints: list[Touchpoint],
) -> list[dict[str, Any]]:
    """Select same-session interactions up to conversion, with stable timestamp ordering."""
    matching = [
        point
        for point in touchpoints
        if point.customer_id == conversion.customer_id
        and point.session_id == conversion.session_id
        and point.timestamp <= conversion.conversion_date
    ]
    matching.sort(key=lambda point: (point.timestamp or datetime.min, point.id))
    return [
        {
            "id": point.id,
            "channel": point.channel.name if point.channel else None,
            "channel_id": point.channel_id,
            "campaign": point.campaign.name if point.campaign else None,
            "campaign_id": point.campaign_id,
            "timestamp": point.timestamp.isoformat() if point.timestamp else "",
        }
        for point in matching
    ]
