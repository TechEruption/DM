from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    segment: Mapped[str] = mapped_column(String(64), default="Standard", nullable=False)
    is_demo: Mapped[bool] = mapped_column(default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    touchpoints: Mapped[list["Touchpoint"]] = relationship(back_populates="customer", cascade="all, delete-orphan")
    conversions: Mapped[list["Conversion"]] = relationship(back_populates="customer", cascade="all, delete-orphan")
