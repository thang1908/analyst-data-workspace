import React from 'react';

interface TopBarProps {
  title: string;
  subtitle?: string;
}

const TopBar: React.FC<TopBarProps> = ({ title, subtitle }) => {
  const isConfigured = Boolean(import.meta.env.VITE_ANALYTICS_PROJECT_ID?.trim());
  return (
    <header className="topbar">
      <div className="topbar-title">
        {title}
        {subtitle && (
          <span style={{ fontSize: 11, fontWeight: 400, color: 'var(--text-muted)', marginLeft: 8 }}>
            {subtitle}
          </span>
        )}
      </div>

      <span className="topbar-context" title="Project được lấy từ VITE_ANALYTICS_PROJECT_ID">
        {isConfigured ? 'Project analytics' : 'Chưa cấu hình project'}
      </span>

      <input
        className="topbar-search"
        placeholder="🔍  Tìm kiếm..."
        type="text"
      />

      <div className="topbar-avatar" title="CX Manager">M</div>
    </header>
  );
};

export default TopBar;
