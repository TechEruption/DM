from typing import Any

from pydantic import BaseModel


class Insight(BaseModel):
    type: str
    title: str
    description: str
    metric: dict[str, Any]
    severity: str
    recommended_action: str


class InsightsResponse(BaseModel):
    attribution_model: str
    count: int
    insights: list[Insight]
