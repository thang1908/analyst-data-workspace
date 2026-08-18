import React, { useMemo, useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Check,
  ChevronLeft,
  ChevronRight,
  FileSpreadsheet,
  RefreshCw,
  UploadCloud,
  ArrowRight,
  CheckCircle2,
  AlertCircle,
  Download,
  FileCheck2,
  Sparkles,
} from 'lucide-react';
import TopBar from '../../components/layout/TopBar';
import {
  ImportJob,
  executeImport,
  getImportJob,
  importActorId,
  importProjectId,
  saveMapping,
  uploadImport,
  validateImport,
} from '../../api/importPipeline';

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
  const [step, setStep] = useState(0); // 0: Chọn file, 1: Xác thực & Xem trước, 2: Hoàn tất
  const [file, setFile] = useState<File | null>(null);
  const [headers, setHeaders] = useState<string[]>([]);
  const [job, setJob] = useState<ImportJob | null>(null);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [isValidTemplate, setIsValidTemplate] = useState<boolean | null>(null);

  const progress = useMemo(() => (job?.totalRows ? Math.round(((job.committedRows ?? 0) / job.totalRows) * 100) : 0), [job]);

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

  // Polling for async background job execution
  useEffect(() => {
    if (!job || !['VALIDATING', 'QUEUED', 'PROCESSING'].includes(job.status)) return;
    const timer = window.setInterval(() => {
      void getImportJob(job.importJobId)
        .then((next) => {
          setJob(next);
          if (['COMPLETED', 'PARTIAL', 'FAILED'].includes(next.status) && step === 1) {
            setStep(2);
          }
        })
        .catch((err: Error) => setMessage(err.message));
    }, 1500);
    return () => window.clearInterval(timer);
  }, [job, step]);

  const handleFileChange = async (selectedFile: File | null) => {
    setFile(selectedFile);
    setHeaders([]);
    setMessage(null);
    setIsValidTemplate(null);
    if (!selectedFile) return;

    if (!selectedFile.name.toLowerCase().endsWith('.csv')) {
      setMessage('Vui lòng chọn đúng tệp định dạng chuẩn .CSV');
      setIsValidTemplate(false);
      return;
    }

    try {
      const text = await selectedFile.text();
      const [firstLine = ''] = text.split(/\r?\n/, 1);
      const cols = firstLine.split(',').map((c) => c.trim().replace(/^["']|["']$/g, '').toLowerCase()).filter(Boolean);
      setHeaders(cols);

      // Check if required content column exists (noi_dung or content)
      const hasContentCol = cols.some((c) => c === 'noi_dung' || c === 'content' || c === 'noidung');
      if (!hasContentCol) {
        setMessage('Tệp CSV không đúng định dạng cột chuẩn: Thiếu cột "noi_dung". Vui lòng tải tệp mẫu chuẩn bên dưới.');
        setIsValidTemplate(false);
        return;
      }

      setIsValidTemplate(true);
    } catch {
      setMessage('Không thể đọc cấu trúc tệp CSV. Vui lòng kiểm tra lại.');
      setIsValidTemplate(false);
    }
  };

  // Start direct 1-click import pipeline with fixed schema mapping
  const handleStartImport = async () => {
    if (!file || !isValidTemplate) return;
    setBusy(true);
    setMessage(null);
    try {
      // Step 1: Upload file
      const uploadedJob = await uploadImport(file, 'resident-app');
      setJob(uploadedJob);

      // Step 2: Auto-map fixed standard schema
      const fixedMapping: Record<string, string> = {};
      headers.forEach((col) => {
        if (col === 'noi_dung' || col === 'content' || col === 'noidung') fixedMapping[col] = 'content';
        else if (col === 'khu_do_thi' || col === 'location' || col === 'khudothi') fixedMapping[col] = 'location';
        else if (col === 'thoi_gian' || col === 'reported_at' || col === 'thoigian') fixedMapping[col] = 'reported_at';
        else if (col === 'ma_phan_anh' || col === 'ticket_id' || col === 'maphananh') fixedMapping[col] = 'source_record_key';
        else if (col === 'kenh_tiep_nhan' || col === 'intake_channel' || col === 'kenhtiepnhan') fixedMapping[col] = 'intake_channel';
      });

      const mappedJob = await saveMapping(uploadedJob, fixedMapping);
      setJob(mappedJob);

      // Step 3: Validate
      const validatedJob = await validateImport(mappedJob);
      setJob(validatedJob);

      // Step 4: Execute Ingestion
      const executingJob = await executeImport(validatedJob);
      setJob(executingJob);

      setStep(1); // Move to execution / progress view
    } catch (err) {
      setMessage(err instanceof Error ? err.message : 'Không thể nạp dữ liệu.');
    } finally {
      setBusy(false);
    }
  };

  return (
    <>
      <TopBar title="Nhập dữ liệu" subtitle="Nạp tệp dữ liệu phản ánh theo mẫu chuẩn" />
      <main className="page-content" style={{ padding: '24px 28px', maxWidth: 900, margin: '0 auto', display: 'flex', flexDirection: 'column', gap: 20 }}>
        {/* Header with Template Download Button */}
        <div className="card" style={{ padding: '18px 22px', borderRadius: 8, display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 12 }}>
          <div>
            <h2 style={{ fontSize: 18, fontWeight: 800, color: '#0f172a', margin: '0 0 4px 0' }}>
              Nhập dữ liệu phản ánh khách hàng
            </h2>
            <p style={{ fontSize: 13, color: '#64748b', margin: 0 }}>
              Để đảm bảo tính chính xác, hệ thống yêu cầu tệp tải lên theo đúng định dạng <strong>.CSV chuẩn</strong>.
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
            📋 Quy định 5 cột trong tệp CSV chuẩn:
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: 10 }}>
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

        {/* Main Step Body */}
        <div className="card" style={{ padding: '28px 32px', borderRadius: 10, minHeight: 300, display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
          {/* STEP 0: Chọn file & Kiểm tra chuẩn */}
          {step === 0 && (
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', textAlign: 'center', gap: 18 }}>
              {/* Upload Dropzone */}
              <label
                style={{
                  width: '100%',
                  maxWidth: 560,
                  border: isValidTemplate === true ? '2px solid #22c55e' : isValidTemplate === false ? '2px solid #ef4444' : '2px dashed #cbd5e1',
                  borderRadius: 10,
                  padding: '36px 24px',
                  background: isValidTemplate === true ? '#f0fdf4' : isValidTemplate === false ? '#fef2f2' : '#fafafa',
                  cursor: 'pointer',
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  gap: 12,
                  transition: 'all 0.2s ease',
                }}
                onMouseEnter={(e) => {
                  if (isValidTemplate === null) e.currentTarget.style.borderColor = '#2563eb';
                }}
                onMouseLeave={(e) => {
                  if (isValidTemplate === null) e.currentTarget.style.borderColor = '#cbd5e1';
                }}
              >
                <input
                  type="file"
                  accept=".csv,text/csv"
                  style={{ display: 'none' }}
                  onChange={(e) => void handleFileChange(e.target.files?.[0] ?? null)}
                />
                <UploadCloud size={38} color={isValidTemplate === true ? '#16a34a' : isValidTemplate === false ? '#dc2626' : '#2563eb'} />
                <span style={{ fontSize: 14, fontWeight: 700, color: '#0f172a' }}>
                  {file ? file.name : 'Nhấp để chọn tệp CSV chuẩn hoặc kéo thả file vào đây'}
                </span>
                <span style={{ fontSize: 12, color: '#64748b' }}>
                  {file ? `Dung lượng: ${formatSize(file.size)} · Đã nhận diện ${headers.length} cột` : 'Chỉ chấp nhận tệp .CSV đúng cấu trúc 5 cột quy định'}
                </span>
              </label>

              {/* Status Banner when Validated */}
              {file && isValidTemplate === true && (
                <div style={{ display: 'flex', alignItems: 'center', gap: 8, background: '#f0fdf4', border: '1px solid #86efac', padding: '10px 18px', borderRadius: 8, color: '#166534', fontSize: 13, fontWeight: 600 }}>
                  <CheckCircle2 size={18} color="#16a34a" />
                  <span>Cấu trúc tệp hợp lệ! Sẵn sàng nạp vào hệ thống.</span>
                </div>
              )}

              {/* Action Button */}
              <button
                onClick={handleStartImport}
                disabled={!file || !isValidTemplate || busy}
                style={{
                  marginTop: 10,
                  padding: '11px 32px',
                  borderRadius: 6,
                  background: !file || !isValidTemplate || busy ? '#94a3b8' : '#2563eb',
                  color: '#ffffff',
                  border: 'none',
                  fontSize: 14,
                  fontWeight: 700,
                  cursor: !file || !isValidTemplate || busy ? 'not-allowed' : 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: 8,
                  boxShadow: isValidTemplate ? '0 4px 12px rgba(37,99,235,0.25)' : 'none',
                }}
              >
                {busy ? (
                  <>
                    <RefreshCw size={16} className="spin" />
                    <span>Đang xử lý nạp dữ liệu...</span>
                  </>
                ) : (
                  <>
                    <span>Xác nhận & Nạp dữ liệu ngay</span>
                    <Sparkles size={16} />
                  </>
                )}
              </button>
            </div>
          )}

          {/* STEP 1: Đang nạp dữ liệu vào hệ thống (Processing) */}
          {step === 1 && (
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', textAlign: 'center', gap: 16 }}>
              <RefreshCw size={36} color="#2563eb" className="spin" />
              <div>
                <h3 style={{ fontSize: 18, fontWeight: 800, color: '#0f172a', margin: '0 0 6px 0' }}>
                  Đang ghi nhận dữ liệu phản ánh vào hệ thống...
                </h3>
                <p style={{ fontSize: 13, color: '#64748b', margin: 0 }}>
                  Tiến trình đang nạp theo từng lô dữ liệu và che mờ thông tin bảo mật tự động.
                </p>
              </div>

              <div style={{ width: '100%', maxWidth: 480, background: '#e2e8f0', borderRadius: 10, height: 10, overflow: 'hidden', margin: '10px 0' }}>
                <div style={{ width: `${Math.max(progress, 15)}%`, background: '#2563eb', height: '100%', transition: 'width 0.3s' }} />
              </div>
              <span style={{ fontSize: 13, fontWeight: 600, color: '#475569' }}>
                {job?.committedRows ? `${job.committedRows} / ${job.totalRows ?? '—'} dòng` : 'Đang xử lý...'}
              </span>
            </div>
          )}

          {/* STEP 2: Nạp hoàn tất (Completed) */}
          {step === 2 && (
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', textAlign: 'center', gap: 16 }}>
              <div style={{ width: 64, height: 64, borderRadius: '50%', background: '#dcfce7', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <CheckCircle2 size={38} color="#16a34a" />
              </div>

              <div>
                <h3 style={{ fontSize: 19, fontWeight: 800, color: '#0f172a', margin: '0 0 6px 0' }}>
                  Nạp dữ liệu phản ánh hoàn tất!
                </h3>
                <p style={{ fontSize: 13, color: '#64748b', margin: 0 }}>
                  Đã ghi nhận thành công <strong>{job?.committedRows?.toLocaleString() ?? job?.totalRows?.toLocaleString()}</strong> phản ánh vào cơ sở dữ liệu.
                </p>
              </div>

              <div style={{ display: 'flex', gap: 12, marginTop: 12 }}>
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
                    setStep(0);
                    setJob(null);
                    setFile(null);
                    setHeaders([]);
                    setIsValidTemplate(null);
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
          )}
        </div>
      </main>
    </>
  );
};

export default ImportWizardPage;
