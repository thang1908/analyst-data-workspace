import React from 'react';
import {
  PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis,
  Tooltip, ResponsiveContainer, LabelList,
} from 'recharts';
import { HotspotItemData } from '../../api/hotspots';
import { AlertTriangle, Flame, ShieldAlert, ClipboardList } from 'lucide-react';

interface HotspotDashboardProps {
  hotspots: HotspotItemData[];
}

const PRIORITY_LABELS_FULL: Record<string, string> = {
  IMMEDIATE: 'Xử lý ngay',
  URGENT:    'Khẩn cấp',
  PLANNED:   'Theo kế hoạch',
  MONITOR:   'Theo dõi',
};
const PRIORITY_COLORS: Record<string, string> = {
  IMMEDIATE: '#dc2626',
  URGENT:    '#ea580c',
  PLANNED:   '#ca8a04',
  MONITOR:   '#2563eb',
};
const STATUS_LABELS_VI: Record<string, string> = {
  CANDIDATE:    'Mới phát hiện',
  ACKNOWLEDGED: 'Đã ghi nhận',
  INVESTIGATING:'Đang xử lý',
  RESOLVED:     'Đã giải quyết',
  DISMISSED:    'Đã đóng',
};
const STATUS_COLORS: Record<string, string> = {
  CANDIDATE:    '#8b5cf6',
  ACKNOWLEDGED: '#ea580c',
  INVESTIGATING:'#2563eb',
  RESOLVED:     '#16a34a',
  DISMISSED:    '#94a3b8',
};

const KPIBox: React.FC<{ icon: React.ReactNode; label: string; value: number; color: string; bg: string }> = ({
  icon, label, value, color, bg
}) => (
  <div style={{
    flex: '1 1 120px', minWidth: 110,
    background: bg, borderRadius: 10,
    padding: '12px 16px',
    display: 'flex', alignItems: 'center', gap: 12,
    border: '1px solid ' + color + '33',
  }}>
    <div style={{ color, flexShrink: 0 }}>{icon}</div>
    <div>
      <div style={{ fontSize: 22, fontWeight: 800, color, lineHeight: 1.1 }}>{value}</div>
      <div style={{ fontSize: 11, fontWeight: 600, color: '#64748b', marginTop: 2 }}>{label}</div>
    </div>
  </div>
);

const SimplePieTooltip = ({ active, payload }: any) => {
  if (!active || !payload?.length) return null;
  const d = payload[0].payload;
  return (
    <div style={{ background: '#fff', border: '1px solid #e2e8f0', borderRadius: 8, padding: '8px 12px', fontSize: 12, boxShadow: '0 4px 12px rgba(0,0,0,0.1)' }}>
      <strong style={{ color: d.color }}>{d.name}</strong>: {d.value} điểm nóng
    </div>
  );
};

const BarTooltip = ({ active, payload, label }: any) => {
  if (!active || !payload?.length) return null;
  return (
    <div style={{ background: '#fff', border: '1px solid #e2e8f0', borderRadius: 8, padding: '8px 12px', fontSize: 12, boxShadow: '0 4px 12px rgba(0,0,0,0.1)' }}>
      <div style={{ fontWeight: 700, marginBottom: 4, color: '#0f172a' }}>{label}</div>
      {payload.map((p: any) => (
        <div key={p.dataKey} style={{ color: p.fill }}>{p.name}: <strong>{p.value}</strong> phản ánh</div>
      ))}
    </div>
  );
};

