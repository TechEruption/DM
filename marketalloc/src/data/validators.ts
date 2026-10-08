import type { CampaignRecord, ChannelRecord, CustomerRecord, Dataset, DatasetKind, TouchpointRecord } from "../types/data";

type Raw = Record<string, string | number | boolean | null | undefined>;
const requiredColumns: Record<DatasetKind, string[]> = {
  channels: ["name", "description"],
  customers: ["customer_id", "segment"],
  campaigns: ["campaign_id", "name", "channel", "objective", "spend", "impressions", "clicks", "sessions", "product_views", "leads", "start_date", "end_date"],
  touchpoints: ["external_id", "customer_id", "channel", "campaign_id", "session_id", "timestamp", "touchpoint_type", "conversion", "revenue", "order_id"],
};
const text = (value: Raw[string]): string => String(value ?? "").trim();
const num = (value: Raw[string], field: string, row: number, errors: string[]): number => {
  const source = text(value);
  if (source === "") return 0;
  const result = Number(source);
  if (!Number.isFinite(result) || result < 0) errors.push(`Row ${row}: “${field}” must be a non-negative number.`);
  return Number.isFinite(result) && result >= 0 ? result : 0;
};
const bool = (value: Raw[string]): boolean => ["true", "1", "yes"].includes(text(value).toLowerCase());
const unique = (values: string[], label: string, errors: string[]) => {
  const seen = new Set<string>();
  values.forEach((value, index) => {
    if (!value) errors.push(`${label} is missing in row ${index + 2}.`);
    else if (seen.has(value)) errors.push(`Duplicate ${label} “${value}”.`);
    seen.add(value);
  });
};
const validDateOnly = (value: string): boolean => {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(value) || Number.isNaN(Date.parse(value))) return false;
  return new Date(`${value}T00:00:00Z`).toISOString().slice(0, 10) === value;
};
const validTimestamp = (value: string): boolean =>
  /^\d{4}-\d{2}-\d{2}T/.test(value) && validDateOnly(value.slice(0, 10)) && !Number.isNaN(Date.parse(value));

