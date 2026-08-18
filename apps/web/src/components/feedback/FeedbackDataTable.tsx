import React from 'react';
import { Eye, MapPin, Tag } from 'lucide-react';
import { FeedbackWorkspaceItem } from '../../api/feedback';

interface FeedbackDataTableProps {
  items: FeedbackWorkspaceItem[];
  selectedId?: string;
  onSelect: (item: FeedbackWorkspaceItem) => void;
}

const formatDate = (value: string) => {
  try {
    const d = new Date(value);
    const day = String(d.getDate()).padStart(2, '0');
    const month = String(d.getMonth() + 1).padStart(2, '0');
    const year = d.getFullYear();
    const hours = String(d.getHours()).padStart(2, '0');
    const mins = String(d.getMinutes()).padStart(2, '0');
    return `${day}/${month}/${year} ${hours}:${mins}`;
  } catch {
    return value;
  }
};

const renderSentimentBadge = (sentiment: string | null | undefined) => {
  const norm = (sentiment ?? '').toUpperCase();
  if (norm === 'NEGATIVE' || norm === 'TIÊU CỰC') {
    return (
      <span
        style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: 4,
          padding: '3px 8px',
          borderRadius: 12,
          fontSize: 11,
          fontWeight: 700,
          background: '#fef2f2',
          color: '#dc2626',
          border: '1px solid #fca5a5',
          letterSpacing: '0.3px',
        }}
      >
        <span style={{ width: 6, height: 6, borderRadius: '50%', background: '#ef4444' }} />
        TIÊU CỰC
      </span>
    );
  }
  if (norm === 'POSITIVE' || norm === 'TÍCH CỰC') {
    return (
      <span
        style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: 4,
          padding: '3px 8px',
          borderRadius: 12,
          fontSize: 11,
          fontWeight: 700,
          background: '#f0fdf4',
          color: '#16a34a',
          border: '1px solid #86efac',
          letterSpacing: '0.3px',
        }}
      >
        <span style={{ width: 6, height: 6, borderRadius: '50%', background: '#22c55e' }} />
        TÍCH CỰC
      </span>
    );
  }
  return (
    <span
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: 4,
        padding: '3px 8px',
        borderRadius: 12,
        fontSize: 11,
        fontWeight: 600,
        background: '#f8fafc',
        color: '#64748b',
        border: '1px solid #e2e8f0',
        letterSpacing: '0.3px',
      }}
    >
      <span style={{ width: 6, height: 6, borderRadius: '50%', background: '#94a3b8' }} />
      {norm ? 'TRUNG TÍNH' : 'CHƯA PHÂN LOẠI'}
    </span>
  );
};

export const FeedbackDataTable: React.FC<FeedbackDataTableProps> = ({
  items,
  selectedId,
  onSelect,
}) => {
  return (
    <div className="feedback-table-container" style={{ overflowX: 'auto', background: '#ffffff', borderRadius: 8, border: '1px solid #e2e8f0' }}>
      <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: 13 }}>
        <thead>
          <tr style={{ background: '#f8fafc', borderBottom: '1px solid #e2e8f0', color: '#475569', fontSize: 12, fontWeight: 700 }}>
            <th style={{ padding: '12px 14px', minWidth: 260 }}>Tiêu đề phản ánh</th>
            <th style={{ padding: '12px 14px', minWidth: 160 }}>Khu đô thị</th>
            <th style={{ padding: '12px 14px', minWidth: 160 }}>Nhóm dịch vụ</th>
            <th style={{ padding: '12px 14px', width: 130 }}>Cảm xúc</th>
            <th style={{ padding: '12px 14px', width: 130 }}>Kênh phản ánh</th>
            <th style={{ padding: '12px 14px', width: 140 }}>Thời gian ↕</th>
            <th style={{ padding: '12px 14px', width: 70, textAlign: 'center' }}>Chi tiết</th>
          </tr>
        </thead>
        <tbody>
          {items.map((item, idx) => {
            const isSelected = selectedId === item.feedbackItemId;
            const locationName = item.location.name || item.location.code || 'Toàn dự án';
            const serviceName = item.currentClassification.service?.nameVi || 'Chưa phân loại';
            const channel = item.sourceSystem || 'Tại quầy';

            return (
              <tr
                key={item.feedbackItemId}
                onClick={() => onSelect(item)}
                style={{
                  borderBottom: '1px solid #f1f5f9',
                  background: isSelected ? '#f8fafc' : idx % 2 === 0 ? '#ffffff' : '#fafafa',
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
                {/* Tiêu đề phản ánh / Nội dung Masked */}
                <td style={{ padding: '12px 14px', color: '#1e293b' }}>
                  <div style={{ fontWeight: 600, color: '#0f172a', marginBottom: 2, display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden', lineHeight: 1.4 }}>
                    {item.contentMasked}
                  </div>
                  {item.currentClassification.issue?.nameVi && (
                    <span style={{ fontSize: 11, color: '#64748b', display: 'inline-flex', alignItems: 'center', gap: 3, marginTop: 2 }}>
                      <Tag size={10} color="#94a3b8" /> {item.currentClassification.issue.nameVi}
                    </span>
                  )}
                </td>

                {/* Khu đô thị */}
                <td style={{ padding: '12px 14px', color: '#334155' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 5 }}>
                    <MapPin size={13} color="#64748b" style={{ flexShrink: 0 }} />
                    <span style={{ fontWeight: 500 }}>{locationName}</span>
                  </div>
                </td>

                {/* Nhóm dịch vụ */}
                <td style={{ padding: '12px 14px', color: '#334155', fontWeight: 500 }}>
                  {serviceName}
                </td>

                {/* Cảm xúc */}
                <td style={{ padding: '12px 14px' }}>
                  {renderSentimentBadge(item.currentClassification.sentiment)}
                </td>

                {/* Kênh phản ánh */}
                <td style={{ padding: '12px 14px', color: '#475569', fontSize: 12 }}>
                  <span style={{ background: '#f1f5f9', padding: '3px 7px', borderRadius: 4, fontWeight: 500 }}>
                    {channel}
                  </span>
                </td>

                {/* Thời gian */}
                <td style={{ padding: '12px 14px', color: '#64748b', fontSize: 12, whiteSpace: 'nowrap' }}>
                  {formatDate(item.reportedAt)}
                </td>

                {/* Chi tiết Eye Action */}
                <td style={{ padding: '12px 14px', textAlign: 'center' }}>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      onSelect(item);
                    }}
                    style={{
                      display: 'inline-flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      width: 28,
                      height: 28,
                      borderRadius: 6,
                      border: '1px solid #cbd5e1',
                      background: '#ffffff',
                      color: '#475569',
                      cursor: 'pointer',
                      transition: 'all 0.15s ease',
                    }}
                    title="Xem chi tiết"
                    onMouseEnter={(e) => {
                      e.currentTarget.style.background = '#2563eb';
                      e.currentTarget.style.color = '#ffffff';
                      e.currentTarget.style.borderColor = '#2563eb';
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.background = '#ffffff';
                      e.currentTarget.style.color = '#475569';
                      e.currentTarget.style.borderColor = '#cbd5e1';
                    }}
                  >
                    <Eye size={15} />
                  </button>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
};

export default FeedbackDataTable;
