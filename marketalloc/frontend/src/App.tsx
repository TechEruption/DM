import { Navigate, Route, Routes } from "react-router-dom";
import Dashboard from "./pages/Dashboard";
import Attribution from "./pages/Attribution";
import CustomerJourneys from "./pages/CustomerJourneys";
import Campaigns from "./pages/Campaigns";
import Channels from "./pages/Channels";
import BudgetOptimizer from "./pages/BudgetOptimizer";
import ScenarioSimulator from "./pages/ScenarioSimulator";
import FunnelAnalytics from "./pages/FunnelAnalytics";
import Insights from "./pages/Insights";
import DataImport from "./pages/DataImport";
import Methodology from "./pages/Methodology";

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/dashboard" replace />} />
      <Route path="/dashboard" element={<Dashboard />} />
      <Route path="/attribution" element={<Attribution />} />
      <Route path="/customer-journeys" element={<CustomerJourneys />} />
      <Route path="/campaigns" element={<Campaigns />} />
      <Route path="/channels" element={<Channels />} />
      <Route path="/budget-optimizer" element={<BudgetOptimizer />} />
      <Route path="/scenario-simulator" element={<ScenarioSimulator />} />
      <Route path="/funnel" element={<FunnelAnalytics />} />
      <Route path="/insights" element={<Insights />} />
      <Route path="/data-import" element={<DataImport />} />
      <Route path="/methodology" element={<Methodology />} />
    </Routes>
  );
}
