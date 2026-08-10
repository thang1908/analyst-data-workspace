import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Shield, FileSpreadsheet, Lock, CheckCircle2 } from 'lucide-react';
import { api } from '../../client/api';
import { FeedbackDetail } from '../../client/types';

export const FeedbackDetailView: React.FC = () => {
  const { itemId } = useParams<{ itemId: string }>();
  const navigate = useNavigate();

  const [detail, setDetail] = useState<FeedbackDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!itemId) return;
    setLoading(true);
    api.getFeedbackDetail(itemId)
      .then(setDetail)
      .catch(err => setError(err.message || 'Không tìm thấy hoặc bạn không có quyền xem feedback này'))
      .finally(() => setLoading(false));
  }, [itemId]);

  if (loading) {
    return (
      <div className="glass-panel" style={{ padding: 40, textAlign: 'center' }}>
        <p className="subtext">Đang tải thông tin chi tiết feedback và nguồn gốc dữ liệu (provenance)...</p>
      </div>
    );
  }

  if (error || !detail) {
    return (
      <div className="glass-panel" style={{ padding: 32, textAlign: 'center' }}>
        <h2 className="heading-md" style={{ marginBottom: 8, color: '#fb7185' }}>{error || 'Không tìm thấy dữ liệu'}</h2>
        <button onClick={() => navigate('/feedback')} className="btn-secondary" style={{ marginTop: 16 }}>
          Quay lại danh sách
        </button>
      </div>
    );
  }

  return (
    <div style={{ maxWidth: 800, margin: '0 auto' }}>
      <button 
        onClick={() => navigate('/feedback')} 
        className="btn-secondary" 
        style={{ marginBottom: 20 }}
      >
        <ArrowLeft size={16} /> Danh Sách Feedback
      </button>

      <div className="glass-panel" style={{ padding: 32, marginBottom: 24 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
          <span style={{ fontSize: '0.875rem', fontWeight: 600, color: 'var(--accent-cyan)' }}>
            FEEDBACK ITEM ID: {detail.feedback_item_id}
          </span>
          <div style={{ display: 'flex', gap: 8 }}>
            <span className={`badge ${detail.sentiment === 'NEGATIVE' ? 'badge-neg' : 'badge-pos'}`}>
              {detail.sentiment}
            </span>
            <span className="badge badge-high">{detail.severity}</span>
          </div>
        </div>

        <h2 className="heading-md" style={{ marginBottom: 12 }}>{detail.service_name} • {detail.issue_name}</h2>
        <p className="subtext" style={{ marginBottom: 24 }}>Vị trí: {detail.location_name} • Ngày ghi nhận: {new Date(detail.created_at).toLocaleString('vi-VN')}</p>

        <div style={{ background: 'rgba(15, 23, 42, 0.6)', padding: 20, borderRadius: 12, border: '1px solid var(--border-color)', marginBottom: 24 }}>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: 8, display: 'flex', alignItems: 'center', gap: 4 }}>
            <Lock size={12} /> NỘI DUNG ĐÃ ĐƯỢC MASKED (BẢO VỆ PII):
          </div>
          <div style={{ fontSize: '1rem', lineHeight: 1.6, color: 'var(--text-primary)' }}>
            "{detail.masked_text}"
          </div>
        </div>
      </div>

      {/* Provenance Panel */}
      <div className="glass-panel" style={{ padding: 24 }}>
        <h3 className="heading-md" style={{ marginBottom: 16, display: 'flex', alignItems: 'center', gap: 8 }}>
          <Shield size={20} style={{ color: 'var(--accent-indigo)' }} /> Nguồn Gốc Dữ Liệu & Audit Provenance
        </h3>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: 16 }}>
          <div style={{ background: 'rgba(255, 255, 255, 0.03)', padding: 16, borderRadius: 12 }}>
            <div className="subtext" style={{ fontSize: '0.75rem' }}>IMPORT JOB</div>
            <div style={{ fontWeight: 600, marginTop: 4 }}><code>{detail.provenance.import_job_id}</code></div>
          </div>
          <div style={{ background: 'rgba(255, 255, 255, 0.03)', padding: 16, borderRadius: 12 }}>
            <div className="subtext" style={{ fontSize: '0.75rem' }}>FILE NGUỒN CSV</div>
            <div style={{ fontWeight: 600, marginTop: 4, display: 'flex', alignItems: 'center', gap: 6 }}>
              <FileSpreadsheet size={16} style={{ color: 'var(--accent-cyan)' }} />
              {detail.provenance.source_reference}
            </div>
          </div>
          <div style={{ background: 'rgba(255, 255, 255, 0.03)', padding: 16, borderRadius: 12 }}>
            <div className="subtext" style={{ fontSize: '0.75rem' }}>DÒNG DỮ LIỆU</div>
            <div style={{ fontWeight: 600, marginTop: 4 }}>Dòng #{detail.provenance.row_index}</div>
          </div>
          <div style={{ background: 'rgba(255, 255, 255, 0.03)', padding: 16, borderRadius: 12 }}>
            <div className="subtext" style={{ fontSize: '0.75rem' }}>QUYẾT ĐỊNH PHÂN LOẠI</div>
            <div style={{ fontWeight: 600, marginTop: 4, color: 'var(--sentiment-pos-text)', display: 'flex', alignItems: 'center', gap: 4 }}>
              <CheckCircle2 size={16} /> {detail.provenance.decision}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
