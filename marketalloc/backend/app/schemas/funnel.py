from pydantic import BaseModel


class FunnelStage(BaseModel):
    key: str
    stage: str
    count: int | float
    unit: str | None = None
    conversion_rate_from_previous: float | None
    drop_off_rate: float | None


class FunnelLeakage(BaseModel):
    from_stage: str
    to_stage: str
    drop_off_rate: float


class FunnelResponse(BaseModel):
    currency: str
    stages: list[FunnelStage]
    largest_leakage: FunnelLeakage | None
