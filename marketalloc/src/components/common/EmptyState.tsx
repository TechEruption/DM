import { ArrowRight, FileUp } from "lucide-react";
import { Link } from "react-router-dom";

export default function EmptyState({ title = "No marketing dataset loaded", detail = "Upload your CSV files to analyze campaign performance, customer journeys, attribution and budget allocation." }: { title?: string; detail?: string }) {
  return (
    <section className="empty-state">
      <span className="empty-icon"><FileUp size={21} /></span>
      <h2>{title}</h2>
      <p>{detail}</p>
      <Link className="button button-accent" to="/upload">Upload your data <ArrowRight size={15} /></Link>
      <small>Your files are analyzed in this browser session and are not saved.</small>
    </section>
  );
}