export function validateRows(kind: "channels", rows: Raw[]): { records: ChannelRecord[]; errors: string[] };
export function validateRows(kind: "customers", rows: Raw[]): { records: CustomerRecord[]; errors: string[] };
export function validateRows(kind: "campaigns", rows: Raw[]): { records: CampaignRecord[]; errors: string[] };
export function validateRows(kind: "touchpoints", rows: Raw[]): { records: TouchpointRecord[]; errors: string[] };
export function validateRows(kind: DatasetKind, rows: Raw[]): { records: Dataset[DatasetKind]; errors: string[] } {
  const errors: string[] = [];
  if (rows.length === 0) return { records: [], errors: [`${kind}.csv is empty. Add at least one data row.`] };
  const headers = Object.keys(rows[0]).map((key) => key.trim());
  requiredColumns[kind].forEach((column) => {
    if (!headers.includes(column)) errors.push(`${kind}.csv is missing the required column: ${column}.`);
  });
  if (errors.length) return { records: [], errors };
  if (kind === "channels") {
    const records: ChannelRecord[] = rows.map((row, index) => {
      if (!text(row.description)) errors.push(`Channel row ${index + 2} is missing a description.`);
      return { name: text(row.name), description: text(row.description), is_demo: bool(row.is_demo) };
    });
    unique(records.map((item) => item.name), "channel name", errors);
    return { records, errors };
  }
  if (kind === "customers") {
    const records: CustomerRecord[] = rows.map((row, index) => {
      if (!text(row.segment)) errors.push(`Customer row ${index + 2} is missing a segment.`);
      return { customer_id: text(row.customer_id), segment: text(row.segment), is_demo: bool(row.is_demo) };
    });
    unique(records.map((item) => item.customer_id), "customer ID", errors);
    return { records, errors };
  }
  if (kind === "campaigns") {
    const records: CampaignRecord[] = rows.map((row, index) => {
      const line = index + 2;
      const start = text(row.start_date);
      const end = text(row.end_date);
      if (!validDateOnly(start)) errors.push(`Campaign row ${line} has an invalid start_date; use YYYY-MM-DD.`);
      if (!validDateOnly(end)) errors.push(`Campaign row ${line} has an invalid end_date; use YYYY-MM-DD.`);
      if (!text(row.name) || !text(row.channel) || !text(row.objective)) errors.push(`Campaign row ${line} needs a name, channel and objective.`);
      if (validDateOnly(start) && validDateOnly(end) && Date.parse(start) > Date.parse(end)) errors.push(`Campaign row ${line} ends before it starts.`);
      return {
        campaign_id: text(row.campaign_id), name: text(row.name), channel: text(row.channel), objective: text(row.objective),
        spend: num(row.spend, "spend", line, errors), impressions: num(row.impressions, "impressions", line, errors),
        clicks: num(row.clicks, "clicks", line, errors), sessions: num(row.sessions, "sessions", line, errors),
        product_views: num(row.product_views, "product_views", line, errors), leads: num(row.leads, "leads", line, errors),
        start_date: start, end_date: end, is_demo: bool(row.is_demo),
      }
    });
    unique(records.map((item) => item.campaign_id), "campaign ID", errors);
    return { records, errors };
  }
  const records: TouchpointRecord[] = rows.map((row, index) => {
    const line = index + 2;
    const timestamp = text(row.timestamp);
    if (!validTimestamp(timestamp)) errors.push(`Touchpoint row ${line} has an invalid timestamp; use an ISO 8601 date and time.`);
    const conversionText = text(row.conversion).toLowerCase();
    if (!["true", "false", "1", "0", "yes", "no"].includes(conversionText)) errors.push(`Touchpoint row ${line} conversion must be true or false.`);
    const conversion = ["true", "1", "yes"].includes(conversionText);
    const order = text(row.order_id);
    if (conversion && !order) errors.push(`Converting touchpoint row ${line} needs an order_id.`);
    if (!text(row.customer_id) || !text(row.channel) || !text(row.campaign_id) || !text(row.session_id) || !text(row.touchpoint_type)) {
      errors.push(`Touchpoint row ${line} needs a customer, channel, campaign, session and touchpoint type.`);
    }
    return {
      external_id: text(row.external_id), customer_id: text(row.customer_id), channel: text(row.channel),
      campaign_id: text(row.campaign_id), session_id: text(row.session_id), timestamp,
      touchpoint_type: text(row.touchpoint_type), conversion, revenue: num(row.revenue, "revenue", line, errors),
      order_id: order, is_demo: bool(row.is_demo),
    };
  });
  unique(records.map((item) => item.external_id), "touchpoint external ID", errors);
  unique(records.filter((item) => item.conversion).map((item) => item.order_id), "conversion order ID", errors);
  return { records, errors };
};

export const validateDatasetReferences = (dataset: Dataset): string[] => {
  const errors: string[] = [];
  const channels = new Set(dataset.channels.map((item) => item.name));
  const customers = new Set(dataset.customers.map((item) => item.customer_id));
  const campaigns = new Map(dataset.campaigns.map((item) => [item.campaign_id, item]));
  const unknownCampaign = dataset.touchpoints.filter((touch) => !campaigns.has(touch.campaign_id)).length;
  const unknownCustomer = dataset.touchpoints.filter((touch) => !customers.has(touch.customer_id)).length;
  const unknownTouchChannel = dataset.touchpoints.filter((touch) => !channels.has(touch.channel)).length;
  const unknownCampaignChannel = dataset.campaigns.filter((campaign) => !channels.has(campaign.channel)).length;
  if (unknownCampaign) errors.push(`${unknownCampaign} touchpoints reference a campaign that does not exist.`);
  if (unknownCustomer) errors.push(`${unknownCustomer} touchpoints reference a customer that does not exist.`);
  if (unknownTouchChannel) errors.push(`${unknownTouchChannel} touchpoints reference a channel that does not exist.`);
  if (unknownCampaignChannel) errors.push(`${unknownCampaignChannel} campaigns reference a channel that does not exist.`);
  return errors;
};
