import { createContext, useContext, useMemo, useState, type ReactNode } from "react";
import { processDataset } from "../analytics/dataProcessor";
import type { AttributionModel, AnalyticsReport } from "../types/analytics";
import type { Dataset } from "../types/data";

type DatasetContextValue = {
  dataset: Dataset | null;
  model: AttributionModel;
  report: AnalyticsReport | null;
  setDataset: (dataset: Dataset) => void;
  setModel: (model: AttributionModel) => void;
  clearDataset: () => void;
};
const DatasetContext = createContext<DatasetContextValue | null>(null);

export function DatasetProvider({ children }: { children: ReactNode }) {
  const [dataset, setDataset] = useState<Dataset | null>(null);
  const [model, setModel] = useState<AttributionModel>("linear");
  const report = useMemo(() => dataset ? processDataset(dataset, model) : null, [dataset, model]);
  const value = useMemo(() => ({
    dataset, model, report, setDataset, setModel, clearDataset: () => setDataset(null),
  }), [dataset, model, report]);
  return <DatasetContext.Provider value={value}>{children}</DatasetContext.Provider>;
}

export const useDataset = (): DatasetContextValue => {
  const context = useContext(DatasetContext);
  if (!context) throw new Error("useDataset must be used inside DatasetProvider.");
  return context;
};
