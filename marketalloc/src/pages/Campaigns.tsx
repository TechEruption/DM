import { useMemo, useState } from "react";
import { Search } from "lucide-react";
import EmptyState from "../components/common/EmptyState";
import PageHeader from "../components/common/PageHeader";
import { useDataset } from "../context/DatasetContext";
import { formatCurrency, formatNumber, formatPercent, formatRoas } from "../utils/formatters";

type SortField = "spend" | "attributedRevenue" | "roas" | "conversions" | "campaignName";

export default function Campaigns() {
  const { dataset, report } = useDataset();
  const [query, setQuery] = useState("");
  const [sortBy, setSortBy] = useState<SortField>("spend");
  const [rowLimit, setRowLimit] = useState(200);
  const rows = useMemo(() => {
    const filtered = report?.campaigns.filter((item) => `${item.campaignName} ${item.channel} ${item.campaignId}`.toLowerCase().includes(query.trim().toLowerCase())) ?? [];
    return [...filtered].sort((a, b) => {
      const left = a[sortBy];
      const right = b[sortBy];
      if (typeof left === "number" && typeof right === "number") return right - left;
      return String(left ?? "").localeCompare(String(right ?? ""));
    });
  }, [report, query, sortBy]);
  if (!dataset || !report) return <main className="content-wrap"><PageHeader eyebrow="CAMPAIGN RESULTS" title="Campaign performance" description="Compare campaign delivery, conversions, revenue and return." /><EmptyState /></main>;
  return (
    <main className="content-wrap"><PageHeader eyebrow="CAMPAIGN RESULTS" title="Campaign performance" description={`${dataset.campaigns.length.toLocaleString("en-IN")} campaigns measured across your marketing mix.`} />
      <section className="panel table-panel"><div className="table-controls"><label className="search-input"><Search size={15} /><input value={query} onChange={(event) => { setQuery(event.target.value); setRowLimit(200); }} placeholder="Search campaign, ID or channel" /></label><label className="sort-control"><span>Sort by</span><select value={sortBy} onChange={(event) => setSortBy(event.target.value as SortField)}><option value="spend">Spend</option><option value="attributedRevenue">Attributed revenue</option><option value="roas">ROAS</option><option value="conversions">Conversions</option><option value="campaignName">Campaign name</option></select></label></div>
        <div className="table-scroll"><table><thead><tr><th>Campaign</th><th>Channel</th><th>Spend</th><th>Impressions</th><th>Clicks</th><th>Sessions</th><th>Leads</th><th>Conversions</th><th>Revenue</th><th>CTR</th><th>CPC</th><th>CVR</th><th>CAC</th><th>ROAS</th><th>ROI</th></tr></thead><tbody>{rows.slice(0, rowLimit).map((item) => <tr key={item.campaignId}><td><strong>{item.campaignName}</strong><small>{item.campaignId}</small></td><td>{item.channel}</td><td>{formatCurrency(item.spend)}</td><td>{formatNumber(item.impressions)}</td><td>{formatNumber(item.clicks)}</td><td>{formatNumber(item.sessions)}</td><td>{formatNumber(item.leads)}</td><td>{formatNumber(item.conversions, 2)}</td><td>{formatCurrency(item.revenue)}</td><td>{formatPercent(item.ctr)}</td><td>{formatCurrency(item.cpc)}</td><td>{formatPercent(item.conversionRate)}</td><td>{formatCurrency(item.cac)}</td><td className="roas-cell">{formatRoas(item.roas)}</td><td>{formatPercent(item.roi)}</td></tr>)}</tbody></table></div>
        <p className="table-footnote">Showing {Math.min(rowLimit, rows.length).toLocaleString("en-IN")} of {rows.length.toLocaleString("en-IN")} matching campaigns.</p>
        {rows.length > rowLimit && <button className="button button-outline load-more" onClick={() => setRowLimit((limit) => limit + 200)}>Load 200 more campaigns</button>}
      </section>
    </main>
  );
}
