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

      <span className="topbar-context" title="Dự án được kết nối từ hệ thống dữ liệu">
        {isConfigured ? 'Dự án phân tích CX' : 'Chưa kết nối dự án'}
      </span>

      <input
        className="topbar-search"
        placeholder="🔍  Tìm kiếm nhanh..."
        type="text"
      />

      <div className="topbar-avatar" title="Quản trị viên CX">CX</div>
    </header>
  );
};

export default TopBar;
