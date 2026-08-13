import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';

interface NavItem {
  label: string;
  icon: string;
  path: string;
  badge?: number;
}

const NAV_SECTIONS: { title: string; items: NavItem[] }[] = [
  {
    title: 'TỔNG QUAN',
    items: [
      { label: 'CX Overview', icon: '⬡', path: '/overview' },
    ],
  },
  {
    title: 'TRẢI NGHIỆM KHÁCH HÀNG',
    items: [
      { label: 'Customer Journey', icon: '↗', path: '/customer-journey' },
      { label: 'Service & Pain Points', icon: '⚡', path: '/service-pain-points' },
      { label: 'Hotspot & Root Cause', icon: '🔥', path: '/hotspot' },
    ],
  },
  {
    title: 'VẬN HÀNH',
    items: [
      { label: 'Feedback Explorer', icon: '◎', path: '/feedback' },
      { label: 'Review Queue', icon: '⊞', path: '/review', badge: 128 },
      { label: 'Imports', icon: '↑', path: '/imports', badge: 1 },
    ],
  },
  {
    title: 'QUẢN TRỊ',
    items: [
      { label: 'Data Quality', icon: '◈', path: '/data-quality' },
      { label: 'Taxonomy', icon: '⊞', path: '/admin/taxonomy' },
      { label: 'Audit', icon: '≡', path: '/audit' },
    ],
  },
];

const Sidebar: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();

  return (
    <aside className="sidebar">
      {/* Logo */}
      <div className="sidebar-logo">
        <div className="sidebar-logo-icon">⬡</div>
        <div>
          <div className="sidebar-logo-text">CX Platform</div>
          <div className="sidebar-logo-sub">Intelligence & Operations</div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="sidebar-nav">
        {NAV_SECTIONS.map((section, si) => (
          <div key={si}>
            <div className="sidebar-section-label">{section.title}</div>
            {section.items.map((item) => {
              const isActive = location.pathname === item.path ||
                (item.path !== '/' && location.pathname.startsWith(item.path));
              return (
                <button
                  key={item.path}
                  className={`sidebar-link${isActive ? ' active' : ''}`}
                  onClick={() => navigate(`${item.path}${location.search}`)}
                >
                  <span className="sidebar-link-icon">{item.icon}</span>
                  <span>{item.label}</span>
                  {item.badge !== undefined && (
                    <span className="sidebar-badge">{item.badge}</span>
                  )}
                </button>
              );
            })}
            {si < NAV_SECTIONS.length - 1 && <div className="sidebar-divider" />}
          </div>
        ))}
      </nav>
    </aside>
  );
};

export default Sidebar;
