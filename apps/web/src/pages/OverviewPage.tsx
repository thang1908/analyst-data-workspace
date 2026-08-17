import React, { useCallback, useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import TopBar from '../components/layout/TopBar';
import KPICard, { buildKPICards } from '../components/analytics/KPICard';
import TrendChart from '../components/analytics/TrendChart';
import PainPointsList, { PainPoint } from '../components/analytics/PainPointsList';
import AnalyticsState from '../components/analytics/AnalyticsState';
import AnalyticsFilterBar from '../components/analytics/AnalyticsFilterBar';
import { HotspotActionQueue } from '../components/hotspot/HotspotActionQueue';
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
        getAnalyticsBreakdown(filters, 'touchpoint'),
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
      <TopBar title="CX Operating Dashboard" subtitle="Giám sát hành trình, chất lượng dịch vụ & hàng đợi điểm nóng" />
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

            {/* Customer Journey Stages */}
            <div className="section-header">
              <div>
                <span className="section-title">Hành trình khách hàng (Customer Journey)</span>
                <span className="dashboard-helper">
                  6 giai đoạn chuẩn hóa — Nhấp chọn để xem các bước và điểm chạm chi tiết
                </span>
              </div>
              <button
                className="section-action"
                onClick={() =>
                  handleDrilldownToExplorer(
                    filters?.customerLifecycleStageCode
                      ? { customer_lifecycle_stage_code: filters.customerLifecycleStageCode }
                      : {}
                  )
                }
              >
                <ExternalLink size={14} /> Xem feedback hành trình
              </button>
            </div>

            <div className="journey-stages animate-in">
              {stages.map((stage) => (
                <button
                  key={stage.code}
                  className={`journey-stage-item${
                    filters?.customerLifecycleStageCode === stage.code ? ' active' : ''
                  }`}
                  onClick={() => {
                    setFilter(
                      'customerLifecycleStageCode',
                      filters?.customerLifecycleStageCode === stage.code ? undefined : stage.code
                    );
                  }}
                >
                  <div className="journey-stage-name">{stage.name}</div>
                  <div className="journey-stage-neg" style={{ color: 'var(--text-accent)' }}>
                    {(stage.negativeRate * 100).toFixed(1)}%
                  </div>
                  <div className="journey-stage-vol">{stage.itemVolume.toLocaleString()} phản hồi</div>
                  <div className="neg-bar-bg" style={{ marginTop: 8 }}>
                    <div
                      className="neg-bar-fill"
                      style={{
                        width: `${stage.negativeRate * 100}%`,
                        background: 'var(--text-accent)',
                        opacity: 0.7,
                      }}
                    />
                  </div>
                </button>
              ))}
            </div>

            {/* Journey Details: Steps & Touchpoints & Services (3-column breakdown) */}
            <div className="dashboard-detail-grid-three">
              {/* Steps */}
              <section className="card dashboard-scroll-panel animate-in">
                <div className="section-header">
                  <div>
                    <span className="section-title">Bước hành trình</span>
                    <p>
                      {filters?.customerLifecycleStageCode
                        ? `Các bước của ${filters.customerLifecycleStageCode}`
                        : 'Tất cả bước hành trình'}
                    </p>
                  </div>
                  <span className="panel-count">{steps.length} bước</span>
                </div>
                <div className="dashboard-scroll-list" aria-label="Danh sách bước hành trình">
                  {steps.map((step) => (
                    <button
                      key={step.code}
                      className={`dashboard-metric-row${
                        filters?.customerLifecycleStepCode === step.code ? ' selected' : ''
                      }`}
                      onClick={() =>
                        setFilter(
                          'customerLifecycleStepCode',
                          filters?.customerLifecycleStepCode === step.code ? undefined : step.code
                        )
                      }
                    >
                      <span>
                        <strong>{step.name}</strong>
                        <small>{step.itemVolume.toLocaleString()} phản hồi</small>
                      </span>
                      <span className="dashboard-row-metric">
                        <strong>{(step.negativeRate * 100).toFixed(1)}%</strong>
                        <small>tiêu cực</small>
                      </span>
                    </button>
                  ))}
                </div>
              </section>

              {/* Touchpoints */}
              <section className="card dashboard-scroll-panel animate-in">
                <div className="section-header">
                  <div>
                    <span className="section-title">Điểm chạm (Touchpoints)</span>
                    <p>
                      {filters?.customerLifecycleStepCode
                        ? `Điểm chạm thuộc ${filters.customerLifecycleStepCode}`
                        : 'Điểm chạm theo bộ lọc'}
                    </p>
                  </div>
                  <span className="panel-count">{touchpoints.length} điểm chạm</span>
                </div>
                <div className="dashboard-scroll-list" aria-label="Danh sách điểm chạm">
                  {touchpoints.length === 0 ? (
                    <div className="empty-panel-text">Không có điểm chạm tương ứng</div>
                  ) : (
                    touchpoints.map((tp) => (
                      <button
                        key={tp.code}
                        className={`dashboard-metric-row${
                          filters?.touchpointCode === tp.code ? ' selected' : ''
                        }`}
                        onClick={() =>
                          setFilter(
                            'touchpointCode',
                            filters?.touchpointCode === tp.code ? undefined : tp.code
                          )
                        }
                      >
                        <span>
                          <strong>{tp.name}</strong>
                          <small>{tp.code} • {tp.itemVolume.toLocaleString()} phản hồi</small>
                        </span>
                        <span className="dashboard-row-metric">
                          <strong>{(tp.negativeRate * 100).toFixed(1)}%</strong>
                          <small>tiêu cực</small>
                        </span>
                      </button>
                    ))
                  )}
                </div>
              </section>

              {/* Services */}
              <section className="card dashboard-scroll-panel animate-in">
                <div className="section-header">
                  <div>
                    <span className="section-title">10 Dịch vụ vận hành</span>
                    <p>Lọc theo dịch vụ để xem cụ thể vấn đề</p>
                  </div>
                  <span className="panel-count">{services.length} dịch vụ</span>
                </div>
                <div className="dashboard-scroll-list" aria-label="Danh sách dịch vụ">
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
                        <strong>{(service.negativeRate * 100).toFixed(1)}%</strong>
                        <small>tiêu cực</small>
                      </span>
                    </button>
                  ))}
                </div>
              </section>
            </div>

            {/* Hotspot Action Priority Queue Section */}
            {filters && (
              <HotspotActionQueue
                projectId={filters.projectId}
                hotspots={hotspots}
                loading={hotspotsLoading}
                onRefresh={() => void loadHotspotsData()}
              />
            )}

            {/* Trend Chart & Highlighted Issues */}
            <div className="two-col-grid">
              <div className="card animate-in">
                <div className="section-header">
                  <span className="section-title">Xu hướng trải nghiệm & tỷ lệ tiêu cực</span>
                </div>
                {trend.length ? (
                  <TrendChart data={trend} />
                ) : (
                  <AnalyticsState message="Chưa có xu hướng trong bộ lọc này." />
                )}
              </div>

              <div className="card animate-in">
                <div className="section-header">
                  <div>
                    <span className="section-title">Vấn đề phát sinh nổi bật (Pain Points)</span>
                    <p className="dashboard-helper">Nhấp vào vấn đề để xem chi tiết bằng chứng phản ánh</p>
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
          </>
        )}
      </div>
    </>
  );
};

export default OverviewPage;
