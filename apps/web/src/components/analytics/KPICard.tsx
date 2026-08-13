import React from 'react';
import { KPIData } from '../../mock/analyticsData';

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

// Helper to build KPI cards from mock data
export const buildKPICards = (data: KPIData) => [
  {
    type: 'negative' as const,
    label: 'NEGATIVE RATE',
    icon: '↓',
    value: `${data.negativeRate}%`,
    delta: data.negativeRateDelta,
    deltaLabel: ' pts',
    subtitle: 'So với kỳ trước',
  },
  {
    type: 'volume' as const,
    label: 'FEEDBACK VOLUME',
    icon: '◎',
    value: data.feedbackVolume.toLocaleString(),
    delta: data.feedbackVolumeDelta,
    deltaLabel: '%',
    subtitle: '30 ngày gần nhất',
  },
  {
    type: 'hotspot' as const,
    label: 'ACTIVE HOTSPOTS',
    icon: '🔥',
    value: String(data.activeHotspots),
    delta: undefined,
    subtitle: `${data.criticalHotspots} critical cần xử lý ngay`,
  },
  {
    type: 'unknown' as const,
    label: 'UNKNOWN RATE',
    icon: '◈',
    value: `${data.unknownRate}%`,
    delta: data.unknownRateDelta,
    deltaLabel: ' pts',
    subtitle: 'Chưa phân loại',
  },
];
