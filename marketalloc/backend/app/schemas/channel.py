from pydantic import BaseModel


class ChannelPerformance(BaseModel):
    channel_id: int
    channel: str
    description: str
    is_demo: bool
    spend: float
    impressions: int
    clicks: int
    sessions: int
    product_views: int
    leads: int
    conversions: int
    revenue: float
    attributed_revenue: float
    ctr: float
    cpc: float | None
    conversion_rate: float
    cac: float | None
    aov: float | None
    roas: float | None
    roi: float | None


class ChannelListResponse(BaseModel):
    dataset_label: str
    is_demo_dataset: bool
    attribution_model: str
    channels: list[ChannelPerformance]


class ChannelDetailResponse(ChannelPerformance):
    attribution_model: str
