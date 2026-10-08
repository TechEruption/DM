import type { ReactNode } from "react";

export default function MetricCard({ label, value, note, icon }: { label: string; value: string; note?: string; icon?: ReactNode }) {
  return (
    <article className="metric-tile">
      <div className="metric-tile-top"><span>{label}</span>{icon && <span className="metric-icon">{icon}</span>}</div>
      <strong>{value}</strong>
      {note && <small>{note}</small>}
    </article>
  );
}
