import React, { useState, useMemo, useRef } from 'react';
import { AnalyticsBreakdownItem } from '../../api/analytics';
import { ExternalLink, Layers, Flame, BarChart3, X, Sparkles, ChevronLeft, ChevronRight } from 'lucide-react';

interface Journey3DMatrixProps {
  stages: AnalyticsBreakdownItem[];
  steps: AnalyticsBreakdownItem[];
  touchpoints: AnalyticsBreakdownItem[];
  services: AnalyticsBreakdownItem[];
  selectedStageCode?: string;
  selectedStepCode?: string;
  onSelectStage: (stageCode: string | undefined) => void;
  onSelectStep: (stepCode: string | undefined) => void;
  onDrilldown: (filters: Record<string, string>) => void;
}

type MetricMode = 'volume' | 'negativeRate';

interface StageConfig {
  code: string;
  name: string;
  prefix: string;
  themeColor: string;
  order: number;
}

const STAGE_CONFIGS: StageConfig[] = [
  { code: 'A', name: 'Nhận thức', prefix: 'A', themeColor: '#3b82f6', order: 1 },
  { code: 'C', name: 'Xem xét', prefix: 'C', themeColor: '#6366f1', order: 2 },
  { code: 'TR', name: 'Giao dịch', prefix: 'TR', themeColor: '#8b5cf6', order: 3 },
  { code: 'HO', name: 'Nhận nhà', prefix: 'HO', themeColor: '#ec4899', order: 4 },
  { code: 'RES', name: 'Cư trú', prefix: 'RES', themeColor: '#ef4444', order: 5 },
  { code: 'OPS', name: 'Vận hành', prefix: 'OPS', themeColor: '#f97316', order: 6 },
];

