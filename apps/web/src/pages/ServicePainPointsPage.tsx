import React, { useState } from 'react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, Cell,
} from 'recharts';
import { useNavigate } from 'react-router-dom';
import TopBar from '../components/layout/TopBar';
import PainPointsList from '../components/analytics/PainPointsList';
import { mockPainPoints } from '../mock/analyticsData';

const SERVICE_DATA = [
  { code: 'SV-05', name: 'Tiếp cận & Di chuyển', count: 2140, negRate: 51 },
  { code: 'SV-02', name: 'App & Hệ thống số', count: 1800, negRate: 44 },
  { code: 'SV-06', name: 'Thanh toán & Phí', count: 1560, negRate: 47 },
  { code: 'SV-07', name: 'Kỹ thuật & Tài sản', count: 1200, negRate: 39 },
  { code: 'SV-03', name: 'Giao tiếp & CSKH', count: 980, negRate: 35 },
  { code: 'SV-08', name: 'An ninh', count: 740, negRate: 28 },
  { code: 'SV-01', name: 'Hạ tầng kỹ thuật', count: 520, negRate: 22 },
  { code: 'SV-04', name: 'Môi trường sống', count: 380, negRate: 18 },
];

const COLORS = ['#dc2626','#ea580c','#d97706','#65a30d','#16a34a','#0891b2','#2563eb','#7c3aed'];

const CustomTooltip = ({ active, payload }: any) => {
  if (!active || !payload?.length) return null;
  const d = payload[0].payload;
  return (
    <div style={{
      background: '#fff', border: '1px solid var(--border-default)',
      borderRadius: 10, padding: '10px 14px', boxShadow: 'var(--shadow-card)',
    }}>
      <div style={{ fontSize: 12, fontWeight: 700, color: 'var(--text-primary)', marginBottom: 6 }}>
        {d.name}
      </div>
      <div style={{ fontSize: 12, color: 'var(--text-secondary)' }}>
        Phản hồi: <b style={{ color: 'var(--text-primary)' }}>{d.count.toLocaleString()}</b>
      </div>
      <div style={{ fontSize: 12, color: 'var(--text-secondary)' }}>
        Tỷ lệ tiêu cực: <b style={{ color: 'var(--color-negative)' }}>{d.negRate}%</b>
      </div>
    </div>
  );
};

// Tên rút gọn cho trục Y chart (tối đa ~12 ký tự)
const SHORT_NAME: Record<string, string> = {
  'SV-05': 'Tiếp cận',
  'SV-02': 'App & hệ thống',
  'SV-06': 'Thanh toán',
  'SV-07': 'Kỹ thuật',
  'SV-03': 'CSKH',
  'SV-08': 'An ninh',
  'SV-01': 'Hạ tầng',
  'SV-04': 'Môi trường',
};

