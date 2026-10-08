import Papa from "papaparse";
import type { DatasetKind } from "../types/data";

export const datasetKinds: DatasetKind[] = ["channels", "customers", "campaigns", "touchpoints"];

export const readCsvFile = (file: File): Promise<{ rows: Record<string, string>[]; errors: string[] }> =>
  new Promise((resolve, reject) => {
    Papa.parse<Record<string, string>>(file, {
      header: true,
      skipEmptyLines: "greedy",
      transformHeader: (header) => header.trim().replace(/^\uFEFF/, ""),
      complete: (result) => resolve({
        rows: result.data,
        errors: result.errors.slice(0, 20).map((error) => `Row ${(error.row ?? 0) + 2}: ${error.message}`),
      }),
      error: (error) => reject(new Error(error.message)),
    });
  });
