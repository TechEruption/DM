import { useMemo } from "react";
import { ArrowDownRight, ArrowUpRight, CircleHelp } from "lucide-react";
import EmptyState from "../components/common/EmptyState";
import PageHeader from "../components/common/PageHeader";
import { buildInsights } from "../analytics/insights";
import { useDataset } from "../context/DatasetContext";

export default function Insights() {
  const { dataset, report } = useDataset();
  const insights = useMemo(() => report ? buildInsights(report) : [], [report]);
  if (!dataset || !report) return <main className="content-wrap"><PageHeader eyebrow="BUSINESS FINDINGS" title="Marketing insights" description="See practical observations based on the data in your current session." /><EmptyState /></main>;
  return <main className="content-wrap"><PageHeader eyebrow="BUSINESS FINDINGS" title="Marketing insights" description="Evidence-based observations derived from your uploaded marketing data." />
    <div className="insight-disclaimer"><CircleHelp size={16} /><span>Findings use deterministic comparisons of this dataset. Review the underlying figures before making decisions.</span></div>
    {insights.length ? <section className="insights-grid">{insights.map((insight) => <article className={`panel insight-card ${insight.kind}`} key={insight.title}><span className="insight-icon">{insight.kind === "positive" ? <ArrowUpRight size={17} /> : <ArrowDownRight size={17} />}</span><div><span className="insight-type">{insight.kind === "positive" ? "OPPORTUNITY" : insight.kind === "watch" ? "REVIEW" : "OBSERVATION"}</span><h2>{insight.title}</h2><p>{insight.detail}</p></div></article>)}</section> : <div className="inline-empty">There is not enough conversion or delivery data to generate insights yet.</div>}
  </main>;
}
