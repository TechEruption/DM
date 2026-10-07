from app.services.funnel_analyzer import analyze_funnel


def test_funnel_stage_rates_dropoff_and_largest_leakage():
    result = analyze_funnel(
        impressions=1000,
        clicks=100,
        sessions=80,
        product_views=40,
        leads=20,
        conversions=10,
        revenue=5000,
    )
    assert result["stages"][1]["conversion_rate_from_previous"] == 10
    assert result["stages"][3]["drop_off_rate"] == 50
    assert result["largest_leakage"] == {
        "from_stage": "Impressions",
        "to_stage": "Clicks",
        "drop_off_rate": 90,
    }
    assert result["stages"][-1]["count"] == 5000


def test_funnel_handles_empty_stages_without_division_errors():
    result = analyze_funnel()
    assert result["stages"][0]["conversion_rate_from_previous"] is None
    assert result["stages"][1]["conversion_rate_from_previous"] is None
    assert result["largest_leakage"] is None
