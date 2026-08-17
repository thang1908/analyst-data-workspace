import React from 'react';
import { BrowserRouter, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import './index.css';
import Sidebar from './components/layout/Sidebar';
import OverviewPage from './pages/OverviewPage';
import ImportWizardPage from './pages/import/ImportWizardPage';
import FeedbackExplorerPage from './pages/feedback/FeedbackExplorerPage';

// Placeholder page for routes not yet built
const ComingSoon: React.FC<{ title: string }> = ({ title }) => (
  <div style={{
    display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
    height: '100%', gap: 12, color: 'var(--text-muted)',
  }}>
    <div style={{ fontSize: 48 }}>🚧</div>
    <div style={{ fontSize: 18, fontWeight: 700, color: 'var(--text-secondary)' }}>{title}</div>
    <div style={{ fontSize: 13 }}>Tính năng đang được phát triển</div>
  </div>
);

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
            <Route path="/hotspot" element={<ComingSoon title="Hotspot & Root Cause" />} />
            <Route path="/feedback" element={<FeedbackExplorerPage />} />
            <Route path="/review" element={<ComingSoon title="Review Queue" />} />
            <Route path="/import" element={<ImportWizardPage />} />
            <Route path="/imports" element={<Navigate to="/import" replace />} />
            <Route path="/data-quality" element={<ComingSoon title="Data Quality" />} />
            <Route path="/admin/taxonomy" element={<ComingSoon title="Taxonomy Admin" />} />
            <Route path="/audit" element={<ComingSoon title="Audit Log" />} />
            <Route path="*" element={<Navigate to="/overview" replace />} />
          </Routes>
        </div>
      </div>
    </BrowserRouter>
  );
};

export default App;
