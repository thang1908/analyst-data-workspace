import React from 'react';
import { X, ShieldCheck, MapPin, Tag, Calendar, Layers, GitBranch, MessageSquare, AlertCircle } from 'lucide-react';
import { FeedbackWorkspaceItem } from '../../api/feedback';

interface FeedbackDetailModalProps {
  item: FeedbackWorkspaceItem | null;
  onClose: () => void;
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

export const FeedbackDetailModal: React.FC<FeedbackDetailModalProps> = ({ item, onClose }) => {
  if (!item) return null;

  const classification = item.currentClassification;
  const locationName = item.location.name || item.location.code || 'Toàn dự án';

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
            padding: '18px 22px',
            borderBottom: '1px solid #e2e8f0',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            background: '#f8fafc',
          }}
        >
          <div>
            <h3 style={{ fontSize: 17, fontWeight: 800, color: '#0f172a', margin: 0, display: 'flex', alignItems: 'center', gap: 8 }}>
              <MessageSquare size={18} color="#2563eb" />
              Chi tiết phản ánh của khách hàng
            </h3>
            <span style={{ fontSize: 11, color: '#64748b', marginTop: 2, display: 'block' }}>
              Mã ID: <code>{item.feedbackItemId}</code>
            </span>
          </div>

          <button
            onClick={onClose}
            style={{
              width: 32,
              height: 32,
              borderRadius: 8,
              border: '1px solid #e2e8f0',
              background: '#ffffff',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              cursor: 'pointer',
              color: '#64748b',
            }}
          >
            <X size={18} />
          </button>
        </div>

        {/* Modal Body */}
        <div style={{ padding: 22, overflowY: 'auto', flex: 1, display: 'flex', flexDirection: 'column', gap: 18 }}>
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
              <span>Kênh: <strong>{item.sourceSystem}</strong></span>
            </div>
          </div>

          {/* Classification & Metadata Grid */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 12 }}>
            <div style={{ background: '#ffffff', border: '1px solid #e2e8f0', borderRadius: 8, padding: 12 }}>
              <span style={{ fontSize: 11, color: '#64748b', display: 'block', marginBottom: 4 }}>Nhóm dịch vụ</span>
              <strong style={{ fontSize: 14, color: '#0f172a' }}>{classification.service?.nameVi || 'Chưa phân loại'}</strong>
            </div>

            <div style={{ background: '#ffffff', border: '1px solid #e2e8f0', borderRadius: 8, padding: 12 }}>
              <span style={{ fontSize: 11, color: '#64748b', display: 'block', marginBottom: 4 }}>Vấn đề chi tiết</span>
              <strong style={{ fontSize: 14, color: '#0f172a' }}>{classification.issue?.nameVi || 'Chưa phân loại'}</strong>
            </div>

            <div style={{ background: '#ffffff', border: '1px solid #e2e8f0', borderRadius: 8, padding: 12 }}>
              <span style={{ fontSize: 11, color: '#64748b', display: 'block', marginBottom: 6 }}>Cảm xúc ghi nhận</span>
              <div>{renderSentimentBadge(classification.sentiment)}</div>
            </div>

            <div style={{ background: '#ffffff', border: '1px solid #e2e8f0', borderRadius: 8, padding: 12 }}>
              <span style={{ fontSize: 11, color: '#64748b', display: 'block', marginBottom: 4 }}>Mức độ vận hành</span>
              <strong style={{ fontSize: 14, color: classification.operationalSeverity === 'SEV-1' ? '#dc2626' : '#0f172a' }}>
                {classification.operationalSeverity || 'SEV-4 (Thấp)'}
              </strong>
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
              <strong style={{ fontSize: 13, color: '#16a34a' }}>{item.analyticEligibility}</strong>
            </div>
          </div>

          {/* Lineage & Split Section */}
          <div style={{ background: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: 8, padding: 12, fontSize: 12 }}>
            <div style={{ fontWeight: 700, color: '#475569', marginBottom: 4, display: 'flex', alignItems: 'center', gap: 6 }}>
              <GitBranch size={14} /> Dòng tách ý định (Lineage)
            </div>
            <span style={{ color: '#64748b' }}>
              {item.parentItemId
                ? `Item này là phân đoạn con tách từ Feedback gốc #${item.parentItemId}`
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
