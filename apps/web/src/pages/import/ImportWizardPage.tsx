import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  UploadCloud,
  CheckCircle2,
  AlertCircle,
  Download,
  ArrowRight,
  RefreshCw,
  Sparkles,
} from 'lucide-react';
import TopBar from '../../components/layout/TopBar';
import { directImportCsv, DirectImportResponse } from '../../api/importPipeline';

const STANDARD_COLUMNS = [
  { key: 'noi_dung', label: 'noi_dung', desc: 'Nội dung phản ánh của cư dân / khách hàng (Bắt buộc)', required: true },
  { key: 'khu_do_thi', label: 'khu_do_thi', desc: 'Tên khu đô thị / Vị trí (VD: Vinhomes Smart City)', required: false },
  { key: 'thoi_gian', label: 'thoi_gian', desc: 'Thời điểm phản hồi (VD: 2026-08-18 08:30:00)', required: false },
  { key: 'ma_phan_anh', label: 'ma_phan_anh', desc: 'Mã số phiếu / ID phản hồi (VD: PA-00123)', required: false },
  { key: 'kenh_tiep_nhan', label: 'kenh_tiep_nhan', desc: 'Kênh gửi (VD: App cư dân, Hotline, Quầy)', required: false },
];

const SAMPLE_CSV_CONTENT = `noi_dung,khu_do_thi,thoi_gian,ma_phan_anh,kenh_tiep_nhan
"Cửa barrier cổng hầm quẹt thẻ không nhận vào giờ cao điểm sáng","Vinhomes Smart City","2026-08-15 07:45:00","PA-00101","App cư dân"
"Hành lang tầng 12 tòa S1 có mùi rác bốc lên nồng nặc","Vinhomes Ocean Park","2026-08-16 14:20:00","PA-00102","Tổng đài"
"Nhân viên lễ tân sảnh A hướng dẫn thủ tục nhận nhà rất tận tình","Vinhomes Global Gate","2026-08-17 09:15:00","PA-00103","Tại quầy"
"Hồ bơi cuối tuần nước hơi đục cần lọc vệ sinh thường xuyên hơn","Vinhomes Smart City","2026-08-17 17:30:00","PA-00104","App cư dân"
`;

const formatSize = (bytes: number) => {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
};

