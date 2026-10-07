from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from io import BytesIO
from typing import Any

import pandas as pd
from collections import Counter
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models import AttributionResult, Campaign, Channel, Conversion, Customer, Touchpoint


REQUIRED_COLUMNS = {
    "channels": {"name", "description"},
    "campaigns": {
        "campaign_id", "name", "channel", "objective", "spend", "impressions", "clicks",
        "sessions", "product_views", "leads", "start_date", "end_date",
    },
    "customers": {"customer_id", "segment"},
    "touchpoints": {
        "external_id", "customer_id", "channel", "campaign_id", "session_id", "timestamp",
        "touchpoint_type", "conversion", "revenue", "order_id",
    },
}
IDENTIFIER_COLUMNS = {
    "channels": ["name"],
    "campaigns": ["campaign_id"],
    "customers": ["customer_id"],
    "touchpoints": ["external_id"],
}


class CSVImportError(ValueError):
    pass


def _clean(value: Any) -> str:
    if value is None or pd.isna(value):
        return ""
    return str(value).strip()


def _read_csv(contents: bytes, kind: str) -> list[dict[str, Any]]:
    try:
        frame = pd.read_csv(BytesIO(contents), dtype=str, keep_default_na=False)
    except (pd.errors.ParserError, UnicodeDecodeError, ValueError) as error:
        raise CSVImportError(f"Could not parse {kind}.csv: {error}") from error
    missing = sorted(REQUIRED_COLUMNS[kind] - set(frame.columns))
    if missing:
        raise CSVImportError(f"{kind}.csv is missing required columns: {', '.join(missing)}.")
    if frame.empty:
        raise CSVImportError(f"{kind}.csv contains no data rows.")
    records = frame.to_dict(orient="records")
    errors = []
    for row_number, row in enumerate(records, start=2):
        for column in REQUIRED_COLUMNS[kind]:
            if _clean(row.get(column)) == "" and not (kind == "touchpoints" and column in {"channel", "campaign_id", "order_id"}):
                errors.append(f"row {row_number}: required value '{column}' is missing")
    for column in IDENTIFIER_COLUMNS[kind]:
        identifiers = [_clean(row.get(column)) for row in records]
        duplicates = sorted(value for value, count in Counter(identifiers).items() if value and count > 1)
        if duplicates:
            errors.append(f"duplicate {column} values in file: {', '.join(duplicates[:10])}")
    if kind == "touchpoints":
        converting_rows = [
            row for row in records
            if _clean(row.get("conversion")).lower() in {"true", "1", "yes"}
        ]
        orders = [_clean(row.get("order_id")) for row in converting_rows]
        duplicate_orders = sorted(value for value, count in Counter(orders).items() if value and count > 1)
        if duplicate_orders:
            errors.append(f"duplicate order_id values in file: {', '.join(duplicate_orders[:10])}")
        invalid_flags = [
            str(index + 2) for index, row in enumerate(records)
            if _clean(row.get("conversion")).lower() not in {"true", "false", "1", "0", "yes", "no"}
        ]
        if invalid_flags:
            errors.append(f"conversion must be a boolean on row(s): {', '.join(invalid_flags[:10])}.")
    if errors:
        raise CSVImportError("; ".join(errors))
    return records


def _decimal(value: Any, row_number: int, column: str) -> Decimal:
    try:
        number = Decimal(_clean(value))
    except (InvalidOperation, TypeError) as error:
        raise CSVImportError(f"row {row_number}: '{column}' must be a number.") from error
    if not number.is_finite() or number < 0:
        raise CSVImportError(f"row {row_number}: '{column}' must be a finite non-negative number.")
    return number


def _integer(value: Any, row_number: int, column: str) -> int:
    try:
        number = int(_clean(value))
    except (TypeError, ValueError) as error:
        raise CSVImportError(f"row {row_number}: '{column}' must be a whole number.") from error
    if number < 0:
        raise CSVImportError(f"row {row_number}: '{column}' cannot be negative.")
    return number


def _date(value: Any, row_number: int, column: str):
    try:
        parsed = pd.to_datetime(_clean(value), errors="raise")
        return parsed.date()
    except (ValueError, TypeError) as error:
        raise CSVImportError(f"row {row_number}: '{column}' must be a valid date.") from error


def _datetime(value: Any, row_number: int, column: str) -> datetime:
    try:
        parsed = pd.to_datetime(_clean(value), errors="raise")
        dt = parsed.to_pydatetime()
        return dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else dt
    except (ValueError, TypeError) as error:
        raise CSVImportError(f"row {row_number}: '{column}' must be a valid timestamp.") from error


def import_csv_data(db: Session, kind: str, contents: bytes) -> dict[str, Any]:
    normalized_kind = kind.strip().lower().removesuffix(".csv")
    if normalized_kind not in REQUIRED_COLUMNS:
        raise CSVImportError("dataset_type must be one of channels, campaigns, customers, or touchpoints.")
    rows = _read_csv(contents, normalized_kind)
    try:
        if normalized_kind == "channels":
            inserted = _import_channels(db, rows)
        elif normalized_kind == "customers":
            inserted = _import_customers(db, rows)
        elif normalized_kind == "campaigns":
            inserted = _import_campaigns(db, rows)
        else:
            inserted = _import_touchpoints(db, rows)
        if inserted:
            db.execute(delete(AttributionResult))
        db.commit()
        return {"dataset_type": normalized_kind, "rows_received": len(rows), "rows_inserted": inserted, "rows_skipped_existing": len(rows) - inserted}
    except Exception:
        db.rollback()
        raise


