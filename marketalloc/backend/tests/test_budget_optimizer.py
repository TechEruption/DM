import pytest

from app.services.budget_optimizer import optimize_budget


@pytest.fixture
def channels():
    return [
        {
            "channel": "Search",
            "spend": 1000,
            "impressions": 20000,
            "clicks": 1000,
            "conversions": 50,
            "revenue": 10000,
            "attributed_revenue": 9000,
        },
        {
            "channel": "Email",
            "spend": 500,
            "impressions": 4000,
            "clicks": 400,
            "conversions": 40,
            "revenue": 8000,
            "attributed_revenue": 7000,
        },
        {
            "channel": "Social",
            "spend": 800,
            "impressions": 30000,
            "clicks": 600,
            "conversions": 18,
            "revenue": 4500,
            "attributed_revenue": 4000,
        },
    ]


def test_budget_is_fully_allocated_and_estimates_are_labeled(channels):
    result = optimize_budget(channels, 1200)
    assert result["recommended_allocation"] == pytest.approx(1200, abs=0.03)
    assert sum(row["recommended_allocation"] for row in result["channels"]) == pytest.approx(1200, abs=0.03)
    assert result["forecast_label"] == "Projected / Estimated"
    assert result["projected_revenue"] > 0
    assert all("diminishing-return" in row["explanation"] for row in result["channels"])


def test_minimum_and_maximum_constraints_are_respected(channels):
    result = optimize_budget(
        channels,
        1200,
        min_allocations={"Search": 300, "Email": 200},
        max_allocations={"Search": 450, "Email": 350, "Social": 500},
    )
    by_name = {row["channel"]: row["recommended_allocation"] for row in result["channels"]}
    assert by_name["Search"] >= 300
    assert by_name["Search"] <= 450
    assert by_name["Email"] >= 200
    assert by_name["Email"] <= 350
    assert by_name["Social"] <= 500
    assert sum(by_name.values()) == pytest.approx(1200, abs=0.03)


@pytest.mark.parametrize(
    ("budget", "minimum", "maximum", "message"),
    [
        (0, {}, {}, "greater than zero"),
        (100, {"Search": 101}, {}, "Minimum allocation exceeds maximum"),
        (1000, {}, {"Search": 200, "Email": 200, "Social": 200}, "maximum allocations"),
        (500, {"Unknown": 1}, {}, "Unknown channel"),
        (500, {"Search": 300}, {"Search": 200}, "Minimum allocation exceeds maximum"),
    ],
)
def test_invalid_budget_and_constraints_raise(channels, budget, minimum, maximum, message):
    with pytest.raises(ValueError, match=message):
        optimize_budget(channels, budget, min_allocations=minimum, max_allocations=maximum)


def test_historical_roas_does_not_get_all_budget(channels):
    channels[0]["attributed_revenue"] = 1000000
    result = optimize_budget(channels, 10000)
    positive_allocations = [row for row in result["channels"] if row["recommended_allocation"] > 0]
    assert len(positive_allocations) > 1
