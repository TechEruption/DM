from datetime import datetime

from pydantic import BaseModel, Field, model_validator


class BudgetOptimizationRequest(BaseModel):
    total_budget: float = Field(..., gt=0, allow_inf_nan=False)
    attribution_model: str = "linear"
    min_allocations: dict[str, float] = Field(default_factory=dict)
    max_allocations: dict[str, float] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_constraints(self):
        if any(value < 0 for value in self.min_allocations.values()):
            raise ValueError("Minimum allocations cannot be negative.")
        if any(value < 0 for value in self.max_allocations.values()):
            raise ValueError("Maximum allocations cannot be negative.")
        for channel in self.min_allocations.keys() & self.max_allocations.keys():
            if self.min_allocations[channel] > self.max_allocations[channel]:
                raise ValueError(f"Minimum allocation exceeds maximum for channel '{channel}'.")
        return self


class BudgetScenarioRequest(BudgetOptimizationRequest):
    scenario_name: str = Field(default="Scenario", min_length=1, max_length=128)


class BudgetRecommendation(BaseModel):
    channel: str
    current_allocation: float
    recommended_allocation: float
    allocation_change: float
    projected_revenue: float
    projected_conversions: float
    projected_roas: float | None
    projected_roi: float | None
    projected_cac: float | None


class BudgetOptimizationResponse(BaseModel):
    forecast_label: str
    attribution_model: str
    total_budget: float
    current_allocation: float
    recommended_allocation: float
    projected_revenue: float
    projected_conversions: float
    projected_roas: float | None
    projected_roi: float | None
    projected_cac: float | None
    channels: list[BudgetRecommendation]
    method: str
    scenario_id: int | None = None
    scenario_name: str | None = None


class SavedRecommendationsResponse(BaseModel):
    scenario_id: int | None = None
    scenario_name: str | None = None
    created_at: datetime | None = None
    recommendations: list[BudgetRecommendation]
    projected: dict[str, float | None] | None = None
    message: str | None = None
