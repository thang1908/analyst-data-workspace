import React, { useState } from 'react';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer,
} from 'recharts';

interface TrendChartProps {
  data: { bucket: string; itemVolume: number; negativeRate: number; unknownRate: number; activeHotspots: number }[];
}

type Metric = 'itemVolume' | 'negativeRate' | 'unknownRate' | 'activeHotspots';

const METRICS: { key: Metric; label: string; color: string; percentage?: boolean }[] = [
  { key: 'itemVolume', label: 'Lượng phản hồi', color: '#2563eb' },
  { key: 'negativeRate', label: 'Tỷ lệ tiêu cực', color: '#dc2626', percentage: true },
  { key: 'unknownRate', label: 'Chưa xác định', color: '#7c3aed', percentage: true },
  { key: 'activeHotspots', label: 'Hotspot', color: '#ea580c' },
];

const CustomTooltip = ({ active, payload, label }: any) => {
  if (!active || !payload?.length) return null;
  return (
    <div style={{
      background: 'var(--bg-elevated)',
      border: '1px solid var(--border-default)',
      borderRadius: 10,
      padding: '10px 14px',
      boxShadow: 'var(--shadow-card)',
      minWidth: 160,
    }}>
      <div style={{ fontSize: 11, color: 'var(--text-muted)', marginBottom: 8 }}>{label}</div>
      {payload.map((p: any) => (
        <div key={p.dataKey} style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
          <div style={{ width: 8, height: 8, borderRadius: '50%', background: p.color }} />
          <span style={{ fontSize: 12, color: 'var(--text-secondary)' }}>{p.name}</span>
          <span style={{ fontSize: 13, fontWeight: 700, color: 'var(--text-primary)', marginLeft: 'auto' }}>
            {typeof p.value === 'number'
              ? METRICS.find((metric) => metric.key === p.dataKey)?.percentage
                ? `${(p.value * 100).toFixed(1)}%`
                : p.value.toLocaleString()
              : p.value}
          </span>
        </div>
      ))}
    </div>
  );
};

const TrendChart: React.FC<TrendChartProps> = ({ data }) => {
  const [activeMetric, setActiveMetric] = useState<Metric>('itemVolume');
  const formatted = data.map(d => ({
    ...d,
    label: new Date(d.bucket).toLocaleDateString('vi-VN', { day: '2-digit', month: '2-digit' }),
  }));

  // Show every 5th label to avoid clutter
  const tickFormatter = (_: any, index: number) =>
    index % 5 === 0 ? formatted[index]?.label ?? '' : '';

  return (
    <div>
      <div className="chart-toggles">
        {METRICS.map((metric) => (
          <button
            key={metric.key}
            className={`toggle-btn${activeMetric === metric.key ? ' active' : ''}`}
            style={activeMetric === metric.key ? { borderColor: metric.color, color: metric.color } : undefined}
            onClick={() => setActiveMetric(metric.key)}
          >{metric.label}</button>
        ))}
      </div>

      <ResponsiveContainer width="100%" height={200}>
        <LineChart data={formatted} margin={{ top: 4, right: 4, left: -28, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
          <XAxis
            dataKey="label"
            tick={{ fontSize: 10, fill: 'var(--text-muted)' }}
            tickFormatter={tickFormatter}
            tickLine={false}
            axisLine={{ stroke: 'var(--border-subtle)' }}
          />
          <YAxis
            tick={{ fontSize: 10, fill: 'var(--text-muted)' }}
            tickLine={false}
            axisLine={false}
          />
          <Tooltip content={<CustomTooltip />} />

          <Line
            type="monotone"
            dataKey={activeMetric}
            name={METRICS.find((metric) => metric.key === activeMetric)?.label}
            stroke={METRICS.find((metric) => metric.key === activeMetric)?.color}
            strokeWidth={2}
            dot={false}
            activeDot={{ r: 4, fill: METRICS.find((metric) => metric.key === activeMetric)?.color, stroke: 'var(--bg-base)', strokeWidth: 2 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default TrendChart;
