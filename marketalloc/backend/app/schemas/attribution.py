from datetime import date

from pydantic import AliasChoices, BaseModel, Field, model_validator


class AttributionCalculateRequest(BaseModel):
    attribution_model: str = Field(
        default="linear",
        validation_alias=AliasChoices("attribution_model", "model"),
    )
    date_from: date | None = None
    date_to: date | None = None
    channel_id: int | None = Field(default=None, gt=0)
    campaign_id: str | None = Field(default=None, min_length=1)
    decay_parameter: float = Field(default=0.7, gt=0, le=1)
    first_weight: float = Field(default=0.4, ge=0)
    middle_weight: float = Field(default=0.2, ge=0)
    last_weight: float = Field(default=0.4, ge=0)

    @model_validator(mode="after")
    def validate_inputs(self):
        if self.date_from and self.date_to and self.date_from > self.date_to:
            raise ValueError("date_from must be on or before date_to.")
        if self.first_weight + self.middle_weight + self.last_weight <= 0:
            raise ValueError("Position-based weights must have a positive total.")
        return self


AttributionRequest = AttributionCalculateRequest


class AttributionResult(BaseModel):
    conversion_id: int
    order_id: str
    model: str
    channel: str | None
    campaign: str | None
    credit_share: float
    attributed_revenue: float


class AttributionAggregate(BaseModel):
    key: str
    attributed_revenue: float
    credit_share: float
    conversions: int


class AttributionCalculateResponse(BaseModel):
    attribution_model: str
    model_label: str
    conversion_count: int
    touchpoint_credit_count: int
    total_attributed_revenue: float
    results: list[AttributionAggregate]


class AttributionResultsResponse(BaseModel):
    attribution_model: str
    group_by: str
    conversion_count: int
    results: list[AttributionAggregate]


class AttributionComparisonRow(BaseModel):
    model: str
    model_label: str
    key: str
    channel: str | None
    attributed_revenue: float
    credit_share: float
    conversion_count: int


class AttributionComparisonResponse(BaseModel):
    group_by: str
    models: list[str]
    results: list[AttributionComparisonRow]
