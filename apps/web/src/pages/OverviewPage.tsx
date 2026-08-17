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
  const [steps, setSteps] = useState<AnalyticsBreakdownItem[]>([]);
  const [services, setServices] = useState<AnalyticsBreakdownItem[]>([]);
  const [issues, setIssues] = useState<PainPoint[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(Boolean(filters));

  const loadDashboard = useCallback(async () => {
    if (!filters) return;
    setLoading(true);
    setError(null);
    try {
      const [nextSummary, nextTrend, nextStages, nextSteps, nextServices, nextIssues, taxonomy] = await Promise.all([
        getAnalyticsSummary(filters),
        getAnalyticsTrend(filters),
        getAnalyticsBreakdown({ ...filters, customerLifecycleStageCode: undefined, customerLifecycleStepCode: undefined }, 'journey_stage'),
        getAnalyticsBreakdown(filters, 'journey_step'),
        getAnalyticsBreakdown({ ...filters, serviceCode: undefined, issueCode: undefined }, 'service'),
        getAnalyticsBreakdown(filters, 'issue', 6),
        getAnalyticsFilterOptions(filters),
      ]);
      setSummary(nextSummary);
      setTrend(nextTrend);
      setStages(mergeTaxonomyBreakdown(taxonomy.journeyStages, nextStages));
      setSteps(mergeTaxonomyBreakdown(taxonomy.journeySteps, nextSteps));
      setServices(mergeTaxonomyBreakdown(taxonomy.services, nextServices));
      const issueNames = new Map(taxonomy.issues.map((issue) => [issue.code, issue.name]));
      setIssues(nextIssues.map((item) => ({
        code: item.code,
        name: issueNames.get(item.code) ?? item.name,
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
      <TopBar title="CX Dashboard" subtitle="Từ trải nghiệm khách hàng đến ưu tiên xử lý" />
      <div className="page-content">
        <AnalyticsFilterBar filters={filters} activeFilterCount={activeFilterCount} onChange={setFilter} onReset={resetFilters} />
        {loading && <AnalyticsState title="Đang tải dashboard" message="Đang truy vấn dữ liệu theo bộ lọc đã chọn…" />}
        {!loading && error && <AnalyticsState title="Chưa kết nối được Analytics API" message={error} onRetry={() => void loadDashboard()} />}
        {!loading && !error && summary && (
          <>
            {!hasData && <AnalyticsState title="Chưa có feedback khớp bộ lọc" message="Các chỉ số và hành trình vẫn được hiển thị với giá trị 0." onRetry={resetFilters} />}
            <div className="kpi-grid">{kpiCards.map((card) => <KPICard key={card.type} {...card} />)}</div>
            <div className="section-header"><span className="section-title">Hành trình khách hàng</span><span className="dashboard-helper">Chọn giai đoạn để xem bước và dịch vụ liên quan</span></div>
            <div className="journey-stages animate-in">
              {stages.map((stage) => (
                <button key={stage.code} className={`journey-stage-item${filters?.customerLifecycleStageCode === stage.code ? ' active' : ''}`} onClick={() => {
                  setFilter('customerLifecycleStageCode', filters?.customerLifecycleStageCode === stage.code ? undefined : stage.code);
                }}>
                  <div className="journey-stage-name">{stage.name}</div>
                  <div className="journey-stage-neg" style={{ color: 'var(--text-accent)' }}>{(stage.negativeRate * 100).toFixed(1)}%</div>
                  <div className="journey-stage-vol">{stage.itemVolume.toLocaleString()} phản hồi</div>
                  <div className="neg-bar-bg" style={{ marginTop: 8 }}><div className="neg-bar-fill" style={{ width: `${stage.negativeRate * 100}%`, background: 'var(--text-accent)', opacity: 0.7 }} /></div>
                </button>
              ))}
            </div>
            <div className="dashboard-detail-grid">
              <section className="card dashboard-scroll-panel animate-in">
                <div className="section-header"><div><span className="section-title">Bước hành trình</span><p>{filters?.customerLifecycleStageCode ? 'Các bước của giai đoạn đang chọn' : 'Chọn giai đoạn để thu hẹp danh sách'}</p></div><span className="panel-count">{steps.length} bước</span></div>
                <div className="dashboard-scroll-list" aria-label="Danh sách bước hành trình">
                  {steps.map((step) => <button key={step.code} className={`dashboard-metric-row${filters?.customerLifecycleStepCode === step.code ? ' selected' : ''}`} onClick={() => setFilter('customerLifecycleStepCode', filters?.customerLifecycleStepCode === step.code ? undefined : step.code)}><span><strong>{step.name}</strong><small>{step.itemVolume.toLocaleString()} phản hồi</small></span><span className="dashboard-row-metric"><strong>{(step.negativeRate * 100).toFixed(1)}%</strong><small>tiêu cực</small></span></button>)}
                </div>
              </section>
              <section className="card dashboard-scroll-panel animate-in">
                <div className="section-header"><div><span className="section-title">Dịch vụ liên quan</span><p>Chọn dịch vụ để lọc vấn đề nổi bật</p></div><span className="panel-count">{services.length} dịch vụ</span></div>
                <div className="dashboard-scroll-list" aria-label="Danh sách dịch vụ">
                  {services.map((service) => <button key={service.code} className={`dashboard-metric-row${filters?.serviceCode === service.code ? ' selected' : ''}`} onClick={() => setFilter('serviceCode', filters?.serviceCode === service.code ? undefined : service.code)}><span><strong>{service.name}</strong><small>{service.itemVolume.toLocaleString()} phản hồi</small></span><span className="dashboard-row-metric"><strong>{(service.negativeRate * 100).toFixed(1)}%</strong><small>tiêu cực</small></span></button>)}
                </div>
              </section>
            </div>
            <div className="two-col-grid">
              <div className="card animate-in"><div className="section-header"><span className="section-title">Xu hướng trải nghiệm</span></div>{trend.length ? <TrendChart data={trend} /> : <AnalyticsState message="Chưa có xu hướng trong bộ lọc này." />}</div>
              <div className="card animate-in"><div className="section-header"><span className="section-title">Vấn đề nổi bật</span></div>{issues.length ? <PainPointsList data={issues} onItemClick={(item) => { const next = new URLSearchParams(location.search); next.set('issue_code', item.code); navigate(`/feedback?${next.toString()}`); }} /> : <AnalyticsState message="Chưa có vấn đề trong bộ lọc này." />}</div>
            </div>
          </>
        )}
      </div>
    </>
  );
};

export default OverviewPage;
