import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import TopBar from '../components/layout/TopBar';
import {
  mockJourneyStages,
  mockStageSteps,
  JourneyStage,
  JourneyStep,
} from '../mock/analyticsData';

const negColor = (rate: number) => {
  if (rate >= 40) return 'var(--color-negative)';
  if (rate >= 25) return 'var(--color-warning)';
  return 'var(--color-positive)';
};

const CustomerJourneyPage: React.FC = () => {
  const navigate = useNavigate();
  const [selectedStage, setSelectedStage] = useState<JourneyStage>(mockJourneyStages[4]);
  
  const currentSteps = mockStageSteps[selectedStage.code] || [];
  const [selectedStep, setSelectedStep] = useState<JourneyStep | null>(currentSteps[0] || null);

  const handleStageSelect = (stage: JourneyStage) => {
    setSelectedStage(stage);
    const steps = mockStageSteps[stage.code] || [];
    setSelectedStep(steps[0] || null);
  };

  return (
    <>
      <TopBar title="Customer Journey" subtitle="Khách hàng đang gặp khó khăn ở đâu?" />

      <div className="page-content">
        {/* Filter Bar */}
        <div className="filter-bar">
          <span style={{ fontSize: 11, color: 'var(--text-muted)', marginRight: 4 }}>Lọc:</span>
          {['Kênh ▾', 'Vị trí ▾', 'Thời gian ▾'].map(f => (
            <button key={f} className="filter-chip">{f}</button>
          ))}
        </div>

        {/* Stage Selector */}
        <div className="section-header">
          <span className="section-title">Vòng đời khách hàng</span>
        </div>

        <div className="journey-stages animate-in" style={{ marginBottom: 24 }}>
          {mockJourneyStages.map((stage) => (
            <div
              key={stage.code}
              className={`journey-stage-item${selectedStage.code === stage.code ? ' active' : ''}`}
              onClick={() => handleStageSelect(stage)}
            >
              <div className="journey-stage-name">{stage.name}</div>
              <div className="journey-stage-neg" style={{ color: negColor(stage.negativeRate) }}>
                {stage.negativeRate}%
              </div>
              <div className="journey-stage-vol">{stage.feedbackCount.toLocaleString()} phản hồi</div>
              <div className="neg-bar-bg" style={{ marginTop: 8 }}>
                <div className="neg-bar-fill" style={{
                  width: `${stage.negativeRate}%`,
                  background: negColor(stage.negativeRate),
                  opacity: 0.7,
                }} />
              </div>
            </div>
          ))}
        </div>

        {/* Selected Stage Step Grid */}
        <div className="card animate-in" style={{ marginBottom: 20 }}>
          <div className="section-header">
            <span className="section-title">
              Các bước trong giai đoạn:{' '}
              <span style={{ color: 'var(--text-accent)', textTransform: 'none', letterSpacing: 0 }}>
                {selectedStage.name}
              </span>
            </span>
          </div>

          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(4, 1fr)',
            gap: 12,
          }}>
            {currentSteps.map((step) => (
              <div
                key={step.code}
                onClick={() => setSelectedStep(step)}
                style={{
                  background: selectedStep?.code === step.code
                    ? 'rgba(220,38,38,0.04)' : 'var(--bg-elevated)',
                  border: `1px solid ${selectedStep?.code === step.code
                    ? 'var(--border-active)' : 'var(--border-subtle)'}`,
                  borderRadius: 'var(--radius-md)',
                  padding: '14px 16px',
                  cursor: 'pointer',
                  transition: 'all 0.15s',
                }}
              >
                <div style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-primary)', marginBottom: 8 }}>
                  {step.name}
                </div>
                <div style={{ fontSize: 22, fontWeight: 800, color: negColor(step.negativeRate), lineHeight: 1 }}>
                  {step.negativeRate}%
                </div>
                <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 2 }}>
                  {step.feedbackCount.toLocaleString()} phản hồi
                </div>
                <div className="neg-bar-bg" style={{ marginTop: 8 }}>
                  <div className="neg-bar-fill" style={{
                    width: `${step.negativeRate}%`,
                    background: negColor(step.negativeRate),
                    opacity: 0.7,
                  }} />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Step Detail Panel */}
        {selectedStep && (
          <div className="two-col-grid animate-in">
            <div className="card">
              <div className="section-header">
                <span className="section-title">
                  Dịch vụ liên quan — {selectedStep.name}
                </span>
              </div>
              {[
                { name: 'Tiếp cận & Di chuyển', pct: 51 },
                { name: 'Kỹ thuật & Tài sản', pct: 31 },
                { name: 'An ninh', pct: 12 },
                { name: 'Dịch vụ khác', pct: 6 },
              ].map(sv => (
                <div key={sv.name} style={{ marginBottom: 14 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
                    <span style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-primary)' }}>
                      {sv.name}
                    </span>
                    <span style={{ fontSize: 12, fontWeight: 700, color: 'var(--text-primary)' }}>
                      {sv.pct}%
                    </span>
                  </div>
                  <div className="neg-bar-bg">
                    <div className="neg-bar-fill" style={{
                      width: `${sv.pct}%`,
                      background: 'var(--text-accent)',
                      opacity: 0.7,
                    }} />
                  </div>
                </div>
              ))}
              <button
                className="section-action"
                style={{ marginTop: 8 }}
                onClick={() => navigate('/service-pain-points')}
              >
                Xem chi tiết dịch vụ & vấn đề →
              </button>
            </div>

            <div className="card">
              <div className="section-header">
                <span className="section-title">Thống kê nhanh</span>
              </div>
              {[
                { label: 'Tổng phản hồi', value: selectedStep.feedbackCount.toLocaleString(), color: 'var(--text-primary)' },
                { label: 'Tỷ lệ tiêu cực', value: `${selectedStep.negativeRate}%`, color: negColor(selectedStep.negativeRate) },
                { label: 'Tỷ lệ tích cực', value: `${100 - selectedStep.negativeRate - 10}%`, color: 'var(--color-positive)' },
                { label: 'Hotspot đang mở', value: selectedStep.negativeRate > 40 ? '2 đang hoạt động' : 'Không có', color: selectedStep.negativeRate > 40 ? 'var(--color-negative)' : 'var(--text-muted)' },
              ].map(stat => (
                <div key={stat.label} style={{
                  display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                  padding: '10px 0', borderBottom: '1px solid var(--border-subtle)',
                }}>
                  <span style={{ fontSize: 12, color: 'var(--text-secondary)' }}>{stat.label}</span>
                  <span style={{ fontSize: 15, fontWeight: 800, color: stat.color }}>{stat.value}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </>
  );
};

export default CustomerJourneyPage;
