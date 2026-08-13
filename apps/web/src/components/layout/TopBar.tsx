import React from 'react';

interface TopBarProps {
  title: string;
  subtitle?: string;
}

const TopBar: React.FC<TopBarProps> = ({ title, subtitle }) => {
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

      <select className="topbar-select">
        <option>Vinhomes Symphony ▼</option>
        <option>Vinhomes Ocean Park</option>
        <option>Vinhomes Smart City</option>
      </select>

      <select className="topbar-select">
        <option>Last 30 days</option>
        <option>Last 7 days</option>
        <option>Last 90 days</option>
        <option>This year</option>
      </select>

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