const ServicePainPointsPage: React.FC = () => {
  const navigate = useNavigate();
  const [selectedService, setSelectedService] = useState<string | null>('SV-05');

  const selectedServiceName = selectedService
    ? SERVICE_DATA.find(s => s.code === selectedService)?.name
    : null;

  const filteredPains = selectedService
    ? mockPainPoints.filter(p => p.serviceCode === selectedService)
    : mockPainPoints;

  return (
    <>
      <TopBar title="Service & Pain Points" subtitle="Dịch vụ nào đang gây trải nghiệm xấu nhất?" />

      <div className="page-content">
        {/* Filter Bar */}
        <div className="filter-bar">
          <span style={{ fontSize: 11, color: 'var(--text-muted)', marginRight: 4 }}>Lọc:</span>
          {['Hành trình ▾', 'Vị trí ▾', 'Mức độ ▾'].map(f => (
            <button key={f} className="filter-chip">{f}</button>
          ))}
          {selectedService && (
            <button
              className="filter-chip active"
              onClick={() => setSelectedService(null)}
            >
              ✕ {selectedServiceName}
            </button>
          )}
        </div>

        <div className="two-col-grid" style={{ marginBottom: 24 }}>
          {/* Top Services Bar Chart — theo lượng phản hồi */}
          <div className="card animate-in">
            <div className="section-header">
              <span className="section-title">Lượng phản hồi theo dịch vụ</span>
              <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>Nhấp để lọc</span>
            </div>
            <ResponsiveContainer width="100%" height={280}>
              <BarChart
                data={SERVICE_DATA}
                layout="vertical"
                margin={{ top: 0, right: 16, left: 4, bottom: 0 }}
                barSize={16}
              >
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(0,0,0,0.04)" horizontal={false} />
                <XAxis
                  type="number"
                  tick={{ fontSize: 10, fill: 'var(--text-muted)' }}
                  tickLine={false}
                  axisLine={false}
                />
                <YAxis
                  dataKey="code"
                  type="category"
                  tick={({ x, y, payload }: any) => (
                    <text x={x} y={y} dy={4} textAnchor="end" fontSize={11} fill="var(--text-secondary)" fontWeight={500}>
                      {SHORT_NAME[payload.value] ?? payload.value}
                    </text>
                  )}
                  tickLine={false}
                  axisLine={false}
                  width={72}
                />
                <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(0,0,0,0.03)' }} />
                <Bar
                  dataKey="count"
                  radius={[0, 4, 4, 0]}
                  cursor="pointer"
                  onClick={(d) => setSelectedService(d.code === selectedService ? null : d.code)}
                >
                  {SERVICE_DATA.map((d, idx) => (
                    <Cell
                      key={idx}
                      fill={COLORS[idx % COLORS.length]}
                      opacity={selectedService && d.code !== selectedService ? 0.25 : 0.85}
                    />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Negative Rate Bar Chart */}
          <div className="card animate-in">
            <div className="section-header">
              <span className="section-title">Tỷ lệ tiêu cực theo dịch vụ</span>
            </div>
            <ResponsiveContainer width="100%" height={280}>
              <BarChart
                data={SERVICE_DATA}
                layout="vertical"
                margin={{ top: 0, right: 16, left: 4, bottom: 0 }}
                barSize={16}
              >
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(0,0,0,0.04)" horizontal={false} />
                <XAxis
                  type="number"
                  tick={{ fontSize: 10, fill: 'var(--text-muted)' }}
                  tickLine={false}
                  axisLine={false}
                  tickFormatter={(v) => `${v}%`}
                  domain={[0, 70]}
                />
                <YAxis
                  dataKey="code"
                  type="category"
                  tick={({ x, y, payload }: any) => (
                    <text x={x} y={y} dy={4} textAnchor="end" fontSize={11} fill="var(--text-secondary)" fontWeight={500}>
                      {SHORT_NAME[payload.value] ?? payload.value}
                    </text>
                  )}
                  tickLine={false}
                  axisLine={false}
                  width={72}
                />
                <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(0,0,0,0.03)' }} />
                <Bar dataKey="negRate" radius={[0, 4, 4, 0]}>
                  {SERVICE_DATA.map((d, idx) => (
                    <Cell
                      key={idx}
                      fill={d.negRate >= 40 ? '#dc2626' : d.negRate >= 25 ? '#d97706' : '#16a34a'}
                      opacity={selectedService && d.code !== selectedService ? 0.25 : 0.85}
                    />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Pain Points Detail */}
        <div className="card animate-in">
          <div className="section-header">
            <span className="section-title">
              Vấn đề nổi bật
              {selectedServiceName && (
                <span style={{ color: 'var(--text-accent)', textTransform: 'none', letterSpacing: 0, marginLeft: 8 }}>
                  — {selectedServiceName}
                </span>
              )}
            </span>
            {selectedService && (
              <button className="section-action" onClick={() => setSelectedService(null)}>
                Xem tất cả dịch vụ →
              </button>
            )}
          </div>

          {filteredPains.length > 0 ? (
            <PainPointsList
              data={filteredPains}
              onItemClick={() => navigate('/hotspot')}
            />
          ) : (
            <div style={{ textAlign: 'center', padding: '32px 0', color: 'var(--text-muted)', fontSize: 13 }}>
              Không có vấn đề nào cho dịch vụ này
            </div>
          )}
        </div>
      </div>
    </>
  );
};

export default ServicePainPointsPage;
