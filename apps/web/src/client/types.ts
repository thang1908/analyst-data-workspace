export interface AnalyticsFilterParams {
  from_date?: string;
  to_date?: string;
  service_ids?: string;
  location_ids?: string;
  sentiments?: string;
  severities?: string;
  cursor?: string;
}

export interface ImportJobCounts {
  total_rows: number;
  valid_rows: number;
  invalid_rows: number;
  duplicate_rows: number;
}

export interface FieldError {
  row_number: number;
  column_name: string;
  error_code: string;
  message: string;
}

export interface ImportJob {
  import_job_id: string;
  status: 'VALIDATING' | 'VALIDATED' | 'PROCESSING' | 'COMMITTED' | 'FAILED' | 'CANCELLED';
  filename: string;
  total_rows: number;
  uploaded_at: string;
  committed_at?: string;
  counts?: ImportJobCounts;
  errors_sample?: FieldError[];
  can_execute?: boolean;
}

export interface AnalyticsMetrics {
  total_feedback_volume: number;
  negative_feedback_volume: number;
  negative_rate: number;
  sentiment_unknown_rate: number;
  high_severity_count: number;
  validation_pass_rate: number;
}

export interface AnalyticsSummary {
  snapshot_token: string;
  metrics: AnalyticsMetrics;
}

export interface TrendPoint {
  date: string;
  total_count: number;
  negative_count: number;
  negative_rate: number;
}

export interface TrendResponse {
  snapshot_token: string;
  points: TrendPoint[];
}

export interface BreakdownSegment {
  key: string;
  label: string;
  total_count: number;
  negative_count: number;
}

export interface BreakdownResponse {
  dimension: string;
  snapshot_token: string;
  segments: BreakdownSegment[];
}

export interface FeedbackItem {
  feedback_item_id: string;
  created_at: string;
  service_name: string;
  location_name: string;
  sentiment: 'POSITIVE' | 'NEUTRAL' | 'NEGATIVE' | 'UNKNOWN';
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  masked_text: string;
}

export interface FeedbackListResponse {
  items: FeedbackItem[];
  next_cursor?: string;
  has_more: boolean;
}

export interface Provenance {
  import_job_id: string;
  source_reference: string;
  row_index: number;
  decision: string;
  committed_at: string;
}

export interface FeedbackDetail extends FeedbackItem {
  issue_name: string;
  provenance: Provenance;
}

export interface ProblemDetails {
  type: string;
  title: string;
  status: number;
  detail: string;
  instance?: string;
  code: string;
}
