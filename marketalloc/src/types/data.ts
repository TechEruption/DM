export type ChannelRecord = {
  name: string;
  description: string;
  is_demo: boolean;
};

export type CustomerRecord = {
  customer_id: string;
  segment: string;
  is_demo: boolean;
};

export type CampaignRecord = {
  campaign_id: string;
  name: string;
  channel: string;
  objective: string;
  spend: number;
  impressions: number;
  clicks: number;
  sessions: number;
  product_views: number;
  leads: number;
  start_date: string;
  end_date: string;
  is_demo: boolean;
};

export type TouchpointRecord = {
  external_id: string;
  customer_id: string;
  channel: string;
  campaign_id: string;
  session_id: string;
  timestamp: string;
  touchpoint_type: string;
  conversion: boolean;
  revenue: number;
  order_id: string;
  is_demo: boolean;
};

export type Dataset = {
  channels: ChannelRecord[];
  customers: CustomerRecord[];
  campaigns: CampaignRecord[];
  touchpoints: TouchpointRecord[];
};

export type DatasetKind = keyof Dataset;
export type CsvFiles = Partial<Record<DatasetKind, File>>;
