import React, { useCallback, useEffect, useState } from 'react';
import { Bar, BarChart, CartesianGrid, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import TopBar from '../components/layout/TopBar';
import PainPointsList, { PainPoint } from '../components/analytics/PainPointsList';
import AnalyticsState from '../components/analytics/AnalyticsState';
import AnalyticsFilterBar from '../components/analytics/AnalyticsFilterBar';
import { AnalyticsBreakdownItem, getAnalyticsBreakdown } from '../api/analytics';
import { useAnalyticsFilters } from '../hooks/useAnalyticsFilters';

const COLORS = ['#dc2626', '#ea580c', '#d97706', '#65a30d', '#16a34a', '#0891b2', '#2563eb', '#7c3aed'];

const ServiceTooltip = ({ active, payload }: { active?: boolean; payload?: Array<{ payload: AnalyticsBreakdownItem }> }) => {
  if (!active || !payload?.length) return null;
  const item = payload[0].payload;
  return <div className="chart-tooltip"><strong>{item.name}</strong><span>{item.itemVolume.toLocaleString()} phản hồi</span><span>Tiêu cực: {(item.negativeRate * 100).toFixed(1)}%</span><span>{item.activeHotspots} hotspot đang hoạt động</span></div>;
};

const ServicePainPointsPage: React.FC = () => {
  const { filters, setFilter, resetFilters, activeFilterCount } = useAnalyticsFilters();
  const [services, setServices] = useState<AnalyticsBreakdownItem[]>([]);
  const [issues, setIssues] = useState<PainPoint[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(Boolean(filters));

  const loadServices = useCallback(async () => {
    if (!filters) return;
    setLoading(true); setError(null);
    try {
      const [nextServices, nextIssues] = await Promise.all([
        getAnalyticsBreakdown({ ...filters, serviceCode: undefined, issueCode: undefined }, 'service'),
        getAnalyticsBreakdown(filters, 'issue'),
      ]);
      setServices(nextServices);
      setIssues(nextIssues.map((item) => ({ name: item.name, count: item.itemVolume, percentage: item.percentage, negativeRate: item.negativeRate, activeHotspots: item.activeHotspots })));
    } catch (loadError) {
      setError(loadError instanceof Error ? loadError.message : 'Không thể tải dữ liệu dịch vụ.');
    } finally { setLoading(false); }
  }, [filters]);

  useEffect(() => { void loadServices(); }, [loadServices]);
  const selectedService = filters?.serviceCode;
  const selectedServiceName = services.find((service) => service.code === selectedService)?.name;

  return <>
    <TopBar title="Service & Pain Points" subtitle="Dịch vụ nào cần được ưu tiên cải thiện?" />
    <div className="page-content">
      <AnalyticsFilterBar filters={filters} activeFilterCount={activeFilterCount} onChange={setFilter} onReset={resetFilters} />
      {loading && <AnalyticsState title="Đang tải dịch vụ" message="Đang áp dụng bộ lọc…" />}
      {!loading && error && <AnalyticsState title="Chưa kết nối được Analytics API" message={error} onRetry={() => void loadServices()} />}
      {!loading && !error && <>
        <div className="card animate-in" style={{ marginBottom: 24 }}>
          <div className="section-header"><span className="section-title">Lượng phản hồi theo dịch vụ</span><span style={{ fontSize: 11, color: 'var(--text-muted)' }}>Nhấp vào dịch vụ để lọc vấn đề</span></div>
          {services.length ? <ResponsiveContainer width="100%" height={Math.max(260, services.length * 56)}>
            <BarChart data={services} layout="vertical" margin={{ top: 0, right: 16, left: 92, bottom: 0 }} barSize={16}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(0,0,0,0.04)" horizontal={false} />
              <XAxis type="number" tick={{ fontSize: 10, fill: 'var(--text-muted)' }} tickLine={false} axisLine={false} />
              <YAxis dataKey="name" type="category" tick={{ fontSize: 11, fill: 'var(--text-secondary)', fontWeight: 500 }} tickLine={false} axisLine={false} width={180} />
              <Tooltip content={<ServiceTooltip />} cursor={{ fill: 'rgba(0,0,0,0.03)' }} />
              <Bar dataKey="itemVolume" radius={[0, 4, 4, 0]} cursor="pointer" onClick={(_, index) => { const service = services[index]; if (service) setFilter('serviceCode', selectedService === service.code ? undefined : service.code); }}>
                {services.map((item, index) => <Cell key={item.code} fill={COLORS[index % COLORS.length]} opacity={selectedService && item.code !== selectedService ? 0.25 : 0.85} />)}
              </Bar>
            </BarChart>
          </ResponsiveContainer> : <AnalyticsState message="Không có dịch vụ khớp bộ lọc này." />}
        </div>
        <div className="card animate-in"><div className="section-header"><span className="section-title">{selectedServiceName ? `Vấn đề nổi bật — ${selectedServiceName}` : 'Vấn đề nổi bật'}</span>{selectedService && <button className="section-action" onClick={() => setFilter('serviceCode', undefined)}>Xem tất cả dịch vụ →</button>}</div>{issues.length ? <PainPointsList data={issues} /> : <AnalyticsState message="Không có vấn đề khớp bộ lọc này." />}</div>
      </>}
    </div>
  </>;
};

export default ServicePainPointsPage;
