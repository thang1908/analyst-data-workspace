import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { UploadCloud, FileText, CheckCircle2, AlertCircle, ArrowLeft } from 'lucide-react';
import { api } from '../../client/api';

export const UploadView: React.FC = () => {
  const navigate = useNavigate();
  const [file, setFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selected = e.target.files[0];
      if (!selected.name.endsWith('.csv')) {
        setError('Chỉ chấp nhận file định dạng .csv chuẩn trusted-feedback-csv/v1');
        setFile(null);
        return;
      }
      if (selected.size > 15 * 1024 * 1024) {
        setError('Kích thước file không được vượt quá 15MB');
        setFile(null);
        return;
      }
      setError(null);
      setFile(selected);
    }
  };

  const handleUpload = async () => {
    if (!file) return;
    setIsUploading(true);
    setError(null);

    try {
      const job = await api.uploadCsv(file);
      navigate(`/imports/${job.import_job_id}`);
    } catch (err: any) {
      setError(err.message || 'Không thể upload file CSV. Vui lòng thử lại.');
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div style={{ maxWidth: 800, margin: '0 auto', padding: '24px 0' }}>
      <button 
        onClick={() => navigate('/imports')}
        className="btn-secondary" 
        style={{ marginBottom: 20 }}
      >
        <ArrowLeft size={16} /> Quay lại danh sách Job
      </button>

      <div className="glass-panel" style={{ padding: 32 }}>
        <h1 className="heading-lg" style={{ marginBottom: 8 }}>Upload File CSV Trusted</h1>
        <p className="subtext" style={{ marginBottom: 24 }}>
          Tải lên dữ liệu phản ánh khách hàng đã được che mờ (masked) theo hợp đồng định dạng <code>trusted-feedback-csv/v1</code>.
        </p>

        {error && (
          <div style={{ 
            background: 'rgba(244, 63, 94, 0.15)', 
            border: '1px solid rgba(244, 63, 94, 0.4)', 
            borderRadius: 8, 
            padding: 16, 
            marginBottom: 24, 
            display: 'flex', 
            alignItems: 'center', 
            gap: 12, 
            color: '#fb7185' 
          }}>
            <AlertCircle size={20} />
            <span>{error}</span>
          </div>
        )}

        <div style={{
          border: '2px dashed rgba(99, 102, 241, 0.3)',
          borderRadius: 16,
          padding: 40,
          textAlign: 'center',
          background: 'rgba(15, 23, 42, 0.4)',
          transition: 'all 0.2s ease',
          marginBottom: 24
        }}>
          <UploadCloud size={48} style={{ color: '#818cf8', marginBottom: 16 }} />
          <h3 className="heading-md" style={{ marginBottom: 8 }}>Kéo và thả file CSV vào đây</h3>
          <p className="subtext" style={{ marginBottom: 16 }}>Hoặc chọn file từ máy tính của bạn (tối đa 15MB)</p>
          
          <input 
            type="file" 
            accept=".csv" 
            id="csv-file-input" 
            onChange={handleFileChange}
            style={{ display: 'none' }}
          />
          <label htmlFor="csv-file-input" className="btn-secondary" style={{ cursor: 'pointer' }}>
            <FileText size={16} /> Chọn File CSV
          </label>
        </div>

        {file && (
          <div style={{ 
            background: 'rgba(255, 255, 255, 0.05)', 
            borderRadius: 12, 
            padding: 16, 
            marginBottom: 24, 
            display: 'flex', 
            alignItems: 'center', 
            justifyContent: 'space-between' 
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
              <FileText size={24} style={{ color: '#06b6d4' }} />
              <div>
                <div style={{ fontWeight: 600, color: '#f8fafc' }}>{file.name}</div>
                <div style={{ fontSize: '0.75rem', color: '#94a3b8' }}>
                  {(file.size / (1024 * 1024)).toFixed(2)} MB • trusted-feedback-csv/v1
                </div>
              </div>
            </div>
            <CheckCircle2 size={20} style={{ color: '#34d399' }} />
          </div>
        )}

        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 12 }}>
          <button 
            className="btn-secondary" 
            onClick={() => navigate('/imports')} 
            disabled={isUploading}
          >
            Hủy bỏ
          </button>
          <button 
            className="btn-primary" 
            onClick={handleUpload} 
            disabled={!file || isUploading}
          >
            {isUploading ? 'Đang Upload...' : 'Upload & Kiểm Tra Dữ Liệu'}
          </button>
        </div>
      </div>
    </div>
  );
};
