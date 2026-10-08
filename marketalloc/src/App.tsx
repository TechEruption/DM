import { lazy, Suspense } from "react";
import { Navigate, Route, Routes } from "react-router-dom";
import { DatasetProvider } from "./context/DatasetContext";
import AppLayout from "./components/layout/AppLayout";

const Landing = lazy(() => import("./pages/Landing"));
const Dashboard = lazy(() => import("./pages/Dashboard"));
const DataImport = lazy(() => import("./pages/DataImport"));
const Attribution = lazy(() => import("./pages/Attribution"));
const CustomerJourneys = lazy(() => import("./pages/CustomerJourneys"));
const Campaigns = lazy(() => import("./pages/Campaigns"));
const Channels = lazy(() => import("./pages/Channels"));
const BudgetOptimizer = lazy(() => import("./pages/BudgetOptimizer"));
const ScenarioSimulator = lazy(() => import("./pages/ScenarioSimulator"));
const FunnelAnalytics = lazy(() => import("./pages/FunnelAnalytics"));
const Insights = lazy(() => import("./pages/Insights"));
const Methodology = lazy(() => import("./pages/Methodology"));
const NotFound = lazy(() => import("./pages/NotFound"));

export default function App() {
  return (
    <DatasetProvider>
      <Suspense fallback={<div className="route-loading" role="status">Loading…</div>}>
        <Routes>
          <Route path="/" element={<AppLayout><Landing /></AppLayout>} />
          <Route path="/dashboard" element={<AppLayout><Dashboard /></AppLayout>} />
          <Route path="/upload" element={<AppLayout><DataImport /></AppLayout>} />
          <Route path="/data-import" element={<Navigate to="/upload" replace />} />
          <Route path="/attribution" element={<AppLayout><Attribution /></AppLayout>} />
          <Route path="/journeys" element={<AppLayout><CustomerJourneys /></AppLayout>} />
          <Route path="/customer-journeys" element={<Navigate to="/journeys" replace />} />
          <Route path="/campaigns" element={<AppLayout><Campaigns /></AppLayout>} />
          <Route path="/channels" element={<AppLayout><Channels /></AppLayout>} />
          <Route path="/budget" element={<AppLayout><BudgetOptimizer /></AppLayout>} />
          <Route path="/budget-optimizer" element={<Navigate to="/budget" replace />} />
          <Route path="/scenarios" element={<AppLayout><ScenarioSimulator /></AppLayout>} />
          <Route path="/scenario-simulator" element={<Navigate to="/scenarios" replace />} />
          <Route path="/funnel" element={<AppLayout><FunnelAnalytics /></AppLayout>} />
          <Route path="/insights" element={<AppLayout><Insights /></AppLayout>} />
          <Route path="/methodology" element={<AppLayout><Methodology /></AppLayout>} />
          <Route path="*" element={<AppLayout><NotFound /></AppLayout>} />
        </Routes>
      </Suspense>
    </DatasetProvider>
  );
}
