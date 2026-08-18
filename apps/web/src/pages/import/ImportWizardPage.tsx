import React, { useEffect, useMemo, useState } from 'react';
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

const STEPS = [
  { title: 'Tải tệp nguồn', desc: 'Chọn file CSV hoặc Excel' },
  { title: 'Ánh xạ cột', desc: 'Gán cột vào trường dữ liệu chuẩn' },
  { title: 'Kiểm tra dữ liệu', desc: 'Xác thực cấu trúc & số dòng' },
  { title: 'Nạp dữ liệu', desc: 'Ghi nhận vào hệ thống' },
];

const CANONICAL_FIELDS = [
  { key: 'content', label: 'Nội dung phản ánh (Bắt buộc)', required: true },
  { key: 'source_record_key', label: 'Mã định danh bản ghi (ID)', required: false },
  { key: 'reported_at', label: 'Thời điểm phản hồi', required: false },
  { key: 'intake_channel', label: 'Kênh tiếp nhận', required: false },
  { key: 'location', label: 'Khu đô thị / Vị trí', required: false },
];

const formatSize = (bytes: number) => {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
};

const autoGuessField = (colName: string): string => {
  const norm = colName.toLowerCase().replace(/[\s_-]/g, '');
  if (['content', 'message', 'feedback', 'comment', 'noidung', 'review', 'phananh'].some((k) => norm.includes(k))) return 'content';
  if (['id', 'ticketid', 'recordkey', 'maphananh', 'code'].some((k) => norm.includes(k))) return 'source_record_key';
  if (['date', 'time', 'reportedat', 'createdat', 'ngay', 'thoigian'].some((k) => norm.includes(k))) return 'reported_at';
  if (['channel', 'intakechannel', 'kenh', 'source'].some((k) => norm.includes(k))) return 'intake_channel';
  if (['location', 'khudothi', 'duan', 'toanha', 'vitri'].some((k) => norm.includes(k))) return 'location';
  return '';
};

