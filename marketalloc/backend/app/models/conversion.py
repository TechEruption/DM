from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Conversion(Base):
    __tablename__ = "conversions"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[str] = mapped_column(String(128), unique=True, nullable=False, index=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id", ondelete="CASCADE"), index=True, nullable=False)
    touchpoint_id: Mapped[int | None] = mapped_column(ForeignKey("touchpoints.id", ondelete="SET NULL"), unique=True)
    session_id: Mapped[str] = mapped_column(String(128), index=True, nullable=False)
    conversion_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True, nullable=False)
    revenue: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    is_demo: Mapped[bool] = mapped_column(default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    customer: Mapped["Customer"] = relationship(back_populates="conversions")
    touchpoint: Mapped["Touchpoint | None"] = relationship(back_populates="conversion")
