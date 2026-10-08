import { calculateAttribution } from "./attribution";
import { calculateFunnel } from "./funnel";
import { buildMetrics } from "./metrics";
import type { AnalyticsReport, AttributionModel, CampaignMetrics, ChannelMetrics, MonthlyMetrics } from "../types/analytics";
import type { Dataset } from "../types/data";

const sum = (values: number[]): number => values.reduce((total, value) => total + value, 0);

export const processDataset = (data: Dataset, model: AttributionModel): AnalyticsReport => {
  const credits = calculateAttribution(data.touchpoints, model);
  const conversionTouches = data.touchpoints.filter((touch) => touch.conversion);
  const append = <T,>(map: Map<string, T[]>, key: string, value: T): void => {
    const items = map.get(key);
    if (items) items.push(value);
    else map.set(key, [value]);
  };
  const touchesByCampaign = new Map<string, typeof data.touchpoints>();
  const convertingTouchesByChannel = new Map<string, typeof data.touchpoints>();
  const creditsByCampaign = new Map<string, typeof credits>();
  const creditsByChannel = new Map<string, typeof credits>();
  const campaignsByChannel = new Map<string, CampaignMetrics[]>();
  data.touchpoints.forEach((touch) => {
    append(touchesByCampaign, touch.campaign_id, touch);
    if (touch.conversion) append(convertingTouchesByChannel, touch.channel, touch);
  });
  credits.forEach((credit) => {
    append(creditsByCampaign, credit.campaignId, credit);
    append(creditsByChannel, credit.channel, credit);
  });
  const campaigns: CampaignMetrics[] = data.campaigns.map((campaign) => {
    const campaignTouches = touchesByCampaign.get(campaign.campaign_id) ?? [];
    const campaignCredits = creditsByCampaign.get(campaign.campaign_id) ?? [];
    const creditedConversions = new Map<string, number>();
    campaignCredits.forEach((credit) => creditedConversions.set(credit.orderId, (creditedConversions.get(credit.orderId) ?? 0) + credit.share));
    return {
      campaignId: campaign.campaign_id,
      campaignName: campaign.name,
      channel: campaign.channel,
      objective: campaign.objective,
      startDate: campaign.start_date,
      endDate: campaign.end_date,
      ...buildMetrics({
        spend: campaign.spend,
        impressions: campaign.impressions,
        clicks: campaign.clicks,
        sessions: campaign.sessions,
        productViews: campaign.product_views,
        leads: campaign.leads,
        conversions: sum([...creditedConversions.values()]),
        revenue: sum(campaignTouches.filter((touch) => touch.conversion).map((touch) => touch.revenue)),
        attributedRevenue: sum(campaignCredits.map((credit) => credit.revenue)),
      }),
    };
  });
  campaigns.forEach((campaign) => append(campaignsByChannel, campaign.channel, campaign));
  const channels: ChannelMetrics[] = data.channels.map((channel) => {
    const channelCampaigns = campaignsByChannel.get(channel.name) ?? [];
    const channelTouches = convertingTouchesByChannel.get(channel.name) ?? [];
    const channelCredits = creditsByChannel.get(channel.name) ?? [];
    return {
      channel: channel.name,
      description: channel.description,
      ...buildMetrics({
        spend: sum(channelCampaigns.map((item) => item.spend)),
        impressions: sum(channelCampaigns.map((item) => item.impressions)),
        clicks: sum(channelCampaigns.map((item) => item.clicks)),
        sessions: sum(channelCampaigns.map((item) => item.sessions)),
        productViews: sum(channelCampaigns.map((item) => item.productViews)),
        leads: sum(channelCampaigns.map((item) => item.leads)),
        conversions: sum(channelCredits.map((item) => item.share)),
        revenue: sum(channelTouches.map((item) => item.revenue)),
        attributedRevenue: sum(channelCredits.map((item) => item.revenue)),
      }),
    };
  });
  const totalSpend = sum(campaigns.map((item) => item.spend));
  const totalRevenue = sum(conversionTouches.map((item) => item.revenue));
  const totalAttributedRevenue = sum(credits.map((item) => item.revenue));
  const summary = buildMetrics({
    spend: totalSpend,
    impressions: sum(campaigns.map((item) => item.impressions)),
    clicks: sum(campaigns.map((item) => item.clicks)),
    sessions: sum(campaigns.map((item) => item.sessions)),
    productViews: sum(campaigns.map((item) => item.productViews)),
    leads: sum(campaigns.map((item) => item.leads)),
    conversions: conversionTouches.length,
    revenue: totalRevenue,
    attributedRevenue: totalAttributedRevenue,
  });
  const monthly = new Map<string, MonthlyMetrics>();
  campaigns.forEach((campaign) => {
    const month = campaign.startDate.slice(0, 7);
    const current = monthly.get(month) ?? { month, spend: 0, revenue: 0, attributedRevenue: 0, conversions: 0 };
    current.spend += campaign.spend;
    monthly.set(month, current);
  });
  conversionTouches.forEach((touch) => {
    const month = touch.timestamp.slice(0, 7);
    const current = monthly.get(month) ?? { month, spend: 0, revenue: 0, attributedRevenue: 0, conversions: 0 };
    current.revenue += touch.revenue;
    current.conversions += 1;
    monthly.set(month, current);
  });
  credits.forEach((credit) => {
    const month = credit.convertedAt.slice(0, 7);
    const current = monthly.get(month) ?? { month, spend: 0, revenue: 0, attributedRevenue: 0, conversions: 0 };
    current.attributedRevenue += credit.revenue;
    monthly.set(month, current);
  });
  const funnel = calculateFunnel(data.campaigns, data.touchpoints);
  return {
    summary,
    channels,
    campaigns,
    credits,
    trends: [...monthly.values()].sort((left, right) => left.month.localeCompare(right.month)),
    funnel: funnel.stages,
    largestLeakage: funnel.largestLeakage,
  };
};
