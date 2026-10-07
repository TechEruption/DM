import csv
from collections import Counter, defaultdict
from pathlib import Path

from app.services.analytics_service import dataset_metadata

SEED_DIR = Path(__file__).parents[1] / "app" / "seed"


def read_rows(name):
    with (SEED_DIR / name).open(encoding="utf-8-sig", newline="") as source:
        return list(csv.DictReader(source))


def test_demo_dataset_has_required_scale_and_channel_coverage():
    customers = read_rows("customers.csv")
    campaigns = read_rows("campaigns.csv")
    channels = read_rows("channels.csv")
    touchpoints = read_rows("touchpoints.csv")
    assert len(customers) >= 100
    assert len(channels) == 7
    assert len(campaigns) > 7
    assert len({row["start_date"][:7] for row in campaigns}) >= 3
    assert {row["channel"] for row in campaigns} == {row["name"] for row in channels}
    assert all(row["is_demo"].lower() == "true" for row in customers + campaigns)
    assert all(row["is_demo"].lower() == "true" for row in channels + touchpoints)
    assert len(touchpoints) > len(customers)


def test_demo_dataset_contains_single_and_multi_touch_converting_and_nonconverting_paths():
    touchpoints = read_rows("touchpoints.csv")
    by_customer = defaultdict(list)
    for row in touchpoints:
        by_customer[row["customer_id"]].append(row)
    conversions = [row for row in touchpoints if row["conversion"].lower() == "true"]
    nonconverting_customers = [
        customer_id for customer_id, rows in by_customer.items()
        if not any(row["conversion"].lower() == "true" for row in rows)
    ]
    path_lengths = Counter(len(rows) for rows in by_customer.values())
    assert conversions
    assert nonconverting_customers
    assert path_lengths[1] > 0
    assert any(length > 1 for length in path_lengths)
    assert all(row["order_id"] for row in conversions)


def test_dataset_marker_is_explicit_and_handles_imported_data():
    assert dataset_metadata([{"is_demo": True}]) == {
        "dataset_label": "DEMO DATASET",
        "is_demo_dataset": True,
    }
    assert dataset_metadata([{"is_demo": False}]) == {
        "dataset_label": "MARKETING DATASET",
        "is_demo_dataset": False,
    }
    assert dataset_metadata([])["dataset_label"] == "NO DATASET"
