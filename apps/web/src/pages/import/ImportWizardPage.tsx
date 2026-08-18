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
  FileSpreadsheet,
} from 'lucide-react';
import TopBar from '../../components/layout/TopBar';
import { directImportCsv, DirectImportResponse } from '../../api/importPipeline';

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

    const name = selectedFile.name.toLowerCase();
    if (!name.endsWith('.csv') && !name.endsWith('.tsv') && !name.endsWith('.txt')) {
      setMessage('Vui lòng chọn tệp bảng tính có định dạng .CSV hoặc .TSV');
    }
  };

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
      <TopBar title="Nhập dữ liệu" subtitle="Nạp nhanh tệp dữ liệu phản ánh khách hàng" />
      <main className="page-content" style={{ padding: '32px 28px', maxWidth: 780, margin: '0 auto', display: 'flex', flexDirection: 'column', gap: 20 }}>
        {/* Main Card */}
        <div className="card" style={{ padding: '32px 36px', borderRadius: 12, display: 'flex', flexDirection: 'column', gap: 24, boxShadow: '0 1px 3px rgba(0,0,0,0.05)' }}>
          {/* Header */}
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderBottom: '1px solid #f1f5f9', paddingBottom: 16 }}>
            <h2 style={{ fontSize: 18, fontWeight: 800, color: '#0f172a', margin: 0 }}>
              Tải lên tệp phản ánh (.CSV)
            </h2>

            <button
              onClick={handleDownloadTemplate}
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: 6,
                padding: '8px 14px',
                borderRadius: 6,
                background: '#f8fafc',
                color: '#2563eb',
                border: '1px solid #e2e8f0',
                fontWeight: 600,
                fontSize: 12,
                cursor: 'pointer',
                flexShrink: 0,
                transition: 'all 0.15s ease',
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.background = '#eff6ff';
                e.currentTarget.style.borderColor = '#bfdbfe';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = '#f8fafc';
                e.currentTarget.style.borderColor = '#e2e8f0';
              }}
            >
              <Download size={14} />
              <span>Tải file CSV mẫu</span>
            </button>
          </div>

          {message && (
            <div style={{ padding: '12px 16px', background: '#fef2f2', border: '1px solid #fca5a5', borderRadius: 8, color: '#b91c1c', fontSize: 13, display: 'flex', alignItems: 'center', gap: 8 }}>
              <AlertCircle size={16} style={{ flexShrink: 0 }} />
              <span>{message}</span>
            </div>
          )}

          {result ? (
            /* Success State */
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', textAlign: 'center', gap: 16, padding: '20px 0' }}>
              <div style={{ width: 56, height: 56, borderRadius: '50%', background: '#dcfce7', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <CheckCircle2 size={32} color="#16a34a" />
              </div>

              <div>
                <h3 style={{ fontSize: 18, fontWeight: 800, color: '#0f172a', margin: '0 0 6px 0' }}>
                  Nạp dữ liệu thành công!
                </h3>
                <p style={{ fontSize: 13, color: '#475569', margin: 0 }}>
                  Đã ghi nhận <strong>{result.imported_rows.toLocaleString()}</strong> phản ánh vào kho dữ liệu.
                </p>
              </div>

              <div style={{ display: 'flex', gap: 12, marginTop: 12 }}>
                <button
                  onClick={() => navigate('/feedback')}
                  style={{
                    padding: '9px 20px',
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
                    boxShadow: '0 2px 8px rgba(37,99,235,0.2)',
                  }}
                >
                  <span>Xem danh sách phản hồi</span>
                  <ArrowRight size={14} />
                </button>

                <button
                  onClick={() => {
                    setFile(null);
                    setResult(null);
                    setMessage(null);
                  }}
                  style={{
                    padding: '9px 16px',
                    borderRadius: 6,
                    background: '#ffffff',
                    color: '#475569',
                    border: '1px solid #cbd5e1',
                    fontSize: 13,
                    fontWeight: 600,
                    cursor: 'pointer',
                  }}
                >
                  Nhập tệp khác
                </button>
              </div>
            </div>
          ) : (
            /* Upload Zone */
            <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
              <label
                style={{
                  width: '100%',
                  border: file ? '2px solid #22c55e' : '2px dashed #cbd5e1',
                  borderRadius: 10,
                  padding: '40px 24px',
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
                  accept=".csv,.tsv,.txt,text/csv,text/tab-separated-values"
                  style={{ display: 'none' }}
                  onChange={(e) => handleFileChange(e.target.files?.[0] ?? null)}
                />
                {file ? (
                  <FileSpreadsheet size={40} color="#16a34a" />
                ) : (
                  <UploadCloud size={40} color="#64748b" />
                )}
                <div>
                  <span style={{ fontSize: 14, fontWeight: 700, color: '#0f172a', display: 'block' }}>
                    {file ? file.name : 'Nhấp để chọn tệp (.CSV / .TSV) hoặc kéo thả vào đây'}
                  </span>
                  <span style={{ fontSize: 12, color: '#64748b', display: 'block', marginTop: 4 }}>
                    {file ? `Dung lượng: ${formatSize(file.size)} · Đã sẵn sàng` : 'Hỗ trợ định dạng bảng tính .CSV hoặc .TSV (UTF-8)'}
                  </span>
                </div>
              </label>

              {/* Action Buttons */}
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end', gap: 12 }}>
                {file && (
                  <button
                    onClick={() => {
                      setFile(null);
                      setMessage(null);
                    }}
                    style={{
                      padding: '9px 16px',
                      borderRadius: 6,
                      background: '#ffffff',
                      color: '#64748b',
                      border: '1px solid #e2e8f0',
                      fontSize: 13,
                      fontWeight: 600,
                      cursor: 'pointer',
                    }}
                  >
                    Hủy chọn
                  </button>
                )}

                <button
                  onClick={handleDirectImport}
                  disabled={!file || busy}
                  style={{
                    padding: '10px 24px',
                    borderRadius: 6,
                    background: !file || busy ? '#94a3b8' : '#2563eb',
                    color: '#ffffff',
                    border: 'none',
                    fontSize: 13,
                    fontWeight: 700,
                    cursor: !file || busy ? 'not-allowed' : 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: 8,
                    boxShadow: file ? '0 2px 8px rgba(37,99,235,0.25)' : 'none',
                  }}
                >
                  {busy ? (
                    <>
                      <RefreshCw size={15} className="spin" />
                      <span>Đang nạp dữ liệu...</span>
                    </>
                  ) : (
                    <>
                      <span>Nạp dữ liệu vào hệ thống</span>
                      <Sparkles size={15} />
                    </>
                  )}
                </button>
              </div>
            </div>
          )}
        </div>
      </main>
    </>
  );
};

export default ImportWizardPage;
