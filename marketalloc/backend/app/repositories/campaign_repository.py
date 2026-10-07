from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models import Campaign


class CampaignRepository:
    def __init__(self, db: Session):
        self.db = db

    def get(self, campaign_id: int) -> Campaign | None:
        return self.db.scalar(
            select(Campaign)
            .where(Campaign.id == campaign_id)
            .options(joinedload(Campaign.channel))
        )

    def list(self, *, channel_id: int | None = None) -> list[Campaign]:
        query = select(Campaign).options(joinedload(Campaign.channel)).order_by(Campaign.name)
        if channel_id is not None:
            query = query.where(Campaign.channel_id == channel_id)
        return list(self.db.scalars(query).unique().all())
