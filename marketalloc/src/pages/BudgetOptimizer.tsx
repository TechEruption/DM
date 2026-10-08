import { useMemo, useState } from "react";
import EmptyState from "../components/common/EmptyState";
import MetricCard from "../components/common/MetricCard";
import PageHeader from "../components/common/PageHeader";
import { recommendBudget } from "../analytics/budgetOptimizer";
import { useDataset } from "../context/DatasetContext";
import { formatCurrency, formatNumber, formatPercent, formatRoas } from "../utils/formatters";

export default function BudgetOptimizer() {
  const { dataset, report } = useDataset();
  const [budget, setBudget] = useState(100000);
  const [minimum, setMinimum] = useState(0);
  const [maximum, setMaximum] = useState(100000);
  const plan = useMemo(() => report ? recommendBudget(report.channels, budget, minimum, maximum) : null, [report, budget, minimum, maximum]);
  if (!dataset || !report) return <main className="content-wrap"><PageHeader eyebrow="PLANNING" title="Budget optimization" description="Plan future spend using historical channel performance and transparent constraints." /><EmptyState /></main>;
  return <main className="content-wrap">
    <PageHeader eyebrow="PLANNING" title="Budget optimization" description="Explore a constrained allocation informed by historical efficiency and diminishing returns." />
    <section className="panel optimizer-inputs"><div><h2>Planning assumptions</h2><p>Enter a future budget and optional per-channel allocation limits.</p></div><div className="budget-fields"><label className="search-field"><span>Future marketing budget (₹)</span><input type="number" min="0" value={budget} onChange={(event) => setBudget(Number(event.target.value))} /></label><label className="search-field"><span>Minimum per channel (₹)</span><input type="number" min="0" value={minimum} onChange={(event) => setMinimum(Number(event.target.value))} /></label><label className="search-field"><span>Maximum per channel (₹)</span><input type="number" min="0" value={maximum} onChange={(event) => setMaximum(Number(event.target.value))} /></label></div></section>
    {plan?.error ? <div className="validation-errors" role="status"><strong>Recommendation unavailable</strong><pre>{plan.error}</pre></div> : plan && <>
      <div className="projection-label">PLANNING ESTIMATE · NOT ACTUAL RESULTS</div>
      <div className="metric-grid projection-grid"><MetricCard label="Projected revenue" value={formatCurrency(plan.projectedRevenue)} note="Modelled from historical return" /><MetricCard label="Projected conversions" value={formatNumber(plan.projectedConversions, 1)} note="Estimated conversion volume" /><MetricCard label="Projected ROAS" value={formatRoas(plan.projectedRoas)} note="Projected revenue ÷ budget" /><MetricCard label="Projected ROI" value={formatPercent(plan.projectedRoi)} note={`Projected CAC ${formatCurrency(plan.projectedCac)}`} /></div>
      <section className="panel table-panel"><div className="panel-heading"><div><h2>Recommended channel allocation</h2><p>Incremental distribution balances observed efficiency with diminishing returns.</p></div><span className="panel-meta">Planned: {formatCurrency(budget)}</span></div><div className="table-scroll"><table><thead><tr><th>Channel</th><th>Current allocation</th><th>Recommended</th><th>Change</th><th>Projected conversions</th><th>Projected revenue</th><th>Projected ROAS</th><th>Projected ROI</th><th>Projected CAC</th></tr></thead><tbody>{plan.allocations.map((row) => <tr key={row.channel}><td><strong>{row.channel}</strong></td><td>{formatCurrency(row.currentAllocation)}</td><td>{formatCurrency(row.recommendedAllocation)}</td><td className={row.change >= 0 ? "positive-value" : "negative-value"}>{row.change >= 0 ? "+" : ""}{formatCurrency(row.change)}</td><td>{formatNumber(row.projectedConversions, 1)}</td><td>{formatCurrency(row.projectedRevenue)}</td><td>{formatRoas(row.projectedRoas)}</td><td>{formatPercent(row.projectedRoi)}</td><td>{formatCurrency(row.projectedCac)}</td></tr>)}</tbody></table></div><p className="table-footnote">The projection uses relative historical ROAS, conversion efficiency and revenue contribution. Diminishing returns reduce the marginal estimate as allocations grow.</p></section>
    </>}
  </main>;
}
