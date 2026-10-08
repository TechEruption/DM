import { useMemo, useState } from "react";
import EmptyState from "../components/common/EmptyState";
import PageHeader from "../components/common/PageHeader";
import { recommendBudget } from "../analytics/budgetOptimizer";
import { useDataset } from "../context/DatasetContext";
import { formatCurrency, formatNumber, formatPercent, formatRoas } from "../utils/formatters";

export default function ScenarioSimulator() {
  const { dataset, report } = useDataset();
  const base = report?.summary.spend ?? 0;
  const [budgets, setBudgets] = useState<number[]>([Math.round(base * 0.75), Math.round(base), Math.round(base * 1.25)]);
  const scenarios = useMemo(() => report ? budgets.map((budget, index) => ({ name: `Scenario ${String.fromCharCode(65 + index)}`, plan: recommendBudget(report.channels, budget) })) : [], [report, budgets]);
  if (!dataset || !report) return <main className="content-wrap"><PageHeader eyebrow="PLANNING" title="Scenario simulator" description="Compare different future investment levels with estimated channel returns." /><EmptyState /></main>;
  return <main className="content-wrap"><PageHeader eyebrow="PLANNING" title="Scenario simulator" description="Compare projected marketing outcomes before choosing a future budget." />
    <div className="projection-label">ALL RESULTS ARE PROJECTED ESTIMATES</div>
    <section className="scenario-grid">{scenarios.map((scenario, index) => <article className="panel scenario-card" key={scenario.name}><div className="scenario-card-head"><span>{scenario.name}</span><span>Projection</span></div><label className="search-field"><span>Scenario budget (₹)</span><input type="number" min="0" value={budgets[index]} onChange={(event) => setBudgets((current) => current.map((value, position) => position === index ? Math.max(0, Number(event.target.value)) : value))} /></label>{scenario.plan.error ? <p className="validation-inline">{scenario.plan.error}</p> : <dl className="scenario-results"><div><dt>Projected revenue</dt><dd>{formatCurrency(scenario.plan.projectedRevenue)}</dd></div><div><dt>Projected conversions</dt><dd>{formatNumber(scenario.plan.projectedConversions, 1)}</dd></div><div><dt>Projected ROAS</dt><dd>{formatRoas(scenario.plan.projectedRoas)}</dd></div><div><dt>Projected ROI</dt><dd>{formatPercent(scenario.plan.projectedRoi)}</dd></div><div><dt>Projected CAC</dt><dd>{formatCurrency(scenario.plan.projectedCac)}</dd></div></dl>}</article>)}</section>
    <section className="panel table-panel"><div className="panel-heading"><div><h2>Compare scenarios</h2><p>Estimated outcomes from the same historical channel profile</p></div></div><div className="table-scroll"><table><thead><tr><th>Scenario</th><th>Budget</th><th>Projected revenue</th><th>Projected conversions</th><th>Projected ROAS</th><th>Projected ROI</th><th>Projected CAC</th></tr></thead><tbody>{scenarios.map(({ name, plan }) => <tr key={name}><td><strong>{name}</strong></td><td>{formatCurrency(plan.budget)}</td><td>{plan.error ? "—" : formatCurrency(plan.projectedRevenue)}</td><td>{plan.error ? "—" : formatNumber(plan.projectedConversions, 1)}</td><td>{formatRoas(plan.projectedRoas)}</td><td>{formatPercent(plan.projectedRoi)}</td><td>{formatCurrency(plan.projectedCac)}</td></tr>)}</tbody></table></div><p className="table-footnote">Projections are estimates based on historic channel behavior and are not guaranteed results.</p></section>
  </main>;
}
