import React, { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import {
  AlertOctagon,
  AlertTriangle,
  ArrowRight,
  CheckCircle2,
  Clock,
  ExternalLink,
  Flame,
  Layers,
  RefreshCw,
  Search,
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

export const HotspotActionQueue: React.FC<HotspotActionQueueProps> = ({
  projectId,
  hotspots,
  loading,
  onRefresh,
}) => {
  const navigate = useNavigate();
  const location = useLocation();
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
      setDetectMessage(`Đã quét xong: Tìm thấy ${detected.length} điểm nóng theo luật xác định.`);
      onRefresh();
    } catch (err) {
      setDetectMessage(err instanceof Error ? err.message : 'Quét thất bại');
    } finally {
      setDetecting(false);
    }
  };

  const priorityCounts = {
    IMMEDIATE: hotspots.filter((h) => h.action_priority === 'IMMEDIATE').length,
    URGENT: hotspots.filter((h) => h.action_priority === 'URGENT').length,
    PLANNED: hotspots.filter((h) => h.action_priority === 'PLANNED').length,
    MONITOR: hotspots.filter((h) => h.action_priority === 'MONITOR').length,
  };

  return (
    <section className="hotspot-queue-container" aria-label="Hotspot Action Priority Queue">
      <div className="hotspot-queue-header">
        <div className="hotspot-queue-title">
          <div className="icon-badge">
            <Flame className="flame-icon" size={20} />
          </div>
          <div>
            <h3 style={{ fontSize: 17, fontWeight: 800, margin: 0, letterSpacing: '-0.2px' }}>Hàng đợi điểm nóng</h3>
          </div>
        </div>

        <div className="hotspot-queue-actions">
          <button
            className="btn-secondary scan-btn"
            onClick={handleDetect}
            disabled={detecting || loading}
          >
            <Sparkles size={15} />
            {detecting ? 'Đang quét...' : 'Quét điểm nóng'}
          </button>
          <button className="btn-secondary refresh-btn" onClick={onRefresh} disabled={loading}>
            <RefreshCw size={15} className={loading ? 'spin' : ''} />
          </button>
        </div>
      </div>

      {detectMessage && <div className="info-banner">{detectMessage}</div>}

      {/* Priority Summary Tabs */}
      <div className="priority-tabs">
        <button
          className={`priority-tab ${priorityFilter === 'ALL' ? 'active' : ''}`}
          onClick={() => setPriorityFilter('ALL')}
        >
          Tất cả ({hotspots.length})
        </button>
        <button
          className={`priority-tab tab-immediate ${priorityFilter === 'IMMEDIATE' ? 'active' : ''}`}
          onClick={() => setPriorityFilter('IMMEDIATE')}
        >
          <span className="dot immediate-dot" /> IMMEDIATE ({priorityCounts.IMMEDIATE})
        </button>
        <button
          className={`priority-tab tab-urgent ${priorityFilter === 'URGENT' ? 'active' : ''}`}
          onClick={() => setPriorityFilter('URGENT')}
        >
          <span className="dot urgent-dot" /> URGENT ({priorityCounts.URGENT})
        </button>
        <button
          className={`priority-tab tab-planned ${priorityFilter === 'PLANNED' ? 'active' : ''}`}
          onClick={() => setPriorityFilter('PLANNED')}
        >
          <span className="dot planned-dot" /> PLANNED ({priorityCounts.PLANNED})
        </button>
        <button
          className={`priority-tab tab-monitor ${priorityFilter === 'MONITOR' ? 'active' : ''}`}
          onClick={() => setPriorityFilter('MONITOR')}
        >
          <span className="dot monitor-dot" /> MONITOR ({priorityCounts.MONITOR})
        </button>
      </div>

      {/* Status Filter Sub-bar */}
      <div className="queue-status-bar">
        <span className="status-label">Trạng thái:</span>
        {['ACTIVE', 'ALL', 'CANDIDATE', 'ACKNOWLEDGED', 'INVESTIGATING', 'RESOLVED', 'DISMISSED'].map((st) => (
          <button
            key={st}
            className={`status-chip ${statusFilter === st ? 'active' : ''}`}
            onClick={() => setStatusFilter(st)}
          >
            {st === 'ACTIVE' ? 'Đang hoạt động' : st}
          </button>
        ))}
      </div>

      {/* Hotspots Grid */}
      {loading ? (
        <div className="loading-state">Đang tải danh sách điểm nóng...</div>
      ) : filteredHotspots.length === 0 ? (
        <div className="empty-hotspot-state">
          <CheckCircle2 size={36} className="empty-icon" />
          <h4>Không có điểm nóng nào trong bộ lọc hiện tại</h4>
          <p>Tất cả cụm sự cố đã được phân loại và xử lý theo quy trình vận hành chuẩn.</p>
        </div>
      ) : (
        <div className="hotspot-cards-grid">
          {filteredHotspots.map((h) => {
            const drillDownUrl = getDrillDownUrl(h);
            return (
              <div key={h.hotspot_id} className={`hotspot-card priority-card-${h.action_priority.toLowerCase()}`}>
                <div className="hotspot-card-header">
                  <div className="badges-group">
                    <span className={`priority-pill priority-${h.action_priority.toLowerCase()}`}>
                      {h.action_priority}
                    </span>
                    <span className={`severity-pill severity-${h.operational_severity.toLowerCase()}`}>
                      {h.operational_severity}
                    </span>
                  </div>
                  <span className={`status-pill status-${h.status.toLowerCase()}`}>{h.status}</span>
                </div>

                <div className="hotspot-card-body">
                  <h4 className="hotspot-card-title">
                    {h.service.name_vi ?? h.service.code}
                  </h4>
                  <p className="hotspot-issue-name">
                    {h.issue.name_vi ?? h.issue.code}
                  </p>
                  <div className="hotspot-meta">
                    <span className="location-tag">
                      {h.location?.name_vi ? `Vị trí: ${h.location.name_vi}` : 'Toàn dự án'}
                    </span>
                    <span className="count-tag">
                      <strong>{h.evidence_count}</strong> phản ánh
                    </span>
                  </div>
                </div>

                <div className="hotspot-card-footer">
                  <button
                    className="btn-card-drilldown"
                    onClick={() => navigate(drillDownUrl)}
                    title="Xem danh sách phản ánh chứng minh trong Feedback Explorer"
                  >
                    <ExternalLink size={14} /> Bằng chứng
                  </button>
                  <button
                    className="btn-card-action"
                    onClick={() => handleOpenDetail(h.hotspot_id)}
                  >
                    Xử lý <ArrowRight size={14} />
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
