import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { CheckCircle2, AlertTriangle, Play, RefreshCw, BarChart2, ArrowLeft } from 'lucide-react';
import { api } from '../../client/api';
import { ImportJob } from '../../client/types';

export const JobDetailView: React.FC = () => {
  const { jobId } = useParams<{ jobId: string }>();
  const navigate = useNavigate();

  const [job, setJob] = useState<ImportJob | null>(null);
  const [loading, setLoading] = useState(true);
  const [executing, setExecuting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchJob = async () => {
    if (!jobId) return;
    setLoading(true);
    try {
      const data = await api.getImportJob(jobId);
      setJob(data);
    } catch (err: any) {
      setError(err.message || 'Không thể tải thông tin Import Job');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchJob();
  }, [jobId]);

  const handleExecute = async () => {
    if (!jobId || !job) return;
    setExecuting(true);
    setError(null);
    try {
      const updated = await api.executeImportJob(jobId);
      setJob(updated);
    } catch (err: any) {
      setError(err.message || 'Không thể thực thi Import Job');
    } finally {
      setExecuting(false);
    }
  };

  if (loading) {
    return (
      <div className="glass-panel" style={{ padding: 32, textAlign: 'center' }}>
        <RefreshCw size={32} className="skeleton" style={{ margin: '0 auto 16px' }} />
        <p className="subtext">Đang tải thông tin tiến trình Import Job...</p>
      </div>
    );
  }

  if (error || !job) {
    return (
      <div className="glass-panel" style={{ padding: 32, textAlign: 'center' }}>
        <AlertTriangle size={32} style={{ color: '#fb7185', margin: '0 auto 16px' }} />
        <h2 className="heading-md" style={{ marginBottom: 8 }}>Đã xảy ra lỗi</h2>
        <p className="subtext" style={{ marginBottom: 20 }}>{error || 'Không tìm thấy thông tin Job'}</p>
        <button onClick={() => navigate('/imports')} className="btn-secondary">
          Quay lại danh sách
        </button>
      </div>
    );
  }

  return (
    <div style={{ maxWidth: 960, margin: '0 auto' }}>
      <button 
        onClick={() => navigate('/imports')} 
        className="btn-secondary" 
        style={{ marginBottom: 20 }}
      >
        <ArrowLeft size={16} /> Danh Sách Jobs
      </button>

      <div className="glass-panel" style={{ padding: 32, marginBottom: 24 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 20 }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 8 }}>
              <h1 className="heading-lg">{job.filename}</h1>
              <span className={`badge ${job.status === 'COMMITTED' ? 'badge-pos' : 'badge-neu'}`}>
                {job.status}
              </span>
            </div>
            <p className="subtext">
              Job ID: <code>{job.import_job_id}</code> • Upload lúc {new Date(job.uploaded_at).toLocaleString('vi-VN')}
            </p>
          </div>

          {job.status === 'COMMITTED' ? (
            <button 
              className="btn-primary" 
              onClick={() => navigate('/dashboard')}
            >
              <BarChart2 size={16} /> Xem Dashboard
            </button>
          ) : (
            <button 
              className="btn-primary" 
              onClick={handleExecute}
              disabled={!job.can_execute || executing}
            >
              <Play size={16} /> {executing ? 'Đang Xử Lý...' : 'Thực Thi Import (Execute Valid)'}
            </button>
          )}
        </div>

        {/* Counts summary grid */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: 16, marginTop: 24 }}>
          <div style={{ background: 'rgba(255, 255, 255, 0.03)', padding: 16, borderRadius: 12, border: '1px solid var(--border-color)' }}>
            <div className="subtext" style={{ fontSize: '0.75rem' }}>TỔNG SỐ DÒNG</div>
            <div style={{ fontSize: '1.5rem', fontWeight: 700, marginTop: 4 }}>{job.counts?.total_rows.toLocaleString() || job.total_rows}</div>
          </div>
          <div style={{ background: 'rgba(16, 185, 129, 0.08)', padding: 16, borderRadius: 12, border: '1px solid rgba(16, 185, 129, 0.2)' }}>
            <div className="subtext" style={{ fontSize: '0.75rem', color: '#34d399' }}>HỢP LỆ (VALID)</div>
            <div style={{ fontSize: '1.5rem', fontWeight: 700, marginTop: 4, color: '#34d399' }}>
              {job.counts?.valid_rows.toLocaleString() || 0}
            </div>
          </div>
          <div style={{ background: 'rgba(244, 63, 94, 0.08)', padding: 16, borderRadius: 12, border: '1px solid rgba(244, 63, 94, 0.2)' }}>
            <div className="subtext" style={{ fontSize: '0.75rem', color: '#fb7185' }}>KHÔNG HỢP LỆ (INVALID)</div>
            <div style={{ fontSize: '1.5rem', fontWeight: 700, marginTop: 4, color: '#fb7185' }}>
              {job.counts?.invalid_rows.toLocaleString() || 0}
            </div>
          </div>
          <div style={{ background: 'rgba(245, 158, 11, 0.08)', padding: 16, borderRadius: 12, border: '1px solid rgba(245, 158, 11, 0.2)' }}>
            <div className="subtext" style={{ fontSize: '0.75rem', color: '#fbbf24' }}>TRÙNG LẶP (DUPLICATE)</div>
            <div style={{ fontSize: '1.5rem', fontWeight: 700, marginTop: 4, color: '#fbbf24' }}>
              {job.counts?.duplicate_rows.toLocaleString() || 0}
            </div>
          </div>
        </div>
      </div>

      {/* Errors sample list if present */}
      {job.errors_sample && job.errors_sample.length > 0 && (
        <div className="glass-panel" style={{ padding: 24 }}>
          <h3 className="heading-md" style={{ marginBottom: 16, display: 'flex', alignItems: 'center', gap: 8 }}>
            <AlertTriangle size={18} style={{ color: '#fb7185' }} /> Mẫu Lỗi Validate ({job.errors_sample.length})
          </h3>
          <div className="table-container">
            <table className="custom-table">
              <thead>
                <tr>
                  <th>Dòng</th>
                  <th>Cột</th>
                  <th>Mã Lỗi</th>
                  <th>Chi Tiết Thông Báo</th>
                </tr>
              </thead>
              <tbody>
                {job.errors_sample.map((err, idx) => (
                  <tr key={idx}>
                    <td><code>#{err.row_number}</code></td>
                    <td><code>{err.column_name}</code></td>
                    <td><span className="badge badge-neg">{err.error_code}</span></td>
                    <td style={{ color: '#94a3b8' }}>{err.message}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};
