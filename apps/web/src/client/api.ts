import {
  AnalyticsFilterParams,
  AnalyticsSummary,
  TrendResponse,
  BreakdownResponse,
  FeedbackListResponse,
  FeedbackDetail,
  ImportJob,
} from './types';

import {
  MOCK_IMPORT_JOBS,
  MOCK_SUMMARY,
  MOCK_TREND,
  MOCK_BREAKDOWN_SERVICE,
  MOCK_BREAKDOWN_LOCATION,
  MOCK_BREAKDOWN_SEVERITY,
  MOCK_FEEDBACK_ITEMS,
  MOCK_FEEDBACK_DETAIL,
} from '../mocks/fixtures';

const PROJECT_ID_DEFAULT = 'proj_pilot_01';

export class ApiClient {
  private baseUrl: string;
  private useMock: boolean;

  constructor() {
    this.baseUrl = '/api/v1/projects/' + PROJECT_ID_DEFAULT;
    this.useMock = true; // Default to true for pilot contract testing
  }

  async uploadCsv(file: File): Promise<ImportJob> {
    if (this.useMock) {
      const newJobId = 'job_' + Math.random().toString(36).substring(2, 9);
      const mockJob: ImportJob = {
        import_job_id: newJobId,
        status: 'VALIDATING',
        filename: file.name,
        total_rows: 5000,
        uploaded_at: new Date().toISOString(),
        counts: {
          total_rows: 5000,
          valid_rows: 4920,
          invalid_rows: 80,
          duplicate_rows: 0,
        },
        errors_sample: [
          {
            row_number: 14,
            column_name: 'reported_at',
            error_code: 'INVALID_TIMESTAMP',
            message: 'Timestamp must be ISO-8601 format',
          },
        ],
        can_execute: true,
      };
      MOCK_IMPORT_JOBS[newJobId] = mockJob;
      return mockJob;
    }

    const formData = new FormData();
    formData.append('file', file);

    const res = await fetch(`${this.baseUrl}/imports/upload`, {
      method: 'POST',
      body: formData,
    });
    if (!res.ok) throw new Error('Failed to upload CSV');
    return res.json();
  }

  async getImportJob(jobId: string): Promise<ImportJob> {
    if (this.useMock) {
      const job = MOCK_IMPORT_JOBS[jobId] || MOCK_IMPORT_JOBS['job_9842a1b7'];
      return { ...job };
    }

    const res = await fetch(`${this.baseUrl}/imports/${jobId}`);
    if (!res.ok) throw new Error('Failed to fetch import job');
    return res.json();
  }

  async executeImportJob(jobId: string): Promise<ImportJob> {
    if (this.useMock) {
      const job = MOCK_IMPORT_JOBS[jobId] || MOCK_IMPORT_JOBS['job_9842a1b7'];
      job.status = 'COMMITTED';
      job.committed_at = new Date().toISOString();
      return { ...job };
    }

    const res = await fetch(`${this.baseUrl}/imports/${jobId}/execute`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ idempotency_key: `exec_${Date.now()}` }),
    });
    if (!res.ok) throw new Error('Failed to execute import job');
    return res.json();
  }

  async getSummary(_params?: AnalyticsFilterParams): Promise<AnalyticsSummary> {
    if (this.useMock) {
      return MOCK_SUMMARY;
    }
    const query = new URLSearchParams(_params as Record<string, string>).toString();
    const res = await fetch(`${this.baseUrl}/analytics/summary?${query}`);
    if (!res.ok) throw new Error('Failed to fetch summary');
    return res.json();
  }

  async getTrend(_params?: AnalyticsFilterParams): Promise<TrendResponse> {
    if (this.useMock) {
      return MOCK_TREND;
    }
    const query = new URLSearchParams(_params as Record<string, string>).toString();
    const res = await fetch(`${this.baseUrl}/analytics/trend?${query}`);
    if (!res.ok) throw new Error('Failed to fetch trend');
    return res.json();
  }

  async getBreakdown(dimension: 'service' | 'location' | 'severity', _params?: AnalyticsFilterParams): Promise<BreakdownResponse> {
    if (this.useMock) {
      if (dimension === 'location') return MOCK_BREAKDOWN_LOCATION;
      if (dimension === 'severity') return MOCK_BREAKDOWN_SEVERITY;
      return MOCK_BREAKDOWN_SERVICE;
    }
    const query = new URLSearchParams({ ..._params, dimension } as Record<string, string>).toString();
    const res = await fetch(`${this.baseUrl}/analytics/breakdown?${query}`);
    if (!res.ok) throw new Error('Failed to fetch breakdown');
    return res.json();
  }

  async getFeedbackItems(params?: AnalyticsFilterParams): Promise<FeedbackListResponse> {
    if (this.useMock) {
      let filtered = [...MOCK_FEEDBACK_ITEMS.items];
      if (params?.sentiments) {
        const selectedSentiments = params.sentiments.split(',');
        filtered = filtered.filter(item => selectedSentiments.includes(item.sentiment));
      }
      if (params?.severities) {
        const selectedSeverities = params.severities.split(',');
        filtered = filtered.filter(item => selectedSeverities.includes(item.severity));
      }
      return {
        items: filtered,
        next_cursor: MOCK_FEEDBACK_ITEMS.next_cursor,
        has_more: MOCK_FEEDBACK_ITEMS.has_more,
      };
    }
    const query = new URLSearchParams(params as Record<string, string>).toString();
    const res = await fetch(`${this.baseUrl}/feedback/items?${query}`);
    if (!res.ok) throw new Error('Failed to fetch feedback items');
    return res.json();
  }

  async getFeedbackDetail(itemId: string): Promise<FeedbackDetail> {
    if (this.useMock) {
      const detail = MOCK_FEEDBACK_DETAIL[itemId] || {
        ...MOCK_FEEDBACK_DETAIL['fb_item_98214'],
        feedback_item_id: itemId,
      };
      return detail;
    }
    const res = await fetch(`${this.baseUrl}/feedback/items/${itemId}`);
    if (!res.ok) throw new Error('Failed to fetch feedback detail');
    return res.json();
  }
}

export const api = new ApiClient();
