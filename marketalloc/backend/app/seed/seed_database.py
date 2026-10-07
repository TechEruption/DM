from pathlib import Path

from sqlalchemy import select

from app.core.database import Base, SessionLocal, engine
from app.models import AttributionResult, BudgetScenario, Campaign, Channel, Conversion, Customer, Touchpoint
from app.utils.csv_loader import import_csv_data


SEED_DIR = Path(__file__).resolve().parent


def seed_database() -> dict[str, int]:
    Base.metadata.create_all(bind=engine)
    results = {}
    with SessionLocal() as db:
        # Import order honors the relational dependencies.
        for kind in ("channels", "campaigns", "customers", "touchpoints"):
            path = SEED_DIR / f"{kind}.csv"
            if not path.is_file():
                raise FileNotFoundError(f"Required demo dataset file is missing: {path}")
            outcome = import_csv_data(db, kind, path.read_bytes())
            results[kind] = outcome["rows_inserted"]
        results["channels_total"] = len(db.scalars(select(Channel)).all())
        results["campaigns_total"] = len(db.scalars(select(Campaign)).all())
        results["customers_total"] = len(db.scalars(select(Customer)).all())
        results["touchpoints_total"] = len(db.scalars(select(Touchpoint)).all())
        results["conversions_total"] = len(db.scalars(select(Conversion)).all())
    return results


if __name__ == "__main__":
    counts = seed_database()
    print("DEMO DATASET seeding complete.")
    for name, count in counts.items():
        print(f"{name}: {count}")
