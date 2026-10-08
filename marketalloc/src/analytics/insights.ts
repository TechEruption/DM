import type { AnalyticsReport, Insight } from "../types/analytics";

export const buildInsights = (report: AnalyticsReport): Insight[] => {
  const insights: Insight[] = [];
  const topRevenue = [...report.channels].sort((a, b) => b.attributedRevenue - a.attributedRevenue)[0];
  const topRoas = [...report.channels].filter((item) => item.roas !== null).sort((a, b) => (b.roas ?? 0) - (a.roas ?? 0))[0];
  const highCac = [...report.channels].filter((item) => item.cac !== null).sort((a, b) => (b.cac ?? 0) - (a.cac ?? 0))[0];
  if (topRevenue && topRevenue.attributedRevenue > 0) insights.push({ title: `${topRevenue.channel} leads attributed revenue`, detail: `It contributed ${topRevenue.attributedRevenue.toLocaleString("en-IN", { style: "currency", currency: "INR", maximumFractionDigits: 0 })} under the selected attribution model.`, kind: "positive" });
  if (topRoas) insights.push({ title: `${topRoas.channel} has the strongest ROAS`, detail: `Attributed revenue is ${(topRoas.roas ?? 0).toFixed(2)}× the channel's spend.`, kind: (topRoas.roas ?? 0) >= 1 ? "positive" : "watch" });
  if (highCac?.cac !== null && highCac?.cac !== undefined) insights.push({ title: `${highCac.channel} has the highest customer acquisition cost`, detail: `Current CAC is ${highCac.cac.toLocaleString("en-IN", { style: "currency", currency: "INR", maximumFractionDigits: 0 })}; compare its conversion efficiency with the rest of the mix.`, kind: "watch" });
  if (report.largestLeakage) insights.push({ title: `Largest funnel drop-off: ${report.largestLeakage.from} to ${report.largestLeakage.to}`, detail: `${report.largestLeakage.dropOff.toFixed(1)}% of measured volume is lost between these stages.`, kind: "watch" });
  if (report.summary.roas !== null) insights.push({ title: report.summary.roas >= 1 ? "Marketing spend is returning above break-even" : "Marketing spend is below break-even", detail: `Overall attributed ROAS is ${report.summary.roas.toFixed(2)}× with ${report.summary.roi?.toFixed(1) ?? "—"}% ROI.`, kind: report.summary.roas >= 1 ? "positive" : "watch" });
  return insights;
};