const ImportWizardPage: React.FC = () => {
  const navigate = useNavigate();
  const [file, setFile] = useState<File | null>(null);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [result, setResult] = useState<DirectImportResponse | null>(null);

  // Download Sample Template CSV
  const handleDownloadTemplate = () => {
    const blob = new Blob(['\uFEFF' + SAMPLE_CSV_CONTENT], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'mau_nhap_lieu_phan_anh_cx.csv';
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleFileChange = (selectedFile: File | null) => {
    setFile(selectedFile);
    setMessage(null);
    setResult(null);
    if (!selectedFile) return;

    if (!selectedFile.name.toLowerCase().endsWith('.csv')) {
      setMessage('Vui lòng chọn đúng tệp bảng tính định dạng chuẩn .CSV');
    }
  };

  // Direct 1-Click Upload and Ingest
  const handleDirectImport = async () => {
    if (!file) return;
    setBusy(true);
    setMessage(null);
    setResult(null);
    try {
      const res = await directImportCsv(file);
      setResult(res);
    } catch (err) {
      setMessage(err instanceof Error ? err.message : 'Không thể nạp dữ liệu từ tệp.');
    } finally {
      setBusy(false);
    }
  };

  return (
    <>
      <TopBar title="Nhập dữ liệu" subtitle="Tải lên và nạp nhanh tệp dữ liệu phản ánh (.CSV)" />
      <main className="page-content" style={{ padding: '24px 28px', maxWidth: 860, margin: '0 auto', display: 'flex', flexDirection: 'column', gap: 20 }}>
        {/* Header with Template Download Button */}
        <div className="card" style={{ padding: '18px 22px', borderRadius: 8, display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 12 }}>
          <div>
            <h2 style={{ fontSize: 18, fontWeight: 800, color: '#0f172a', margin: '0 0 4px 0' }}>
              Nạp dữ liệu phản ánh khách hàng
            </h2>
            <p style={{ fontSize: 13, color: '#64748b', margin: 0 }}>
              Chọn tệp <strong>.CSV</strong> theo mẫu chuẩn để nạp trực tiếp vào hệ thống ngay lập tức.
            </p>
          </div>

          <button
            onClick={handleDownloadTemplate}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: 6,
              padding: '9px 15px',
              borderRadius: 6,
              background: '#eff6ff',
              color: '#2563eb',
              border: '1px solid #bfdbfe',
              fontWeight: 700,
              fontSize: 13,
              cursor: 'pointer',
            }}
          >
            <Download size={16} />
            Tải tệp mẫu chuẩn (.CSV)
          </button>
        </div>

        {/* Standard Columns Specification Box */}
        <div style={{ background: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: 8, padding: '16px 20px' }}>
          <div style={{ fontSize: 12, fontWeight: 700, color: '#334155', marginBottom: 10, textTransform: 'uppercase', letterSpacing: '0.4px' }}>
            📋 Quy định các cột trong tệp CSV mẫu:
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 10 }}>
            {STANDARD_COLUMNS.map((col) => (
              <div key={col.key} style={{ background: '#ffffff', border: '1px solid #cbd5e1', borderRadius: 6, padding: '8px 12px' }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 2 }}>
                  <code style={{ fontSize: 13, fontWeight: 700, color: col.required ? '#dc2626' : '#2563eb' }}>{col.label}</code>
                  <span style={{ fontSize: 10, fontWeight: 700, color: col.required ? '#dc2626' : '#64748b' }}>
                    {col.required ? 'Bắt buộc' : 'Tùy chọn'}
                  </span>
                </div>
                <span style={{ fontSize: 11, color: '#64748b', lineHeight: 1.3, display: 'block' }}>{col.desc}</span>
              </div>
            ))}
          </div>
        </div>

        {message && (
          <div style={{ padding: '12px 16px', background: '#fef2f2', border: '1px solid #fca5a5', borderRadius: 8, color: '#b91c1c', fontSize: 13, display: 'flex', alignItems: 'center', gap: 8 }}>
            <AlertCircle size={16} style={{ flexShrink: 0 }} />
            <span>{message}</span>
          </div>
        )}

        {/* Main Upload Box */}
        <div className="card" style={{ padding: '32px 28px', borderRadius: 10, minHeight: 280, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
          {result ? (
            /* Result Success View */
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', textAlign: 'center', gap: 16 }}>
              <div style={{ width: 64, height: 64, borderRadius: '50%', background: '#dcfce7', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <CheckCircle2 size={38} color="#16a34a" />
              </div>

              <div>
                <h3 style={{ fontSize: 19, fontWeight: 800, color: '#0f172a', margin: '0 0 6px 0' }}>
                  Nạp dữ liệu phản ánh thành công!
                </h3>
                <p style={{ fontSize: 14, color: '#15803d', margin: 0, fontWeight: 600 }}>
                  Đã ghi nhận thành công {result.imported_rows.toLocaleString()} / {result.total_rows.toLocaleString()} phản ánh vào hệ thống.
                </p>
              </div>

              <div style={{ display: 'flex', gap: 12, marginTop: 10 }}>
                <button
                  onClick={() => navigate('/feedback')}
                  style={{
                    padding: '10px 22px',
                    borderRadius: 6,
                    background: '#2563eb',
                    color: '#ffffff',
                    border: 'none',
                    fontSize: 13,
                    fontWeight: 700,
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: 6,
                    boxShadow: '0 4px 12px rgba(37,99,235,0.25)',
                  }}
                >
                  <span>Xem danh sách phản hồi vừa nạp</span>
                  <ArrowRight size={15} />
                </button>

                <button
                  onClick={() => {
                    setFile(null);
                    setResult(null);
                    setMessage(null);
                  }}
                  style={{
                    padding: '10px 18px',
                    borderRadius: 6,
                    background: '#ffffff',
                    color: '#475569',
                    border: '1px solid #cbd5e1',
                    fontSize: 13,
                    fontWeight: 600,
                    cursor: 'pointer',
                  }}
                >
                  Nhập thêm tệp khác
                </button>
              </div>
            </div>
          ) : (
            /* Upload Action View */
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', textAlign: 'center', gap: 18, width: '100%' }}>
              <label
                style={{
                  width: '100%',
                  maxWidth: 540,
                  border: file ? '2px solid #22c55e' : '2px dashed #cbd5e1',
                  borderRadius: 10,
                  padding: '36px 24px',
                  background: file ? '#f0fdf4' : '#fafafa',
                  cursor: 'pointer',
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  gap: 12,
                  transition: 'all 0.2s ease',
                }}
                onMouseEnter={(e) => {
                  if (!file) e.currentTarget.style.borderColor = '#2563eb';
                }}
                onMouseLeave={(e) => {
                  if (!file) e.currentTarget.style.borderColor = '#cbd5e1';
                }}
              >
                <input
                  type="file"
                  accept=".csv,text/csv"
                  style={{ display: 'none' }}
                  onChange={(e) => handleFileChange(e.target.files?.[0] ?? null)}
                />
                <UploadCloud size={40} color={file ? '#16a34a' : '#2563eb'} />
                <span style={{ fontSize: 14, fontWeight: 700, color: '#0f172a' }}>
                  {file ? file.name : 'Nhấp để chọn tệp .CSV hoặc kéo thả file vào đây'}
                </span>
                <span style={{ fontSize: 12, color: '#64748b' }}>
                  {file ? `Dung lượng: ${formatSize(file.size)} · Sẵn sàng nạp` : 'Hỗ trợ tệp bảng tính định dạng chuẩn .CSV'}
                </span>
              </label>

              <button
                onClick={handleDirectImport}
                disabled={!file || busy}
                style={{
                  padding: '11px 32px',
                  borderRadius: 6,
                  background: !file || busy ? '#94a3b8' : '#2563eb',
                  color: '#ffffff',
                  border: 'none',
                  fontSize: 14,
                  fontWeight: 700,
                  cursor: !file || busy ? 'not-allowed' : 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: 8,
                  boxShadow: file ? '0 4px 12px rgba(37,99,235,0.25)' : 'none',
                }}
              >
                {busy ? (
                  <>
                    <RefreshCw size={16} className="spin" />
                    <span>Đang nạp dữ liệu vào hệ thống...</span>
                  </>
                ) : (
                  <>
                    <span>Tải lên & Nạp dữ liệu ngay</span>
                    <Sparkles size={16} />
                  </>
                )}
              </button>
            </div>
          )}
        </div>
      </main>
    </>
  );
};

export default ImportWizardPage;
