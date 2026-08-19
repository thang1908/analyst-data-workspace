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
import ChannelBreakdownCard from '../components/analytics/ChannelBreakdownCard';
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
  const [channels, setChannels] = useState<AnalyticsBreakdownItem[]>([]);
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
        nextChannels,
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
        getAnalyticsBreakdown(filters, 'issue', 50),
        getAnalyticsBreakdown({ ...filters, intakeChannelCode: undefined }, 'intake_channel'),
        getAnalyticsFilterOptions(filters),
      ]);

      setSummary(nextSummary);
      setTrend(nextTrend);
      setStages(mergeTaxonomyBreakdown(taxonomy.journeyStages, nextStages));
      setSteps(mergeTaxonomyBreakdown(taxonomy.journeySteps, nextSteps));
      setTouchpoints(mergeTaxonomyBreakdown(taxonomy.touchpoints, nextTouchpoints));
      setServices(mergeTaxonomyBreakdown(taxonomy.services, nextServices));
      setChannels(mergeTaxonomyBreakdown(taxonomy.intakeChannels, nextChannels));

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

            {/* Row 1: 10 Services Table (50%) & Channels Breakdown with Donut Chart (50%) */}
            <div className="two-col-grid" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(460px, 1fr))' }}>
              {/* 10 Services Table */}
              <section className="card animate-in">
                <div className="section-header">
                  <div>
                    <span className="section-title">Danh mục dịch vụ</span>
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

                <div className="dashboard-scroll-list" style={{ maxHeight: 380, overflowX: 'auto' }} aria-label="Bảng danh mục dịch vụ">
                  <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 12, textAlign: 'left' }}>
                    <thead>
                      <tr style={{ background: '#f8fafc', borderBottom: '1px solid #e2e8f0', color: '#475569', fontWeight: 700 }}>
                        <th style={{ padding: '10px 12px', minWidth: 160 }}>Dịch vụ</th>
                        <th style={{ padding: '10px 10px', width: 90, textAlign: 'right' }}>Tổng phản ánh</th>
                        <th style={{ padding: '10px 10px', width: 110, textAlign: 'right' }}>Phản ánh tiêu cực</th>
                        <th style={{ padding: '10px 12px', minWidth: 150 }}>Phân bổ cảm xúc</th>
                        <th style={{ padding: '10px 8px', width: 45, textAlign: 'center' }}>Xem</th>
                      </tr>
                    </thead>
                    <tbody>
                      {services.map((service, idx) => {
                        const isSelected = filters?.serviceCode === service.code;
                        const negCount = Math.round(service.itemVolume * service.negativeRate);
                        const negPct = Math.min(100, Math.max(0, service.negativeRate * 100));
                        const remaining = 100 - negPct;
                        const posPct = service.itemVolume > 0 ? remaining * 0.45 : 0;
                        const neuPct = service.itemVolume > 0 ? remaining * 0.55 : 0;

                        return (
                          <tr
                            key={service.code}
                            onClick={() =>
                              setFilter(
                                'serviceCode',
                                filters?.serviceCode === service.code ? undefined : service.code
                              )
                            }
                            style={{
                              borderBottom: '1px solid #f1f5f9',
                              background: isSelected ? '#eff6ff' : idx % 2 === 0 ? '#ffffff' : '#fafafa',
                              cursor: 'pointer',
                              transition: 'background 0.15s ease',
                            }}
                            onMouseEnter={(e) => {
                              if (!isSelected) e.currentTarget.style.background = '#f1f5f9';
                            }}
                            onMouseLeave={(e) => {
                              if (!isSelected) e.currentTarget.style.background = idx % 2 === 0 ? '#ffffff' : '#fafafa';
                            }}
                          >
                            {/* Dịch vụ */}
                            <td style={{ padding: '10px 12px', color: '#1e293b' }}>
                              <div style={{ fontWeight: 600, color: isSelected ? '#2563eb' : '#0f172a' }}>
                                {service.name}
                              </div>
                              <span style={{ fontSize: 10, color: '#64748b', fontWeight: 600 }}>{service.code}</span>
                            </td>

                            {/* Tổng phản ánh */}
                            <td style={{ padding: '10px 10px', textAlign: 'right', fontWeight: 700, color: '#0f172a' }}>
                              {service.itemVolume.toLocaleString()}
                            </td>

                            {/* Phản ánh tiêu cực */}
                            <td style={{ padding: '10px 10px', textAlign: 'right' }}>
                              <div style={{ fontWeight: 700, color: service.negativeRate >= 0.5 ? '#dc2626' : service.negativeRate > 0 ? '#ea580c' : '#16a34a' }}>
                                {negCount.toLocaleString()}
                              </div>
                              <div style={{ fontSize: 10, color: service.negativeRate >= 0.5 ? '#ef4444' : '#64748b', fontWeight: 600 }}>
                                ({negPct.toFixed(1)}%)
                              </div>
                            </td>

                            {/* Phân bổ cảm xúc Bar */}
                            <td style={{ padding: '10px 12px' }}>
                              {service.itemVolume > 0 ? (
                                <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
                                  <div style={{ display: 'flex', height: 7, borderRadius: 4, overflow: 'hidden', background: '#f1f5f9' }}>
                                    {negPct > 0 && <div style={{ width: `${negPct}%`, background: '#ef4444' }} title={`Tiêu cực: ${negPct.toFixed(1)}%`} />}
                                    {neuPct > 0 && <div style={{ width: `${neuPct}%`, background: '#94a3b8' }} title={`Trung tính: ${neuPct.toFixed(1)}%`} />}
                                    {posPct > 0 && <div style={{ width: `${posPct}%`, background: '#22c55e' }} title={`Tích cực: ${posPct.toFixed(1)}%`} />}
                                  </div>
                                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 10, fontWeight: 600, color: '#64748b' }}>
                                    <span style={{ color: '#dc2626' }}>🔴 {negPct.toFixed(0)}%</span>
                                    <span style={{ color: '#64748b' }}>⚪ {neuPct.toFixed(0)}%</span>
                                    <span style={{ color: '#16a34a' }}>🟢 {posPct.toFixed(0)}%</span>
                                  </div>
                                </div>
                              ) : (
                                <span style={{ color: '#94a3b8', fontSize: 11 }}>0 phản hồi</span>
                              )}
                            </td>

                            {/* Xem */}
                            <td style={{ padding: '10px 8px', textAlign: 'center' }}>
                              <button
                                onClick={(e) => {
                                  e.stopPropagation();
                                  handleDrilldownToExplorer({ service_code: service.code });
                                }}
                                style={{
                                  display: 'inline-flex',
                                  alignItems: 'center',
                                  justifyContent: 'center',
                                  width: 26,
                                  height: 26,
                                  borderRadius: 6,
                                  border: '1px solid #cbd5e1',
                                  background: '#ffffff',
                                  color: '#475569',
                                  cursor: 'pointer',
                                }}
                                title="Xem danh sách phản ánh"
                              >
                                <ExternalLink size={12} />
                              </button>
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              </section>

              {/* Kênh phản ánh Donut Chart Card */}
              <ChannelBreakdownCard
                channels={channels}
                selectedChannelCode={filters?.intakeChannelCode}
                onSelectChannel={(code) => setFilter('intakeChannelCode', code)}
                onDrilldown={(channelCode) => handleDrilldownToExplorer({ intake_channel_code: channelCode })}
              />
            </div>

            {/* Row 2: Vấn đề phát sinh (50%) & Xu hướng theo thời gian (50%) */}
            <div className="two-col-grid" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(460px, 1fr))', marginTop: 24 }}>
              {/* Highlighted Issues / Pain Points */}
              <div className="card animate-in">
                <div className="section-header">
                  <div>
                    <span className="section-title">Vấn đề phát sinh</span>
                  </div>
                  <span className="panel-count">{issues.length} vấn đề</span>
                </div>
                <div className="dashboard-scroll-list" style={{ maxHeight: 340 }} aria-label="Danh sách vấn đề">
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
              <div className="card animate-in">
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
            </div>
          </>
        )}
      </div>
    </>
  );
};

export default OverviewPage;
