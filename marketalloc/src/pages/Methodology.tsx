import { Link } from "react-router-dom";
import PageHeader from "../components/common/PageHeader";

const metrics = [
  ["CTR", "Clicks ÷ impressions × 100", "The proportion of ad impressions that resulted in a click."],
  ["CPC", "Spend ÷ clicks", "Average cost for each click."],
  ["CVR", "Conversions ÷ clicks × 100", "The proportion of clicks that resulted in a conversion."],
  ["CAC", "Spend ÷ conversions", "Marketing cost per conversion."],
  ["AOV", "Revenue ÷ conversions", "Average revenue per recorded conversion."],
  ["ROAS", "Attributed revenue ÷ spend", "Attributed revenue returned for each unit of marketing spend."],
  ["ROI", "(Attributed revenue − spend) ÷ spend × 100", "Net return relative to campaign spend; this does not include other business costs."],
];
const models = [
  ["First touch", "100% of conversion credit to the earliest eligible interaction."],
  ["Last touch", "100% of conversion credit to the final eligible interaction before conversion."],
  ["Linear", "Equal credit across all eligible touchpoints in the journey."],
  ["Time decay", "Credit grows toward recent touchpoints using a 0.7 per-step decay factor, then is normalized."],
  ["Position based", "40% to the first touch, 40% to the last and 20% shared between middle touches. One-touch and two-touch journeys are normalized."],
];

export default function Methodology() {
  return <main className="content-wrap"><PageHeader eyebrow="HOW IT WORKS" title="Methodology" description="Clear, deterministic definitions for the measures and recommendations in MARKETALLOC." />
    <section className="panel methodology-panel"><div className="panel-heading"><div><h2>Marketing metrics</h2><p>Ratios return no value when the denominator is zero.</p></div></div><div className="method-grid">{metrics.map(([name, formula, explanation]) => <article className="method-item" key={name}><span>{name}</span><div><strong>{formula}</strong><p>{explanation}</p></div></article>)}</div></section>
    <section className="panel methodology-panel"><div className="panel-heading"><div><h2>Multi-touch attribution</h2><p>Only touchpoints for the same customer at or before a conversion are eligible.</p></div></div><div className="method-grid">{models.map(([name, explanation]) => <article className="method-item" key={name}><span className="model-method">{name}</span><div><p>{explanation}</p></div></article>)}</div></section>
    <section className="panel methodology-panel"><div className="panel-heading"><div><h2>Budget allocation and projections</h2><p>Decision support based on historical observations—not a promise of future performance.</p></div></div><div className="method-prose"><p>Channel efficiency is normalized from historical ROAS, conversion rate, inverse acquisition cost and share of attributed revenue. The proposed budget is distributed incrementally across eligible channels, respecting minimum and maximum allocations. Each incremental amount is discounted as its allocation grows relative to historical spend, representing diminishing returns.</p><p>Projected revenue and conversions are estimates calculated from each recommended allocation and observed historical performance. Market changes, creative quality, seasonality, capacity and other costs are not modelled.</p><h3>Funnel analysis</h3><p>Impressions, clicks, sessions, product views and leads are summed from campaign records. Conversions and revenue are counted from converting touchpoints. Stage rate is the current stage divided by the previous stage; drop-off is one minus that rate, bounded below at zero. Funnel counts may reflect separately reported sources and are not deduplicated user counts.</p></div></section>
    <div className="method-cta"><span>Ready to analyze your own data?</span><Link className="inline-link" to="/upload">Upload marketing data →</Link></div>
  </main>;
}
