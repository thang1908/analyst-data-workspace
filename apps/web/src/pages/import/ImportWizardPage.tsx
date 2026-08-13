import React, { useEffect, useMemo, useState } from 'react';
import { Check, ChevronLeft, ChevronRight, FileSpreadsheet, RefreshCw, UploadCloud } from 'lucide-react';
import TopBar from '../../components/layout/TopBar';
import { ImportJob, executeImport, getImportJob, importActorId, importProjectId, saveMapping, uploadImport, validateImport } from '../../api/importPipeline';

const steps = ['Nguồn & tệp', 'Ánh xạ cột', 'Xem trước', 'Kiểm tra lỗi', 'Nạp dữ liệu', 'Kết quả'];
const canonicalFields = [
  ['source_record_key', 'Mã bản ghi nguồn'], ['reported_at', 'Thời điểm phản hồi'],
  ['content', 'Nội dung phản hồi'], ['intake_channel', 'Kênh tiếp nhận'], ['location', 'Vị trí'],
];
const formatSize = (bytes: number) => `${(bytes / 1024).toFixed(bytes < 1024 * 1024 ? 0 : 1)} KB`;

const ImportWizardPage: React.FC = () => {
  const [step, setStep] = useState(0);
  const [file, setFile] = useState<File | null>(null);
  const [sourceSystem, setSourceSystem] = useState('resident-app');
  const [headers, setHeaders] = useState<string[]>([]);
  const [mapping, setMapping] = useState<Record<string, string>>({});
  const [job, setJob] = useState<ImportJob | null>(null);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const configured = Boolean(importProjectId && importActorId);
  const progress = useMemo(() => job?.totalRows ? Math.round(((job.committedRows ?? 0) / job.totalRows) * 100) : 0, [job]);

  useEffect(() => {
    if (!job || !['VALIDATING', 'QUEUED', 'PROCESSING'].includes(job.status)) return;
    const timer = window.setInterval(() => void getImportJob(job.importJobId).then(setJob).catch((error: Error) => setMessage(error.message)), 1500);
    return () => window.clearInterval(timer);
  }, [job]);

  const chooseFile = async (nextFile: File | null) => {
    setFile(nextFile); setHeaders([]); setMapping({}); setMessage(null);
    if (!nextFile) return;
    if (!/\.(csv|xlsx)$/i.test(nextFile.name)) { setMessage('Chỉ hỗ trợ tệp CSV hoặc XLSX.'); return; }
    if (/\.csv$/i.test(nextFile.name)) {
      const [firstLine = ''] = (await nextFile.text()).split(/\r?\n/, 1);
      const columns = firstLine.split(',').map((value) => value.trim()).filter(Boolean);
      setHeaders(columns);
      setMapping(Object.fromEntries(columns.map((column) => [column, column === 'message' ? 'content' : column === 'ticket_id' ? 'source_record_key' : ''])));
    }
  };
  const run = async (action: () => Promise<ImportJob>, nextStep: number) => {
    setBusy(true); setMessage(null);
    try { setJob(await action()); setStep(nextStep); } catch (error) { setMessage(error instanceof Error ? error.message : 'Không thể hoàn tất thao tác.'); } finally { setBusy(false); }
  };
  const submitUpload = () => file && run(() => uploadImport(file, sourceSystem), 1);
  const submitMapping = () => job && run(() => saveMapping(job, mapping), 2);
  const submitValidation = () => job && run(() => validateImport(job), 3);
  const submitExecution = () => job && run(() => executeImport(job), 4);
  const retryStatus = () => job && void getImportJob(job.importJobId).then((next) => { setJob(next); if (['COMPLETED', 'PARTIAL', 'FAILED'].includes(next.status)) setStep(5); });

  return <><TopBar title="Imports" subtitle="Nạp feedback có kiểm soát và truy vết theo dòng" />
    <main className="page-content import-page">
      <div className="import-header"><div><h1>Nhập dữ liệu phản hồi</h1><p>Kiểm tra cấu trúc, xử lý lỗi và chỉ nạp các dòng đã được xác thực.</p></div><span className="import-scope">{configured ? 'Đã cấu hình project' : 'Thiếu cấu hình project'}</span></div>
      <ol className="import-steps" aria-label="Tiến trình nhập dữ liệu">{steps.map((label, index) => <li key={label} className={index === step ? 'active' : index < step ? 'done' : ''}><span>{index < step ? <Check size={14} /> : index + 1}</span><small>{label}</small></li>)}</ol>
      {message && <div className="import-alert" role="alert">{message}</div>}
      {!configured && <div className="import-alert">Cần đặt <code>VITE_IMPORT_PROJECT_ID</code> và <code>VITE_IMPORT_ACTOR_ID</code> trong <code>apps/web/.env.local</code>.</div>}
      <section className="import-card">
        {step === 0 && <div className="import-upload"><UploadCloud size={38} /><h2>Chọn tệp nguồn</h2><p>Hỗ trợ CSV và XLSX. File gốc được lưu riêng, không hiển thị nội dung thô trên dashboard.</p><label className="import-file"><input type="file" accept=".csv,.xlsx,text/csv,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" onChange={(event) => void chooseFile(event.target.files?.[0] ?? null)} />Chọn tệp</label>{file && <div className="import-file-info"><FileSpreadsheet size={18} /><strong>{file.name}</strong><span>{formatSize(file.size)}</span></div>}<label>Nguồn dữ liệu<input value={sourceSystem} onChange={(event) => setSourceSystem(event.target.value)} /></label></div>}
        {step === 1 && <div><h2>Ánh xạ cột</h2><p>Gán cột trong file vào trường chuẩn. Nội dung phản hồi là bắt buộc.</p>{headers.length ? <div className="mapping-grid">{headers.map((column) => <label key={column}><span>{column}</span><select value={mapping[column] ?? ''} onChange={(event) => setMapping({ ...mapping, [column]: event.target.value })}><option value="">Không dùng</option>{canonicalFields.map(([value, label]) => <option key={value} value={value}>{label}</option>)}</select></label>)}</div> : <div className="import-alert">Với XLSX, mapping sẽ được xác nhận ở bước validate bởi worker.</div>}</div>}
        {step === 2 && <div className="import-summary"><h2>Xem trước & xác thực</h2><p>Job <code>{job?.importJobId}</code> đã lưu mapping. Hệ thống sẽ đọc file theo stream và chưa tạo Feedback.</p><dl><div><dt>Trạng thái</dt><dd>{job?.status}</dd></div><div><dt>Tệp</dt><dd>{job?.filename}</dd></div></dl></div>}
        {step === 3 && <div className="import-summary"><h2>Kiểm tra lỗi & trùng lặp</h2><p>{job?.status === 'VALIDATING' ? 'Worker đang kiểm tra từng dòng…' : 'Kết quả validation đã sẵn sàng.'}</p><dl><div><dt>Hợp lệ</dt><dd>{job?.validRows ?? '—'}</dd></div><div><dt>Cần xử lý</dt><dd>{job?.invalidRows ?? '—'}</dd></div><div><dt>Tổng số dòng</dt><dd>{job?.totalRows ?? '—'}</dd></div></dl>{job?.errorObjectKey && <p className="import-note">Báo cáo lỗi đã được tạo: <code>{job.errorObjectKey}</code></p>}</div>}
        {step === 4 && <div className="import-summary"><h2>Đang nạp dữ liệu</h2><p>Worker nạp theo lô và có thể retry an toàn.</p><div className="import-progress"><span style={{ width: `${progress}%` }} /></div><strong>{progress}% · {job?.committedRows ?? 0}/{job?.totalRows ?? '—'} dòng đã nạp</strong><button className="section-action" onClick={retryStatus}><RefreshCw size={14} /> Làm mới trạng thái</button></div>}
        {step === 5 && <div className="import-summary success"><Check size={36} /><h2>{job?.status === 'COMPLETED' ? 'Nạp dữ liệu hoàn tất' : 'Nạp dữ liệu hoàn tất một phần'}</h2><p>{job?.committedRows ?? 0} dòng đã được ghi; {job?.invalidRows ?? 0} dòng cần xem lại.</p>{job?.errorObjectKey && <p className="import-note">Báo cáo lỗi: <code>{job.errorObjectKey}</code></p>}</div>}
      </section>
      <div className="import-actions"><button className="section-action" disabled={step === 0 || busy} onClick={() => setStep(step - 1)}><ChevronLeft size={15} /> Quay lại</button>{step === 0 && <button className="import-primary" disabled={!file || !configured || busy} onClick={submitUpload}>Tải lên & tiếp tục <ChevronRight size={15} /></button>}{step === 1 && <button className="import-primary" disabled={!job || busy} onClick={submitMapping}>Lưu mapping <ChevronRight size={15} /></button>}{step === 2 && <button className="import-primary" disabled={!job || busy} onClick={submitValidation}>Bắt đầu xác thực <ChevronRight size={15} /></button>}{step === 3 && <button className="import-primary" disabled={!job || job.status === 'VALIDATING' || busy} onClick={submitExecution}>Xác nhận nạp dữ liệu <ChevronRight size={15} /></button>}{step === 4 && <button className="import-primary" onClick={retryStatus}>Kiểm tra kết quả <RefreshCw size={15} /></button>}{step === 5 && <button className="import-primary" onClick={() => { setStep(0); setJob(null); setFile(null); }}>Nhập tệp mới</button>}</div>
    </main></>;
};
export default ImportWizardPage;