const ImportWizardPage: React.FC = () => {
  const navigate = useNavigate();
  const [step, setStep] = useState(0);
  const [file, setFile] = useState<File | null>(null);
  const [sourceSystem, setSourceSystem] = useState('resident-app');
  const [headers, setHeaders] = useState<string[]>([]);
  const [mapping, setMapping] = useState<Record<string, string>>({});
  const [job, setJob] = useState<ImportJob | null>(null);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  const configured = Boolean(importProjectId && importActorId);
  const progress = useMemo(() => (job?.totalRows ? Math.round(((job.committedRows ?? 0) / job.totalRows) * 100) : 0), [job]);

  // Polling for async background job execution
  useEffect(() => {
    if (!job || !['VALIDATING', 'QUEUED', 'PROCESSING'].includes(job.status)) return;
    const timer = window.setInterval(() => {
      void getImportJob(job.importJobId)
        .then((next) => {
          setJob(next);
          if (next.status === 'VALIDATED' && step === 2) {
            // Validation completed
          } else if (['COMPLETED', 'PARTIAL', 'FAILED'].includes(next.status) && step === 3) {
            // Execution completed
          }
        })
        .catch((err: Error) => setMessage(err.message));
    }, 1500);
    return () => window.clearInterval(timer);
  }, [job, step]);

  const chooseFile = async (nextFile: File | null) => {
    setFile(nextFile);
    setHeaders([]);
    setMapping({});
    setMessage(null);
    if (!nextFile) return;

    if (!/\.(csv|xlsx)$/i.test(nextFile.name)) {
      setMessage('Chỉ hỗ trợ tệp định dạng .csv hoặc .xlsx');
      return;
    }

    if (/\.csv$/i.test(nextFile.name)) {
      const text = await nextFile.text();
      const [firstLine = ''] = text.split(/\r?\n/, 1);
      const columns = firstLine.split(',').map((val) => val.trim().replace(/^["']|["']$/g, '')).filter(Boolean);
      setHeaders(columns);

      const initialMap: Record<string, string> = {};
      columns.forEach((col) => {
        initialMap[col] = autoGuessField(col);
      });
      setMapping(initialMap);
    }
  };

  const run = async (action: () => Promise<ImportJob>, nextStep: number) => {
    setBusy(true);
    setMessage(null);
    try {
      const res = await action();
      setJob(res);
      setStep(nextStep);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : 'Thao tác không thành công.');
    } finally {
      setBusy(false);
    }
  };

  const submitUpload = () => file && run(() => uploadImport(file, sourceSystem), 1);
  const submitMapping = () => job && run(() => saveMapping(job, mapping), 2);
  const submitValidation = () => job && run(() => validateImport(job), 2);
  const submitExecution = () => job && run(() => executeImport(job), 3);

  const hasContentFieldMapped = useMemo(() => {
    return Object.values(mapping).includes('content');
  }, [mapping]);

  return (
    <>
      <TopBar title="Nhập dữ liệu" subtitle="Quy trình xác thực & nạp dữ liệu phản hồi" />
      <main className="page-content" style={{ padding: '24px 28px', maxWidth: 1000, margin: '0 auto', display: 'flex', flexDirection: 'column', gap: 20 }}>
        {/* Wizard Step Indicator */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 12 }}>
          {STEPS.map((s, idx) => {
            const isCompleted = step > idx || (step === 3 && job?.status === 'COMPLETED');
            const isActive = step === idx;
            return (
              <div
                key={s.title}
                style={{
                  background: '#ffffff',
                  border: isActive ? '2px solid #2563eb' : isCompleted ? '1px solid #86efac' : '1px solid #e2e8f0',
                  borderRadius: 8,
                  padding: '12px 14px',
                  display: 'flex',
                  alignItems: 'center',
                  gap: 10,
                  boxShadow: isActive ? '0 2px 8px rgba(37,99,235,0.12)' : 'none',
                }}
              >
                <div
                  style={{
                    width: 28,
                    height: 28,
                    borderRadius: '50%',
                    background: isCompleted ? '#22c55e' : isActive ? '#2563eb' : '#f1f5f9',
                    color: isCompleted || isActive ? '#ffffff' : '#64748b',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: 12,
                    fontWeight: 700,
                    flexShrink: 0,
                  }}
                >
                  {isCompleted ? <Check size={16} /> : idx + 1}
                </div>
                <div>
                  <div style={{ fontSize: 13, fontWeight: 700, color: isActive ? '#1d4ed8' : '#0f172a' }}>{s.title}</div>
                  <div style={{ fontSize: 11, color: '#64748b' }}>{s.desc}</div>
                </div>
              </div>
            );
          })}
        </div>

        {message && (
          <div style={{ padding: '12px 16px', background: '#fef2f2', border: '1px solid #fca5a5', borderRadius: 8, color: '#b91c1c', fontSize: 13, display: 'flex', alignItems: 'center', gap: 8 }}>
            <AlertCircle size={16} />
            <span>{message}</span>
          </div>
        )}

        {/* Step Card Content */}
        <div className="card" style={{ padding: '24px 28px', borderRadius: 10, minHeight: 340 }}>
          {/* ─── STEP 0: Chọn tệp tải lên ─── */}
          {step === 0 && (
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', textAlign: 'center', gap: 16 }}>
              <div style={{ width: 56, height: 56, borderRadius: '50%', background: '#eff6ff', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <UploadCloud size={28} color="#2563eb" />
              </div>
              <div>
                <h3 style={{ fontSize: 17, fontWeight: 800, color: '#0f172a', margin: '0 0 6px 0' }}>
                  Tải lên tệp phản hồi khách hàng
                </h3>
                <p style={{ fontSize: 13, color: '#64748b', margin: 0 }}>
                  Hỗ trợ định dạng <strong>.CSV</strong> hoặc <strong>.XLSX</strong>. Tệp gốc được mã hóa an toàn và kiểm tra bảo mật trước khi phân tích.
                </p>
              </div>

              {/* Upload Dropzone */}
              <label
                style={{
                  width: '100%',
                  maxWidth: 520,
                  border: '2px dashed #cbd5e1',
                  borderRadius: 10,
                  padding: '30px 20px',
                  background: '#fafafa',
                  cursor: 'pointer',
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  gap: 10,
                  transition: 'border-color 0.2s',
                }}
                onMouseEnter={(e) => (e.currentTarget.style.borderColor = '#2563eb')}
                onMouseLeave={(e) => (e.currentTarget.style.borderColor = '#cbd5e1')}
              >
                <input
                  type="file"
                  accept=".csv,.xlsx,text/csv,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                  style={{ display: 'none' }}
                  onChange={(e) => void chooseFile(e.target.files?.[0] ?? null)}
                />
                <FileSpreadsheet size={32} color="#64748b" />
                <span style={{ fontSize: 13, fontWeight: 600, color: '#2563eb' }}>
                  {file ? file.name : 'Nhấp để chọn tệp hoặc kéo thả file vào đây'}
                </span>
                <span style={{ fontSize: 11, color: '#94a3b8' }}>
                  {file ? `Dung lượng: ${formatSize(file.size)}` : 'Dung lượng tối đa 50MB'}
                </span>
              </label>

              {file && (
                <div style={{ display: 'flex', alignItems: 'center', gap: 10, background: '#f0fdf4', border: '1px solid #86efac', padding: '8px 16px', borderRadius: 8, color: '#166534', fontSize: 13, fontWeight: 600 }}>
                  <CheckCircle2 size={16} />
                  <span>Đã chọn tệp: <strong>{file.name}</strong> ({formatSize(file.size)})</span>
                </div>
              )}
            </div>
          )}

          {/* ─── STEP 1: Ánh xạ cột (Mapping) ─── */}
          {step === 1 && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
              <div>
                <h3 style={{ fontSize: 17, fontWeight: 800, color: '#0f172a', margin: '0 0 4px 0' }}>
                  Ánh xạ cột dữ liệu nguồn
                </h3>
                <p style={{ fontSize: 13, color: '#64748b', margin: 0 }}>
                  Gán các cột trong tệp của bạn vào các trường thông tin chuẩn của hệ thống. Trường <strong>Nội dung phản ánh</strong> là bắt buộc.
                </p>
              </div>

              {headers.length > 0 ? (
                <div style={{ border: '1px solid #e2e8f0', borderRadius: 8, overflow: 'hidden' }}>
                  <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13 }}>
                    <thead>
                      <tr style={{ background: '#f8fafc', borderBottom: '1px solid #e2e8f0', color: '#475569', fontWeight: 700 }}>
                        <th style={{ padding: '10px 14px', textAlign: 'left' }}>Cột trong tệp ({file?.name})</th>
                        <th style={{ padding: '10px 14px', textAlign: 'left' }}>Trường chuẩn trong hệ thống</th>
                      </tr>
                    </thead>
                    <tbody>
                      {headers.map((col, i) => (
                        <tr key={col} style={{ borderBottom: i < headers.length - 1 ? '1px solid #f1f5f9' : 'none' }}>
                          <td style={{ padding: '10px 14px', fontWeight: 600, color: '#0f172a' }}>
                            {col}
                          </td>
                          <td style={{ padding: '10px 14px' }}>
                            <select
                              value={mapping[col] ?? ''}
                              onChange={(e) => setMapping({ ...mapping, [col]: e.target.value })}
                              style={{
                                width: '100%',
                                maxWidth: 360,
                                padding: '6px 10px',
                                borderRadius: 6,
                                border: '1px solid #cbd5e1',
                                fontSize: 12,
                                background: mapping[col] ? '#eff6ff' : '#ffffff',
                                color: mapping[col] ? '#1d4ed8' : '#334155',
                                fontWeight: mapping[col] ? 600 : 400,
                              }}
                            >
                              <option value="">-- Bỏ qua cột này --</option>
                              {CANONICAL_FIELDS.map((f) => (
                                <option key={f.key} value={f.key}>
                                  {f.label}
                                </option>
                              ))}
                            </select>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <div style={{ padding: 20, textAlign: 'center', color: '#64748b' }}>
                  Đang chuẩn bị danh sách cột từ tệp nguồn...
                </div>
              )}
            </div>
          )}

          {/* ─── STEP 2: Xác thực dữ liệu (Validation) ─── */}
          {step === 2 && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 18 }}>
              <div>
                <h3 style={{ fontSize: 17, fontWeight: 800, color: '#0f172a', margin: '0 0 4px 0' }}>
                  Kiểm tra & Xác thực cấu trúc dữ liệu
                </h3>
                <p style={{ fontSize: 13, color: '#64748b', margin: 0 }}>
                  Hệ thống kiểm tra định dạng từng dòng, phát hiện lỗi cú pháp và trùng lặp trước khi nạp chính thức.
                </p>
              </div>

              {job?.status === 'VALIDATING' || busy ? (
                <div style={{ padding: '40px 20px', textAlign: 'center', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 12 }}>
                  <RefreshCw size={28} color="#2563eb" className="spin" />
                  <span style={{ fontSize: 14, fontWeight: 600, color: '#1e293b' }}>
                    Đang quét và kiểm tra từng dòng dữ liệu...
                  </span>
                </div>
              ) : (
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 14 }}>
                  <div style={{ background: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: 8, padding: 16 }}>
                    <span style={{ fontSize: 11, color: '#64748b', display: 'block', marginBottom: 4 }}>TỔNG SỐ DÒNG</span>
                    <strong style={{ fontSize: 20, color: '#0f172a' }}>{job?.totalRows?.toLocaleString() ?? '—'}</strong>
                  </div>

                  <div style={{ background: '#f0fdf4', border: '1px solid #86efac', borderRadius: 8, padding: 16 }}>
                    <span style={{ fontSize: 11, color: '#166534', display: 'block', marginBottom: 4 }}>DÒNG HỢP LỆ</span>
                    <strong style={{ fontSize: 20, color: '#15803d' }}>{job?.validRows?.toLocaleString() ?? '—'}</strong>
                  </div>

                  <div style={{ background: (job?.invalidRows ?? 0) > 0 ? '#fef2f2' : '#f8fafc', border: (job?.invalidRows ?? 0) > 0 ? '1px solid #fca5a5' : '1px solid #e2e8f0', borderRadius: 8, padding: 16 }}>
                    <span style={{ fontSize: 11, color: (job?.invalidRows ?? 0) > 0 ? '#b91c1c' : '#64748b', display: 'block', marginBottom: 4 }}>CẦN XỬ LÝ</span>
                    <strong style={{ fontSize: 20, color: (job?.invalidRows ?? 0) > 0 ? '#dc2626' : '#0f172a' }}>
                      {job?.invalidRows?.toLocaleString() ?? '0'}
                    </strong>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* ─── STEP 3: Nạp dữ liệu & Kết quả ─── */}
          {step === 3 && (
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', textAlign: 'center', gap: 18, padding: '20px 0' }}>
              {job?.status === 'COMPLETED' ? (
                <>
                  <div style={{ width: 60, height: 60, borderRadius: '50%', background: '#dcfce7', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    <CheckCircle2 size={36} color="#16a34a" />
                  </div>
                  <div>
                    <h3 style={{ fontSize: 18, fontWeight: 800, color: '#0f172a', margin: '0 0 6px 0' }}>
                      Nạp dữ liệu phản hồi thành công!
                    </h3>
                    <p style={{ fontSize: 13, color: '#64748b', margin: 0 }}>
                      Đã ghi nhận <strong>{job.committedRows?.toLocaleString() ?? job.totalRows?.toLocaleString()}</strong> dòng phản ánh vào kho dữ liệu CX.
                    </p>
                  </div>

                  <div style={{ display: 'flex', gap: 12, marginTop: 10 }}>
                    <button
                      onClick={() => navigate('/feedback')}
                      style={{
                        padding: '10px 20px',
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
                        setMapping({});
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
                </>
              ) : (
                <>
                  <RefreshCw size={32} color="#2563eb" className="spin" />
                  <div>
                    <h3 style={{ fontSize: 17, fontWeight: 800, color: '#0f172a', margin: '0 0 6px 0' }}>
                      Đang xử lý nạp dữ liệu vào hệ thống...
                    </h3>
                    <p style={{ fontSize: 13, color: '#64748b', margin: 0 }}>
                      Tiến trình đang chạy tự động trong nền.
                    </p>
                  </div>

                  <div style={{ width: '100%', maxWidth: 460, background: '#e2e8f0', borderRadius: 10, height: 8, overflow: 'hidden' }}>
                    <div style={{ width: `${progress}%`, background: '#2563eb', height: '100%', transition: 'width 0.3s' }} />
                  </div>
                  <span style={{ fontSize: 12, color: '#64748b' }}>{progress}% hoàn tất</span>
                </>
              )}
            </div>
          )}
        </div>

        {/* Wizard Footer Controls */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <button
            onClick={() => setStep((s) => Math.max(0, s - 1))}
            disabled={step === 0 || step === 3 || busy}
            style={{
              padding: '8px 16px',
              borderRadius: 6,
              border: '1px solid #cbd5e1',
              background: '#ffffff',
              color: step === 0 || step === 3 ? '#94a3b8' : '#334155',
              fontSize: 13,
              fontWeight: 600,
              cursor: step === 0 || step === 3 ? 'not-allowed' : 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: 6,
            }}
          >
            <ChevronLeft size={15} /> Quay lại
          </button>

          <div>
            {step === 0 && (
              <button
                onClick={submitUpload}
                disabled={!file || busy}
                style={{
                  padding: '8px 20px',
                  borderRadius: 6,
                  background: !file || busy ? '#94a3b8' : '#2563eb',
                  color: '#ffffff',
                  border: 'none',
                  fontSize: 13,
                  fontWeight: 700,
                  cursor: !file || busy ? 'not-allowed' : 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: 6,
                }}
              >
                {busy ? 'Đang tải tệp...' : 'Tiếp tục: Ánh xạ cột'} <ChevronRight size={15} />
              </button>
            )}

            {step === 1 && (
              <button
                onClick={async () => {
                  await submitMapping();
                  if (job) await validateImport(job);
                }}
                disabled={!hasContentFieldMapped || busy}
                style={{
                  padding: '8px 20px',
                  borderRadius: 6,
                  background: !hasContentFieldMapped || busy ? '#94a3b8' : '#2563eb',
                  color: '#ffffff',
                  border: 'none',
                  fontSize: 13,
                  fontWeight: 700,
                  cursor: !hasContentFieldMapped || busy ? 'not-allowed' : 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: 6,
                }}
              >
                {busy ? 'Đang lưu...' : 'Tiếp tục: Xác thực dữ liệu'} <ChevronRight size={15} />
              </button>
            )}

            {step === 2 && (
              <button
                onClick={submitExecution}
                disabled={job?.status === 'VALIDATING' || busy}
                style={{
                  padding: '8px 20px',
                  borderRadius: 6,
                  background: '#0f172a',
                  color: '#ffffff',
                  border: 'none',
                  fontSize: 13,
                  fontWeight: 700,
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: 6,
                }}
              >
                {busy ? 'Đang gửi...' : 'Bắt đầu nạp dữ liệu'} <Sparkles size={14} />
              </button>
            )}
          </div>
        </div>
      </main>
    </>
  );
};

export default ImportWizardPage;
