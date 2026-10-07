from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Customer


class CustomerRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_external_id(self, customer_id: str) -> Customer | None:
        return self.db.scalar(select(Customer).where(Customer.customer_id == customer_id))
