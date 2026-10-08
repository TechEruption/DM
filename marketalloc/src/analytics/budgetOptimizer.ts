import type { BudgetPlan } from "../types/budget";
import type { ChannelMetrics } from "../types/analytics";

const positive = (value: number): number => Number.isFinite(value) && value > 0 ? value : 0;

export const recommendBudget = (channels: ChannelMetrics[], budget: number, minimum = 0, maximum = budget): BudgetPlan => {
  const entries = channels.filter((channel) => channel.spend > 0 || channel.attributedRevenue > 0);
  const empty = (error: string): BudgetPlan => ({ budget, allocations: [], projectedRevenue: 0, projectedConversions: 0, projectedRoas: null, projectedRoi: null, projectedCac: null, error });
  if (!Number.isFinite(budget) || budget < 0) return empty("Enter a valid non-negative budget.");
  if (entries.length === 0) return empty("Upload campaigns with spend and performance data to create a recommendation.");
  if (!Number.isFinite(minimum) || !Number.isFinite(maximum)) return empty("Enter finite minimum and maximum allocations.");
  const min = Math.max(0, minimum);
  const max = Math.max(0, maximum);
  if (max < min || min * entries.length > budget || max * entries.length < budget) {
    return empty("These minimum and maximum values cannot fit the selected budget across the available channels.");
  }
  const contributionTotal = Math.max(1, entries.reduce((sum, item) => sum + positive(item.attributedRevenue), 0));
  const score = (channel: ChannelMetrics): number => {
    const roas = positive(channel.roas ?? 0);
    const cvr = positive(channel.conversionRate ?? 0) / 100;
    const cacEfficiency = channel.cac && channel.cac > 0 ? 1 / channel.cac : 0;
    const contribution = positive(channel.attributedRevenue) / contributionTotal;
    return 0.5 * Math.min(roas, 5) / 5 + 0.25 * Math.min(cvr * 20, 1) + 0.15 * Math.min(cacEfficiency * 10000, 1) + 0.1 * contribution;
  };
  const scores = entries.map((channel) => Math.max(0.02, score(channel)));
  const spend = entries.map((channel) => positive(channel.spend));
  const allocations = entries.map(() => min);
  let remaining = Math.max(0, budget - min * entries.length);
  const step = Math.max(1, budget / 500);
  for (let count = 0; remaining > 0.01 && count < 10000; count += 1) {
    const eligible = entries.map((_, index) => index).filter((index) => allocations[index] + 0.01 < max);
    if (eligible.length === 0) break;
    const weights = eligible.map((index) => scores[index] / (1 + allocations[index] / Math.max(spend[index], 1)));
    const weightTotal = weights.reduce((sum, value) => sum + value, 0);
    const chunk = Math.min(step, remaining);
    let spent = 0;
    eligible.forEach((index, indexInEligible) => {
      const amount = Math.min(max - allocations[index], chunk * weights[indexInEligible] / weightTotal);
      allocations[index] += amount;
      spent += amount;
    });
    if (spent <= 0.01) break;
    remaining -= spent;
  }
  if (remaining > 1) return empty("Maximum allocations leave part of the budget unassigned. Increase the channel maximum.");
  const recommendations = entries.map((channel, index) => {
    const factor = spend[index] > 0 ? allocations[index] / spend[index] : 0;
    const saturation = 1 / (1 + 0.22 * Math.max(0, factor - 1));
    const projectedRevenue = positive(channel.roas ?? 0) * allocations[index] * saturation;
    const projectedConversions = channel.revenue > 0 ? channel.conversions * projectedRevenue / channel.revenue : 0;
    return {
      channel: channel.channel,
      currentAllocation: spend[index],
      recommendedAllocation: allocations[index],
      change: allocations[index] - spend[index],
      projectedConversions,
      projectedRevenue,
      projectedRoas: allocations[index] > 0 ? projectedRevenue / allocations[index] : null,
      projectedRoi: allocations[index] > 0 ? (projectedRevenue - allocations[index]) / allocations[index] * 100 : null,
      projectedCac: projectedConversions > 0 ? allocations[index] / projectedConversions : null,
    };
  });
  const projectedRevenue = recommendations.reduce((sum, item) => sum + item.projectedRevenue, 0);
  const projectedConversions = recommendations.reduce((sum, item) => sum + item.projectedConversions, 0);
  return {
    budget, allocations: recommendations, projectedRevenue, projectedConversions,
    projectedRoas: budget > 0 ? projectedRevenue / budget : null,
    projectedRoi: budget > 0 ? (projectedRevenue - budget) / budget * 100 : null,
    projectedCac: projectedConversions > 0 ? budget / projectedConversions : null,
    error: null,
  };
};
