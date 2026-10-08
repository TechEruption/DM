import { useState } from "react";
import { Check, FileSpreadsheet, UploadCloud } from "lucide-react";
import { Link, useNavigate } from "react-router-dom";
import { datasetKinds, readCsvFile } from "../data/csvParser";
import { validateDatasetReferences, validateRows } from "../data/validators";
import type { CsvFiles, Dataset, DatasetKind } from "../types/data";
import { useDataset } from "../context/DatasetContext";
import PageHeader from "../components/common/PageHeader";

const guides: { type: DatasetKind; label: string; text: string; columns: string }[] = [
  { type: "channels", label: "Channels", text: "Define your marketing channels.", columns: "name, description" },
  { type: "customers", label: "Customers", text: "Customer identifiers and segments.", columns: "customer_id, segment" },
  { type: "campaigns", label: "Campaigns", text: "Spend and delivery performance.", columns: "campaign_id, name, channel, objective, spend, impressions, clicks, sessions, product_views, leads, start_date, end_date" },
  { type: "touchpoints", label: "Touchpoints", text: "Customer journey events and conversions.", columns: "external_id, customer_id, channel, campaign_id, session_id, timestamp, touchpoint_type, conversion, revenue, order_id" },
];

export default function DataImport() {
  const navigate = useNavigate();
  const { setDataset } = useDataset();
  const [files, setFiles] = useState<CsvFiles>({});
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [success, setSuccess] = useState<Dataset | null>(null);

  const processFiles = async () => {
    setError(null);
    setSuccess(null);
    const missing = datasetKinds.filter((kind) => !files[kind]);
    if (missing.length) {
      setError(`Choose all four CSV files before analyzing. Missing: ${missing.map((item) => `${item}.csv`).join(", ")}.`);
      return;
    }
    const oversized = datasetKinds.find((kind) => (files[kind]?.size ?? 0) > 25 * 1024 * 1024);
    if (oversized) {
      setError(`${oversized}.csv is larger than 25 MB. Reduce the file size and try again.`);
      return;
    }
    setBusy(true);
    try {
      const candidate: Dataset = { channels: [], customers: [], campaigns: [], touchpoints: [] };
      const fileErrors: string[] = [];
      for (const kind of datasetKinds) {
        const file = files[kind];
        if (!file) {
          fileErrors.push(`Choose ${kind}.csv.`);
          continue;
        }
        const result = await readCsvFile(file);
        fileErrors.push(...result.errors.map((message) => `${kind}.csv: ${message}`));
        switch (kind) {
          case "channels": {
            const checked = validateRows("channels", result.rows);
            candidate.channels = checked.records;
            fileErrors.push(...checked.errors.map((message) => `${kind}.csv: ${message}`));
            break;
          }
          case "customers": {
            const checked = validateRows("customers", result.rows);
            candidate.customers = checked.records;
            fileErrors.push(...checked.errors.map((message) => `${kind}.csv: ${message}`));
            break;
          }
          case "campaigns": {
            const checked = validateRows("campaigns", result.rows);
            candidate.campaigns = checked.records;
            fileErrors.push(...checked.errors.map((message) => `${kind}.csv: ${message}`));
            break;
          }
          case "touchpoints": {
            const checked = validateRows("touchpoints", result.rows);
            candidate.touchpoints = checked.records;
            fileErrors.push(...checked.errors.map((message) => `${kind}.csv: ${message}`));
            break;
          }
        }
      }
      if (fileErrors.length) {
        setError(fileErrors.slice(0, 12).join("\n"));
        return;
      }
      const referenceErrors = validateDatasetReferences(candidate);
      if (referenceErrors.length) {
        setError(referenceErrors.join("\n"));
        return;
      }
      setDataset(candidate);
      setSuccess(candidate);
    } catch {
      setError("Unable to read a selected CSV file. Check that it is valid CSV format and try again.");
    } finally {
      setBusy(false);
    }
  };

  return (
    <main className="content-wrap">
      <PageHeader eyebrow="DATA WORKSPACE" title="Upload your marketing data" description="Analyze campaign performance, customer journeys, attribution and marketing ROI from your CSV files." />
      <section className="privacy-note"><span className="note-mark" /><div><strong>Private to this session</strong><p>Files are parsed and analyzed in this browser. Nothing is uploaded or saved; closing or refreshing the page clears your dataset.</p></div></section>
      <section className="upload-grid" aria-label="Select required CSV files">
        {guides.map((guide) => (
          <article className={`upload-card ${files[guide.type] ? "has-file" : ""}`} key={guide.type}>
            <div className="upload-card-head"><span className="upload-icon"><FileSpreadsheet size={18} /></span><div><h2>{guide.label}</h2><p>{guide.text}</p></div>{files[guide.type] && <Check className="file-check" size={18} />}</div>
            <p className="column-list"><strong>Required columns</strong>{guide.columns}</p>
            <label className="file-picker">
              <UploadCloud size={15} /><span>{files[guide.type]?.name ?? `Choose ${guide.type}.csv`}</span>
              <input type="file" accept=".csv,text/csv" onChange={(event) => {
                const file = event.currentTarget.files?.[0];
                if (file && !file.name.toLowerCase().endsWith(".csv")) {
                  setFiles((current) => {
                    const next = { ...current };
                    delete next[guide.type];
                    return next;
                  });
                  setError(`${file.name} is not a CSV file. Choose a .csv file and try again.`);
                  setSuccess(null);
                  return;
                }
                setFiles((current) => ({ ...current, [guide.type]: file }));
                setError(null);
                setSuccess(null);
              }} />
            </label>
          </article>
        ))}
      </section>
      {error && <div className="validation-errors" role="alert"><strong>We found a problem with this dataset</strong><pre>{error}</pre><span>Correct the highlighted CSV values and select the updated files.</span></div>}
      <div className="upload-actions"><span>Accepts CSV files up to 25 MB each.</span><button className="button button-accent button-large" disabled={busy} onClick={processFiles}>{busy ? "Validating files…" : "Validate & analyze"}</button></div>
      {success && (
        <section className="success-panel" aria-live="polite">
          <span className="success-mark"><Check size={18} /></span>
          <div className="success-copy"><h2>Dataset loaded successfully</h2><p>Four files processed. These records are now available for analysis.</p>
            <div className="dataset-counts"><span><strong>{success.customers.length.toLocaleString("en-IN")}</strong> customers</span><span><strong>{success.touchpoints.length.toLocaleString("en-IN")}</strong> touchpoints</span><span><strong>{success.campaigns.length.toLocaleString("en-IN")}</strong> campaigns</span><span><strong>{success.channels.length.toLocaleString("en-IN")}</strong> channels</span></div>
          </div>
          <button className="button button-accent" onClick={() => navigate("/dashboard")}>Open dashboard</button>
        </section>
      )}
      <section className="template-help"><div><h2>Need a starting point?</h2><p>Download header-only CSV templates, then add your own business data.</p></div><div className="template-links">{guides.map((guide) => <a key={guide.type} href={`data:text/csv;charset=utf-8,${encodeURIComponent(`${guide.columns}\n`)}`} download={`${guide.type}.csv`}>{guide.label} template</a>)}</div></section>
      <p className="upload-back"><Link to="/">Back to product overview</Link></p>
    </main>
  );
}
