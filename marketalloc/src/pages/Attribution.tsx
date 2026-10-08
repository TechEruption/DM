import { useMemo } from "react";
import { Link } from "react-router-dom";
import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";
import EmptyState from "../components/common/EmptyState";
import PageHeader from "../components/common/PageHeader";
import { useDataset } from "../context/DatasetContext";
import { formatCurrency, formatNumber, formatPercent } from "../utils/formatters";
import type { AttributionModel } from "../types/analytics";

const labels: Record<AttributionModel, string> = { first_touch: "First Touch", last_touch: "Last Touch", linear: "Linear", time_decay: "Time Decay", position_based: "Position Based (40/20/40)" };
const colors = ["#5756d8", "#22a891", "#4c9bc9", "#e2a63c", "#8066c7", "#d77555", "#6582a3"];

export default function Attribution() {
  const { dataset, report, model, setModel } = useDataset();
  const distribution = useMemo(() => {
    if (!report) return [];
    return report.channels.map((channel) => ({
      channel: channel.channel,
      revenue: channel.attributedRevenue,
      conversions: channel.conversions,
      creditShare: report.summary.conversions > 0 ? channel.conversions / report.summary.conversions * 100 : 0,
    }));
  }, [report]);
  if (!dataset || !report) return <main className="content-wrap"><PageHeader eyebrow="CONVERSION CREDIT" title="Marketing attribution" description="Compare how different models assign value across customer touchpoints." /><EmptyState /></main>;
  return (
    <main className="content-wrap">
      <PageHeader eyebrow="CONVERSION CREDIT" title="Marketing attribution" description="Compare how each marketing interaction contributes to your conversions." actions={<label className="select-field"><span>Attribution model</span><select value={model} onChange={(event) => setModel(event.target.value as AttributionModel)}>{Object.entries(labels).map(([key, label]) => <option key={key} value={key}>{label}</option>)}</select></label>} />
      <div className="attribution-intro"><strong>{labels[model]}</strong><span>{model === "first_touch" ? "All credit goes to the first known touchpoint." : model === "last_touch" ? "All credit goes to the final touchpoint before conversion." : model === "linear" ? "Credit is shared equally by all eligible touchpoints." : model === "time_decay" ? "Recent touchpoints receive more credit using a 0.7 decay factor." : "Credit is split across first, middle and last interactions."}</span></div>
      <section className="dashboard-panels attribution-panels">
        <article className="panel chart-panel"><div className="panel-heading"><div><h2>Attributed revenue share</h2><p>Channel contribution to total attributed revenue</p></div></div><div className="chart-box donut-box">{report.summary.attributedRevenue > 0 ? <ResponsiveContainer width="100%" height="100%"><PieChart><Pie data={distribution.filter((item) => item.revenue > 0)} dataKey="revenue" nameKey="channel" innerRadius="55%" outerRadius="82%" paddingAngle={2}>{distribution.map((item, index) => <Cell key={item.channel} fill={colors[index % colors.length]} />)}</Pie><Tooltip formatter={(value) => formatCurrency(Number(value))} /></PieChart></ResponsiveContainer> : <div className="chart-empty">No conversions to attribute.</div>}<div className="donut-total"><small>Attributed revenue</small><strong>{formatCurrency(report.summary.attributedRevenue)}</strong></div></div></article>
        <article className="panel chart-panel"><div className="panel-heading"><div><h2>Model contribution</h2><p>Conversion credit across channels</p></div></div><div className="attribution-breakdown">{distribution.map((item, index) => <div className="breakdown-row" key={item.channel}><div className="breakdown-head"><span><i style={{ background: colors[index % colors.length] }} />{item.channel}</span><strong>{formatPercent(item.creditShare)}</strong></div><div className="progress-track"><i style={{ width: `${item.creditShare}%`, background: colors[index % colors.length] }} /></div><small>{formatCurrency(item.revenue)} attributed · {formatNumber(item.conversions, 2)} conversion credits</small></div>)}</div></article>
      </section>
      <section className="panel table-panel"><div className="panel-heading"><div><h2>Touchpoint credit</h2><p>Each conversion receives exactly 100% total credit.</p></div><Link className="inline-link" to="/journeys">View journeys</Link></div><div className="table-scroll"><table><thead><tr><th>Customer</th><th>Order</th><th>Converted</th><th>Channel</th><th>Campaign</th><th>Credit</th><th>Attributed value</th></tr></thead><tbody>{report.credits.slice(0, 200).map((credit, index) => <tr key={`${credit.orderId}-${credit.campaignId}-${index}`}><td>{credit.customerId}</td><td>{credit.orderId}</td><td>{credit.convertedAt.slice(0, 10)}</td><td>{credit.channel}</td><td>{credit.campaignId}</td><td>{formatPercent(credit.share * 100, 2)}</td><td>{formatCurrency(credit.revenue)}</td></tr>)}</tbody></table></div><p className="table-footnote">Showing up to 200 credit rows of {report.credits.length.toLocaleString("en-IN")} · Values are unrounded in calculations.</p></section>
    </main>
  );
}
