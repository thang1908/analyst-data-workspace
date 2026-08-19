import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';
import { AnalyticsBreakdownItem } from '../../api/analytics';
import { Radio, ExternalLink } from 'lucide-react';

interface ChannelBreakdownCardProps {
  channels: AnalyticsBreakdownItem[];
  selectedChannelCode?: string;
  onSelectChannel?: (code?: string) => void;
  onDrilldown?: (channelCode: string) => void;
}

const CHANNEL_COLORS: Record<string, string> = {
  APP: '#2563eb',
  APP_RESIDENT: '#2563eb',
  HOTLINE: '#f97316',
  RECEPTION: '#10b981',
  FRONT_DESK: '#10b981',
  ZALO: '#8b5cf6',
  ZALO_CHAT: '#8b5cf6',
  EMAIL: '#06b6d4',
  EMAIL_DOC: '#06b6d4',
  PORTAL: '#3b82f6',
  SURVEY: '#ec4899',
  UNKNOWN: '#94a3b8',
};

const DEFAULT_COLORS = ['#2563eb', '#f97316', '#10b981', '#8b5cf6', '#06b6d4', '#ec4899', '#64748b'];

const getColor = (code: string, index: number) => {
  const norm = code.toUpperCase();
  for (const [k, color] of Object.entries(CHANNEL_COLORS)) {
    if (norm.includes(k)) return color;
  }
  return DEFAULT_COLORS[index % DEFAULT_COLORS.length];
};

const CustomTooltip = ({ active, payload }: any) => {
  if (!active || !payload?.length) return null;
  const data = payload[0].payload;
  return (
    <div
      style={{
        background: '#ffffff',
        border: '1px solid #e2e8f0',
        borderRadius: 8,
        padding: '8px 12px',
        boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
        fontSize: 12,
        color: '#0f172a',
      }}
    >
      <div style={{ fontWeight: 700, marginBottom: 4, display: 'flex', alignItems: 'center', gap: 6 }}>
        <span style={{ width: 8, height: 8, borderRadius: '50%', background: data.color }} />
        {data.name}
      </div>
      <div style={{ color: '#475569', fontSize: 11 }}>
        Số lượng: <strong>{data.itemVolume.toLocaleString()}</strong> phản hồi
      </div>
      <div style={{ color: '#64748b', fontSize: 11 }}>
        Tỷ trọng: <strong>{(data.percentage * 100).toFixed(1)}%</strong>
      </div>
    </div>
  );
};

export const ChannelBreakdownCard: React.FC<ChannelBreakdownCardProps> = ({
  channels,
  selectedChannelCode,
  onSelectChannel,
  onDrilldown,
}) => {
  const validChannels = channels.filter((c) => c.itemVolume > 0);
  const totalVolume = validChannels.reduce((sum, c) => sum + c.itemVolume, 0);

  const chartData = validChannels.map((c, idx) => ({
    ...c,
    color: getColor(c.code, idx),
    value: c.itemVolume,
  }));

  return (
    <section className="card animate-in" style={{ display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <div className="section-header">
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <Radio size={16} color="#2563eb" />
          <span className="section-title">Kênh phản ánh</span>
        </div>
        <span className="panel-count">{channels.length} kênh tiếp nhận</span>
      </div>

      {totalVolume === 0 ? (
        <div style={{ padding: '30px 20px', textAlign: 'center', color: '#94a3b8', fontSize: 13 }}>
          Chưa có dữ liệu phản ánh theo kênh trong khoảng thời gian này.
        </div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'minmax(160px, 190px) 1fr', gap: 14, alignItems: 'center' }}>
          {/* Left: Donut Chart with Center Total */}
          <div style={{ position: 'relative', height: 210, width: '100%' }}>
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={chartData}
                  cx="50%"
                  cy="50%"
                  innerRadius={50}
                  outerRadius={75}
                  paddingAngle={3}
                  dataKey="value"
                  stroke="#ffffff"
                  strokeWidth={2}
                >
                  {chartData.map((entry) => (
                    <Cell
                      key={'cell-' + entry.code}
                      fill={entry.color}
                      opacity={selectedChannelCode && selectedChannelCode !== entry.code ? 0.35 : 1}
                      style={{ cursor: 'pointer', transition: 'opacity 0.2s' }}
                      onClick={() => onSelectChannel && onSelectChannel(selectedChannelCode === entry.code ? undefined : entry.code)}
                    />
                  ))}
                </Pie>
                <Tooltip content={<CustomTooltip />} />
              </PieChart>
            </ResponsiveContainer>

            {/* Center Label */}
            <div
              style={{
                position: 'absolute',
                top: '50%',
                left: '50%',
                transform: 'translate(-50%, -50%)',
                textAlign: 'center',
                pointerEvents: 'none',
              }}
            >
              <div style={{ fontSize: 17, fontWeight: 800, color: '#0f172a', lineHeight: 1.1 }}>
                {totalVolume.toLocaleString()}
              </div>
              <div style={{ fontSize: 10, color: '#64748b', fontWeight: 600 }}>Phản ánh</div>
            </div>
          </div>

          {/* Right: Detailed Legend & Channel List */}
          <div
            className="dashboard-scroll-list"
            style={{ maxHeight: 260, overflowY: 'auto' }}
            aria-label="Danh sách kênh tiếp nhận"
          >
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 12 }}>
              <tbody>
                {chartData.map((channel) => {
                  const isSelected = selectedChannelCode === channel.code;
                  return (
                    <tr
                      key={channel.code}
                      onClick={() => onSelectChannel && onSelectChannel(isSelected ? undefined : channel.code)}
                      style={{
                        borderBottom: '1px solid #f8fafc',
                        background: isSelected ? '#eff6ff' : 'transparent',
                        cursor: 'pointer',
                        transition: 'background 0.15s',
                      }}
                      onMouseEnter={(e) => {
                        if (!isSelected) e.currentTarget.style.background = '#f8fafc';
                      }}
                      onMouseLeave={(e) => {
                        if (!isSelected) e.currentTarget.style.background = 'transparent';
                      }}
                    >
                      {/* Color Dot & Name */}
                      <td style={{ padding: '7px 8px', color: '#1e293b' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 7 }}>
                          <span
                            style={{
                              width: 8,
                              height: 8,
                              borderRadius: '50%',
                              background: channel.color,
                              flexShrink: 0,
                            }}
                          />
                          <span style={{ fontWeight: 600, color: isSelected ? '#2563eb' : '#0f172a' }}>
                            {channel.name}
                          </span>
                        </div>
                      </td>

                      {/* Volume & Percentage */}
                      <td style={{ padding: '7px 8px', textAlign: 'right', whiteSpace: 'nowrap' }}>
                        <strong style={{ color: '#0f172a' }}>{channel.itemVolume.toLocaleString()}</strong>
                        <span style={{ fontSize: 11, color: '#64748b', marginLeft: 5 }}>
                          ({(channel.percentage * 100).toFixed(1)}%)
                        </span>
                      </td>

                      {/* Action Drilldown */}
                      <td style={{ padding: '7px 4px', width: 28, textAlign: 'center' }}>
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            onDrilldown && onDrilldown(channel.code);
                          }}
                          style={{
                            display: 'inline-flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            width: 22,
                            height: 22,
                            borderRadius: 4,
                            border: '1px solid #e2e8f0',
                            background: '#ffffff',
                            color: '#64748b',
                            cursor: 'pointer',
                          }}
                          title={'Xem phản hồi từ kênh ' + channel.name}
                        >
                          <ExternalLink size={11} />
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </section>
  );
};

export default ChannelBreakdownCard;
