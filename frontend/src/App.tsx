import { HashRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import Layout from './components/layout/Layout';
import Dashboard from './pages/Dashboard';
import Production from './pages/Production';
import Quality from './pages/Quality';
import Downtimes from './pages/Downtimes';
import Planning from './pages/Planning';
import Orders from './pages/Orders';
import Launch from './pages/Launch';
import Analysis from './pages/Analysis';
import Pmp from './pages/Pmp';
import HistoryPage from './pages/History';
import Reports from './pages/Reports';
import AdminData from './pages/AdminData';
import Leadership from './pages/Leadership';
import MachineSetup from './pages/MachineSetup';
import Tooling from './pages/Tooling';
import Pcp from './pages/Pcp';
import DashboardTV from './pages/DashboardTV';
import SeedFirestore from './pages/SeedFirestore';

export default function App() {
  return (
    <HashRouter>
      <AuthProvider>
        <Routes>
          <Route path="/tv" element={<DashboardTV />} />
          <Route path="/" element={<Layout />}>
            <Route index element={<Dashboard />} />
            <Route path="production" element={<Production />} />
            <Route path="orders" element={<Orders />} />
            <Route path="launch" element={<Launch />} />
            <Route path="analysis" element={<Analysis />} />
            <Route path="quality" element={<Quality />} />
            <Route path="downtimes" element={<Downtimes />} />
            <Route path="planning" element={<Planning />} />
            <Route path="pmp" element={<Pmp />} />
            <Route path="history" element={<HistoryPage />} />
            <Route path="reports" element={<Reports />} />
            <Route path="admin" element={<AdminData />} />
            <Route path="leadership" element={<Leadership />} />
            <Route path="setup" element={<MachineSetup />} />
            <Route path="tooling" element={<Tooling />} />
            <Route path="pcp" element={<Pcp />} />
            <Route path="seed" element={<SeedFirestore />} />
          </Route>
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </AuthProvider>
    </HashRouter>
  );
}
