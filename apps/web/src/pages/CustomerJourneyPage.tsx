import React, { useCallback, useEffect, useState } from 'react';
import TopBar from '../components/layout/TopBar';
import AnalyticsState from '../components/analytics/AnalyticsState';
import AnalyticsFilterBar from '../components/analytics/AnalyticsFilterBar';
import { mergeTaxonomyBreakdown } from '../components/analytics/journey';
import { AnalyticsBreakdownItem, getAnalyticsBreakdown, getAnalyticsFilterOptions } from '../api/analytics';
import { useAnalyticsFilters } from '../hooks/useAnalyticsFilters';

const CustomerJourneyPage: React.FC = () => {
  const { filters, setFilter, resetFilters, activeFilterCount } = useAnalyticsFilters();
  const [stages, setStages] = useState<AnalyticsBreakdownItem[]>([]);
  const [steps, setSteps] = useState<AnalyticsBreakdownItem[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(Boolean(filters));

  const loadJourney = useCallback(async () => {
    if (!filters) return;
    setLoading(true); setError(null);
    try {
      const [nextStages, nextSteps, taxonomy] = await Promise.all([
        getAnalyticsBreakdown({ ...filters, customerLifecycleStageCode: undefined, customerLifecycleStepCode: undefined }, 'journey_stage'),
        getAnalyticsBreakdown(filters, 'journey_step'),
        getAnalyticsFilterOptions(filters),
      ]);
      setStages(mergeTaxonomyBreakdown(taxonomy.journeyStages, nextStages));
      setSteps(mergeTaxonomyBreakdown(taxonomy.journeySteps, nextSteps));
    } catch (loadError) {
      setError(loadError instanceof Error ? loadError.message : 'Không thể tải hành trình khách hàng.');
    } finally { setLoading(false); }
  }, [filters]);

  useEffect(() => { void loadJourney(); }, [loadJourney]);
  const selectedStage = filters?.customerLifecycleStageCode;

  return <>
    <TopBar title="Customer Journey" subtitle="Khách hàng đang gặp khó khăn ở đâu?" />
    <div className="page-content">
      <AnalyticsFilterBar filters={filters} activeFilterCount={activeFilterCount} onChange={setFilter} onReset={resetFilters} />
      {loading && <AnalyticsState title="Đang tải hành trình" message="Đang áp dụng bộ lọc…" />}
      {!loading && error && <AnalyticsState title="Chưa kết nối được Analytics API" message={error} onRetry={() => void loadJourney()} />}
      {!loading && !error && <>
        <div className="section-header"><span className="section-title">Vòng đời khách hàng</span></div>
        <div className="journey-stages animate-in" style={{ marginBottom: 24 }}>
          {stages.map((stage) => <button key={stage.code} className={`journey-stage-item${selectedStage === stage.code ? ' active' : ''}`} onClick={() => setFilter('customerLifecycleStageCode', selectedStage === stage.code ? undefined : stage.code)}>
            <div className="journey-stage-name">{stage.name}</div><div className="journey-stage-neg" style={{ color: 'var(--text-accent)' }}>{(stage.negativeRate * 100).toFixed(1)}%</div><div className="journey-stage-vol">{stage.itemVolume.toLocaleString()} phản hồi</div>
            <div className="neg-bar-bg" style={{ marginTop: 8 }}><div className="neg-bar-fill" style={{ width: `${stage.negativeRate * 100}%`, background: 'var(--text-accent)', opacity: 0.7 }} /></div>
          </button>)}
        </div>
        <div className="card animate-in"><div className="section-header"><span className="section-title">{selectedStage ? 'Các bước trong giai đoạn đã chọn' : 'Các bước trong hành trình'}</span></div>
          <div className="breakdown-grid">{steps.map((step) => <button key={step.code} className="breakdown-card" onClick={() => setFilter('customerLifecycleStepCode', step.code)}><strong>{step.name}</strong><span>{step.itemVolume.toLocaleString()} phản hồi</span><span>Tiêu cực: {(step.negativeRate * 100).toFixed(1)}%</span><span>{step.activeHotspots} hotspot đang hoạt động</span></button>)}</div>
        </div>
      </>}
    </div>
  </>;
};

export default CustomerJourneyPage;
