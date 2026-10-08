export type AttributionModel =
  | "first_touch"
  | "last_touch"
  | "linear"
  | "time_decay"
  | "position_based";

export type Metrics = {
  spend: number;
  impressions: number;
  clicks: number;
  sessions: number;
  productViews: number;
  leads: number;
  conversions: number;
  revenue: number;
  attributedRevenue: number;
  ctr: number | null;
  cpc: number | null;
  conversionRate: number | null;
  cac: number | null;
  aov: number | null;
  roas: number | null;
  roi: number | null;
};

export type Credit = {
  customerId: string;
  orderId: string;
  convertedAt: string;
  channel: string;
  campaignId: string;
  share: number;
  revenue: number;
};

export type CampaignMetrics = Metrics & {
  campaignId: string;
  campaignName: string;
  channel: string;
  objective: string;
  startDate: string;
  endDate: string;
};

export type ChannelMetrics = Metrics & {
  channel: string;
  description: string;
};

export type MonthlyMetrics = {
  month: string;
  spend: number;
  revenue: number;
  attributedRevenue: number;
  conversions: number;
};

export type FunnelStage = {
  name: string;
  value: number;
  rateFromPrevious: number | null;
  dropOff: number | null;
  kind: "count" | "currency";
};

export type AnalyticsReport = {
  summary: Metrics;
  channels: ChannelMetrics[];
  campaigns: CampaignMetrics[];
  credits: Credit[];
  trends: MonthlyMetrics[];
  funnel: FunnelStage[];
  largestLeakage: { from: string; to: string; dropOff: number } | null;
};

export type Insight = {
  title: string;
  detail: string;
  kind: "positive" | "watch" | "neutral";
};
