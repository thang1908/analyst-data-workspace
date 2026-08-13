import React, { useState } from 'react';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, ReferenceLine,
} from 'recharts';
import { TrendPoint } from '../../mock/analyticsData';

interface TrendChartProps {
  data: TrendPoint[];
}

type Metric = 'negativeRate' | 'feedbackVolume' | 'hotspotCount';

const METRICS: { key: Metric; label: string; color: string; unit: string }[] = [
  { key: 'negativeRate',   label: 'Negative Rate',    color: '#f87171', unit: '%' },
  { key: 'feedbackVolume', label: 'Feedback Volume',  color: '#60a5fa', unit: '' },
  { key: 'hotspotCount',  label: 'Hotspot Count',    color: '#f97316', unit: '' },
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
            {typeof p.value === 'number' ? p.value.toFixed(p.dataKey === 'negativeRate' ? 1 : 0) : p.value}
            {p.dataKey === 'negativeRate' ? '%' : ''}
          </span>
        </div>
      ))}
    </div>
  );
};

const TrendChart: React.FC<TrendChartProps> = ({ data }) => {
  const [activeMetrics, setActiveMetrics] = useState<Set<Metric>>(new Set(['negativeRate']));

  const toggleMetric = (metric: Metric) => {
    setActiveMetrics(prev => {
      const next = new Set(prev);
      if (next.has(metric)) {
        if (next.size > 1) next.delete(metric);
      } else {
        next.add(metric);
      }
      return next;
    });
  };

  // Format date label (show only day/month)
  const formatted = data.map(d => ({
    ...d,
    label: d.date.slice(5), // "08-14"
  }));

  // Show every 5th label to avoid clutter
  const tickFormatter = (_: any, index: number) =>
    index % 5 === 0 ? formatted[index]?.label ?? '' : '';

  return (
    <div>
      <div className="chart-toggles">
        {METRICS.map(m => (
          <button
            key={m.key}
            className={`toggle-btn${activeMetrics.has(m.key) ? ' active' : ''}`}
            onClick={() => toggleMetric(m.key)}
            style={activeMetrics.has(m.key) ? { borderColor: m.color, color: m.color, background: `${m.color}18` } : {}}
          >
            {m.label}
          </button>
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

          {METRICS.filter(m => activeMetrics.has(m.key)).map(m => (
            <Line
              key={m.key}
              type="monotone"
              dataKey={m.key}
              name={m.label}
              stroke={m.color}
              strokeWidth={2}
              dot={false}
              activeDot={{ r: 4, fill: m.color, stroke: 'var(--bg-base)', strokeWidth: 2 }}
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default TrendChart;
