from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Index, Numeric, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class AttributionResult(Base):
    __tablename__ = "attribution_results"
    __table_args__ = (
        UniqueConstraint("conversion_id", "model_name", "touchpoint_id", name="uq_attribution_touchpoint_credit"),
        Index("ix_attribution_model_channel", "model_name", "channel_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    conversion_id: Mapped[int] = mapped_column(ForeignKey("conversions.id", ondelete="CASCADE"), index=True, nullable=False)
    model_name: Mapped[str] = mapped_column(String(32), index=True, nullable=False)
    touchpoint_id: Mapped[int | None] = mapped_column(ForeignKey("touchpoints.id", ondelete="SET NULL"), index=True)
    channel_id: Mapped[int | None] = mapped_column(ForeignKey("channels.id", ondelete="SET NULL"), index=True)
    campaign_id: Mapped[int | None] = mapped_column(ForeignKey("campaigns.id", ondelete="SET NULL"), index=True)
    credit_share: Mapped[Decimal] = mapped_column(Numeric(12, 10), nullable=False)
    attributed_revenue: Mapped[Decimal] = mapped_column(Numeric(18, 6), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    conversion: Mapped["Conversion"] = relationship()
    channel: Mapped["Channel | None"] = relationship()
    campaign: Mapped["Campaign | None"] = relationship()
