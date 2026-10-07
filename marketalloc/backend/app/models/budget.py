from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, JSON, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class BudgetScenario(Base):
    __tablename__ = "budget_scenarios"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    attribution_model: Mapped[str] = mapped_column(String(32), nullable=False)
    total_budget: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    constraints: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    results: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
