export type BudgetRecommendation = {
  channel: string;
  currentAllocation: number;
  recommendedAllocation: number;
  change: number;
  projectedConversions: number;
  projectedRevenue: number;
  projectedRoas: number | null;
  projectedRoi: number | null;
  projectedCac: number | null;
};

export type BudgetPlan = {
  budget: number;
  allocations: BudgetRecommendation[];
  projectedRevenue: number;
  projectedConversions: number;
  projectedRoas: number | null;
  projectedRoi: number | null;
  projectedCac: number | null;
  error: string | null;
};
