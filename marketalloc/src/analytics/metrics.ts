import type { Metrics } from "../types/analytics";

export const safeDivide = (numerator: number, denominator: number): number | null => {
  if (!Number.isFinite(numerator) || !Number.isFinite(denominator) || denominator <= 0) return null;
  const result = numerator / denominator;
  return Number.isFinite(result) ? result : null;
};

export const buildMetrics = (values: Omit<Metrics, "ctr" | "cpc" | "conversionRate" | "cac" | "aov" | "roas" | "roi">): Metrics => {
  const roas = safeDivide(values.attributedRevenue, values.spend);
  return {
    ...values,
    ctr: safeDivide(values.clicks * 100, values.impressions),
    cpc: safeDivide(values.spend, values.clicks),
    conversionRate: safeDivide(values.conversions * 100, values.clicks),
    cac: safeDivide(values.spend, values.conversions),
    aov: safeDivide(values.revenue, values.conversions),
    roas,
    roi: roas === null ? null : (roas - 1) * 100,
  };
};
