import React, { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import {
  AlertTriangle,
  CheckCircle,
  Clock,
  ExternalLink,
  ShieldAlert,
  UserCheck,
  X,
  XCircle,
  RotateCcw,
} from 'lucide-react';
import {
  HotspotDetailData,
  acknowledgeHotspot,
  assignHotspot,
  dismissHotspot,
  reopenHotspot,
  resolveHotspot,
} from '../../api/hotspots';

interface HotspotDetailModalProps {
  detail: HotspotDetailData;
  onClose: () => void;
  onRefresh: () => void;
}

const PRIORITY_LABELS: Record<string, string> = {
  IMMEDIATE: 'Xử lý ngay',
  URGENT: 'Khẩn cấp',
  PLANNED: 'Theo kế hoạch',
  MONITOR: 'Theo dõi',
};

const STATUS_LABELS: Record<string, string> = {
  CANDIDATE: 'Mới phát hiện',
  ACKNOWLEDGED: 'Đã ghi nhận',
  INVESTIGATING: 'Đang xử lý',
  RESOLVED: 'Đã giải quyết',
  DISMISSED: 'Đã đóng',
};

const SEVERITY_LABELS: Record<string, string> = {
  'SEV-1': 'Cấp 1',
  'SEV-2': 'Cấp 2',
  'SEV-3': 'Cấp 3',
  'SEV-4': 'Cấp 4',
};

const SENTIMENT_LABELS: Record<string, string> = {
  NEGATIVE: 'Tiêu cực',
  POSITIVE: 'Tích cực',
  NEUTRAL: 'Trung tính',
  UNKNOWN: 'Chưa rõ',
};

export const HotspotDetailModal: React.FC<HotspotDetailModalProps> = ({
  detail,
  onClose,
  onRefresh,
}) => {
  const navigate = useNavigate();
  const location = useLocation();
  const [submitting, setSubmitting] = useState(false);
  const [actionType, setActionType] = useState<string | null>(null);
  const [reason, setReason] = useState('');
  const [resolutionSummary, setResolutionSummary] = useState('');
  const [ownerUserId, setOwnerUserId] = useState('');
  const [ownerTeamKey, setOwnerTeamKey] = useState('');
  const [error, setError] = useState<string | null>(null);

  const { hotspot, evidence, timeline } = detail;

  const handleAction = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!actionType) return;
    setSubmitting(true);
    setError(null);
    try {
      if (actionType === 'ACKNOWLEDGE') {
        await acknowledgeHotspot(hotspot.hotspot_id, {
          expected_version: hotspot.version,
          reason: reason.trim() || 'Triage acknowledged.',
        });
      } else if (actionType === 'ASSIGN') {
        await assignHotspot(hotspot.hotspot_id, {
          expected_version: hotspot.version,
          owner_user_id: ownerUserId.trim() || undefined,
          owner_team_key: ownerTeamKey.trim() || undefined,
          reason: reason.trim() || 'Assigned to investigator.',
        });
      } else if (actionType === 'DISMISS') {
        if (!reason.trim()) throw new Error('Vui lòng nhập lý do loại bỏ (bắt buộc).');
        await dismissHotspot(hotspot.hotspot_id, {
          expected_version: hotspot.version,
          reason: reason.trim(),
        });
      } else if (actionType === 'RESOLVE') {
        if (!resolutionSummary.trim()) throw new Error('Vui lòng nhập tóm tắt giải pháp xử lý (bắt buộc).');
        await resolveHotspot(hotspot.hotspot_id, {
          expected_version: hotspot.version,
          resolution_summary: resolutionSummary.trim(),
          reason: reason.trim() || 'Operational fix confirmed.',
        });
      } else if (actionType === 'REOPEN') {
        if (!reason.trim()) throw new Error('Vui lòng nhập lý do mở lại (bắt buộc).');
        await reopenHotspot(hotspot.hotspot_id, {
          expected_version: hotspot.version,
          reason: reason.trim(),
        });
      }
      setActionType(null);
      setReason('');
      setResolutionSummary('');
      onRefresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Thao tác thất bại.');
    } finally {
      setSubmitting(false);
    }
  };

  const nextParams = new URLSearchParams(location.search);
  if (hotspot.service.code) nextParams.set('service_code', hotspot.service.code);
  if (hotspot.issue.code) nextParams.set('issue_code', hotspot.issue.code);
  nextParams.set('hotspot_id', hotspot.hotspot_id);
  const drillDownUrl = `/feedback?${nextParams.toString()}`;

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal-card hotspot-detail-modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div className="modal-title-area">
            <div className="hotspot-badges">
              <span className={`priority-badge priority-${hotspot.action_priority.toLowerCase()}`}>
                {PRIORITY_LABELS[hotspot.action_priority] ?? hotspot.action_priority}
              </span>
              <span className={`severity-badge severity-${hotspot.operational_severity.toLowerCase()}`}>
                {SEVERITY_LABELS[hotspot.operational_severity] ?? hotspot.operational_severity}
              </span>
              <span className={`status-badge status-${hotspot.status.toLowerCase()}`}>
                {STATUS_LABELS[hotspot.status] ?? hotspot.status}
              </span>
            </div>
            <h2>
              {hotspot.service.name_vi || 'Dịch vụ'} • {hotspot.issue.name_vi || 'Vấn đề'}
            </h2>
            <p className="modal-subtitle">
              {hotspot.location?.name_vi ? `Vị trí: ${hotspot.location.name_vi}` : 'Phạm vi toàn hệ thống'} • {hotspot.evidence_count} phản ánh phát hiện
            </p>
          </div>
          <button className="icon-button" onClick={onClose}>
            <X size={20} />
          </button>
        </div>

        <div className="modal-body">
          {error && <div className="error-banner">{error}</div>}

          {/* Quick Actions */}
          <div className="hotspot-action-bar">
            <button
              className="action-btn drilldown-btn"
              onClick={() => navigate(drillDownUrl)}
            >
              <ExternalLink size={15} /> Xem trong Feedback Explorer ({hotspot.evidence_count})
            </button>

            {hotspot.status === 'CANDIDATE' && (
              <>
                <button className="action-btn btn-ack" onClick={() => setActionType('ACKNOWLEDGE')}>
                  <CheckCircle size={15} /> Tiếp nhận (Acknowledge)
                </button>
                <button className="action-btn btn-assign" onClick={() => setActionType('ASSIGN')}>
                  <UserCheck size={15} /> Phân công
                </button>
                <button className="action-btn btn-dismiss" onClick={() => setActionType('DISMISS')}>
                  <XCircle size={15} /> Bỏ qua
                </button>
              </>
            )}

            {hotspot.status === 'ACKNOWLEDGED' && (
              <>
                <button className="action-btn btn-assign" onClick={() => setActionType('ASSIGN')}>
                  <UserCheck size={15} /> Phân công xử lý
                </button>
                <button className="action-btn btn-resolve" onClick={() => setActionType('RESOLVE')}>
                  <CheckCircle size={15} /> Đóng / Đã xử lý
                </button>
                <button className="action-btn btn-dismiss" onClick={() => setActionType('DISMISS')}>
                  <XCircle size={15} /> Bỏ qua
                </button>
              </>
            )}

            {hotspot.status === 'INVESTIGATING' && (
              <>
                <button className="action-btn btn-resolve" onClick={() => setActionType('RESOLVE')}>
                  <CheckCircle size={15} /> Đóng / Đã xử lý
                </button>
                <button className="action-btn btn-dismiss" onClick={() => setActionType('DISMISS')}>
                  <XCircle size={15} /> Bỏ qua
                </button>
              </>
            )}

            {(hotspot.status === 'RESOLVED' || hotspot.status === 'DISMISSED') && (
              <button className="action-btn btn-reopen" onClick={() => setActionType('REOPEN')}>
                <RotateCcw size={15} /> Mở lại (Reopen)
              </button>
            )}
          </div>

          {/* Action Form */}
          {actionType && (
            <form className="hotspot-action-form" onSubmit={handleAction}>
              <h4>Thao tác: {actionType}</h4>

              {actionType === 'RESOLVE' && (
                <label className="form-field">
                  <span>Tóm tắt giải pháp khắc phục (bắt buộc)</span>
                  <textarea
                    required
                    value={resolutionSummary}
                    onChange={(e) => setResolutionSummary(e.target.value)}
                    placeholder="Ví dụ: Đã sửa chữa cổng quẹt thẻ sảnh A và thay thế thiết bị đọc RFID."
                  />
                </label>
              )}

              {actionType === 'ASSIGN' && (
                <div className="form-row">
                  <label className="form-field">
                    <span>Đội phụ trách (Team Key)</span>
                    <input
                      type="text"
                      value={ownerTeamKey}
                      onChange={(e) => setOwnerTeamKey(e.target.value)}
                      placeholder="e.g. OPS_TEAM_NORTH"
                    />
                  </label>
                </div>
              )}

              <label className="form-field">
                <span>
                  Lý do ghi nhận {actionType === 'DISMISS' || actionType === 'REOPEN' ? '(bắt buộc)' : '(tùy chọn)'}
                </span>
                <input
                  type="text"
                  required={actionType === 'DISMISS' || actionType === 'REOPEN'}
                  value={reason}
                  onChange={(e) => setReason(e.target.value)}
                  placeholder="Ghi chú thao tác..."
                />
              </label>

              <div className="form-buttons">
                <button type="button" className="btn-secondary" onClick={() => setActionType(null)}>
                  Hủy
                </button>
                <button type="submit" className="btn-primary" disabled={submitting}>
                  {submitting ? 'Đang lưu...' : 'Xác nhận'}
                </button>
              </div>
            </form>
          )}

          {/* Evidence List */}
          <div className="hotspot-section">
            <h3>Bằng chứng liên kết ({evidence.length})</h3>
            <div className="evidence-table-wrapper">
              <table className="evidence-table">
                <thead>
                  <tr>
                    <th>Thời gian</th>
                    <th>Nội dung phản ánh</th>
                    <th>Cảm xúc</th>
                    <th>Mức độ</th>
                  </tr>
                </thead>
                <tbody>
                  {evidence.map((item) => (
                    <tr key={item.feedback_item_id}>
                      <td className="text-nowrap">{new Date(item.reported_at).toLocaleString('vi-VN')}</td>
                      <td>{item.content_masked}</td>
                      <td>
                        <span className={`sentiment-pill sentiment-${item.sentiment.toLowerCase()}`}>
                          {SENTIMENT_LABELS[item.sentiment] ?? item.sentiment}
                        </span>
                      </td>
                      <td>
                        <span className={`severity-badge severity-${item.operational_severity.toLowerCase()}`}>
                          {SEVERITY_LABELS[item.operational_severity] ?? item.operational_severity}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Timeline */}
          <div className="hotspot-section">
            <h3>Lịch sử xử lý & Audit Trail ({timeline.length})</h3>
            <div className="timeline-list">
              {timeline.map((event) => (
                <div key={event.timeline_event_id} className="timeline-item">
                  <div className="timeline-dot" />
                  <div className="timeline-content">
                    <div className="timeline-header">
                      <strong>{event.action}</strong>
                      <span className="timeline-time">
                        {new Date(event.created_at).toLocaleString('vi-VN')}
                      </span>
                    </div>
                    <div className="timeline-sub">
                      {event.from_status ? `${STATUS_LABELS[event.from_status] ?? event.from_status} → ` : ''}{STATUS_LABELS[event.to_status] ?? event.to_status}
                      {event.reason ? ` • Lý do: ${event.reason}` : ''}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
