import type { AttributionModel, Credit } from "../types/analytics";
import type { TouchpointRecord } from "../types/data";

const weightsFor = (count: number, model: AttributionModel): number[] => {
  if (count < 1) return [];
  if (model === "first_touch") return [1, ...Array<number>(count - 1).fill(0)];
  if (model === "last_touch") return [...Array<number>(count - 1).fill(0), 1];
  if (model === "linear") return Array<number>(count).fill(1 / count);
  if (model === "time_decay") {
    const raw = Array.from({ length: count }, (_, index) => 0.7 ** (count - index - 1));
    const total = raw.reduce((sum, value) => sum + value, 0);
    return raw.map((value) => value / total);
  }
  if (count === 1) return [1];
  if (count === 2) return [0.5, 0.5];
  return [0.4, ...Array<number>(count - 2).fill(0.2 / (count - 2)), 0.4];
};

export const calculateAttribution = (
  touchpoints: TouchpointRecord[],
  model: AttributionModel,
): Credit[] => {
  const journeys = new Map<string, TouchpointRecord[]>();
  for (const touch of touchpoints) {
    const journey = journeys.get(touch.customer_id) ?? [];
    journey.push(touch);
    journeys.set(touch.customer_id, journey);
  }
  const credits: Credit[] = [];
  for (const journey of journeys.values()) {
    journey.sort((left, right) =>
      left.timestamp.localeCompare(right.timestamp) || left.external_id.localeCompare(right.external_id),
    );
    for (let conversionIndex = 0; conversionIndex < journey.length; conversionIndex += 1) {
      const conversion = journey[conversionIndex];
      if (!conversion.conversion) continue;
      const touches = journey.slice(0, conversionIndex + 1);
      const rawWeights = weightsFor(touches.length, model);
      const weights = rawWeights.map((weight, index) =>
        index === rawWeights.length - 1 ? 0 : Math.round(weight * 10000) / 10000,
      );
      let assigned = 0;
      touches.forEach((touch, index) => {
        const share = index === touches.length - 1 ? 1 - assigned : weights[index];
        assigned += share;
        credits.push({
          customerId: conversion.customer_id,
          orderId: conversion.order_id,
          convertedAt: conversion.timestamp,
          channel: touch.channel,
          campaignId: touch.campaign_id,
          share,
          revenue: conversion.revenue * share,
        });
      });
    }
  }
  return credits;
};
