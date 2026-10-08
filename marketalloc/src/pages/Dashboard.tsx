import { useMemo } from "react";
import { Link } from "react-router-dom";
import { Bar, BarChart, CartesianGrid, Cell, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { ArrowRight, MousePointer2, ShoppingBag, TrendingUp, Wallet } from "lucide-react";
import EmptyState from "../components/common/EmptyState";
import MetricCard from "../components/common/MetricCard";
import PageHeader from "../components/common/PageHeader";
import { useDataset } from "../context/DatasetContext";
import { buildInsights } from "../analytics/insights";
import { formatCompactCurrency, formatCurrency, formatNumber, formatPercent, formatRoas } from "../utils/formatters";

const palette = ["#5756d8", "#22a891", "#4c9bc9", "#e2a63c", "#8066c7", "#d77555", "#6582a3"];

export default function Dashboard() {
  const { report, dataset, model, setModel } = useDataset();
  const insights = useMemo(() => report ? buildInsights(report).slice(0, 3) : [], [report]);
  if (!report || !dataset) return <main className="content-wrap"><PageHeader eyebrow="OVERVIEW" title="Marketing performance" description="A clear view of spend, revenue, and campaign results." /><EmptyState /></main>;
  const summary = report.summary;
  const modelLabels = { first_touch: "First touch", last_touch: "Last touch", linear: "Linear", time_decay: "Time decay", position_based: "Position based" };
  return (
    <main className="content-wrap">
      <PageHeader eyebrow="BUSINESS OVERVIEW" title="Marketing performance" description="See how your marketing investment contributes to customer growth." actions={<label className="select-field"><span>Attribution model</span><select value={model} onChange={(event) => setModel(event.target.value as typeof model)}>{Object.entries(modelLabels).map(([value, label]) => <option key={value} value={value}>{label}</option>)}</select></label>} />
      <div className="metric-grid">
        <MetricCard label="Total spend" value={formatCurrency(summary.spend)} note={`${formatNumber(dataset.campaigns.length)} campaigns`} icon={<Wallet size={16} />} />
        <MetricCard label="Attributed revenue" value={formatCurrency(summary.attributedRevenue)} note={`${modelLabels[model]} model`} icon={<TrendingUp size={16} />} />
        <MetricCard label="Conversions" value={formatNumber(summary.conversions, 2)} note={`${formatNumber(summary.leads)} leads`} icon={<ShoppingBag size={16} />} />
        <MetricCard label="ROAS" value={formatRoas(summary.roas)} note={`ROI ${formatPercent(summary.roi)}`} icon={<MousePointer2 size={16} />} />
        <MetricCard label="Total revenue" value={formatCurrency(summary.revenue)} note="From converting touchpoints" />
        <MetricCard label="Customer acquisition cost" value={formatCurrency(summary.cac)} note="Spend per conversion" />
        <MetricCard label="Average order value" value={formatCurrency(summary.aov)} note="Revenue per conversion" />
      </div>
      <section className="dashboard-panels">
        <article className="panel chart-panel">
          <div className="panel-heading"><div><h2>Spend and revenue trend</h2><p>Monthly campaign spend compared with actual and attributed revenue</p></div><span className="panel-meta">{report.trends.length} periods</span></div>
          <div className="chart-box">
            {report.trends.length ? <ResponsiveContainer width="100%" height="100%"><BarChart data={report.trends} margin={{ top: 12, right: 8, left: 3, bottom: 0 }}><CartesianGrid stroke="#edf0f5" vertical={false} /><XAxis dataKey="month" axisLine={false} tickLine={false} tick={{ fill: "#788398", fontSize: 10 }} /><YAxis axisLine={false} tickLine={false} tick={{ fill: "#788398", fontSize: 10 }} tickFormatter={formatCompactCurrency} width={60} /><Tooltip formatter={(value) => formatCurrency(Number(value))} /><Bar dataKey="spend" name="Spend" fill="#d7dcf5" radius={[4, 4, 0, 0]} isAnimationActive={false} /><Bar dataKey="revenue" name="Revenue" fill="#5db6c2" radius={[4, 4, 0, 0]} isAnimationActive={false} /><Bar dataKey="attributedRevenue" name="Attributed revenue" fill="#5a58d6" radius={[4, 4, 0, 0]} isAnimationActive={false} /></BarChart></ResponsiveContainer> : <div className="chart-empty">Add campaign dates and performance to see a trend.</div>}
          </div>
          <div className="chart-legend"><span><i className="legend-spend" /> Spend</span><span><i className="legend-revenue" /> Revenue</span><span><i className="legend-attributed" /> Attributed revenue</span></div>
        </article>
        <article className="panel chart-panel">
          <div className="panel-heading"><div><h2>Attributed revenue by channel</h2><p>Contribution under {modelLabels[model].toLowerCase()} attribution</p></div><Link className="inline-link" to="/channels">Channel detail <ArrowRight size={13} /></Link></div>
          <div className="chart-box donut-box">
            {report.channels.some((channel) => channel.attributedRevenue > 0) ? <ResponsiveContainer width="100%" height="100%"><PieChart><Pie data={report.channels.filter((channel) => channel.attributedRevenue > 0)} dataKey="attributedRevenue" nameKey="channel" innerRadius="57%" outerRadius="82%" paddingAngle={2} stroke="none">{report.channels.map((channel, index) => <Cell key={channel.channel} fill={palette[index % palette.length]} />)}</Pie><Tooltip formatter={(value) => formatCurrency(Number(value))} /></PieChart></ResponsiveContainer> : <div className="chart-empty">No attributed revenue to display yet.</div>}
            <div className="donut-total"><small>Attributed revenue</small><strong>{formatCompactCurrency(summary.attributedRevenue)}</strong></div>
          </div>
          <div className="channel-legend">{report.channels.filter((channel) => channel.attributedRevenue > 0).slice(0, 6).map((channel) => <span key={channel.channel}><i style={{ background: palette[report.channels.indexOf(channel) % palette.length] }} />{channel.channel}<strong>{formatCurrency(channel.attributedRevenue)}</strong></span>)}</div>
        </article>
      </section>
      <section className="dashboard-lower">
        <article className="panel concise-funnel">
          <div className="panel-heading"><div><h2>Marketing funnel</h2><p>Measured volume from impression to conversion</p></div><Link className="inline-link" to="/funnel">Explore funnel <ArrowRight size={13} /></Link></div>
          <div className="funnel-mini">{report.funnel.slice(0, 6).map((stage, index) => <div className="funnel-mini-row" key={stage.name}><span>{stage.name}</span><div><i style={{ width: `${Math.max(2, summary.impressions > 0 ? stage.value / summary.impressions * 100 : 0)}%` }} /></div><strong>{formatNumber(stage.value, stage.value % 1 ? 2 : 0)}</strong><small>{index > 0 ? formatPercent(stage.rateFromPrevious) : "—"}</small></div>)}</div>
        </article>
        <article className="panel insight-preview">
          <div className="panel-heading"><div><h2>Key findings</h2><p>Based on the uploaded data</p></div><Link className="inline-link" to="/insights">All insights <ArrowRight size={13} /></Link></div>
          <div className="insight-list">{insights.length ? insights.map((insight) => <div className={`insight-item ${insight.kind}`} key={insight.title}><span className="insight-mark" /><div><strong>{insight.title}</strong><p>{insight.detail}</p></div></div>) : <p className="muted-copy">More data is needed to generate findings.</p>}</div>
        </article>
      </section>
      <footer className="data-note">Current dataset: {dataset.campaigns.length} campaigns · {dataset.channels.length} channels · Data is held in memory for this browser session only.</footer>
    </main>
  );
}
