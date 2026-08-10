import React, { useEffect, useState } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Filter, MessageSquare, ChevronRight, Eye } from 'lucide-react';
import { api } from '../../client/api';
import { FeedbackItem, FeedbackListResponse } from '../../client/types';

interface FeedbackListViewProps {
  onSelectDetail?: (itemId: string) => void;
}

export const FeedbackListView: React.FC<FeedbackListViewProps> = ({ onSelectDetail }) => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  const [data, setData] = useState<FeedbackListResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchItems = async () => {
    setLoading(true);
    setError(null);
    try {
      const paramsObj = Object.fromEntries(searchParams.entries());
      const res = await api.getFeedbackItems(paramsObj);
      setData(res);
    } catch (err: any) {
      setError(err.message || 'Không thể tải danh sách feedback');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchItems();
  }, [searchParams.toString()]);

  const activeFiltersSummary = Array.from(searchParams.entries())
    .map(([key, val]) => `${key}: ${val}`)
    .join(' • ');

  const getSentimentBadgeClass = (s: string) => {
    if (s === 'POSITIVE') return 'badge-pos';
    if (s === 'NEGATIVE') return 'badge-neg';
    return 'badge-neu';
  };

  const getSeverityBadgeClass = (s: string) => {
    if (s === 'CRITICAL' || s === 'HIGH') return 'badge-high';
    if (s === 'MEDIUM') return 'badge-med';
    return 'badge-low';
  };

  return (
    <div>
      <button 
        onClick={() => navigate(`/dashboard?${searchParams.toString()}`)} 
        className="btn-secondary" 
        style={{ marginBottom: 20 }}
      >
        <ArrowLeft size={16} /> Quay lại Dashboard (Giữ Filter)
      </button>

      <div className="glass-panel" style={{ padding: 24, marginBottom: 24 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 16 }}>
          <div>
            <h1 className="heading-lg" style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
              <MessageSquare size={24} style={{ color: 'var(--accent-cyan)' }} /> Danh Sách Feedback Drill-Down
            </h1>
            {activeFiltersSummary && (
              <p className="subtext" style={{ marginTop: 6, display: 'flex', alignItems: 'center', gap: 6 }}>
                <Filter size={14} /> Ngữ cảnh lọc: <code>{activeFiltersSummary}</code>
              </p>
            )}
          </div>
          <span className="badge badge-neu">DỮ LIỆU ĐÃ CHE MỜ (MASKED)</span>
        </div>
      </div>

      {loading ? (
        <div className="glass-panel" style={{ padding: 40, textAlign: 'center' }}>
          <p className="subtext">Đang tải danh sách feedback drill-down...</p>
        </div>
      ) : error ? (
        <div className="glass-panel" style={{ padding: 24, color: '#fb7185' }}>{error}</div>
      ) : data?.items.length === 0 ? (
        <div className="glass-panel" style={{ padding: 40, textAlign: 'center' }}>
          <h3 className="heading-md" style={{ marginBottom: 8 }}>Không có dữ liệu feedback phù hợp</h3>
          <p className="subtext" style={{ marginBottom: 16 }}>Vui lòng thay đổi hoặc xóa bớt tiêu chí lọc trên Dashboard.</p>
          <button className="btn-secondary" onClick={() => navigate('/dashboard')}>Về Dashboard</button>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          {data?.items.map((item: FeedbackItem) => (
            <div 
              key={item.feedback_item_id} 
              className="glass-panel" 
              style={{ padding: 20, transition: 'all 0.2s ease', cursor: 'pointer' }}
              onClick={() => onSelectDetail ? onSelectDetail(item.feedback_item_id) : navigate(`/feedback/${item.feedback_item_id}`)}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 12, flexWrap: 'wrap', gap: 12 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                  <code>{item.feedback_item_id}</code>
                  <span style={{ fontSize: '0.8125rem', color: 'var(--text-muted)' }}>
                    {new Date(item.created_at).toLocaleString('vi-VN')}
                  </span>
                </div>
                <div style={{ display: 'flex', gap: 8 }}>
                  <span className={`badge ${getSentimentBadgeClass(item.sentiment)}`}>
                    {item.sentiment}
                  </span>
                  <span className={`badge ${getSeverityBadgeClass(item.severity)}`}>
                    {item.severity}
                  </span>
                </div>
              </div>

              <div style={{ fontSize: '0.9375rem', color: 'var(--text-primary)', marginBottom: 12, lineHeight: 1.6 }}>
                "{item.masked_text}"
              </div>

              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.8125rem', color: 'var(--text-secondary)' }}>
                <div>
                  <strong style={{ color: 'var(--text-primary)' }}>{item.service_name}</strong> • {item.location_name}
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 4, color: 'var(--accent-indigo)', fontWeight: 600 }}>
                  <Eye size={14} /> Chi tiết provenance <ChevronRight size={14} />
                </div>
              </div>
            </div>
          ))}

          {/* Cursor Pagination */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: 16 }}>
            <button className="btn-secondary" disabled>← Trang trước</button>
            <span style={{ fontSize: '0.8125rem', color: 'var(--text-muted)' }}>Hiển thị dạng Cursor Pagination</span>
            <button className="btn-secondary" disabled={!data?.has_more}>Trang tiếp theo →</button>
          </div>
        </div>
      )}
    </div>
  );
};
