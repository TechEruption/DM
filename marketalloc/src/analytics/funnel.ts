import type { FunnelStage } from "../types/analytics";
import type { CampaignRecord, TouchpointRecord } from "../types/data";

export const calculateFunnel = (
  campaigns: CampaignRecord[],
  touchpoints: TouchpointRecord[],
): { stages: FunnelStage[]; largestLeakage: { from: string; to: string; dropOff: number } | null } => {
  const conversions = touchpoints.filter((touch) => touch.conversion).length;
  const stages: FunnelStage[] = [
    { name: "Impressions", value: campaigns.reduce((sum, item) => sum + item.impressions, 0), rateFromPrevious: null, dropOff: null, kind: "count" },
    { name: "Clicks", value: campaigns.reduce((sum, item) => sum + item.clicks, 0), rateFromPrevious: null, dropOff: null, kind: "count" },
    { name: "Website sessions", value: campaigns.reduce((sum, item) => sum + item.sessions, 0), rateFromPrevious: null, dropOff: null, kind: "count" },
    { name: "Product views", value: campaigns.reduce((sum, item) => sum + item.product_views, 0), rateFromPrevious: null, dropOff: null, kind: "count" },
    { name: "Leads", value: campaigns.reduce((sum, item) => sum + item.leads, 0), rateFromPrevious: null, dropOff: null, kind: "count" },
    { name: "Conversions", value: conversions, rateFromPrevious: null, dropOff: null, kind: "count" },
    { name: "Revenue", value: touchpoints.filter((touch) => touch.conversion).reduce((sum, touch) => sum + touch.revenue, 0), rateFromPrevious: null, dropOff: null, kind: "currency" },
  ];
  stages.forEach((stage, index) => {
    if (index === 0 || stage.kind === "currency") return;
    const previous = stages[index - 1].value;
    stage.rateFromPrevious = previous > 0 ? stage.value / previous * 100 : null;
    stage.dropOff = previous > 0 ? Math.max(0, (previous - stage.value) / previous * 100) : null;
  });
  const leakage = stages.slice(1, 6)
    .filter((stage): stage is FunnelStage & { dropOff: number } => stage.dropOff !== null)
    .map((stage) => {
      const index = stages.indexOf(stage);
      return { from: stages[index - 1].name, to: stage.name, dropOff: stage.dropOff };
    })
    .sort((left, right) => right.dropOff - left.dropOff)[0] ?? null;
  return { stages, largestLeakage: leakage };
};
