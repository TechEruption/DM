import { useMemo, useState } from "react";
import { ArrowDown, CheckCircle2, Circle } from "lucide-react";
import EmptyState from "../components/common/EmptyState";
import PageHeader from "../components/common/PageHeader";
import { useDataset } from "../context/DatasetContext";
import { formatCurrency } from "../utils/formatters";

export default function CustomerJourneys() {
  const { dataset } = useDataset();
  const [query, setQuery] = useState("");
  const [selected, setSelected] = useState("");
  const customerOptions = useMemo(() => {
    if (!dataset) return [];
    const search = query.trim().toLowerCase();
    return dataset.customers.filter((customer) => !search || `${customer.customer_id} ${customer.segment}`.toLowerCase().includes(search)).slice(0, 100);
  }, [dataset, query]);
  const journey = useMemo(() => dataset?.touchpoints.filter((touch) => touch.customer_id === selected).sort((a, b) => a.timestamp.localeCompare(b.timestamp)) ?? [], [dataset, selected]);
  if (!dataset) return <main className="content-wrap"><PageHeader eyebrow="CUSTOMER EXPERIENCE" title="Customer journeys" description="Explore the sequence of marketing touchpoints leading to a conversion." /><EmptyState /></main>;
  return (
    <main className="content-wrap">
      <PageHeader eyebrow="CUSTOMER EXPERIENCE" title="Customer journeys" description="Trace each customer's interactions, from the first touch to conversion." />
      <section className="panel journey-panel">
        <div className="journey-filters"><label className="search-field"><span>Search customers</span><input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Customer ID or segment" /></label><label className="search-field"><span>Select customer</span><select value={selected} onChange={(event) => setSelected(event.target.value)}><option value="">Choose a customer</option>{customerOptions.map((customer) => <option key={customer.customer_id} value={customer.customer_id}>{customer.customer_id} · {customer.segment}</option>)}</select></label></div>
        {!selected ? <div className="inline-empty">Choose a customer to inspect their journey. {dataset.customers.length.toLocaleString("en-IN")} customers are available.</div> : journey.length === 0 ? <div className="inline-empty">No touchpoints found for this customer.</div> : (
          <div className="journey-flow">{journey.map((touch, index) => <article className={`journey-event ${touch.conversion ? "is-conversion" : ""}`} key={touch.external_id}><div className="journey-event-icon">{touch.conversion ? <CheckCircle2 size={17} /> : <Circle size={15} />}</div><div className="journey-event-card"><div className="journey-event-top"><strong>{touch.channel}</strong><time>{new Date(touch.timestamp).toLocaleString()}</time></div><p>{touch.touchpoint_type} · Campaign {touch.campaign_id}</p><div className="journey-event-meta"><span>Session {touch.session_id}</span>{touch.conversion && <span>Conversion · {formatCurrency(touch.revenue)} · Order {touch.order_id}</span>}</div></div>{index < journey.length - 1 && <ArrowDown className="journey-down" size={15} />}</article>)}</div>
        )}
      </section>
    </main>
  );
}
