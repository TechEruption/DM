from datetime import date

from pydantic import BaseModel


class CampaignSummary(BaseModel):
    campaign_id: str
    campaign_name: str
    channel: str
    channel_id: int
    objective: str
    spend: float
    impressions: int
    clicks: int
    ctr: float
    cpc: float | None
    sessions: int
    product_views: int
    leads: int
    conversions: int
    revenue: float
    attributed_revenue: float
    conversion_rate: float
    cac: float | None
    aov: float | None
    roas: float | None
    roi: float | None
    start_date: date
    end_date: date
    is_demo: bool


class CampaignListResponse(BaseModel):
    dataset_label: str
    is_demo_dataset: bool
    attribution_model: str
    count: int
    campaigns: list[CampaignSummary]
