import React from 'react';
import { BrowserRouter, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import './index.css';
import Sidebar from './components/layout/Sidebar';
import OverviewPage from './pages/OverviewPage';
import ImportWizardPage from './pages/import/ImportWizardPage';
import FeedbackExplorerPage from './pages/feedback/FeedbackExplorerPage';
import HotspotPage from './pages/hotspot/HotspotPage';

const LegacyDashboardRedirect: React.FC = () => {
  const location = useLocation();
  return <Navigate to={`/overview${location.search}`} replace />;
};

const App: React.FC = () => {
  return (
    <BrowserRouter>
      <div className="app-shell">
        <Sidebar />
        <div className="main-area">
          <Routes>
            <Route path="/" element={<Navigate to="/overview" replace />} />
            <Route path="/overview" element={<OverviewPage />} />
            <Route path="/customer-journey" element={<LegacyDashboardRedirect />} />
            <Route path="/service-pain-points" element={<LegacyDashboardRedirect />} />
            <Route path="/hotspot" element={<HotspotPage />} />
            <Route path="/hotspots" element={<Navigate to="/hotspot" replace />} />
            <Route path="/feedback" element={<FeedbackExplorerPage />} />
            <Route path="/import" element={<ImportWizardPage />} />
            <Route path="/imports" element={<Navigate to="/import" replace />} />
            <Route path="*" element={<Navigate to="/overview" replace />} />
          </Routes>
        </div>
      </div>
    </BrowserRouter>
  );
};

export default App;
