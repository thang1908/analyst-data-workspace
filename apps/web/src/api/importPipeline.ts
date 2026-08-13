export interface ImportJob {
  importJobId: string;
  status: string;
  filename: string;
  fileSizeBytes: number;
  totalRows: number | null;
  validRows: number | null;
  invalidRows: number | null;
  committedRows: number | null;
  errorObjectKey: string | null;
  version: number;
}

type ApiJob = {
  import_job_id: string; status: string; filename: string; file_size_bytes: number;
  total_rows: number | null; valid_rows: number | null; invalid_rows: number | null;
  committed_rows: number | null; error_object_key: string | null; version: number;
};

const baseUrl = (import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000').replace(/\/$/, '');
export const importProjectId = import.meta.env.VITE_IMPORT_PROJECT_ID?.trim();
export const importActorId = import.meta.env.VITE_IMPORT_ACTOR_ID?.trim();

const headers = (): HeadersInit => ({ 'X-Actor-ID': importActorId ?? '' });
const mapJob = (job: ApiJob): ImportJob => ({
  importJobId: job.import_job_id, status: job.status, filename: job.filename,
  fileSizeBytes: job.file_size_bytes, totalRows: job.total_rows, validRows: job.valid_rows,
  invalidRows: job.invalid_rows, committedRows: job.committed_rows,
  errorObjectKey: job.error_object_key, version: job.version,
});

const request = async <T>(path: string, init?: RequestInit): Promise<T> => {
  const response = await fetch(`${baseUrl}/api/v1/import-jobs${path}`, init);
  if (!response.ok) {
    const body = await response.json().catch(() => null) as { detail?: string } | null;
    throw new Error(body?.detail ?? `Import API trả về lỗi ${response.status}.`);
  }
  return response.json() as Promise<T>;
};

export const uploadImport = async (file: File, sourceSystem: string): Promise<ImportJob> => {
  if (!importProjectId || !importActorId) throw new Error('Thiếu VITE_IMPORT_PROJECT_ID hoặc VITE_IMPORT_ACTOR_ID.');
  const body = new FormData(); body.set('file', file);
  const params = new URLSearchParams({ project_id: importProjectId, source_system: sourceSystem });
  const response = await request<{ data: ApiJob }>(`/upload?${params}`, { method: 'POST', headers: headers(), body });
  return mapJob(response.data);
};

export const saveMapping = async (job: ImportJob, mapping: Record<string, string>): Promise<ImportJob> =>
  mapJob((await request<{ data: ApiJob }>(`/${job.importJobId}/map`, {
    method: 'POST', headers: { ...headers(), 'Content-Type': 'application/json' },
    body: JSON.stringify({ expected_version: job.version, mapping }),
  })).data);

export const validateImport = async (job: ImportJob): Promise<ImportJob> =>
  mapJob((await request<{ data: ApiJob }>(`/${job.importJobId}/validate`, { method: 'POST' })).data);

export const executeImport = async (job: ImportJob): Promise<ImportJob> =>
  mapJob((await request<{ data: ApiJob }>(`/${job.importJobId}/execute`, {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ expected_version: job.version, allow_partial: true }),
  })).data);

export const getImportJob = async (importJobId: string): Promise<ImportJob> =>
  mapJob((await request<{ data: ApiJob }>(`/${importJobId}`)).data);
