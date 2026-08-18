import React from 'react';

export interface KPIData {
  negativeRate: number;
  feedbackVolume: number;
  unknownRate: number;
  activeHotspots: number;
}

interface KPICardProps {
  type: 'negative' | 'volume' | 'hotspot' | 'unknown';
  label: string;
  value: string;
  delta?: number;
  deltaLabel?: string;
  subtitle?: string;
  icon: string;
  onClick?: () => void;
}

const KPICard: React.FC<KPICardProps> = ({
  type, label, value, delta, deltaLabel, subtitle, icon, onClick,
}) => {
  const deltaGood = type === 'negative'
    ? (delta ?? 0) < 0
    : type === 'unknown'
    ? (delta ?? 0) < 0
    : (delta ?? 0) > 0;

  const deltaClass = delta === undefined
    ? ''
    : deltaGood ? 'good' : 'bad';

  const deltaSign = delta !== undefined && delta > 0 ? '+' : '';

  return (
    <div className={`kpi-card ${type} animate-in`} onClick={onClick}>
      <div className="kpi-label">
        <span>{icon}</span>
        {label}
      </div>
      <div className="kpi-value">{value}</div>
      {delta !== undefined && (
        <span className={`kpi-delta ${deltaClass}`}>
          {deltaGood ? '↓' : '↑'} {deltaSign}{Math.abs(delta)}{deltaLabel ?? ''}
        </span>
      )}
      {subtitle && <div className="kpi-subtitle">{subtitle}</div>}
    </div>
  );
};

export default KPICard;

// Helper to build KPI cards from governed analytics metrics.
const percentage = (value: number) => `${value.toFixed(1)}%`;

export const buildKPICards = (data: KPIData) => [
  {
    type: 'negative' as const,
    label: 'TỶ LỆ TIÊU CỰC',
    icon: '↓',
    value: percentage(data.negativeRate),
    subtitle: 'Trong bộ lọc hiện tại',
  },
  {
    type: 'volume' as const,
    label: 'TỔNG PHẢN HỒI',
    icon: '◎',
    value: data.feedbackVolume.toLocaleString(),
    subtitle: 'Phản hồi đủ điều kiện',
  },
  {
    type: 'hotspot' as const,
    label: 'ĐIỂM NÓNG ĐANG MỞ',
    icon: '🔥',
    value: String(data.activeHotspots),
    delta: undefined,
    subtitle: data.activeHotspots ? 'Cần được theo dõi' : 'Không có điểm nóng',
  },
  {
    type: 'unknown' as const,
    label: 'CHƯA RÕ CẢM XÚC',
    icon: '◈',
    value: percentage(data.unknownRate),
    subtitle: 'Phản hồi chưa phân loại',
  },
];
