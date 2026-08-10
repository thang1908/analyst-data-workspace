import React, { useEffect, useState } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { RefreshCw, Clock, Layers } from 'lucide-react';
import { api } from '../../client/api';
import {
  AnalyticsFilterParams,
  AnalyticsSummary,
  TrendResponse,
  BreakdownResponse,
} from '../../client/types';

import { FilterBar } from './FilterBar';
import { KpiCards } from './KpiCards';
import { ChartsSection } from './ChartsSection';
import { DataQualityPanel } from './DataQualityPanel';

export const DashboardView: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const navigate = useNavigate();

  const [summary, setSummary] = useState<AnalyticsSummary | null>(null);
  const [trend, setTrend] = useState<TrendResponse | null>(null);
  const [breakdownService, setBreakdownService] = useState<BreakdownResponse | null>(null);
  const [breakdownLocation, setBreakdownLocation] = useState<BreakdownResponse | null>(null);
  const [breakdownSeverity, setBreakdownSeverity] = useState<BreakdownResponse | null>(null);

  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const currentFilters: AnalyticsFilterParams = {
    from_date: searchParams.get('from_date') || '2026-08-01',
    to_date: searchParams.get('to_date') || '2026-08-10',
    service_ids: searchParams.get('service_ids') || undefined,
    location_ids: searchParams.get('location_ids') || undefined,
    sentiments: searchParams.get('sentiments') || undefined,
    severities: searchParams.get('severities') || undefined,
  };

  const loadData = async (isExplicitRefresh = false) => {
    if (isExplicitRefresh) setRefreshing(true);
    else setLoading(true);
    setError(null);

    try {
      const [sumData, trData, srvData, locData, sevData] = await Promise.all([
        api.getSummary(currentFilters),
        api.getTrend(currentFilters),
        api.getBreakdown('service', currentFilters),
        api.getBreakdown('location', currentFilters),
        api.getBreakdown('severity', currentFilters),
      ]);

      setSummary(sumData);
      setTrend(trData);
      setBreakdownService(srvData);
      setBreakdownLocation(locData);
      setBreakdownSeverity(sevData);
    } catch (err: any) {
      setError(err.message || 'Không thể tải dữ liệu Analytics');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [searchParams.toString()]);

  const handleApplyFilters = (newFilters: AnalyticsFilterParams) => {
    const params = new URLSearchParams();
    if (newFilters.from_date) params.set('from_date', newFilters.from_date);
    if (newFilters.to_date) params.set('to_date', newFilters.to_date);
    if (newFilters.service_ids) params.set('service_ids', newFilters.service_ids);
    if (newFilters.location_ids) params.set('location_ids', newFilters.location_ids);
    if (newFilters.sentiments) params.set('sentiments', newFilters.sentiments);
    if (newFilters.severities) params.set('severities', newFilters.severities);

    setSearchParams(params);
  };

  const handleResetFilters = () => {
    setSearchParams(new URLSearchParams({ from_date: '2026-08-01', to_date: '2026-08-10' }));
  };

  const handleDrillDownFromKpi = (extraFilters: { sentiment?: string; severity?: string }) => {
    const params = new URLSearchParams(searchParams);
    if (extraFilters.sentiment) params.set('sentiments', extraFilters.sentiment);
    if (extraFilters.severity) params.set('severities', extraFilters.severity);
    navigate(`/feedback?${params.toString()}`);
  };

  const handleSegmentClick = (dimension: string, key: string) => {
    const params = new URLSearchParams(searchParams);
    if (dimension === 'service') params.set('service_ids', key);
    if (dimension === 'location') params.set('location_ids', key);
    if (dimension === 'severity') params.set('severities', key);
    navigate(`/feedback?${params.toString()}`);
  };

  if (loading && !summary) {
    return (
      <div style={{ textAlign: 'center', padding: 64 }}>
        <RefreshCw size={36} className="skeleton" style={{ margin: '0 auto 16px' }} />
        <h2 className="heading-md">Đang tải dữ liệu Dashboard Analytics...</h2>
      </div>
    );
  }

  return (
    <div>
      {/* Dashboard Top Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20, flexWrap: 'wrap', gap: 16 }}>
        <div>
          <h1 className="heading-lg" style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <Layers size={28} style={{ color: 'var(--accent-primary)' }} /> Trusted CSV to Dashboard
          </h1>
          <p className="subtext" style={{ marginTop: 4 }}>
            Báo cáo phân tích chất lượng trải nghiệm khách hàng (CX Intelligence Platform Pilot)
          </p>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          {summary?.snapshot_token && (
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: 6, background: 'rgba(255, 255, 255, 0.04)', padding: '6px 12px', borderRadius: 8 }}>
              <Clock size={14} /> Snapshot: <code>{summary.snapshot_token}</code>
            </div>
          )}
          <button 
            className="btn-secondary" 
            onClick={() => loadData(true)}
            disabled={refreshing}
          >
            <RefreshCw size={16} className={refreshing ? 'skeleton' : ''} />
            {refreshing ? 'Đang cập nhật...' : 'Làm mới số liệu'}
          </button>
        </div>
      </div>

      {/* Filter Bar */}
      <FilterBar 
        initialFilters={currentFilters}
        onApply={handleApplyFilters}
        onReset={handleResetFilters}
      />

      {/* Error Notice if any */}
      {error && (
        <div style={{ background: 'rgba(244, 63, 94, 0.15)', border: '1px solid rgba(244, 63, 94, 0.4)', borderRadius: 8, padding: 16, marginBottom: 24, color: '#fb7185' }}>
          {error}
        </div>
      )}

      {/* KPI Cards */}
      {summary && (
        <KpiCards 
          metrics={summary.metrics} 
          onDrillDown={handleDrillDownFromKpi}
        />
      )}

      {/* Charts Section */}
      {trend && breakdownService && breakdownLocation && breakdownSeverity && (
        <ChartsSection 
          trend={trend}
          breakdownService={breakdownService}
          breakdownLocation={breakdownLocation}
          breakdownSeverity={breakdownSeverity}
          onSegmentClick={handleSegmentClick}
        />
      )}

      {/* Data Quality Panel */}
      <DataQualityPanel />
    </div>
  );
};
