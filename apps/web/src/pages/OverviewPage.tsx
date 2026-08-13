import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import TopBar from '../components/layout/TopBar';
import KPICard, { buildKPICards } from '../components/analytics/KPICard';
import TrendChart from '../components/analytics/TrendChart';
import PainPointsList from '../components/analytics/PainPointsList';
import HotspotTable from '../components/analytics/HotspotTable';
import {
  mockKPI,
  mockJourneyStages,
  mockTrend,
  mockPainPoints,
  mockHotspots,
  JourneyStage,
} from '../mock/analyticsData';

// Negative rate → color
const negColor = (rate: number) => {
  if (rate >= 40) return 'var(--color-negative)';
  if (rate >= 25) return 'var(--color-warning)';
  return 'var(--color-positive)';
};

const OverviewPage: React.FC = () => {
  const navigate = useNavigate();
  const [activeStage, setActiveStage] = useState<string>('STG-05');

  const kpiCards = buildKPICards(mockKPI);

  return (
    <>
      <TopBar title="CX Overview" subtitle="Tổng quan trải nghiệm khách hàng" />

      <div className="page-content">
        {/* Filter Bar */}
        <div className="filter-bar">
          <span style={{ fontSize: 11, color: 'var(--text-muted)', marginRight: 4 }}>Lọc:</span>
          {['Hành trình ▾', 'Dịch vụ ▾', 'Vị trí ▾', 'Kênh ▾', 'Mức độ ▾'].map(f => (
            <button key={f} className="filter-chip">{f}</button>
          ))}
          <button className="filter-chip active" style={{ marginLeft: 'auto' }}>
            ✕ Xoá bộ lọc
          </button>
        </div>

        {/* KPI Grid */}
        <div className="kpi-grid">
          {kpiCards.map((card) => (
            <KPICard key={card.type} {...card} />
          ))}
        </div>

        {/* Customer Journey Stages */}
        <div className="section-header">
          <span className="section-title">Customer Journey</span>
          <button className="section-action" onClick={() => navigate('/customer-journey')}>
            Xem chi tiết →
          </button>
        </div>

        <div className="journey-stages animate-in">
          {mockJourneyStages.map((stage: JourneyStage, idx) => (
            <div
              key={stage.code}
              className={`journey-stage-item${activeStage === stage.code ? ' active' : ''}`}
              onClick={() => {
                setActiveStage(stage.code);
                navigate('/customer-journey');
              }}
            >
              <div className="journey-stage-name">{stage.name}</div>
              <div
                className="journey-stage-neg"
                style={{ color: negColor(stage.negativeRate) }}
              >
                {stage.negativeRate}%
              </div>
              <div className="journey-stage-vol">
                {stage.feedbackCount.toLocaleString()} phản hồi
              </div>

              {/* Negative bar */}
              <div className="neg-bar-bg" style={{ marginTop: 8 }}>
                <div
                  className="neg-bar-fill"
                  style={{
                    width: `${stage.negativeRate}%`,
                    background: negColor(stage.negativeRate),
                    opacity: 0.7,
                  }}
                />
              </div>

              {idx < mockJourneyStages.length - 1 && (
                <div className="journey-stage-connector">›</div>
              )}
            </div>
          ))}
        </div>

        {/* Trend + Pain Points */}
        <div className="two-col-grid">
          <div className="card animate-in">
            <div className="section-header">
              <span className="section-title">Experience Trend</span>
              <button className="section-action">Toàn màn hình ↗</button>
            </div>
            <TrendChart data={mockTrend} />
          </div>

          <div className="card animate-in">
            <div className="section-header">
              <span className="section-title">Top Pain Points</span>
              <button
                className="section-action"
                onClick={() => navigate('/service-pain-points')}
              >
                Xem tất cả →
              </button>
            </div>
            <PainPointsList
              data={mockPainPoints.slice(0, 6)}
              onItemClick={() => navigate('/service-pain-points')}
            />
          </div>
        </div>

        {/* Emerging Hotspots */}
        <div className="card animate-in" style={{ marginBottom: 32 }}>
          <div className="section-header">
            <span className="section-title">
              🔥 Emerging Hotspots
              <span style={{
                marginLeft: 8,
                fontSize: 10,
                fontWeight: 700,
                background: 'rgba(248,113,113,0.15)',
                color: 'var(--color-negative)',
                padding: '2px 7px',
                borderRadius: 99,
              }}>
                {mockHotspots.length} active
              </span>
            </span>
            <button
              className="section-action"
              onClick={() => navigate('/hotspot')}
            >
              Điều tra →
            </button>
          </div>
          <HotspotTable
            data={mockHotspots}
            onRowClick={() => navigate('/hotspot')}
          />
        </div>
      </div>
    </>
  );
};

export default OverviewPage;
