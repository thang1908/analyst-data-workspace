import React, { useState } from 'react';
import { X, ShieldCheck, MapPin, Tag, Calendar, Layers, GitBranch, MessageSquare, AlertCircle, Edit3, Check, Loader2 } from 'lucide-react';
import { FeedbackWorkspaceItem, updateFeedbackItem, UpdateFeedbackPayload } from '../../api/feedback';

interface FeedbackDetailModalProps {
  item: FeedbackWorkspaceItem | null;
  onClose: () => void;
  onItemUpdated?: (updatedItem: FeedbackWorkspaceItem) => void;
}

const formatDate = (value: string) => {
  try {
    return new Intl.DateTimeFormat('vi-VN', {
      dateStyle: 'full',
      timeStyle: 'medium',
    }).format(new Date(value));
  } catch {
    return value;
  }
};

const SERVICE_OPTIONS = [
  { code: 'SV-01', name: 'SV-01: Bán hàng, tư vấn & thông tin dự án' },
  { code: 'SV-02', name: 'SV-02: Bàn giao, nghiệm thu & bảo hành' },
  { code: 'SV-03', name: 'SV-03: Hồ sơ, thủ tục & App cư dân' },
  { code: 'SV-04', name: 'SV-04: Phí quản lý, hóa đơn & thanh toán' },
  { code: 'SV-05', name: 'SV-05: Ra vào, thẻ từ & bãi đỗ xe' },
  { code: 'SV-06', name: 'SV-06: Tiện ích nội khu (hồ bơi, gym, BBQ)' },
  { code: 'SV-07', name: 'SV-07: Kỹ thuật hạ tầng, thang máy & điện nước' },
  { code: 'SV-08', name: 'SV-08: An ninh trật tự, tiếng ồn & PCCC' },
  { code: 'SV-09', name: 'SV-09: Vệ sinh môi trường & rác thải' },
  { code: 'SV-10', name: 'SV-10: Khác / Ngoài phạm vi / Spam' },
];

const renderSentimentBadge = (sentiment: string | null | undefined) => {
  const norm = (sentiment ?? '').toUpperCase();
  if (norm === 'NEGATIVE' || norm === 'TIÊU CỰC') {
    return (
      <span style={{ padding: '4px 10px', borderRadius: 12, fontSize: 12, fontWeight: 700, background: '#fef2f2', color: '#dc2626', border: '1px solid #fca5a5' }}>
        ● TIÊU CỰC
      </span>
    );
  }
  if (norm === 'POSITIVE' || norm === 'TÍCH CỰC') {
    return (
      <span style={{ padding: '4px 10px', borderRadius: 12, fontSize: 12, fontWeight: 700, background: '#f0fdf4', color: '#16a34a', border: '1px solid #86efac' }}>
        ● TÍCH CỰC
      </span>
    );
  }
  return (
    <span style={{ padding: '4px 10px', borderRadius: 12, fontSize: 12, fontWeight: 600, background: '#f8fafc', color: '#64748b', border: '1px solid #e2e8f0' }}>
      ● {norm ? 'TRUNG TÍNH' : 'CHƯA PHÂN LOẠI'}
    </span>
  );
};