export const HotspotDashboard: React.FC<HotspotDashboardProps> = ({ hotspots }) => {
  if (hotspots.length === 0) return null;

  const active = hotspots.filter(h => h.status === 'CANDIDATE' || h.status === 'ACKNOWLEDGED' || h.status === 'INVESTIGATING');
  const resolved = hotspots.filter(h => h.status === 'RESOLVED');
  const totalEvidence = hotspots.reduce((s, h) => s + h.evidence_count, 0);

  // Priority Donut
  const priorityData = (['IMMEDIATE', 'URGENT', 'PLANNED', 'MONITOR'] as const)
    .map(p => ({ name: PRIORITY_LABELS_FULL[p], value: hotspots.filter(h => h.action_priority === p).length, color: PRIORITY_COLORS[p] }))
    .filter(d => d.value > 0);

  // Status Donut
  const statusData = (['CANDIDATE', 'ACKNOWLEDGED', 'INVESTIGATING', 'RESOLVED', 'DISMISSED'] as const)
    .map(s => ({ name: STATUS_LABELS_VI[s], value: hotspots.filter(h => h.status === s).length, color: STATUS_COLORS[s] }))
    .filter(d => d.value > 0);

  // Top services by evidence
  const serviceEvidenceMap: Record<string, { name: string; count: number; priority: string }> = {};
  hotspots.forEach(h => {
    const key = h.service.code ?? h.service.name_vi ?? 'Khac';
    const name = h.service.name_vi ?? key;
    if (!serviceEvidenceMap[key]) serviceEvidenceMap[key] = { name, count: 0, priority: h.action_priority };
    serviceEvidenceMap[key].count += h.evidence_count;
  });
  const topServices = Object.values(serviceEvidenceMap)
    .sort((a, b) => b.count - a.count)
    .slice(0, 6);

  return (
    <div style={{ marginBottom: 24, display: 'flex', flexDirection: 'column', gap: 16 }}>
      {/* Row 1: KPI badges */}
      <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
        <KPIBox icon={<Flame size={22} />} label="Tổng điểm nóng" value={hotspots.length} color="#dc2626" bg="#fef2f2" />
        <KPIBox icon={<AlertTriangle size={22} />} label="Đang xử lý" value={active.length} color="#ea580c" bg="#fff7ed" />
        <KPIBox icon={<ShieldAlert size={22} />} label="Xử lý ngay + Khẩn cấp" value={hotspots.filter(h => h.action_priority === 'IMMEDIATE' || h.action_priority === 'URGENT').length} color="#ca8a04" bg="#fefce8" />
        <KPIBox icon={<ClipboardList size={22} />} label="Tổng phản ánh" value={totalEvidence} color="#2563eb" bg="#eff6ff" />
      </div>

      {/* Row 2: 3 Charts side by side */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 2fr', gap: 14, alignItems: 'start' }}>

        {/* Chart 1: Mức độ ưu tiên */}
        <div className="card" style={{ padding: '14px 16px' }}>
          <div style={{ fontSize: 13, fontWeight: 700, color: '#0f172a', marginBottom: 12 }}>Mức độ ưu tiên</div>
          <div style={{ position: 'relative', height: 160 }}>
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={priorityData} cx="50%" cy="50%" innerRadius={45} outerRadius={68} paddingAngle={3} dataKey="value" stroke="#fff" strokeWidth={2}>
                  {priorityData.map((d, i) => <Cell key={i} fill={d.color} />)}
                </Pie>
                <Tooltip content={<SimplePieTooltip />} />
              </PieChart>
            </ResponsiveContainer>
            <div style={{ position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%,-50%)', textAlign: 'center', pointerEvents: 'none' }}>
              <div style={{ fontSize: 18, fontWeight: 800, color: '#0f172a' }}>{hotspots.length}</div>
              <div style={{ fontSize: 10, color: '#64748b', fontWeight: 600 }}>điểm nóng</div>
            </div>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 5, marginTop: 10 }}>
            {priorityData.map((d, i) => (
              <div key={i} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: 11 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                  <span style={{ width: 8, height: 8, borderRadius: '50%', background: d.color }} />
                  <span style={{ color: '#475569', fontWeight: 500 }}>{d.name}</span>
                </div>
                <strong style={{ color: d.color }}>{d.value}</strong>
              </div>
            ))}
          </div>
        </div>

        {/* Chart 2: Trạng thái xử lý */}
        <div className="card" style={{ padding: '14px 16px' }}>
          <div style={{ fontSize: 13, fontWeight: 700, color: '#0f172a', marginBottom: 12 }}>Trạng thái xử lý</div>
          <div style={{ position: 'relative', height: 160 }}>
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={statusData} cx="50%" cy="50%" innerRadius={45} outerRadius={68} paddingAngle={3} dataKey="value" stroke="#fff" strokeWidth={2}>
                  {statusData.map((d, i) => <Cell key={i} fill={d.color} />)}
                </Pie>
                <Tooltip content={<SimplePieTooltip />} />
              </PieChart>
            </ResponsiveContainer>
            <div style={{ position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%,-50%)', textAlign: 'center', pointerEvents: 'none' }}>
              <div style={{ fontSize: 18, fontWeight: 800, color: '#0f172a' }}>{active.length}</div>
              <div style={{ fontSize: 10, color: '#64748b', fontWeight: 600 }}>đang mở</div>
            </div>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 5, marginTop: 10 }}>
            {statusData.map((d, i) => (
              <div key={i} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: 11 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                  <span style={{ width: 8, height: 8, borderRadius: '50%', background: d.color }} />
                  <span style={{ color: '#475569', fontWeight: 500 }}>{d.name}</span>
                </div>
                <strong style={{ color: d.color }}>{d.value}</strong>
              </div>
            ))}
          </div>
        </div>

        {/* Chart 3: Top dịch vụ theo số phản ánh */}
        <div className="card" style={{ padding: '14px 16px' }}>
          <div style={{ fontSize: 13, fontWeight: 700, color: '#0f172a', marginBottom: 12 }}>Top dịch vụ có nhiều phản ánh nhất</div>
          <div style={{ height: 250 }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={topServices} layout="vertical" margin={{ left: 0, right: 44, top: 4, bottom: 4 }}>
                <XAxis type="number" tick={{ fontSize: 10, fill: '#94a3b8' }} axisLine={false} tickLine={false} />
                <YAxis type="category" dataKey="name" tick={{ fontSize: 11, fill: '#475569', fontWeight: 600 }} axisLine={false} tickLine={false} width={120} />
                <Tooltip content={<BarTooltip />} />
                <Bar dataKey="count" name="Phản ánh" radius={[0, 5, 5, 0]} fill="#2563eb" minPointSize={2}>
                  {topServices.map((s, i) => <Cell key={i} fill={PRIORITY_COLORS[s.priority] ?? '#2563eb'} />)}
                  <LabelList dataKey="count" position="right" style={{ fontSize: 11, fontWeight: 700, fill: '#0f172a' }} />
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

      </div>
    </div>
  );
};

export default HotspotDashboard;

