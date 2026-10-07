from typing import Any


def generate_insights(
    channel_metrics: list[dict[str, Any]],
    funnel: dict[str, Any],
    attribution_comparison: list[dict[str, Any]] | None = None,
    budget_result: dict[str, Any] | None = None,
    campaign_metrics: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    insights = []
    measurable_roas = [item for item in channel_metrics if item.get("roas") is not None]
    if measurable_roas:
        best = max(measurable_roas, key=lambda row: row["roas"])
        worst = min(measurable_roas, key=lambda row: row["roas"])
        insights.append(
            {
                "type": "channel_performance",
                "title": f"{best['channel']} currently has the highest ROAS.",
                "description": "Among channels with measurable spend, this channel generated the most attributed revenue per unit of spend.",
                "metric": {"name": "ROAS", "value": best["roas"]},
                "severity": "positive",
                "recommended_action": "Review campaign mix and capacity before scaling; historical ROAS is not a guarantee of future performance.",
            }
        )
        if best["channel"] != worst["channel"]:
            insights.append(
                {
                    "type": "channel_performance",
                    "title": f"{worst['channel']} currently has the lowest ROAS.",
                    "description": "This channel produced the least attributed revenue per unit of spend in the selected period.",
                    "metric": {"name": "ROAS", "value": worst["roas"]},
                    "severity": "warning",
                    "recommended_action": "Review targeting, creative, and conversion tracking before reducing spend.",
                }
            )
        highest_conversion = max(channel_metrics, key=lambda row: row.get("conversions", 0))
        if highest_conversion.get("conversions", 0) > 0:
            insights.append(
                {
                    "type": "conversion_volume",
                    "title": f"{highest_conversion['channel']} currently has the highest conversion volume.",
                    "description": "This channel is associated with the most observed conversions in the selected period.",
                    "metric": {"name": "Conversions", "value": highest_conversion.get("conversions", 0)},
                    "severity": "positive",
                    "recommended_action": "Compare conversion quality and acquisition cost before scaling this channel.",
                }
            )
    if campaign_metrics:
        measurable_campaigns = [
            item for item in campaign_metrics
            if item.get("clicks", 0) > 0 and item.get("conversion_rate") is not None
        ]
        if len(measurable_campaigns) > 1:
            average_cvr = sum(item["conversion_rate"] for item in measurable_campaigns) / len(measurable_campaigns)
            weak = min(measurable_campaigns, key=lambda row: row["conversion_rate"])
            if average_cvr > 0 and weak["conversion_rate"] < average_cvr * 0.75:
                insights.append(
                    {
                        "type": "campaign_performance",
                        "title": f"{weak['campaign_name']} has an unusually weak conversion rate.",
                        "description": "Its click-to-conversion rate is more than 25% below the campaign average.",
                        "metric": {"name": "Conversion rate", "value": weak["conversion_rate"], "unit": "%"},
                        "severity": "warning",
                        "recommended_action": "Review targeting, landing-page alignment, and conversion tracking.",
                    }
                )
    measurable_cac = [item for item in channel_metrics if item.get("cac") is not None]
    if len(measurable_cac) > 1:
        average_cac = sum(item["cac"] for item in measurable_cac) / len(measurable_cac)
        high_cac = max(measurable_cac, key=lambda row: row["cac"])
        if high_cac["cac"] > average_cac * 1.25:
            insights.append(
                {
                    "type": "acquisition_cost",
                    "title": f"{high_cac['channel']} has relatively high customer acquisition cost.",
                    "description": "Its CAC is more than 25% above the unweighted channel average for this period.",
                    "metric": {"name": "CAC", "value": high_cac["cac"], "currency": "INR"},
                    "severity": "warning",
                    "recommended_action": "Inspect audience quality and landing-page conversion before reallocating.",
                }
            )
    leakage = funnel.get("largest_leakage")
    if leakage:
        insights.append(
            {
                "type": "funnel",
                "title": f"The largest funnel leakage occurs between {leakage['from_stage']} and {leakage['to_stage']}.",
                "description": "This stage transition has the highest observed drop-off rate.",
                "metric": {"name": "Drop-off rate", "value": leakage["drop_off_rate"], "unit": "%"},
                "severity": "warning",
                "recommended_action": "Investigate friction and measurement quality at this transition.",
            }
        )
    if attribution_comparison:
        by_channel: dict[str, dict[str, float]] = {}
        for row in attribution_comparison:
            by_channel.setdefault(row["channel"], {})[row["model"]] = float(row["attributed_revenue"])
        deltas = [
            (name, abs(models.get("first_touch", 0) - models.get("last_touch", 0)))
            for name, models in by_channel.items()
            if "first_touch" in models and "last_touch" in models
        ]
        if deltas:
            channel, delta = max(deltas, key=lambda entry: entry[1])
            if delta > 0:
                insights.append(
                    {
                        "type": "attribution",
                        "title": f"{channel} receives substantially different credit under First Touch and Last Touch.",
                        "description": "The difference reflects the channel's position in customer paths; it is a model comparison, not a change in actual revenue.",
                        "metric": {"name": "Attributed revenue difference", "value": round(delta, 2), "currency": "INR"},
                        "severity": "info",
                        "recommended_action": "Compare additional models before making channel decisions.",
                    }
                )
    if budget_result:
        increases = [item for item in budget_result.get("channels", []) if item["allocation_change"] > 0]
        if increases:
            strongest = max(increases, key=lambda row: row["allocation_change"])
            insights.append(
                {
                    "type": "budget",
                    "title": f"The optimizer recommends increasing allocation to {strongest['channel']}.",
                    "description": "This is based on historical efficiency and estimated marginal return under the supplied constraints.",
                    "metric": {"name": "Recommended allocation change", "value": strongest["allocation_change"], "currency": "INR"},
                    "severity": "info",
                    "recommended_action": "Treat as a projected scenario and validate against capacity before deployment.",
                }
            )
        decreases = [item for item in budget_result.get("channels", []) if item["allocation_change"] < 0]
        if decreases:
            strongest = min(decreases, key=lambda row: row["allocation_change"])
            insights.append(
                {
                    "type": "budget",
                    "title": f"The optimizer recommends reducing allocation to {strongest['channel']}.",
                    "description": "The estimated marginal return is lower after considering historical efficiency and the supplied constraints.",
                    "metric": {"name": "Recommended allocation change", "value": strongest["allocation_change"], "currency": "INR"},
                    "severity": "info",
                    "recommended_action": "Validate the estimate and preserve a controlled test budget before reducing spend.",
                }
            )
    return insights
