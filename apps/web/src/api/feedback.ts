import { AnalyticsApiError, formatAnalyticsApiError } from './analytics';

export interface FeedbackReference {
  code: string | null;
  nameVi: string | null;
}

export interface FeedbackWorkspaceItem {
  feedbackItemId: string;
  feedbackId: string;
  reportedAt: string;
  sourceSystem: string;
  contentMasked: string;
  location: { id: string | null; code: string | null; name: string | null };
  affectedChannelCodes: string[];
  currentClassification: {
    service: FeedbackReference | null;
    issue: FeedbackReference | null;
    sentiment: string | null;
    operationalSeverity: string | null;
    classificationState: string | null;
    projectionVersion: number | null;
  };
  status: string;
  analyticEligibility: string;
  parentItemId: string | null;
}

export interface FeedbackListFilters {
  projectId: string;
  dateFrom?: string;
  dateTo?: string;
  sourceSystem?: string;
  intakeChannelCode?: string;
  affectedChannelCode?: string;
  locationId?: string;
  serviceCode?: string;
  issueCode?: string;
  sentiment?: string;
  operationalSeverity?: string;
  customerLifecycleStageCode?: string;
  customerLifecycleStepCode?: string;
  touchpointCode?: string;
  hotspotId?: string;
  query?: string;
  limit?: number;
  offset?: number;
}

export interface FeedbackListResult {
  items: FeedbackWorkspaceItem[];
  total: number;
  limit: number;
  offset: number;
}

interface ApiReference { code: string | null; name_vi: string | null }
interface ApiFeedbackItem {
  feedback_item_id: string;
  feedback_id: string;
  reported_at: string;
  source_system: string;
  content_masked: string;
  location: { id: string | null; code: string | null; name: string | null };
  affected_channel_codes: string[];
  current_classification: {
    service: ApiReference | null;
    issue: ApiReference | null;
    sentiment: string | null;
    operational_severity: string | null;
    classification_state: string | null;
    projection_version: number | null;
  };
  status: string;
  analytic_eligibility: string;
  parent_item_id: string | null;
}

interface ApiListResponse {
  data: ApiFeedbackItem[];
  meta: { total: number; limit: number; offset: number };
}

import { getApiBaseUrl } from './config';

export const feedbackProjectId = import.meta.env.VITE_ANALYTICS_PROJECT_ID?.trim();

const toItem = (item: ApiFeedbackItem): FeedbackWorkspaceItem => ({
  feedbackItemId: item.feedback_item_id,
  feedbackId: item.feedback_id,
  reportedAt: item.reported_at,
  sourceSystem: item.source_system,
  contentMasked: item.content_masked,
  location: item.location,
  affectedChannelCodes: item.affected_channel_codes,
  currentClassification: {
    service: item.current_classification.service && { code: item.current_classification.service.code, nameVi: item.current_classification.service.name_vi },
    issue: item.current_classification.issue && { code: item.current_classification.issue.code, nameVi: item.current_classification.issue.name_vi },
    sentiment: item.current_classification.sentiment,
    operationalSeverity: item.current_classification.operational_severity,
    classificationState: item.current_classification.classification_state,
    projectionVersion: item.current_classification.projection_version,
  },
  status: item.status,
  analyticEligibility: item.analytic_eligibility,
  parentItemId: item.parent_item_id,
});

export const listFeedbackItems = async (filters: FeedbackListFilters): Promise<FeedbackListResult> => {
  const params = new URLSearchParams({ project_id: filters.projectId, limit: String(filters.limit ?? 100), offset: String(filters.offset ?? 0) });
  const fields: Record<Exclude<keyof FeedbackListFilters, 'projectId' | 'limit' | 'offset' | 'query'>, string> = {
    dateFrom: 'date_from',
    dateTo: 'date_to',
    sourceSystem: 'source_system',
    intakeChannelCode: 'intake_channel_code',
    affectedChannelCode: 'affected_channel_code',
    locationId: 'location_id',
    serviceCode: 'service_code',
    issueCode: 'issue_code',
    sentiment: 'sentiment',
    operationalSeverity: 'operational_severity',
    customerLifecycleStageCode: 'customer_lifecycle_stage_code',
    customerLifecycleStepCode: 'customer_lifecycle_step_code',
    touchpointCode: 'touchpoint_code',
    hotspotId: 'hotspot_id',
  };
  for (const [field, apiName] of Object.entries(fields)) {
    const value = filters[field as keyof typeof fields];
    if (value) params.set(apiName, value);
  }
  if (filters.query?.trim()) params.set('q', filters.query.trim());

  const response = await fetch(`${getApiBaseUrl()}/api/v1/feedback-items?${params.toString()}`);
  if (!response.ok) {
    let message = `Feedback API trả về lỗi ${response.status}.`;
    try {
      message = formatAnalyticsApiError((await response.json() as { detail?: unknown }).detail) ?? message;
    } catch {
      // Use the status message when the server did not return JSON.
    }
    throw new AnalyticsApiError(message, response.status);
  }
  const data = await response.json() as ApiListResponse;
  return { items: data.data.map(toItem), total: data.meta.total, limit: data.meta.limit, offset: data.meta.offset };
};

export const getFeedbackItem = async (feedbackItemId: string): Promise<FeedbackWorkspaceItem> => {
  const response = await fetch(`${getApiBaseUrl()}/api/v1/feedback-items/${feedbackItemId}`);
  if (!response.ok) throw new AnalyticsApiError(`Không tải được feedback item (${response.status}).`, response.status);
  return toItem((await response.json() as { data: ApiFeedbackItem }).data);
};
