const moneyFormatter = new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR", maximumFractionDigits: 0 });
const preciseMoneyFormatter = new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR", maximumFractionDigits: 2 });
const numberFormatter = new Intl.NumberFormat("en-IN", { maximumFractionDigits: 0 });
const compactMoneyFormatter = new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR", notation: "compact", maximumFractionDigits: 1 });

export const formatCurrency = (value: number | null, precise = false): string =>
  value === null || !Number.isFinite(value) ? "—" : (precise ? preciseMoneyFormatter : moneyFormatter).format(value);
export const formatCompactCurrency = (value: number): string => Number.isFinite(value) ? compactMoneyFormatter.format(value) : "—";
export const formatNumber = (value: number | null, digits = 0): string =>
  value === null || !Number.isFinite(value)
    ? "—"
    : new Intl.NumberFormat("en-IN", { maximumFractionDigits: digits }).format(value);
export const formatPercent = (value: number | null, digits = 1): string =>
  value === null || !Number.isFinite(value) ? "—" : `${value.toFixed(digits)}%`;
export const formatRoas = (value: number | null): string =>
  value === null || !Number.isFinite(value) ? "—" : `${value.toFixed(2)}×`;