export const FeedbackDetailModal: React.FC<FeedbackDetailModalProps> = ({ item: initialItem, onClose, onItemUpdated }) => {
  const [item, setItem] = useState<FeedbackWorkspaceItem | null>(initialItem);
  const [isEditing, setIsEditing] = useState(false);
  const [saving, setSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Form edit states
  const [serviceCode, setServiceCode] = useState(initialItem?.currentClassification.service?.code ?? 'SV-07');
  const [sentiment, setSentiment] = useState(initialItem?.currentClassification.sentiment ?? 'NEUTRAL');
  const [severity, setSeverity] = useState(initialItem?.currentClassification.operationalSeverity ?? 'SEV-4');
  const [eligibility, setEligibility] = useState(initialItem?.analyticEligibility ?? 'INCLUDED');
  const [reason, setReason] = useState('');

  if (!item) return null;

  const classification = item.currentClassification;
  const locationName = item.location.name || item.location.code || 'Toàn dự án';

  const handleSaveCorrection = async () => {
    setSaving(true);
    setErrorMsg(null);
    try {
      const payload: UpdateFeedbackPayload = {
        service_code: serviceCode,
        sentiment: sentiment,
        operational_severity: severity,
        analytic_eligibility: eligibility,
        correction_reason: reason || 'Người dùng hiệu chỉnh thông tin phân loại',
      };
      const updated = await updateFeedbackItem(item.feedbackItemId, payload);
      setItem(updated);
      setIsEditing(false);
      setSaveSuccess(true);
      onItemUpdated?.(updated);
      setTimeout(() => setSaveSuccess(false), 3000);
    } catch (err) {
      setErrorMsg(err instanceof Error ? err.message : 'Không thể lưu thay đổi.');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        background: 'rgba(15, 23, 42, 0.65)',
        backdropFilter: 'blur(4px)',
        zIndex: 1000,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: 20,
      }}
      onClick={onClose}
    >
      <div
        style={{
          background: '#ffffff',
          borderRadius: 14,
          maxWidth: 680,
          width: '100%',
          maxHeight: '90vh',
          display: 'flex',
          flexDirection: 'column',
          boxShadow: '0 20px 40px rgba(0,0,0,0.3)',
          overflow: 'hidden',
          animation: 'fadeIn 0.2s ease',
        }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Modal Header */}
        <div
          style={{
            padding: '16px 22px',
            borderBottom: '1px solid #e2e8f0',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            background: '#f8fafc',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <MessageSquare size={18} color="#2563eb" />
            <h3 style={{ fontSize: 16, fontWeight: 800, color: '#0f172a', margin: 0 }}>
              Chi tiết & Hiệu chỉnh phản ánh
            </h3>
            {saveSuccess && (
              <span style={{ fontSize: 12, background: '#dcfce7', color: '#15803d', padding: '2px 8px', borderRadius: 10, display: 'flex', alignItems: 'center', gap: 4, fontWeight: 600 }}>
                <Check size={13} /> Đã lưu thành công
              </span>
            )}
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            {!isEditing && (
              <button
                onClick={() => setIsEditing(true)}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 5,
                  padding: '5px 12px',
                  borderRadius: 6,
                  background: '#eff6ff',
                  color: '#2563eb',
                  border: '1px solid #bfdbfe',
                  fontWeight: 600,
                  fontSize: 12,
                  cursor: 'pointer',
                }}
              >
                <Edit3 size={13} /> Hiệu chỉnh
              </button>
            )}

            <button
              onClick={onClose}
              style={{
                width: 30,
                height: 30,
                borderRadius: 6,
                border: '1px solid #e2e8f0',
                background: '#ffffff',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                cursor: 'pointer',
                color: '#64748b',
              }}
            >
              <X size={16} />
            </button>
          </div>
        </div>

        {/* Modal Body */}
        <div style={{ padding: 22, overflowY: 'auto', flex: 1, display: 'flex', flexDirection: 'column', gap: 16 }}>
          {errorMsg && (
            <div style={{ padding: '10px 14px', background: '#fef2f2', border: '1px solid #fecaca', color: '#b91c1c', borderRadius: 8, fontSize: 13 }}>
              {errorMsg}
            </div>
          )}

          {/* Masked Content Box */}
          <div style={{ background: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: 10, padding: 16 }}>
            <div style={{ fontSize: 11, fontWeight: 700, color: '#475569', textTransform: 'uppercase', marginBottom: 8, display: 'flex', alignItems: 'center', gap: 6 }}>
              <ShieldCheck size={14} color="#16a34a" />
              Nội dung phản ánh (Đã che mờ bảo mật)
            </div>
            <blockquote style={{ margin: 0, fontSize: 14, lineHeight: 1.6, color: '#0f172a', fontWeight: 500, fontStyle: 'normal' }}>
              "{item.contentMasked}"
            </blockquote>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginTop: 12, paddingTop: 10, borderTop: '1px solid #e2e8f0', fontSize: 12, color: '#64748b' }}>
              <span style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                <Calendar size={13} /> {formatDate(item.reportedAt)}
              </span>
              <span>Nguồn: <strong>{item.sourceSystem || 'Hệ thống'}</strong></span>
            </div>
          </div>

          {/* Edit Form or View Grid */}
          {isEditing ? (
            <div style={{ background: '#f0fdf4', border: '1px solid #bbf7d0', borderRadius: 10, padding: 16, display: 'flex', flexDirection: 'column', gap: 12 }}>
              <div style={{ fontSize: 13, fontWeight: 700, color: '#166534', display: 'flex', alignItems: 'center', gap: 6 }}>
                <Edit3 size={15} /> Chế độ hiệu chỉnh thông tin phân loại
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 12 }}>
                {/* Service Select */}
                <div>
                  <label style={{ display: 'block', fontSize: 11, fontWeight: 700, color: '#374151', marginBottom: 4 }}>
                    Dịch vụ chính
                  </label>
                  <select
                    value={serviceCode}
                    onChange={(e) => setServiceCode(e.target.value)}
                    style={{ width: '100%', padding: '7px 10px', borderRadius: 6, border: '1px solid #cbd5e1', fontSize: 12, background: '#ffffff' }}
                  >
                    {SERVICE_OPTIONS.map((s) => (
                      <option key={s.code} value={s.code}>{s.name}</option>
                    ))}
                  </select>
                </div>

                {/* Sentiment Select */}
                <div>
                  <label style={{ display: 'block', fontSize: 11, fontWeight: 700, color: '#374151', marginBottom: 4 }}>
                    Cảm xúc
                  </label>
                  <select
                    value={sentiment}
                    onChange={(e) => setSentiment(e.target.value)}
                    style={{ width: '100%', padding: '7px 10px', borderRadius: 6, border: '1px solid #cbd5e1', fontSize: 12, background: '#ffffff' }}
                  >
                    <option value="NEGATIVE">NEGATIVE (Tiêu cực / Sự cố)</option>
                    <option value="NEUTRAL">NEUTRAL (Trung tính / Hỏi han)</option>
                    <option value="POSITIVE">POSITIVE (Tích cực / Lời khen)</option>
                  </select>
                </div>

                {/* Severity Select */}
                <div>
                  <label style={{ display: 'block', fontSize: 11, fontWeight: 700, color: '#374151', marginBottom: 4 }}>
                    Mức độ nghiêm trọng
                  </label>
                  <select
                    value={severity}
                    onChange={(e) => setSeverity(e.target.value)}
                    style={{ width: '100%', padding: '7px 10px', borderRadius: 6, border: '1px solid #cbd5e1', fontSize: 12, background: '#ffffff' }}
                  >
                    <option value="SEV-1">SEV-1 (Khẩn cấp / PCCC / An toàn)</option>
                    <option value="SEV-2">SEV-2 (Nghiêm trọng / Kẹt thang)</option>
                    <option value="SEV-3">SEV-3 (Trung bình / Bãi xe / Vệ sinh)</option>
                    <option value="SEV-4">SEV-4 (Thấp / Thủ tục / Góp ý)</option>
                  </select>
                </div>

                {/* Eligibility Select */}
                <div>
                  <label style={{ display: 'block', fontSize: 11, fontWeight: 700, color: '#374151', marginBottom: 4 }}>
                    Tính hợp lệ (Eligibility)
                  </label>
                  <select
                    value={eligibility}
                    onChange={(e) => setEligibility(e.target.value)}
                    style={{ width: '100%', padding: '7px 10px', borderRadius: 6, border: '1px solid #cbd5e1', fontSize: 12, background: '#ffffff' }}
                  >
                    <option value="INCLUDED">INCLUDED (Hợp lệ đưa vào phân tích & CSAT)</option>
                    <option value="EXCLUDED">EXCLUDED (Loại trừ / Tin rác / Test / Spam)</option>
                  </select>
                </div>
              </div>

              {/* Correction Reason */}
              <div>
                <label style={{ display: 'block', fontSize: 11, fontWeight: 700, color: '#374151', marginBottom: 4 }}>
                  Ghi chú / Lý do hiệu chỉnh
                </label>
                <input
                  type="text"
                  placeholder="Ví dụ: Phân loại lại sang SV-05 do sự cố thuộc bãi xe..."
                  value={reason}
                  onChange={(e) => setReason(e.target.value)}
                  style={{ width: '100%', padding: '7px 10px', borderRadius: 6, border: '1px solid #cbd5e1', fontSize: 12, background: '#ffffff' }}
                />
              </div>

              {/* Edit Actions */}
              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 8, marginTop: 6 }}>
                <button
                  type="button"
                  onClick={() => setIsEditing(false)}
                  disabled={saving}
                  style={{ padding: '6px 14px', borderRadius: 6, background: '#ffffff', border: '1px solid #cbd5e1', color: '#475569', fontSize: 12, fontWeight: 600, cursor: 'pointer' }}
                >
                  Hủy
                </button>
                <button
                  type="button"
                  onClick={handleSaveCorrection}
                  disabled={saving}
                  style={{ padding: '6px 16px', borderRadius: 6, background: '#16a34a', border: 'none', color: '#ffffff', fontSize: 12, fontWeight: 700, cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 6 }}
                >
                  {saving ? <Loader2 size={13} className="spin" /> : <Check size={13} />}
                  Lưu thay đổi
                </button>
              </div>
            </div>
          ) : (
            /* View Grid */
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 12 }}>
              <div style={{ background: '#ffffff', border: '1px solid #e2e8f0', borderRadius: 8, padding: 12 }}>
                <span style={{ fontSize: 11, color: '#64748b', display: 'block', marginBottom: 4 }}>Nhóm dịch vụ</span>
                <strong style={{ fontSize: 14, color: '#0f172a' }}>{classification.service?.nameVi || 'Chưa phân loại'}</strong>
                <span style={{ fontSize: 11, color: '#2563eb', display: 'block', marginTop: 2, fontWeight: 600 }}>{classification.service?.code}</span>
              </div>

              <div style={{ background: '#ffffff', border: '1px solid #e2e8f0', borderRadius: 8, padding: 12 }}>
                <span style={{ fontSize: 11, color: '#64748b', display: 'block', marginBottom: 4 }}>Vấn đề chi tiết</span>
                <strong style={{ fontSize: 14, color: '#0f172a' }}>{classification.issue?.nameVi || 'Chưa phân loại'}</strong>
                <span style={{ fontSize: 11, color: '#64748b', display: 'block', marginTop: 2 }}>{classification.issue?.code}</span>
              </div>

              <div style={{ background: '#ffffff', border: '1px solid #e2e8f0', borderRadius: 8, padding: 12 }}>
                <span style={{ fontSize: 11, color: '#64748b', display: 'block', marginBottom: 6 }}>Cảm xúc ghi nhận</span>
                <div>{renderSentimentBadge(classification.sentiment)}</div>
              </div>

              <div style={{ background: '#ffffff', border: '1px solid #e2e8f0', borderRadius: 8, padding: 12 }}>
                <span style={{ fontSize: 11, color: '#64748b', display: 'block', marginBottom: 4 }}>Mức độ vận hành</span>
                <strong style={{ fontSize: 14, color: classification.operationalSeverity === 'SEV-1' ? '#dc2626' : '#0f172a' }}>
                  {{ 'SEV-1': 'Cấp 1 (Khẩn cấp / PCCC)', 'SEV-2': 'Cấp 2 (Cao / Kẹt thang)', 'SEV-3': 'Cấp 3 (Trung bình)', 'SEV-4': 'Cấp 4 (Nhẹ / Thấp)' }[classification.operationalSeverity ?? ''] ?? (classification.operationalSeverity || 'Cấp 4 (Nhẹ / Thấp)')}
                </strong>
              </div>

              <div style={{ background: '#ffffff', border: '1px solid #e2e8f0', borderRadius: 8, padding: 12 }}>
                <span style={{ fontSize: 11, color: '#64748b', display: 'block', marginBottom: 4 }}>Bước hành trình</span>
                <strong style={{ fontSize: 14, color: '#0f172a' }}>{classification.journeyStep?.nameVi || classification.journeyStage?.nameVi || 'Chưa phân loại'}</strong>
                <span style={{ fontSize: 11, color: '#0284c7', display: 'block', marginTop: 2, fontWeight: 600 }}>
                  {classification.journeyStep?.code || classification.journeyStage?.code}
                </span>
              </div>

              <div style={{ background: '#ffffff', border: '1px solid #e2e8f0', borderRadius: 8, padding: 12 }}>
                <span style={{ fontSize: 11, color: '#64748b', display: 'block', marginBottom: 4 }}>Điểm chạm (Touchpoint)</span>
                <strong style={{ fontSize: 14, color: '#0f172a' }}>{classification.touchpoint?.nameVi || 'Chưa xác định'}</strong>
                <span style={{ fontSize: 11, color: '#475569', display: 'block', marginTop: 2 }}>{classification.touchpoint?.code}</span>
              </div>

              <div style={{ background: '#ffffff', border: '1px solid #e2e8f0', borderRadius: 8, padding: 12 }}>
                <span style={{ fontSize: 11, color: '#64748b', display: 'block', marginBottom: 4 }}>Khu đô thị / Vị trí</span>
                <div style={{ display: 'flex', alignItems: 'center', gap: 5 }}>
                  <MapPin size={14} color="#64748b" />
                  <strong style={{ fontSize: 14, color: '#0f172a' }}>{locationName}</strong>
                </div>
              </div>

              <div style={{ background: '#ffffff', border: '1px solid #e2e8f0', borderRadius: 8, padding: 12 }}>
                <span style={{ fontSize: 11, color: '#64748b', display: 'block', marginBottom: 4 }}>Điều kiện phân tích</span>
                <strong style={{ fontSize: 13, color: item.analyticEligibility === 'INCLUDED' ? '#16a34a' : '#dc2626' }}>
                  {item.analyticEligibility === 'INCLUDED' ? '● Hợp lệ đưa vào phân tích' : '○ Đã loại trừ (Không tính CSAT)'}
                </strong>
              </div>
            </div>
          )}

          {/* Lineage & Split Section */}
          <div style={{ background: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: 8, padding: 12, fontSize: 12 }}>
            <div style={{ fontWeight: 700, color: '#475569', marginBottom: 4, display: 'flex', alignItems: 'center', gap: 6 }}>
              <GitBranch size={14} /> Dòng tách ý định (Lineage)
            </div>
            <span style={{ color: '#64748b' }}>
              {item.parentItemId
                ? 'Item này là phân đoạn con tách từ phản hồi gốc ban đầu.'
                : 'Đây là phản hồi gốc ban đầu, không qua phân tách ý định.'}
            </span>
          </div>
        </div>

        {/* Modal Footer */}
        <div style={{ padding: '14px 22px', borderTop: '1px solid #e2e8f0', display: 'flex', justifyContent: 'flex-end', background: '#fafafa' }}>
          <button
            onClick={onClose}
            style={{
              padding: '8px 18px',
              borderRadius: 6,
              background: '#0f172a',
              color: '#ffffff',
              border: 'none',
              fontWeight: 600,
              fontSize: 13,
              cursor: 'pointer',
            }}
          >
            Đóng
          </button>
        </div>
      </div>
    </div>
  );
};

export default FeedbackDetailModal;
