from datetime import datetime

from pydantic import BaseModel


class JourneyTouchpoint(BaseModel):
    id: str
    timestamp: datetime
    channel: str | None
    campaign: str | None
    campaign_id: str | None
    touchpoint_type: str


class JourneyConversion(BaseModel):
    order_id: str
    timestamp: datetime
    revenue: float
    touchpoint_id: str | None


class JourneySession(BaseModel):
    session_id: str
    touchpoints: list[JourneyTouchpoint]
    conversions: list[JourneyConversion]
    converted: bool


class CustomerJourneyResponse(BaseModel):
    customer_id: str
    segment: str
    is_demo: bool
    journeys: list[JourneySession]
    conversion_count: int
    total_revenue: float
