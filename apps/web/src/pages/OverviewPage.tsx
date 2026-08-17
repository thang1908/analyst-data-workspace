import React, { useCallback, useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import TopBar from '../components/layout/TopBar';
import KPICard, { buildKPICards } from '../components/analytics/KPICard';
import TrendChart from '../components/analytics/TrendChart';
import PainPointsList, { PainPoint } from '../components/analytics/PainPointsList';
import AnalyticsState from '../components/analytics/AnalyticsState';
import AnalyticsFilterBar from '../components/analytics/AnalyticsFilterBar';
import { mergeTaxonomyBreakdown } from '../components/analytics/journey';
import { AnalyticsBreakdownItem, AnalyticsSummary, AnalyticsTrendPoint, getAnalyticsBreakdown, getAnalyticsFilterOptions, getAnalyticsSummary, getAnalyticsTrend } from '../api/analytics';
import { useAnalyticsFilters } from '../hooks/useAnalyticsFilters';

const OverviewPage: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { filters, setFilter, resetFilters, activeFilterCount } = useAnalyticsFilters();
  const [summary, setSummary] = useState<AnalyticsSummary | null>(null);
  const [trend, setTrend] = useState<AnalyticsTrendPoint[]>([]);
  const [stages, setStages] = useState<AnalyticsBreakdownItem[]>([]);
  const [issues, setIssues] = useState<PainPoint[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(Boolean(filters));

  const loadDashboard = useCallback(async () => {
    if (!filters) return;
    setLoading(true);
    setError(null);
    try {
      const [nextSummary, nextTrend, nextStages, nextIssues, taxonomy] = await Promise.all([
        getAnalyticsSummary(filters),
        getAnalyticsTrend(filters),
        getAnalyticsBreakdown({ ...filters, customerLifecycleStageCode: undefined, customerLifecycleStepCode: undefined }, 'journey_stage'),
        getAnalyticsBreakdown(filters, 'issue', 6),
        getAnalyticsFilterOptions({ ...filters, customerLifecycleStageCode: undefined, customerLifecycleStepCode: undefined }),
      ]);
      setSummary(nextSummary);
      setTrend(nextTrend);
      setStages(mergeTaxonomyBreakdown(taxonomy.journeyStages, nextStages));
      setIssues(nextIssues.map((item) => ({
        name: item.name,
        count: item.itemVolume,
        percentage: item.percentage,
        negativeRate: item.negativeRate,
        activeHotspots: item.activeHotspots,
      })));
    } catch (loadError) {
      setError(loadError instanceof Error ? loadError.message : 'Không thể tải dữ liệu analytics.');
    } finally {
      setLoading(false);
    }
  }, [filters]);

  useEffect(() => { void loadDashboard(); }, [loadDashboard]);

  const hasData = Boolean(summary && summary.itemVolume > 0);
  const kpiCards = summary ? buildKPICards({
    negativeRate: summary.negativeRate * 100,
    feedbackVolume: summary.itemVolume,
    unknownRate: summary.unknownRate * 100,
    activeHotspots: summary.activeHotspots,
  }) : [];

  return (
    <>
      <TopBar title="CX Overview" subtitle="Tổng quan trải nghiệm khách hàng" />
      <div className="page-content">
        <AnalyticsFilterBar filters={filters} activeFilterCount={activeFilterCount} onChange={setFilter} onReset={resetFilters} />
        {loading && <AnalyticsState title="Đang tải dashboard" message="Đang truy vấn dữ liệu theo bộ lọc đã chọn…" />}
        {!loading && error && <AnalyticsState title="Chưa kết nối được Analytics API" message={error} onRetry={() => void loadDashboard()} />}
        {!loading && !error && summary && (
          <>
            {!hasData && <AnalyticsState title="Chưa có feedback khớp bộ lọc" message="Các chỉ số và hành trình vẫn được hiển thị với giá trị 0." onRetry={resetFilters} />}
            <div className="kpi-grid">{kpiCards.map((card) => <KPICard key={card.type} {...card} />)}</div>
            <div className="section-header"><span className="section-title">Hành trình khách hàng</span><button className="section-action" onClick={() => navigate(`/customer-journey${location.search}`)}>Xem chi tiết →</button></div>
            <div className="journey-stages animate-in">
              {stages.map((stage, index) => (
                <button key={stage.code} className="journey-stage-item" onClick={() => {
                  const nextQuery = new URLSearchParams(location.search);
                  nextQuery.set('customer_lifecycle_stage_code', stage.code);
                  nextQuery.delete('customer_lifecycle_step_code');
                  navigate(`/customer-journey?${nextQuery.toString()}`);
                }}>
                  <div className="journey-stage-name">{stage.name}</div>
                  <div className="journey-stage-neg" style={{ color: 'var(--text-accent)' }}>{(stage.negativeRate * 100).toFixed(1)}%</div>
                  <div className="journey-stage-vol">{stage.itemVolume.toLocaleString()} phản hồi</div>
                  <div className="neg-bar-bg" style={{ marginTop: 8 }}><div className="neg-bar-fill" style={{ width: `${stage.negativeRate * 100}%`, background: 'var(--text-accent)', opacity: 0.7 }} /></div>
                  {index < stages.length - 1 && <div className="journey-stage-connector">›</div>}
                </button>
              ))}
            </div>
            <div className="two-col-grid">
              <div className="card animate-in"><div className="section-header"><span className="section-title">Xu hướng trải nghiệm</span></div>{trend.length ? <TrendChart data={trend} /> : <AnalyticsState message="Chưa có xu hướng trong bộ lọc này." />}</div>
              <div className="card animate-in"><div className="section-header"><span className="section-title">Vấn đề nổi bật</span><button className="section-action" onClick={() => navigate(`/service-pain-points${location.search}`)}>Xem tất cả →</button></div>{issues.length ? <PainPointsList data={issues} onItemClick={() => navigate(`/service-pain-points${location.search}`)} /> : <AnalyticsState message="Chưa có vấn đề trong bộ lọc này." />}</div>
            </div>
          </>
        )}
      </div>
    </>
  );
};

export default OverviewPage;
