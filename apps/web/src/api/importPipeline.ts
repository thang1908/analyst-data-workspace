const baseUrl = (import.meta.env.VITE_API_BASE_URL ?? import.meta.env.VITE_API_URL ?? 'http://localhost:8000').replace(/\/$/, '');

export const importProjectId =
  import.meta.env.VITE_IMPORT_PROJECT_ID?.trim() ||
  import.meta.env.VITE_ANALYTICS_PROJECT_ID?.trim() ||
  '00000000-0000-0000-0000-000000000001';

export interface DirectImportResponse {
  success: boolean;
  total_rows: number;
  imported_rows: number;
  message: string;
}

export const directImportCsv = async (file: File): Promise<DirectImportResponse> => {
  const formData = new FormData();
  formData.append('file', file);
  const response = await fetch(`${baseUrl}/api/v1/feedback-items/direct-import-csv?project_id=${importProjectId}`, {
    method: 'POST',
    body: formData,
  });
  if (!response.ok) {
    const errorBody = (await response.json().catch(() => null)) as { detail?: string } | null;
    throw new Error(errorBody?.detail ?? `Lỗi tải lên (${response.status})`);
  }
  return response.json() as Promise<DirectImportResponse>;
};
