from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db_session
from app.schemas.journey import CustomerJourneyResponse
from app.services.journey_builder import build_customer_journey

router = APIRouter(prefix="/api/customers", tags=["customers"])


@router.get("/{customer_id}/journey", summary="Get chronological customer journey", response_model=CustomerJourneyResponse)
def customer_journey(customer_id: str, db: Session = Depends(get_db_session)):
    journey = build_customer_journey(db, customer_id)
    if journey is None:
        raise HTTPException(status_code=404, detail="Customer not found.")
    return journey
