from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Touchpoint(Base):
    __tablename__ = "touchpoints"
    __table_args__ = (Index("ix_touchpoints_customer_timestamp", "customer_id", "timestamp"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    external_id: Mapped[str] = mapped_column(String(128), unique=True, index=True, nullable=False)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id", ondelete="CASCADE"), index=True, nullable=False)
    channel_id: Mapped[int | None] = mapped_column(ForeignKey("channels.id", ondelete="SET NULL"), index=True)
    campaign_id: Mapped[int | None] = mapped_column(ForeignKey("campaigns.id", ondelete="SET NULL"), index=True)
    session_id: Mapped[str] = mapped_column(String(128), index=True, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    touchpoint_type: Mapped[str] = mapped_column(String(64), default="visit", nullable=False)
    is_demo: Mapped[bool] = mapped_column(default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    customer: Mapped["Customer"] = relationship(back_populates="touchpoints")
    channel: Mapped["Channel | None"] = relationship(back_populates="touchpoints")
    campaign: Mapped["Campaign | None"] = relationship(back_populates="touchpoints")
    conversion: Mapped["Conversion | None"] = relationship(back_populates="touchpoint", uselist=False)
