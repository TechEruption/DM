import pytest

from app.services.attribution_engine import attribute_conversion, calculate_touchpoint_credits


def journey(*channels):
    return [
        {"id": index, "channel": channel, "campaign": f"campaign-{index}", "timestamp": f"2025-01-01T00:0{index}:00"}
        for index, channel in enumerate(channels)
    ]


@pytest.mark.parametrize(
    ("model", "expected"),
    [
        ("first_touch", [1.0, 0.0, 0.0]),
        ("last_touch", [0.0, 0.0, 1.0]),
        ("linear", [1 / 3, 1 / 3, 1 / 3]),
    ],
)
def test_first_last_and_linear_attribution(model, expected):
    credits = calculate_touchpoint_credits(journey("Google Ads", "Email", "Meta Ads"), model)
    assert [item["credit_share"] for item in credits] == pytest.approx(expected)
    assert sum(item["credit_share"] for item in credits) == 1.0


def test_time_decay_gives_more_credit_to_recent_touch():
    credits = calculate_touchpoint_credits(journey("Search", "Email", "Social"), "time_decay", decay_parameter=0.5)
    assert credits[0]["credit_share"] < credits[1]["credit_share"] < credits[2]["credit_share"]
    assert sum(item["credit_share"] for item in credits) == 1.0


def test_position_based_default_and_custom_weights():
    credits = calculate_touchpoint_credits(journey("Search", "Email", "Social"), "position_based")
    assert [item["credit_share"] for item in credits] == pytest.approx([0.4, 0.2, 0.4])
    custom = calculate_touchpoint_credits(
        journey("Search", "Email", "Social", "Referral"),
        "position_based",
        first_weight=0.5,
        middle_weight=0.25,
        last_weight=0.25,
    )
    assert [item["credit_share"] for item in custom] == pytest.approx([0.5, 0.125, 0.125, 0.25])


def test_one_touch_and_two_touch_position_based_journeys():
    one = calculate_touchpoint_credits(journey("Email"), "position_based")
    two = calculate_touchpoint_credits(journey("Search", "Email"), "position_based")
    assert [item["credit_share"] for item in one] == [1.0]
    assert [item["credit_share"] for item in two] == pytest.approx([0.5, 0.5])


def test_missing_channel_gets_unknown_credit_and_duplicate_times_are_stable():
    points = [
        {"id": 2, "channel": None, "timestamp": "2025-01-01T00:00:00"},
        {"id": 1, "channel": "Search", "timestamp": "2025-01-01T00:00:00"},
    ]
    credits = calculate_touchpoint_credits(points, "linear")
    assert [item["id"] for item in credits] == [1, 2]
    assert [item["channel"] for item in credits] == ["Search", "Unknown"]
    assert sum(item["credit_share"] for item in credits) == 1.0


def test_missing_touchpoint_journey_gets_unknown_credit_and_invalid_parameters_raise():
    missing_journey_credit = attribute_conversion([], 100, "linear")
    assert missing_journey_credit[0]["channel"] == "Unknown"
    assert missing_journey_credit[0]["credit_share"] == 1.0
    assert missing_journey_credit[0]["attributed_revenue"] == 100
    with pytest.raises(ValueError):
        calculate_touchpoint_credits(journey("A"), "time_decay", decay_parameter=0)
    with pytest.raises(ValueError):
        calculate_touchpoint_credits(journey("A", "B"), "position_based", first_weight=0, middle_weight=1, last_weight=0)
    with pytest.raises(ValueError):
        attribute_conversion(journey("A"), float("nan"), "linear")
    with pytest.raises(ValueError):
        calculate_touchpoint_credits([None], "linear")


def test_credits_sum_to_conversion_revenue():
    credits = attribute_conversion(journey("Search", "Email", "Social"), 4500, "linear")
    assert sum(item["attributed_revenue"] for item in credits) == pytest.approx(4500)
