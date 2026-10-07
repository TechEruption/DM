from pydantic import BaseModel


class DashboardSummary(BaseModel):
    dataset_label: str
    is_demo_dataset: bool
    currency: str
    attribution_model: str
    total_revenue: float
    total_attributed_revenue: float
    total_conversions: int
    total_spend: float
    impressions: int
    clicks: int
    ctr: float
    cpc: float | None
    conversion_rate: float
    cac: float | None
    aov: float | None
    roas: float | None
    roi: float | None


class DashboardTrend(BaseModel):
    period: str
    revenue: float
    conversions: float
    spend: float
    attributed_revenue: float


class DashboardTrendResponse(BaseModel):
    dataset_label: str
    is_demo_dataset: bool
    attribution_model: str
    trends: list[DashboardTrend]