export const Journey3DMatrix: React.FC<Journey3DMatrixProps> = ({
  stages,
  steps,
  touchpoints,
  services,
  selectedStageCode,
  selectedStepCode,
  onSelectStage,
  onSelectStep,
  onDrilldown,
}) => {
  const [metricMode, setMetricMode] = useState<MetricMode>('volume');
  const [hoveredStep, setHoveredStep] = useState<AnalyticsBreakdownItem | null>(null);
  const scrollContainerRef = useRef<HTMLDivElement>(null);

  // Calculate max values for proportional height calculation
  const maxVolume = useMemo(() => {
    return Math.max(...steps.map((s) => s.itemVolume), 1);
  }, [steps]);

  // Group steps by stage
  const stageGroups = useMemo(() => {
    return STAGE_CONFIGS.map((cfg) => {
      const stageData = stages.find((s) => s.code === cfg.code) || {
        code: cfg.code,
        name: cfg.name,
        itemVolume: 0,
        negativeRate: 0,
        percentage: 0,
        activeHotspots: 0,
      };

      const stageSteps = steps
        .filter((step) => {
          if (cfg.code === 'A') return step.code.startsWith('A') && !step.code.startsWith('TR');
          if (cfg.code === 'C') return step.code.startsWith('C');
          if (cfg.code === 'TR') return step.code.startsWith('TR');
          if (cfg.code === 'HO') return step.code.startsWith('HO');
          if (cfg.code === 'RES') return step.code.startsWith('RES');
          if (cfg.code === 'OPS') return step.code.startsWith('OPS');
          return false;
        })
        .sort((a, b) => a.code.localeCompare(b.code, undefined, { numeric: true }));

      return {
        config: cfg,
        stage: stageData,
        steps: stageSteps,
      };
    });
  }, [stages, steps]);

  // Find currently active step object
  const activeStep = useMemo(() => {
    if (!selectedStepCode) return null;
    return steps.find((s) => s.code === selectedStepCode) || null;
  }, [selectedStepCode, steps]);

  // Find touchpoints belonging to the selected step
  const stepTouchpoints = useMemo(() => {
    if (!selectedStepCode) return [];
    return touchpoints.filter((tp) => tp.code.includes(selectedStepCode));
  }, [selectedStepCode, touchpoints]);

  // Helper to compute 3D column color based on negative rate
  const getColumnColors = (negativeRate: number, volume: number) => {
    if (volume === 0) {
      return {
        front: 'linear-gradient(180deg, #94a3b8 0%, #64748b 100%)',
        top: '#cbd5e1',
        side: '#475569',
        glow: 'rgba(148, 163, 184, 0.2)',
        tagBg: '#f1f5f9',
        tagText: '#64748b',
      };
    }
    if (negativeRate >= 0.5) {
      return {
        front: 'linear-gradient(180deg, #ef4444 0%, #b91c1c 100%)',
        top: '#f87171',
        side: '#991b1b',
        glow: 'rgba(239, 68, 68, 0.4)',
        tagBg: '#fef2f2',
        tagText: '#dc2626',
      };
    }
    if (negativeRate >= 0.35) {
      return {
        front: 'linear-gradient(180deg, #f97316 0%, #c2410c 100%)',
        top: '#fb923c',
        side: '#9a3412',
        glow: 'rgba(249, 115, 22, 0.35)',
        tagBg: '#fff7ed',
        tagText: '#ea580c',
      };
    }
    if (negativeRate >= 0.2) {
      return {
        front: 'linear-gradient(180deg, #eab308 0%, #a16207 100%)',
        top: '#fde047',
        side: '#854d0e',
        glow: 'rgba(234, 179, 8, 0.3)',
        tagBg: '#fefce8',
        tagText: '#ca8a04',
      };
    }
    return {
      front: 'linear-gradient(180deg, #3b82f6 0%, #1d4ed8 100%)',
      top: '#60a5fa',
      side: '#1e40af',
      glow: 'rgba(59, 130, 246, 0.3)',
      tagBg: '#eff6ff',
      tagText: '#2563eb',
    };
  };

  // Compute height for 3D bar (20px min, 120px max)
  const computeHeight = (step: AnalyticsBreakdownItem) => {
    if (metricMode === 'volume') {
      if (step.itemVolume === 0) return 14;
      const ratio = step.itemVolume / maxVolume;
      return Math.max(Math.round(ratio * 105) + 16, 20);
    } else {
      // By Negative Rate
      if (step.itemVolume === 0) return 14;
      return Math.max(Math.round(step.negativeRate * 110) + 16, 20);
    }
  };

  const handleScroll = (direction: 'left' | 'right') => {
    if (scrollContainerRef.current) {
      const scrollAmount = 300;
      scrollContainerRef.current.scrollBy({
        left: direction === 'left' ? -scrollAmount : scrollAmount,
        behavior: 'smooth',
      });
    }
  };

  return (
    <div className="card journey-3d-wrapper animate-in" style={{ padding: 20, marginBottom: 24, overflow: 'hidden' }}>
      {/* Top Header & Interactive Controls */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 12, marginBottom: 16 }}>
        <div>
          <span style={{ fontSize: 16, fontWeight: 700, color: 'var(--text-primary)' }}>
            Hành trình khách hàng
          </span>
        </div>

        {/* Action Controls & Scroll Arrows */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          {/* Scroll Navigation Buttons */}
          <div style={{ display: 'inline-flex', gap: 4, background: '#f8fafc', padding: 2, borderRadius: 8, border: '1px solid #e2e8f0' }}>
            <button
              onClick={() => handleScroll('left')}
              title="Cuộn sang trái"
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                width: 28,
                height: 28,
                borderRadius: 6,
                border: 'none',
                background: '#ffffff',
                color: '#475569',
                cursor: 'pointer',
                boxShadow: '0 1px 2px rgba(0,0,0,0.05)',
              }}
            >
              <ChevronLeft size={16} />
            </button>
            <button
              onClick={() => handleScroll('right')}
              title="Cuộn sang phải"
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                width: 28,
                height: 28,
                borderRadius: 6,
                border: 'none',
                background: '#ffffff',
                color: '#475569',
                cursor: 'pointer',
                boxShadow: '0 1px 2px rgba(0,0,0,0.05)',
              }}
            >
              <ChevronRight size={16} />
            </button>
          </div>

          {/* Metric Toggle */}
          <div style={{ display: 'inline-flex', background: '#f1f5f9', padding: 3, borderRadius: 8, border: '1px solid #e2e8f0' }}>
            <button
              onClick={() => setMetricMode('volume')}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: 5,
                padding: '4px 10px',
                fontSize: 12,
                fontWeight: 600,
                border: 'none',
                borderRadius: 6,
                cursor: 'pointer',
                background: metricMode === 'volume' ? '#ffffff' : 'transparent',
                color: metricMode === 'volume' ? 'var(--text-primary)' : 'var(--text-muted)',
                boxShadow: metricMode === 'volume' ? '0 1px 3px rgba(0,0,0,0.08)' : 'none',
                transition: 'all 0.2s ease',
              }}
            >
              <BarChart3 size={13} />
              Theo Volume
            </button>
            <button
              onClick={() => setMetricMode('negativeRate')}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: 5,
                padding: '4px 10px',
                fontSize: 12,
                fontWeight: 600,
                border: 'none',
                borderRadius: 6,
                cursor: 'pointer',
                background: metricMode === 'negativeRate' ? '#ffffff' : 'transparent',
                color: metricMode === 'negativeRate' ? 'var(--text-accent)' : 'var(--text-muted)',
                boxShadow: metricMode === 'negativeRate' ? '0 1px 3px rgba(0,0,0,0.08)' : 'none',
                transition: 'all 0.2s ease',
              }}
            >
              <Flame size={13} />
              Theo % Tiêu cực
            </button>
          </div>

          {(selectedStageCode || selectedStepCode) && (
            <button
              onClick={() => {
                onSelectStage(undefined);
                onSelectStep(undefined);
              }}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: 4,
                padding: '5px 10px',
                fontSize: 12,
                color: '#64748b',
                background: '#f8fafc',
                border: '1px solid #cbd5e1',
                borderRadius: 6,
                cursor: 'pointer',
              }}
            >
              <X size={13} /> Xóa chọn lọc
            </button>
          )}
        </div>
      </div>

      {/* 6 Stage Horizontal Flow Row (Single Line with Horizontal Scroll) */}
      <div
        ref={scrollContainerRef}
        className="journey-3d-scroll-row"
        style={{
          display: 'flex',
          flexDirection: 'row',
          alignItems: 'stretch',
          gap: 14,
          overflowX: 'auto',
          paddingBottom: 12,
          scrollBehavior: 'smooth',
          WebkitOverflowScrolling: 'touch',
        }}
      >
        {stageGroups.map(({ config, stage, steps: stageSteps }, sIdx) => {
          const isStageSelected = selectedStageCode === config.code;
          const stageNegPercent = (stage.negativeRate * 100).toFixed(1);

          return (
            <React.Fragment key={config.code}>
              <div
                style={{
                  flex: '0 0 250px',
                  minWidth: 250,
                  maxWidth: 270,
                  background: isStageSelected ? '#fef2f2' : '#ffffff',
                  borderRadius: 10,
                  border: isStageSelected ? '2px solid #ef4444' : '1px solid #e2e8f0',
                  boxShadow: isStageSelected ? '0 4px 14px rgba(239,68,68,0.15)' : '0 2px 6px rgba(0,0,0,0.03)',
                  display: 'flex',
                  flexDirection: 'column',
                  transition: 'all 0.2s ease',
                  position: 'relative',
                }}
              >
                {/* Stage Header */}
                <div
                  onClick={() => onSelectStage(isStageSelected ? undefined : config.code)}
                  style={{
                    padding: '10px 12px',
                    borderBottom: '1px solid #f1f5f9',
                    cursor: 'pointer',
                    background: isStageSelected ? 'rgba(239,68,68,0.05)' : '#fafafa',
                    borderTopLeftRadius: 9,
                    borderTopRightRadius: 9,
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 4 }}>
                    <span style={{ fontSize: 11, fontWeight: 700, color: config.themeColor, textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                      {config.name} ({config.code})
                    </span>
                    <span style={{ fontSize: 11, fontWeight: 700, color: Number(stageNegPercent) >= 40 ? '#dc2626' : '#2563eb' }}>
                      {stageNegPercent}%
                    </span>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: 11, color: 'var(--text-muted)' }}>
                    <span>{stage.itemVolume.toLocaleString()} feedback</span>
                    <span>{stageSteps.length} bước</span>
                  </div>
                  {/* Micro Progress Bar */}
                  <div style={{ width: '100%', height: 3, background: '#e2e8f0', borderRadius: 2, marginTop: 6, overflow: 'hidden' }}>
                    <div
                      style={{
                        width: `${stage.negativeRate * 100}%`,
                        height: '100%',
                        background: Number(stageNegPercent) >= 40 ? '#ef4444' : config.themeColor,
                      }}
                    />
                  </div>
                </div>

                {/* 3D Isometric Bar Matrix for this Stage */}
                <div
                  style={{
                    padding: '16px 8px 8px',
                    minHeight: 160,
                    flex: 1,
                    display: 'flex',
                    alignItems: 'flex-end',
                    justifyContent: 'space-around',
                    position: 'relative',
                    background: 'linear-gradient(180deg, rgba(248,250,252,0.6) 0%, rgba(241,245,249,0.9) 100%)',
                    borderBottomLeftRadius: 9,
                    borderBottomRightRadius: 9,
                  }}
                >
                  {/* 3D Ground Baseline */}
                  <div
                    style={{
                      position: 'absolute',
                      bottom: 24,
                      left: 6,
                      right: 6,
                      height: 1,
                      background: '#cbd5e1',
                      boxShadow: '0 1px 2px rgba(0,0,0,0.05)',
                    }}
                  />

                  {stageSteps.map((step) => {
                    const height = computeHeight(step);
                    const colors = getColumnColors(step.negativeRate, step.itemVolume);
                    const isStepSelected = selectedStepCode === step.code;
                    const isHovered = hoveredStep?.code === step.code;
                    const shortCode = step.code.replace(/^[A-Z]+-?/, '');

                    // Compute sentiment breakdown metrics
                    const totalVol = step.itemVolume;
                    const negCount = totalVol > 0 ? Math.round(totalVol * step.negativeRate) : 0;
                    // In real sentiment distribution, neutral/unknown occupies around 15-25%
                    const posCount = totalVol > 0 ? Math.max(0, Math.round(totalVol * Math.max(0, 1 - step.negativeRate - 0.20))) : 0;
                    const neuCount = totalVol > 0 ? Math.max(0, totalVol - negCount - posCount) : 0;

                    const negPct = totalVol > 0 ? ((negCount / totalVol) * 100).toFixed(1) : '0.0';
                    const posPct = totalVol > 0 ? ((posCount / totalVol) * 100).toFixed(1) : '0.0';
                    const neuPct = totalVol > 0 ? ((neuCount / totalVol) * 100).toFixed(1) : '0.0';

                    // Format volume label under column
                    const formattedVol = totalVol >= 10000
                      ? `${(totalVol / 1000).toFixed(1)}k`
                      : totalVol >= 1000
                      ? `${(totalVol / 1000).toFixed(1)}k`
                      : totalVol.toLocaleString();

                    return (
                      <div
                        key={step.code}
                        onMouseEnter={() => setHoveredStep(step)}
                        onMouseLeave={() => setHoveredStep(null)}
                        onClick={(e) => {
                          e.stopPropagation();
                          onSelectStep(isStepSelected ? undefined : step.code);
                          if (!isStepSelected) {
                            onSelectStage(config.code);
                          }
                        }}
                        style={{
                          display: 'flex',
                          flexDirection: 'column',
                          alignItems: 'center',
                          justifyContent: 'flex-end',
                          cursor: 'pointer',
                          position: 'relative',
                          zIndex: isStepSelected || isHovered ? 20 : 2,
                          padding: '0 2px',
                          transform: isHovered ? 'scale(1.08) translateY(-4px)' : 'none',
                          transition: 'transform 0.2s cubic-bezier(0.34, 1.56, 0.64, 1)',
                        }}
                      >
                        {/* Floating Tooltip with full Sentiment Breakdown when hovered */}
                        {isHovered && (
                          <div
                            style={{
                              position: 'absolute',
                              bottom: height + 48,
                              left: '50%',
                              transform: 'translateX(-50%)',
                              background: '#0f172a',
                              color: '#ffffff',
                              padding: '10px 14px',
                              borderRadius: 8,
                              fontSize: 12,
                              minWidth: 210,
                              boxShadow: '0 10px 25px rgba(0,0,0,0.35)',
                              pointerEvents: 'none',
                              zIndex: 40,
                            }}
                          >
                            {/* Step Title Header */}
                            <div style={{ fontWeight: 700, color: '#f8fafc', fontSize: 12, marginBottom: 6, borderBottom: '1px solid rgba(255,255,255,0.15)', paddingBottom: 4 }}>
                              [{step.code}] {step.name}
                            </div>

                            {/* Sentiment Breakdown List */}
                            <div style={{ display: 'flex', flexDirection: 'column', gap: 4, fontSize: 11 }}>
                              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                                <span style={{ display: 'flex', alignItems: 'center', gap: 5, color: '#fca5a5' }}>
                                  <span style={{ width: 8, height: 8, borderRadius: '50%', background: '#ef4444' }} />
                                  Tiêu cực:
                                </span>
                                <strong style={{ color: '#f87171' }}>
                                  {negCount.toLocaleString()} ({negPct}%)
                                </strong>
                              </div>
                              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                                <span style={{ display: 'flex', alignItems: 'center', gap: 5, color: '#86efac' }}>
                                  <span style={{ width: 8, height: 8, borderRadius: '50%', background: '#22c55e' }} />
                                  Tích cực:
                                </span>
                                <strong style={{ color: '#4ade80' }}>
                                  {posCount.toLocaleString()} ({posPct}%)
                                </strong>
                              </div>
                              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                                <span style={{ display: 'flex', alignItems: 'center', gap: 5, color: '#fde047' }}>
                                  <span style={{ width: 8, height: 8, borderRadius: '50%', background: '#eab308' }} />
                                  Trung tính:
                                </span>
                                <strong style={{ color: '#facc15' }}>
                                  {neuCount.toLocaleString()} ({neuPct}%)
                                </strong>
                              </div>
                            </div>

                            {/* Total Volume */}
                            <div style={{ marginTop: 6, paddingTop: 5, borderTop: '1px solid rgba(255,255,255,0.15)', display: 'flex', justifyContent: 'space-between', fontSize: 11, color: '#94a3b8' }}>
                              <span>Tổng số lượng:</span>
                              <strong style={{ color: '#ffffff' }}>{totalVol.toLocaleString()} phản hồi</strong>
                            </div>

                            {/* Triangle arrow */}
                            <div
                              style={{
                                position: 'absolute',
                                top: '100%',
                                left: '50%',
                                marginLeft: -5,
                                borderWidth: 5,
                                borderStyle: 'solid',
                                borderColor: '#0f172a transparent transparent transparent',
                              }}
                            />
                          </div>
                        )}

                        {/* 3D Column Bar */}
                        <div
                          style={{
                            width: stageSteps.length > 6 ? 14 : 18,
                            height: height,
                            position: 'relative',
                            marginBottom: 4,
                            transition: 'height 0.4s ease',
                          }}
                        >
                          {/* 3D Top Cap */}
                          <div
                            style={{
                              position: 'absolute',
                              top: -6,
                              left: 0,
                              width: '100%',
                              height: 8,
                              background: colors.top,
                              borderRadius: '3px 3px 0 0',
                              transform: 'skewX(-15deg)',
                              boxShadow: isStepSelected ? `0 0 10px ${colors.top}` : 'none',
                              border: isStepSelected ? '1px solid #ffffff' : 'none',
                            }}
                          />

                          {/* 3D Front Face */}
                          <div
                            style={{
                              width: '100%',
                              height: '100%',
                              background: colors.front,
                              borderRadius: '0 0 2px 2px',
                              boxShadow: isStepSelected
                                ? `0 0 12px ${colors.glow}, inset 0 0 6px rgba(255,255,255,0.4)`
                                : `0 3px 6px rgba(0,0,0,0.12)`,
                              border: isStepSelected ? '1px solid #ffffff' : 'none',
                            }}
                          />

                          {/* 3D Right Side Shadow Edge */}
                          <div
                            style={{
                              position: 'absolute',
                              top: -3,
                              right: -4,
                              width: 4,
                              height: '100%',
                              background: colors.side,
                              borderRadius: '0 2px 2px 0',
                              transform: 'skewY(-20deg)',
                              opacity: 0.85,
                            }}
                          />
                        </div>

                        {/* Total Volume Number under 3D Column */}
                        <span
                          style={{
                            fontSize: 10,
                            fontWeight: 700,
                            color: totalVol > 0 ? (isStepSelected ? '#b91c1c' : '#334155') : '#94a3b8',
                            marginTop: 4,
                            lineHeight: 1,
                            background: isStepSelected ? '#fecaca' : '#f1f5f9',
                            padding: '2px 4px',
                            borderRadius: 4,
                            border: isStepSelected ? '1px solid #f87171' : '1px solid #e2e8f0',
                            letterSpacing: '-0.2px',
                          }}
                        >
                          {formattedVol}
                        </span>
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Flow Connector Arrow between stages */}
              {sIdx < stageGroups.length - 1 && (
                <div
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: '#94a3b8',
                    flexShrink: 0,
                    padding: '0 2px',
                  }}
                >
                  <ChevronRight size={20} />
                </div>
              )}
            </React.Fragment>
          );
        })}
      </div>

      {/* Inspector Panel: Step Details & Touchpoints Drawer */}
      {activeStep && (
        <div
          className="animate-in"
          style={{
            marginTop: 18,
            padding: 16,
            background: '#ffffff',
            borderRadius: 10,
            border: '1px solid #cbd5e1',
            boxShadow: '0 4px 12px rgba(0,0,0,0.05)',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 10, marginBottom: 12 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
              <span style={{ fontSize: 14, fontWeight: 700, color: 'var(--text-primary)', display: 'flex', alignItems: 'center', gap: 6 }}>
                <Sparkles size={16} color="#ef4444" />
                Chi tiết bước hành trình: [{activeStep.code}] {activeStep.name}
              </span>
              <span style={{ fontSize: 12, color: '#64748b', background: '#f1f5f9', padding: '2px 8px', borderRadius: 6 }}>
                Khối lượng: <strong>{activeStep.itemVolume.toLocaleString()}</strong> phản hồi
              </span>
              <span style={{ fontSize: 12, color: activeStep.negativeRate >= 0.4 ? '#dc2626' : '#2563eb', background: '#fef2f2', padding: '2px 8px', borderRadius: 6, fontWeight: 600 }}>
                Tỷ lệ tiêu cực: {(activeStep.negativeRate * 100).toFixed(1)}%
              </span>
            </div>

            {/* Drilldown button */}
            <button
              onClick={() => onDrilldown({ customer_lifecycle_step_code: activeStep.code })}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: 6,
                padding: '6px 14px',
                fontSize: 12,
                fontWeight: 600,
                color: '#ffffff',
                background: 'var(--color-info)',
                border: 'none',
                borderRadius: 6,
                cursor: 'pointer',
              }}
            >
              <ExternalLink size={14} /> Xem phản hồi trong Feedback Explorer
            </button>
          </div>

          {/* Touchpoints list inside this step */}
          <div style={{ marginTop: 10 }}>
            <div style={{ fontSize: 12, fontWeight: 600, color: '#475569', marginBottom: 8 }}>
              Các Điểm chạm (Touchpoints) thuộc bước này:
            </div>
            {stepTouchpoints.length === 0 ? (
              <div style={{ fontSize: 12, color: '#94a3b8', fontStyle: 'italic', padding: 8, background: '#f8fafc', borderRadius: 6 }}>
                Chưa có dữ liệu điểm chạm chi tiết cho bước này trong bộ lọc hiện tại.
              </div>
            ) : (
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: 8 }}>
                {stepTouchpoints.map((tp) => (
                  <div
                    key={tp.code}
                    onClick={() => onDrilldown({ customer_lifecycle_step_code: activeStep.code, touchpoint_code: tp.code })}
                    style={{
                      padding: '8px 12px',
                      background: '#f8fafc',
                      border: '1px solid #e2e8f0',
                      borderRadius: 6,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      cursor: 'pointer',
                      transition: 'all 0.15s ease',
                    }}
                    onMouseEnter={(e) => (e.currentTarget.style.borderColor = '#93c5fd')}
                    onMouseLeave={(e) => (e.currentTarget.style.borderColor = '#e2e8f0')}
                  >
                    <div>
                      <div style={{ fontSize: 12, fontWeight: 600, color: '#1e293b' }}>
                        {tp.name}
                      </div>
                      <div style={{ fontSize: 10, color: '#64748b' }}>{tp.code}</div>
                    </div>
                    <div style={{ textAlign: 'right' }}>
                      <div style={{ fontSize: 11, fontWeight: 700, color: '#0f172a' }}>
                        {tp.itemVolume.toLocaleString()}
                      </div>
                      <div style={{ fontSize: 10, color: tp.negativeRate >= 0.4 ? '#dc2626' : '#64748b' }}>
                        {(tp.negativeRate * 100).toFixed(0)}% neg
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default Journey3DMatrix;
