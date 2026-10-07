from datetime import date
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, model_validator


class FilterParams(BaseModel):
    date_from: date | None = None
    date_to: date | None = None
    channel_id: int | None = Field(default=None, gt=0)
    campaign_id: str | None = Field(default=None, min_length=1)

    @model_validator(mode="after")
    def validate_date_range(self):
        if self.date_from and self.date_to and self.date_from > self.date_to:
            raise ValueError("date_from must be on or before date_to.")
        return self


PositiveMoney = Annotated[float, Field(ge=0)]


class APIModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)
