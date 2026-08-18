import React, { useRef, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import {
  AlertTriangle,
  ArrowRight,
  CheckCircle2,
  ChevronLeft,
  ChevronRight,
  ExternalLink,
  Flame,
  RefreshCw,
  Sparkles,
} from 'lucide-react';
import {
  HotspotDetailData,
  HotspotItemData,
  detectHotspots,
  getHotspot,
} from '../../api/hotspots';
import { HotspotDetailModal } from './HotspotDetailModal';

interface HotspotActionQueueProps {
  projectId: string;
  hotspots: HotspotItemData[];
  loading: boolean;
  onRefresh: () => void;
}

const PRIORITY_LABELS: Record<string, { label: string; color: string; bg: string; border: string }> = {
  IMMEDIATE: { label: 'Xử lý ngay', color: '#dc2626', bg: '#fef2f2', border: '#fca5a5' },
  URGENT: { label: 'Khẩn cấp', color: '#ea580c', bg: '#fff7ed', border: '#fdba74' },
  PLANNED: { label: 'Theo kế hoạch', color: '#ca8a04', bg: '#fefce8', border: '#fde047' },
  MONITOR: { label: 'Theo dõi', color: '#2563eb', bg: '#eff6ff', border: '#bfdbfe' },
};

const STATUS_LABELS: Record<string, string> = {
  ACTIVE: 'Đang mở',
  ALL: 'Tất cả trạng thái',
  CANDIDATE: 'Mới phát hiện',
  ACKNOWLEDGED: 'Đã ghi nhận',
  INVESTIGATING: 'Đang xử lý',
  RESOLVED: 'Đã giải quyết',
  DISMISSED: 'Đã đóng',
};

export const HotspotActionQueue: React.FC<HotspotActionQueueProps> = ({
  projectId,
  hotspots,
  loading,
  onRefresh,
}) => {
  const navigate = useNavigate();
  const location = useLocation();
  const scrollContainerRef = useRef<HTMLDivElement>(null);
  const [priorityFilter, setPriorityFilter] = useState<string>('ALL');
  const [statusFilter, setStatusFilter] = useState<string>('ACTIVE');
  const [selectedHotspot, setSelectedHotspot] = useState<HotspotDetailData | null>(null);
  const [loadingDetail, setLoadingDetail] = useState(false);
  const [detecting, setDetecting] = useState(false);
  const [detectMessage, setDetectMessage] = useState<string | null>(null);

  const getDrillDownUrl = (h: HotspotItemData) => {
    const next = new URLSearchParams(location.search);
    if (h.service.code) next.set('service_code', h.service.code);
    if (h.issue.code) next.set('issue_code', h.issue.code);
    next.set('hotspot_id', h.hotspot_id);
    return `/feedback?${next.toString()}`;
  };

  const filteredHotspots = hotspots.filter((h) => {
    if (priorityFilter !== 'ALL' && h.action_priority !== priorityFilter) return false;
    if (statusFilter === 'ACTIVE') {
      return h.status === 'CANDIDATE' || h.status === 'ACKNOWLEDGED' || h.status === 'INVESTIGATING';
    }
    if (statusFilter !== 'ALL' && h.status !== statusFilter) return false;
    return true;
  });

  const handleOpenDetail = async (hotspotId: string) => {
    setLoadingDetail(true);
    try {
      const detail = await getHotspot(hotspotId);
      setSelectedHotspot(detail);
    } catch (err) {
      console.error('Failed to load hotspot detail', err);
    } finally {
      setLoadingDetail(false);
    }
  };

  const handleDetect = async () => {
    setDetecting(true);
    setDetectMessage(null);
    try {
      const detected = await detectHotspots({
        project_id: projectId,
        window_days: 180,
        threshold_count: 3,
      });
      setDetectMessage(`Đã quét xong: Phát hiện ${detected.length} điểm nóng theo quy tắc chuẩn.`);
      onRefresh();
    } catch (err) {
      setDetectMessage(err instanceof Error ? err.message : 'Quét thất bại');
    } finally {
      setDetecting(false);
    }
  };

  const scroll = (direction: 'left' | 'right') => {
    if (scrollContainerRef.current) {
      const offset = direction === 'left' ? -340 : 340;
      scrollContainerRef.current.scrollBy({ left: offset, behavior: 'smooth' });
    }
  };

  const priorityCounts = {
    IMMEDIATE: hotspots.filter((h) => h.action_priority === 'IMMEDIATE').length,
    URGENT: hotspots.filter((h) => h.action_priority === 'URGENT').length,
    PLANNED: hotspots.filter((h) => h.action_priority === 'PLANNED').length,
    MONITOR: hotspots.filter((h) => h.action_priority === 'MONITOR').length,
  };

  return (
    <section className="hotspot-queue-container" aria-label="Hàng đợi xử lý điểm nóng" style={{ marginBottom: 24 }}>
      {/* Header */}
      <div className="hotspot-queue-header" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 12 }}>
        <div className="hotspot-queue-title" style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <div className="icon-badge" style={{ width: 32, height: 32, borderRadius: 8, background: '#fee2e2', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <Flame size={18} color="#ef4444" />
          </div>
          <div>
            <h3 style={{ fontSize: 17, fontWeight: 800, margin: 0, color: 'var(--text-primary)' }}>
              Hàng đợi điểm nóng
            </h3>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          {/* Scroll Navigation Arrows */}
          <button
            onClick={() => scroll('left')}
            style={{ width: 30, height: 30, borderRadius: 6, border: '1px solid #cbd5e1', background: '#ffffff', display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer' }}
            title="Cuộn sang trái"
          >
            <ChevronLeft size={16} />
          </button>
          <button
            onClick={() => scroll('right')}
            style={{ width: 30, height: 30, borderRadius: 6, border: '1px solid #cbd5e1', background: '#ffffff', display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer' }}
            title="Cuộn sang phải"
          >
            <ChevronRight size={16} />
          </button>

          <button
            className="btn-secondary scan-btn"
            onClick={handleDetect}
            disabled={detecting || loading}
            style={{ display: 'flex', alignItems: 'center', gap: 5, padding: '6px 12px', fontSize: 12, fontWeight: 600 }}
          >
            <Sparkles size={14} />
            {detecting ? 'Đang quét...' : 'Quét điểm nóng'}
          </button>

          <button
            className="btn-secondary refresh-btn"
            onClick={onRefresh}
            disabled={loading}
            style={{ padding: '6px 8px' }}
            title="Làm mới"
          >
            <RefreshCw size={14} className={loading ? 'spin' : ''} />
          </button>
        </div>
      </div>

      {detectMessage && <div className="info-banner" style={{ marginBottom: 10 }}>{detectMessage}</div>}

      {/* Priority Tabs (Translated to Vietnamese) */}
      <div className="priority-tabs" style={{ display: 'flex', gap: 6, flexWrap: 'wrap', marginBottom: 12 }}>
        <button
          className={`priority-tab ${priorityFilter === 'ALL' ? 'active' : ''}`}
          onClick={() => setPriorityFilter('ALL')}
          style={{ fontSize: 12, fontWeight: 600, padding: '5px 12px' }}
        >
          Tất cả ({hotspots.length})
        </button>
        <button
          className={`priority-tab tab-immediate ${priorityFilter === 'IMMEDIATE' ? 'active' : ''}`}
          onClick={() => setPriorityFilter('IMMEDIATE')}
          style={{ fontSize: 12, fontWeight: 600, padding: '5px 12px' }}
        >
          <span className="dot immediate-dot" /> Xử lý ngay ({priorityCounts.IMMEDIATE})
        </button>
        <button
          className={`priority-tab tab-urgent ${priorityFilter === 'URGENT' ? 'active' : ''}`}
          onClick={() => setPriorityFilter('URGENT')}
          style={{ fontSize: 12, fontWeight: 600, padding: '5px 12px' }}
        >
          <span className="dot urgent-dot" /> Khẩn cấp ({priorityCounts.URGENT})
        </button>
        <button
          className={`priority-tab tab-planned ${priorityFilter === 'PLANNED' ? 'active' : ''}`}
          onClick={() => setPriorityFilter('PLANNED')}
          style={{ fontSize: 12, fontWeight: 600, padding: '5px 12px' }}
        >
          <span className="dot planned-dot" /> Theo kế hoạch ({priorityCounts.PLANNED})
        </button>
        <button
          className={`priority-tab tab-monitor ${priorityFilter === 'MONITOR' ? 'active' : ''}`}
          onClick={() => setPriorityFilter('MONITOR')}
          style={{ fontSize: 12, fontWeight: 600, padding: '5px 12px' }}
        >
          <span className="dot monitor-dot" /> Theo dõi ({priorityCounts.MONITOR})
        </button>
      </div>

      {/* Horizontal Carousel List */}
      {loading ? (
        <div className="loading-state">Đang tải danh sách điểm nóng...</div>
      ) : filteredHotspots.length === 0 ? (
        <div className="empty-hotspot-state" style={{ padding: 24, background: '#ffffff', borderRadius: 8, border: '1px solid #e2e8f0' }}>
          <CheckCircle2 size={32} color="#16a34a" style={{ marginBottom: 6 }} />
          <h4 style={{ margin: '0 0 4px 0', fontSize: 14, fontWeight: 700 }}>Không có điểm nóng nào trong bộ lọc này</h4>
          <p style={{ margin: 0, fontSize: 12, color: '#64748b' }}>Tất cả các vấn đề phát sinh đã được xử lý hoặc chưa đạt ngưỡng cảnh báo.</p>
        </div>
      ) : (
        <div
          ref={scrollContainerRef}
          style={{
            display: 'flex',
            gap: 14,
            overflowX: 'auto',
            paddingBottom: 10,
            paddingTop: 2,
            scrollSnapType: 'x mandatory',
            WebkitOverflowScrolling: 'touch',
          }}
        >
          {filteredHotspots.map((h) => {
            const drillDownUrl = getDrillDownUrl(h);
            const priorityConfig = PRIORITY_LABELS[h.action_priority] ?? {
              label: h.action_priority,
              color: '#475569',
              bg: '#f1f5f9',
              border: '#cbd5e1',
            };
            const statusLabel = STATUS_LABELS[h.status] ?? h.status;

            return (
              <div
                key={h.hotspot_id}
                style={{
                  flex: '0 0 300px',
                  scrollSnapAlign: 'start',
                  background: '#ffffff',
                  borderRadius: 10,
                  border: `1px solid ${priorityConfig.border}`,
                  boxShadow: '0 2px 8px rgba(0,0,0,0.04)',
                  padding: 14,
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'space-between',
                  gap: 10,
                  transition: 'transform 0.15s ease, box-shadow 0.15s ease',
                }}
              >
                {/* Card Top: Badges */}
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 8 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                      <span
                        style={{
                          fontSize: 11,
                          fontWeight: 700,
                          padding: '2px 8px',
                          borderRadius: 10,
                          background: priorityConfig.bg,
                          color: priorityConfig.color,
                          border: `1px solid ${priorityConfig.border}`,
                        }}
                      >
                        ● {priorityConfig.label}
                      </span>
                      <span style={{ fontSize: 10, fontWeight: 700, padding: '2px 6px', borderRadius: 6, background: '#f1f5f9', color: '#475569' }}>
                        {{ 'SEV-1': 'Cấp 1', 'SEV-2': 'Cấp 2', 'SEV-3': 'Cấp 3', 'SEV-4': 'Cấp 4' }[h.operational_severity] ?? h.operational_severity}
                      </span>
                    </div>
                    <span style={{ fontSize: 11, color: '#64748b', background: '#f8fafc', padding: '1px 6px', borderRadius: 4 }}>
                      {statusLabel}
                    </span>
                  </div>

                  {/* Title & Issue */}
                  <h4 style={{ fontSize: 14, fontWeight: 700, color: '#0f172a', margin: '0 0 4px 0', lineHeight: 1.3 }}>
                    {h.service.name_vi || 'Dịch vụ'}
                  </h4>
                  <p style={{ fontSize: 12, color: '#475569', margin: '0 0 8px 0', lineHeight: 1.4, fontWeight: 500 }}>
                    {h.issue.name_vi || 'Vấn đề'}
                  </p>

                  {/* Location & Count Tag */}
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: 11, color: '#64748b', background: '#f8fafc', padding: '6px 8px', borderRadius: 6 }}>
                    <span>{h.location?.name_vi ? h.location.name_vi : 'Toàn dự án'}</span>
                    <strong style={{ color: '#dc2626' }}>{h.evidence_count} phản ánh</strong>
                  </div>
                </div>

                {/* Card Bottom Actions */}
                <div style={{ display: 'flex', alignItems: 'center', gap: 8, paddingTop: 6, borderTop: '1px solid #f1f5f9' }}>
                  <button
                    onClick={() => navigate(drillDownUrl)}
                    style={{
                      flex: 1,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      gap: 4,
                      padding: '6px 8px',
                      borderRadius: 6,
                      background: '#eff6ff',
                      color: '#2563eb',
                      border: '1px solid #bfdbfe',
                      fontSize: 11,
                      fontWeight: 600,
                      cursor: 'pointer',
                    }}
                    title="Xem các phản ánh liên quan"
                  >
                    <ExternalLink size={12} /> Bằng chứng
                  </button>

                  <button
                    onClick={() => handleOpenDetail(h.hotspot_id)}
                    style={{
                      flex: 1,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      gap: 4,
                      padding: '6px 8px',
                      borderRadius: 6,
                      background: '#0f172a',
                      color: '#ffffff',
                      border: 'none',
                      fontSize: 11,
                      fontWeight: 600,
                      cursor: 'pointer',
                    }}
                  >
                    Xử lý <ArrowRight size={12} />
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {selectedHotspot && (
        <HotspotDetailModal
          detail={selectedHotspot}
          onClose={() => setSelectedHotspot(null)}
          onRefresh={async () => {
            await handleOpenDetail(selectedHotspot.hotspot.hotspot_id);
            onRefresh();
          }}
        />
      )}
    </section>
  );
};

export default HotspotActionQueue;