def _import_channels(db: Session, rows: list[dict[str, Any]]) -> int:
    inserted = 0
    for row in rows:
        name = _clean(row["name"])
        if not name:
            raise CSVImportError("Channel name cannot be blank.")
        existing = db.scalar(select(Channel).where(Channel.name == name))
        if existing:
            continue
        db.add(
            Channel(
                name=name,
                description=_clean(row["description"]),
                is_demo=_clean(row.get("is_demo", "false")).lower() == "true",
            )
        )
        inserted += 1
    db.flush()
    return inserted


def _import_customers(db: Session, rows: list[dict[str, Any]]) -> int:
    inserted = 0
    for row in rows:
        external_id = _clean(row["customer_id"])
        if db.scalar(select(Customer).where(Customer.customer_id == external_id)):
            continue
        db.add(Customer(customer_id=external_id, segment=_clean(row["segment"]) or "Standard", is_demo=_clean(row.get("is_demo", "false")).lower() == "true"))
        inserted += 1
    db.flush()
    return inserted


def _import_campaigns(db: Session, rows: list[dict[str, Any]]) -> int:
    channels = {channel.name: channel for channel in db.scalars(select(Channel)).all()}
    inserted = 0
    for row_number, row in enumerate(rows, start=2):
        channel_name = _clean(row["channel"])
        if channel_name not in channels:
            raise CSVImportError(f"row {row_number}: unknown channel '{channel_name}'. Import that channel first.")
        start_date = _date(row["start_date"], row_number, "start_date")
        end_date = _date(row["end_date"], row_number, "end_date")
        if start_date > end_date:
            raise CSVImportError(f"row {row_number}: start_date must be on or before end_date.")
        spend = _decimal(row["spend"], row_number, "spend")
        impressions = _integer(row["impressions"], row_number, "impressions")
        clicks = _integer(row["clicks"], row_number, "clicks")
        sessions = _integer(row["sessions"], row_number, "sessions")
        product_views = _integer(row["product_views"], row_number, "product_views")
        leads = _integer(row["leads"], row_number, "leads")
        campaign_key = _clean(row["campaign_id"])
        if db.scalar(select(Campaign).where(Campaign.campaign_id == campaign_key)):
            continue
        db.add(
            Campaign(
                campaign_id=campaign_key,
                name=_clean(row["name"]),
                channel_id=channels[channel_name].id,
                objective=_clean(row["objective"]) or "Acquisition",
                spend=spend,
                impressions=impressions,
                clicks=clicks,
                sessions=sessions,
                product_views=product_views,
                leads=leads,
                start_date=start_date,
                end_date=end_date,
                is_demo=_clean(row.get("is_demo", "false")).lower() == "true",
            )
        )
        inserted += 1
    db.flush()
    return inserted


def _import_touchpoints(db: Session, rows: list[dict[str, Any]]) -> int:
    customers = {customer.customer_id: customer for customer in db.scalars(select(Customer)).all()}
    channels = {channel.name: channel for channel in db.scalars(select(Channel)).all()}
    campaigns = {campaign.campaign_id: campaign for campaign in db.scalars(select(Campaign)).all()}
    inserted = 0
    for row_number, row in enumerate(rows, start=2):
        customer_key = _clean(row["customer_id"])
        if customer_key not in customers:
            raise CSVImportError(f"row {row_number}: unknown customer '{customer_key}'. Import that customer first.")
        external_id = _clean(row["external_id"])
        channel_name = _clean(row.get("channel"))
        channel = channels.get(channel_name) if channel_name else None
        if channel_name and channel is None:
            raise CSVImportError(f"row {row_number}: unknown channel '{channel_name}'.")
        campaign_key = _clean(row.get("campaign_id"))
        campaign = campaigns.get(campaign_key) if campaign_key else None
        if campaign_key and campaign is None:
            raise CSVImportError(f"row {row_number}: unknown campaign '{campaign_key}'.")
        if campaign and channel and campaign.channel_id != channel.id:
            raise CSVImportError(f"row {row_number}: campaign '{campaign_key}' does not belong to channel '{channel_name}'.")
        timestamp = _datetime(row["timestamp"], row_number, "timestamp")
        is_conversion = _clean(row["conversion"]).lower() in {"true", "1", "yes"}
        order_id = _clean(row["order_id"])
        revenue = _decimal(row.get("revenue", "0") or "0", row_number, "revenue")
        if is_conversion and not order_id:
            raise CSVImportError(f"row {row_number}: order_id is required for a converting touchpoint.")
        if db.scalar(select(Touchpoint).where(Touchpoint.external_id == external_id)):
            continue
        if is_conversion and db.scalar(select(Conversion).where(Conversion.order_id == order_id)):
            raise CSVImportError(f"row {row_number}: order_id '{order_id}' already exists.")
        point = Touchpoint(
            external_id=external_id,
            customer_id=customers[customer_key].id,
            channel_id=channel.id if channel else campaign.channel_id if campaign else None,
            campaign_id=campaign.id if campaign else None,
            session_id=_clean(row["session_id"]),
            timestamp=timestamp,
            touchpoint_type=_clean(row["touchpoint_type"]) or "visit",
            is_demo=_clean(row.get("is_demo", str(customers[customer_key].is_demo))).lower() == "true",
        )
        db.add(point)
        db.flush()
        if is_conversion:
            db.add(
                Conversion(
                    order_id=order_id,
                    customer_id=customers[customer_key].id,
                    touchpoint_id=point.id,
                    session_id=point.session_id,
                    conversion_date=timestamp,
                    revenue=revenue,
                    is_demo=point.is_demo,
                )
            )
        inserted += 1
    db.flush()
    return inserted
