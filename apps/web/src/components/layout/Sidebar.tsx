import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { ChevronLeft, ChevronRight, PanelLeftClose, PanelLeft } from 'lucide-react';

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
      { label: 'Tổng quan CX', icon: '⬡', path: '/overview' },
    ],
  },
  {
    title: 'TRẢI NGHIỆM KHÁCH HÀNG',
    items: [
      { label: 'Điểm nóng', icon: '🔥', path: '/hotspot' },
    ],
  },
  {
    title: 'VẬN HÀNH',
    items: [
      { label: 'Tra cứu phản hồi', icon: '◎', path: '/feedback' },
      { label: 'Nhập dữ liệu', icon: '↑', path: '/imports' },
    ],
  },
];

const Sidebar: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const [collapsed, setCollapsed] = useState<boolean>(() => {
    try {
      return localStorage.getItem('cx_sidebar_collapsed') === 'true';
    } catch {
      return false;
    }
  });

  const toggleCollapse = () => {
    setCollapsed((prev) => {
      const next = !prev;
      try {
        localStorage.setItem('cx_sidebar_collapsed', String(next));
      } catch {}
      return next;
    });
  };

  return (
    <aside
      className={`sidebar ${collapsed ? 'collapsed' : ''}`}
      style={{
        width: collapsed ? 64 : 240,
        transition: 'width 0.22s cubic-bezier(0.4, 0, 0.2, 1)',
        display: 'flex',
        flexDirection: 'column',
        height: '100vh',
        background: 'var(--bg-surface)',
        borderRight: '1px solid var(--border-subtle)',
        flexShrink: 0,
        position: 'relative',
        userSelect: 'none',
      }}
    >
      {/* Logo & Toggle Header */}
      <div
        className="sidebar-logo"
        style={{
          padding: collapsed ? '16px 12px 14px' : '16px 16px 14px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: collapsed ? 'center' : 'space-between',
          borderBottom: '1px solid var(--border-subtle)',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, minWidth: 0, overflow: 'hidden' }}>
          <div
            className="sidebar-logo-icon"
            onClick={toggleCollapse}
            style={{ cursor: 'pointer', flexShrink: 0 }}
            title={collapsed ? 'Nhấp để mở rộng menu' : 'CX Platform'}
          >
            ⬡
          </div>
          {!collapsed && (
            <div style={{ whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
              <div className="sidebar-logo-text">CX Platform</div>
              <div className="sidebar-logo-sub">Quản trị & Vận hành CX</div>
            </div>
          )}
        </div>

        {!collapsed && (
          <button
            onClick={toggleCollapse}
            style={{
              background: 'none',
              border: 'none',
              cursor: 'pointer',
              color: 'var(--text-muted)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              padding: 4,
              borderRadius: 6,
            }}
            title="Thu gọn menu"
            onMouseEnter={(e) => (e.currentTarget.style.color = 'var(--text-primary)')}
            onMouseLeave={(e) => (e.currentTarget.style.color = 'var(--text-muted)')}
          >
            <PanelLeftClose size={16} />
          </button>
        )}
      </div>

      {/* Navigation */}
      <nav className="sidebar-nav" style={{ flex: 1, padding: '12px 0', overflowY: 'auto', overflowX: 'hidden' }}>
        {NAV_SECTIONS.map((section, si) => (
          <div key={si}>
            {!collapsed && (
              <div className="sidebar-section-label" style={{ padding: '8px 18px 4px', fontSize: 10, fontWeight: 700, color: 'var(--text-muted)', letterSpacing: '0.8px' }}>
                {section.title}
              </div>
            )}
            {collapsed && si > 0 && <div className="sidebar-divider" style={{ margin: '6px 12px' }} />}

            {section.items.map((item) => {
              const isActive =
                location.pathname === item.path ||
                (item.path !== '/' && location.pathname.startsWith(item.path));

              return (
                <button
                  key={item.path}
                  className={`sidebar-link${isActive ? ' active' : ''}`}
                  onClick={() => navigate(`${item.path}${location.search}`)}
                  title={collapsed ? item.label : undefined}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: collapsed ? 'center' : 'flex-start',
                    gap: 10,
                    padding: collapsed ? '10px 0' : '9px 18px',
                    width: '100%',
                    border: 'none',
                    background: isActive ? 'rgba(220,38,38,0.08)' : 'none',
                    color: isActive ? 'var(--text-accent)' : 'var(--text-secondary)',
                    cursor: 'pointer',
                    fontSize: 13,
                    fontWeight: isActive ? 700 : 500,
                    textAlign: 'left',
                    transition: 'all 0.15s ease',
                    position: 'relative',
                  }}
                >
                  <span className="sidebar-link-icon" style={{ fontSize: 15, flexShrink: 0 }}>
                    {item.icon}
                  </span>
                  {!collapsed && <span style={{ whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{item.label}</span>}
                  {!collapsed && item.badge !== undefined && (
                    <span className="sidebar-badge">{item.badge}</span>
                  )}
                </button>
              );
            })}
            {!collapsed && si < NAV_SECTIONS.length - 1 && <div className="sidebar-divider" style={{ margin: '8px 16px' }} />}
          </div>
        ))}
      </nav>

      {/* Bottom Expand Toggle Button when Collapsed */}
      {collapsed && (
        <div style={{ padding: 12, borderTop: '1px solid var(--border-subtle)', display: 'flex', justifyContent: 'center' }}>
          <button
            onClick={toggleCollapse}
            style={{
              width: 36,
              height: 36,
              borderRadius: 8,
              border: '1px solid var(--border-default)',
              background: 'var(--bg-elevated)',
              color: 'var(--text-secondary)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              cursor: 'pointer',
            }}
            title="Mở rộng thanh menu"
          >
            <PanelLeft size={16} />
          </button>
        </div>
      )}
    </aside>
  );
};

export default Sidebar;
