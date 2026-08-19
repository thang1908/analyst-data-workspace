import React from 'react';
import { Eye, MapPin, Tag, Compass, Navigation } from 'lucide-react';
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
  let badgeStyle = { background: '#f8fafc', color: '#64748b', border: '1px solid #e2e8f0', dot: '#94a3b8', text: norm ? 'TRUNG TÍNH' : 'CHƯA GÁN' };

  if (norm === 'NEGATIVE' || norm === 'TIÊU CỰC') {
    badgeStyle = { background: '#fef2f2', color: '#dc2626', border: '1px solid #fca5a5', dot: '#ef4444', text: 'TIÊU CỰC' };
  } else if (norm === 'POSITIVE' || norm === 'TÍCH CỰC') {
    badgeStyle = { background: '#f0fdf4', color: '#16a34a', border: '1px solid #86efac', dot: '#22c55e', text: 'TÍCH CỰC' };
  }

  return (
    <span
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: 5,
        padding: '3px 9px',
        borderRadius: 12,
        fontSize: 11,
        fontWeight: 700,
        background: badgeStyle.background,
        color: badgeStyle.color,
        border: badgeStyle.border,
        letterSpacing: '0.2px',
        whiteSpace: 'nowrap',
      }}
    >
      <span style={{ width: 6, height: 6, borderRadius: '50%', background: badgeStyle.dot }} />
      {badgeStyle.text}
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
      <table style={{ width: '100%', minWidth: 1250, borderCollapse: 'collapse', textAlign: 'left', fontSize: 13 }}>
        <thead>
          <tr style={{ background: '#f8fafc', borderBottom: '1px solid #e2e8f0', color: '#475569', fontSize: 12, fontWeight: 700 }}>
            <th style={{ padding: '12px 14px', minWidth: 320 }}>Nội dung phản ánh</th>
            <th style={{ padding: '12px 14px', width: 160 }}>Khu đô thị</th>
            <th style={{ padding: '12px 14px', width: 170 }}>Dịch vụ</th>
            <th style={{ padding: '12px 14px', width: 180 }}>Vấn đề</th>
            <th style={{ padding: '12px 14px', width: 160 }}>Bước hành trình</th>
            <th style={{ padding: '12px 14px', width: 160 }}>Điểm chạm</th>
            <th style={{ padding: '12px 14px', width: 110 }}>Cảm xúc</th>
            <th style={{ padding: '12px 14px', width: 130 }}>Thời gian ↕</th>
            <th style={{ padding: '12px 14px', width: 60, textAlign: 'center' }}>Xem</th>
          </tr>
        </thead>
        <tbody>
          {items.map((item, idx) => {
            const isSelected = selectedId === item.feedbackItemId;
            const locationName = item.location.name || item.location.code || 'Toàn dự án';
            const service = item.currentClassification.service;
            const issue = item.currentClassification.issue;
            const journeyStep = item.currentClassification.journeyStep;
            const touchpoint = item.currentClassification.touchpoint;

            return (
              <tr
                key={item.feedbackItemId}
                onClick={() => onSelect(item)}
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
                {/* Nội dung phản ánh Masked - Hiển thị đầy đủ, không bị cắt */}
                <td style={{ padding: '12px 14px', color: '#1e293b' }}>
                  <div style={{ fontWeight: 600, color: '#0f172a', lineHeight: 1.5, wordBreak: 'break-word' }}>
                    {item.contentMasked}
                  </div>
                </td>

                {/* Khu đô thị */}
                <td style={{ padding: '12px 14px', color: '#334155' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 5 }}>
                    <MapPin size={13} color="#64748b" style={{ flexShrink: 0 }} />
                    <span style={{ fontWeight: 500 }}>{locationName}</span>
                  </div>
                </td>

                {/* Dịch vụ */}
                <td style={{ padding: '12px 14px', color: '#334155', fontWeight: 500 }}>
                  {service?.nameVi || 'Chưa phân loại'}
                </td>

                {/* Vấn đề */}
                <td style={{ padding: '12px 14px', color: '#334155' }}>
                  {issue?.nameVi || 'Chưa phân loại'}
                </td>

                {/* Bước hành trình */}
                <td style={{ padding: '12px 14px', color: '#334155', fontWeight: 500 }}>
                  {journeyStep?.nameVi || journeyStep?.code || '-'}
                </td>

                {/* Điểm chạm (Touchpoint) */}
                <td style={{ padding: '12px 14px', color: '#334155' }}>
                  {touchpoint?.nameVi || touchpoint?.code || '-'}
                </td>

                {/* Cảm xúc */}
                <td style={{ padding: '12px 14px' }}>
                  {renderSentimentBadge(item.currentClassification.sentiment)}
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
                    title="Xem & Hiệu chỉnh chi tiết"
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
