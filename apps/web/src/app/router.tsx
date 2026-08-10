import React from 'react';
import { createBrowserRouter, Navigate, Outlet, Link, useLocation } from 'react-router-dom';
import { Layers, UploadCloud, MessageSquare, BarChart2 } from 'lucide-react';

import { DashboardView } from '../features/dashboard/DashboardView';
import { UploadView } from '../features/imports/UploadView';
import { JobDetailView } from '../features/imports/JobDetailView';
import { FeedbackListView } from '../features/feedback/FeedbackListView';
import { FeedbackDetailView } from '../features/feedback/FeedbackDetailView';

const Layout: React.FC = () => {
  const location = useLocation();

  return (
    <div className="app-container">
      {/* Glassmorphic Navbar */}
      <header className="glass-panel navbar">
        <div className="nav-brand">
          <div className="nav-logo-badge">CX</div>
          <div>
            <div style={{ fontWeight: 700, fontSize: '1rem', color: 'var(--text-primary)' }}>
              CX Intelligence
            </div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
              Pilot Platform v0.2
            </div>
          </div>
        </div>

        <nav className="nav-links">
          <Link 
            to="/dashboard" 
            className={`nav-btn ${location.pathname.startsWith('/dashboard') ? 'active' : ''}`}
          >
            <BarChart2 size={16} /> Dashboard
          </Link>
          <Link 
            to="/imports" 
            className={`nav-btn ${location.pathname.startsWith('/imports') ? 'active' : ''}`}
          >
            <UploadCloud size={16} /> Import CSV
          </Link>
          <Link 
            to="/feedback" 
            className={`nav-btn ${location.pathname.startsWith('/feedback') ? 'active' : ''}`}
          >
            <MessageSquare size={16} /> Feedback Drill-down
          </Link>
        </nav>
      </header>

      {/* Main Content Area */}
      <main>
        <Outlet />
      </main>
    </div>
  );
};

export const router = createBrowserRouter([
  {
    path: '/',
    element: <Layout />,
    children: [
      { index: true, element: <Navigate to="/dashboard" replace /> },
      { path: 'dashboard', element: <DashboardView /> },
      { path: 'imports', element: <UploadView /> },
      { path: 'imports/new', element: <UploadView /> },
      { path: 'imports/:jobId', element: <JobDetailView /> },
      { path: 'feedback', element: <FeedbackListView /> },
      { path: 'feedback/:itemId', element: <FeedbackDetailView /> },
    ],
  },
]);
