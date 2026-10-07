export const formatCurrency = (value: number) => `₹${value.toLocaleString("en-IN", { maximumFractionDigits: 2 })}`;
