import React, { useCallback, useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import TopBar from '../components/layout/TopBar';
import KPICard, { buildKPICards } from '../components/analytics/KPICard';
import TrendChart from '../components/analytics/TrendChart';
import PainPointsList, { PainPoint } from '../components/analytics/PainPointsList';
import AnalyticsState from '../components/analytics/AnalyticsState';
import AnalyticsFilterBar from '../components/analytics/AnalyticsFilterBar';
import { HotspotActionQueue } from '../components/hotspot/HotspotActionQueue';
import { Journey3DMatrix } from '../components/analytics/Journey3DMatrix';
import { mergeTaxonomyBreakdown } from '../components/analytics/journey';
import {
  AnalyticsBreakdownItem,
  AnalyticsSummary,
  AnalyticsTrendPoint,
  getAnalyticsBreakdown,
  getAnalyticsFilterOptions,
  getAnalyticsSummary,
  getAnalyticsTrend,
} from '../api/analytics';
import { HotspotItemData, listHotspots } from '../api/hotspots';
import { useAnalyticsFilters } from '../hooks/useAnalyticsFilters';
import { ExternalLink } from 'lucide-react';

const OverviewPage: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { filters, setFilter, resetFilters, activeFilterCount } = useAnalyticsFilters();
  const [summary, setSummary] = useState<AnalyticsSummary | null>(null);
  const [trend, setTrend] = useState<AnalyticsTrendPoint[]>([]);
  const [stages, setStages] = useState<AnalyticsBreakdownItem[]>([]);
  const [steps, setSteps] = useState<AnalyticsBreakdownItem[]>([]);
  const [touchpoints, setTouchpoints] = useState<AnalyticsBreakdownItem[]>([]);
  const [services, setServices] = useState<AnalyticsBreakdownItem[]>([]);
  const [issues, setIssues] = useState<PainPoint[]>([]);
  const [hotspots, setHotspots] = useState<HotspotItemData[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(Boolean(filters));
  const [hotspotsLoading, setHotspotsLoading] = useState(false);

  const loadHotspotsData = useCallback(async () => {
    if (!filters?.projectId) return;
    setHotspotsLoading(true);
    try {
      const res = await listHotspots({
        projectId: filters.projectId,
        serviceCode: filters.serviceCode,
        issueCode: filters.issueCode,
        locationId: filters.locationId,
        dateFrom: filters.dateFrom,
        dateTo: filters.dateTo,
      });
      setHotspots(res.data);
    } catch (e) {
      console.warn('Could not load hotspots for dashboard', e);
    } finally {
      setHotspotsLoading(false);
    }
  }, [filters]);

  const loadDashboard = useCallback(async () => {
    if (!filters) return;
    setLoading(true);
    setError(null);
    try {
      const [
        nextSummary,
        nextTrend,
        nextStages,
        nextSteps,
        nextTouchpoints,
        nextServices,
        nextIssues,
        taxonomy,
      ] = await Promise.all([
        getAnalyticsSummary(filters),
        getAnalyticsTrend(filters),
        getAnalyticsBreakdown(
          { ...filters, customerLifecycleStageCode: undefined, customerLifecycleStepCode: undefined, touchpointCode: undefined },
          'journey_stage'
        ),
        getAnalyticsBreakdown(
          { ...filters, customerLifecycleStepCode: undefined, touchpointCode: undefined },
          'journey_step'
        ),
        getAnalyticsBreakdown(
          { ...filters, touchpointCode: undefined },
          'touchpoint'
        ),
        getAnalyticsBreakdown({ ...filters, serviceCode: undefined, issueCode: undefined }, 'service'),
        getAnalyticsBreakdown(filters, 'issue', 8),
        getAnalyticsFilterOptions(filters),
      ]);

      setSummary(nextSummary);
      setTrend(nextTrend);
      setStages(mergeTaxonomyBreakdown(taxonomy.journeyStages, nextStages));
      setSteps(mergeTaxonomyBreakdown(taxonomy.journeySteps, nextSteps));
      setTouchpoints(mergeTaxonomyBreakdown(taxonomy.touchpoints, nextTouchpoints));
      setServices(mergeTaxonomyBreakdown(taxonomy.services, nextServices));

      const issueNames = new Map(taxonomy.issues.map((issue) => [issue.code, issue.name]));
      setIssues(
        nextIssues.map((item) => ({
          code: item.code,
          name: issueNames.get(item.code) ?? item.name,
          count: item.itemVolume,
          percentage: item.percentage,
          negativeRate: item.negativeRate,
          activeHotspots: item.activeHotspots,
        }))
      );
    } catch (loadError) {
      setError(loadError instanceof Error ? loadError.message : 'Không thể tải dữ liệu analytics.');
    } finally {
      setLoading(false);
    }
  }, [filters]);

  useEffect(() => {
    void loadDashboard();
    void loadHotspotsData();
  }, [loadDashboard, loadHotspotsData]);

  const hasData = Boolean(summary && summary.itemVolume > 0);
  const kpiCards = summary
    ? buildKPICards({
        negativeRate: summary.negativeRate * 100,
        feedbackVolume: summary.itemVolume,
        unknownRate: summary.unknownRate * 100,
        activeHotspots: summary.activeHotspots,
      })
    : [];

  const handleDrilldownToExplorer = (extraParams: Record<string, string>) => {
    const next = new URLSearchParams(location.search);
    for (const [k, v] of Object.entries(extraParams)) {
      if (v) next.set(k, v);
    }
    navigate(`/feedback?${next.toString()}`);
  };

  return (
    <>
      <TopBar title="CX Dashboard" />
      <div className="page-content">
        <AnalyticsFilterBar
          filters={filters}
          activeFilterCount={activeFilterCount}
          onChange={setFilter}
          onReset={resetFilters}
        />
        {loading && <AnalyticsState title="Đang tải dashboard" message="Đang truy vấn dữ liệu theo bộ lọc đã chọn…" />}
        {!loading && error && (
          <AnalyticsState
            title="Chưa kết nối được Analytics API"
            message={error}
            onRetry={() => {
              void loadDashboard();
              void loadHotspotsData();
            }}
          />
        )}
        {!loading && !error && summary && (
          <>
            {!hasData && (
              <AnalyticsState
                title="Chưa có feedback khớp bộ lọc"
                message="Các chỉ số và cấu trúc hành trình/dịch vụ vẫn được hiển thị đầy đủ với giá trị 0."
                onRetry={resetFilters}
              />
            )}

            {/* KPI Summary Cards */}
            <div className="kpi-grid">
              {kpiCards.map((card) => (
                <KPICard key={card.type} {...card} />
              ))}
            </div>

            {/* 3D Visual Journey Matrix Flow */}
            <Journey3DMatrix
              stages={stages}
              steps={steps}
              touchpoints={touchpoints}
              services={services}
              selectedStageCode={filters?.customerLifecycleStageCode}
              selectedStepCode={filters?.customerLifecycleStepCode}
              onSelectStage={(code) => setFilter('customerLifecycleStageCode', code)}
              onSelectStep={(code) => setFilter('customerLifecycleStepCode', code)}
              onDrilldown={(extraParams) => handleDrilldownToExplorer(extraParams)}
            />

            {/* Hotspot Action Priority Queue Section */}
            {filters && (
              <HotspotActionQueue
                projectId={filters.projectId}
                hotspots={hotspots}
                loading={hotspotsLoading}
                onRefresh={() => void loadHotspotsData()}
              />
            )}

            {/* 2-Column Grid: 10 Services & Pain Points */}
            <div className="two-col-grid">
              {/* 10 Services List */}
              <section className="card animate-in">
                <div className="section-header">
                  <div>
                    <span className="section-title">Dịch vụ vận hành</span>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                    <span className="panel-count">{services.length} dịch vụ</span>
                    {filters?.serviceCode && (
                      <button
                        className="section-action"
                        style={{ padding: '2px 8px', fontSize: 12 }}
                        onClick={() =>
                          handleDrilldownToExplorer({
                            service_code: filters.serviceCode!,
                          })
                        }
                        title="Xem phản hồi của dịch vụ này"
                      >
                        <ExternalLink size={12} /> Bằng chứng
                      </button>
                    )}
                  </div>
                </div>
                <div className="dashboard-scroll-list" style={{ maxHeight: 340 }} aria-label="Danh sách dịch vụ">
                  {services.map((service) => (
                    <button
                      key={service.code}
                      className={`dashboard-metric-row${
                        filters?.serviceCode === service.code ? ' selected' : ''
                      }`}
                      onClick={() =>
                        setFilter(
                          'serviceCode',
                          filters?.serviceCode === service.code ? undefined : service.code
                        )
                      }
                    >
                      <span>
                        <strong>{service.name}</strong>
                        <small>{service.itemVolume.toLocaleString()} phản hồi</small>
                      </span>
                      <span className="dashboard-row-metric">
                        <strong style={{ color: service.negativeRate >= 0.4 ? '#dc2626' : '#2563eb' }}>
                          {(service.negativeRate * 100).toFixed(1)}%
                        </strong>
                        <small>tiêu cực</small>
                      </span>
                    </button>
                  ))}
                </div>
              </section>

              {/* Highlighted Issues / Pain Points */}
              <div className="card animate-in">
                <div className="section-header">
                  <div>
                    <span className="section-title">Vấn đề phát sinh</span>
                  </div>
                </div>
                {issues.length ? (
                  <PainPointsList
                    data={issues}
                    onItemClick={(item) => {
                      handleDrilldownToExplorer({ issue_code: item.code });
                    }}
                  />
                ) : (
                  <AnalyticsState message="Chưa có vấn đề trong bộ lọc này." />
                )}
              </div>
            </div>

            {/* Trend Chart */}
            <div className="card animate-in" style={{ marginTop: 24 }}>
              <div className="section-header">
                <div>
                  <span className="section-title">Xu hướng theo thời gian</span>
                </div>
              </div>
              {trend.length ? (
                <TrendChart data={trend} />
              ) : (
                <AnalyticsState message="Chưa có xu hướng trong bộ lọc này." />
              )}
            </div>
          </>
        )}
      </div>
    </>
  );
};

export default OverviewPage;
