import pytest

from app.services.marketing_metrics import (
    aov,
    cac,
    calculate_metrics,
    conversion_rate,
    cpc,
    ctr,
    roi,
    roas,
    safe_divide,
)


def test_metric_formulas():
    assert ctr(25, 1000) == pytest.approx(2.5)
    assert cpc(100, 25) == pytest.approx(4)
    assert conversion_rate(5, 25) == pytest.approx(20)
    assert cac(100, 5) == pytest.approx(20)
    assert aov(500, 5) == pytest.approx(100)
    assert roas(500, 100) == pytest.approx(5)
    assert roi(500, 100) == pytest.approx(400)


def test_zero_denominators_are_safe():
    assert safe_divide(10, 0) is None
    assert cpc(10, 0) is None
    assert cac(10, 0) is None
    assert aov(10, 0) is None
    assert roas(10, 0) is None
    assert roi(10, 0) is None
    assert ctr(0, 0) == 0
    assert conversion_rate(0, 0) == 0


def test_null_and_zero_values_do_not_raise():
    metrics = calculate_metrics(
        spend=None,
        impressions=None,
        clicks=0,
        conversions=None,
        revenue=None,
        attributed_revenue=None,
    )
    assert metrics["ctr"] == 0
    assert metrics["cpc"] is None
    assert metrics["conversion_rate"] == 0
    assert metrics["cac"] is None
    assert metrics["roas"] is None


def test_zero_spend_has_null_roas_and_roi():
    assert roas(100, 0) is None
    assert roi(100, 0) is None
