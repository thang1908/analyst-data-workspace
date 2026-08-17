export interface AnalyticsFilters {
  projectId: string;
  dateFrom?: string;
  dateTo?: string;
  sourceSystem?: string;
  intakeChannelCode?: string;
  affectedChannelCode?: string;
  locationId?: string;
  locationScope?: string;
  customerLifecycleStageCode?: string;
  customerLifecycleStepCode?: string;
  touchpointCode?: string;
  serviceRequestStepCode?: string;
  serviceCode?: string;
  issueCode?: string;
  sentiment?: string;
  operationalSeverity?: string;
}

export interface AnalyticsSummary {
  itemVolume: number;
  csatScore: number;
  positiveRate: number;
  negativeRate: number;
  unknownRate: number;
  activeHotspots: number;
}

export interface AnalyticsTrendPoint {
  bucket: string;
  itemVolume: number;
  negativeRate: number;
  unknownRate: number;
  activeHotspots: number;
}

export interface AnalyticsBreakdownItem {
  code: string;
  name: string;
  itemVolume: number;
  percentage: number;
  negativeRate: number;
  activeHotspots: number;
}

export interface AnalyticsFilterOption {
  code: string;
  name: string;
  id?: string;
}

export interface AnalyticsFilterOptions {
  sourceSystems: AnalyticsFilterOption[];
  intakeChannels: AnalyticsFilterOption[];
  affectedChannels: AnalyticsFilterOption[];
  locations: AnalyticsFilterOption[];
  journeyStages: AnalyticsFilterOption[];
  journeySteps: AnalyticsFilterOption[];
  touchpoints: AnalyticsFilterOption[];
  serviceRequestSteps: AnalyticsFilterOption[];
  services: AnalyticsFilterOption[];
  issues: AnalyticsFilterOption[];
  sentiments: AnalyticsFilterOption[];
  severities: AnalyticsFilterOption[];
}

interface ApiEnvelope<T> {
  data: T;
}

interface ApiSummary {
  item_volume: number;
  csat_score: number;
  positive_rate: number;
  negative_rate: number;
  unknown_rate: number;
  active_hotspots: number;
}

interface ApiTrendPoint {
  bucket: string;
  item_volume: number;
  negative_rate: number;
  unknown_rate: number;
  active_hotspots: number;
}

interface ApiBreakdownItem {
  dimension: { code: string; name_vi: string };
  metrics: { item_volume: number; percentage: number; negative_rate: number; active_hotspots: number };
}

interface ApiFilterOption {
  code: string;
  name_vi: string;
  id: string | null;
}

interface ApiFilterOptions {
  source_systems: ApiFilterOption[];
  intake_channels: ApiFilterOption[];
  affected_channels: ApiFilterOption[];
  locations: ApiFilterOption[];
  journey_stages: ApiFilterOption[];
  journey_steps: ApiFilterOption[];
  touchpoints?: ApiFilterOption[];
  service_request_steps: ApiFilterOption[];
  services: ApiFilterOption[];
  issues: ApiFilterOption[];
  sentiments: ApiFilterOption[];
  severities: ApiFilterOption[];
}

export class AnalyticsApiError extends Error {
  constructor(message: string, public readonly status?: number) {
    super(message);
    this.name = 'AnalyticsApiError';
  }
}

const baseUrl = (import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000').replace(/\/$/, '');
const projectId = import.meta.env.VITE_ANALYTICS_PROJECT_ID?.trim();

type ErrorDetail = {
  loc?: unknown;
  msg?: unknown;
};

const isErrorDetail = (value: unknown): value is ErrorDetail => (
  typeof value === 'object' && value !== null
);

/** Turn FastAPI's string or structured validation detail into readable UI text. */
export const formatAnalyticsApiError = (detail: unknown): string | null => {
  if (typeof detail === 'string' && detail.trim()) return detail;

  if (Array.isArray(detail)) {
    const messages = detail.flatMap((item) => {
      if (!isErrorDetail(item) || typeof item.msg !== 'string') return [];
      const location = Array.isArray(item.loc)
        ? item.loc.filter((part) => part !== 'query' && part !== 'body').join('.')
        : '';
      return [location ? `${location}: ${item.msg}` : item.msg];
    });
    return messages.length ? messages.join(' • ') : null;
  }

  if (isErrorDetail(detail) && typeof detail.msg === 'string') return detail.msg;
  return null;
};

/** Format a calendar date without converting it to UTC first. */
export const formatLocalDate = (value: Date): string => {
  const year = value.getFullYear();
  const month = String(value.getMonth() + 1).padStart(2, '0');
  const day = String(value.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
};

export const analyticsConfigurationError = projectId
  ? null
  : 'Thiếu VITE_ANALYTICS_PROJECT_ID. Hãy cấu hình UUID project trong apps/web/.env.local.';

export const defaultAnalyticsFilters = (): AnalyticsFilters | null => {
  if (!projectId) return null;
  const dateTo = new Date();
  const dateFrom = new Date();
  dateFrom.setDate(dateTo.getDate() - 29);
  return {
    projectId,
    dateFrom: formatLocalDate(dateFrom),
    dateTo: formatLocalDate(dateTo),
  };
};

const filterParams = (filters: AnalyticsFilters): URLSearchParams => {
  const params = new URLSearchParams({ project_id: filters.projectId });
  const names: Record<Exclude<keyof AnalyticsFilters, 'projectId'>, string> = {
    dateFrom: 'date_from',
    dateTo: 'date_to',
    sourceSystem: 'source_system',
    intakeChannelCode: 'intake_channel_code',
    affectedChannelCode: 'affected_channel_code',
    locationId: 'location_id',
    locationScope: 'location_scope',
    customerLifecycleStageCode: 'customer_lifecycle_stage_code',
    customerLifecycleStepCode: 'customer_lifecycle_step_code',
    touchpointCode: 'touchpoint_code',
    serviceRequestStepCode: 'service_request_step_code',
    serviceCode: 'service_code',
    issueCode: 'issue_code',
    sentiment: 'sentiment',
    operationalSeverity: 'operational_severity',
  };
  for (const [key, apiName] of Object.entries(names)) {
    const value = filters[key as keyof typeof names];
    if (value) params.set(apiName, value);
  }
  return params;
};

const request = async <T>(path: string, params: URLSearchParams): Promise<T> => {
  const response = await fetch(`${baseUrl}/api/v1/analytics${path}?${params.toString()}`);
  if (!response.ok) {
    let detail = `Analytics API trả về lỗi ${response.status}.`;
    try {
      const body = await response.json() as { detail?: unknown };
      detail = formatAnalyticsApiError(body.detail) ?? detail;
    } catch {
      // Keep the HTTP status message if the response body is not JSON.
    }
    throw new AnalyticsApiError(detail, response.status);
  }
  return response.json() as Promise<T>;
};

export const getAnalyticsSummary = async (filters: AnalyticsFilters): Promise<AnalyticsSummary> => {
  const response = await request<ApiEnvelope<ApiSummary>>('/summary', filterParams(filters));
  return {
    itemVolume: response.data.item_volume,
    csatScore: response.data.csat_score,
    positiveRate: response.data.positive_rate,
    negativeRate: response.data.negative_rate,
    unknownRate: response.data.unknown_rate,
    activeHotspots: response.data.active_hotspots,
  };
};

export const getAnalyticsTrend = async (
  filters: AnalyticsFilters,
  grain: 'day' | 'week' | 'month' = 'day',
): Promise<AnalyticsTrendPoint[]> => {
  const params = filterParams(filters);
  params.set('grain', grain);
  const response = await request<ApiEnvelope<ApiTrendPoint[]>>('/trend', params);
  return response.data.map((point) => ({
    bucket: point.bucket,
    itemVolume: point.item_volume,
    negativeRate: point.negative_rate,
    unknownRate: point.unknown_rate,
    activeHotspots: point.active_hotspots,
  }));
};

export const getAnalyticsBreakdown = async (
  filters: AnalyticsFilters,
  dimension: string,
  limit = 20,
): Promise<AnalyticsBreakdownItem[]> => {
  const params = filterParams(filters);
  params.set('dimension', dimension);
  params.set('limit', String(limit));
  const response = await request<ApiEnvelope<ApiBreakdownItem[]>>('/breakdown', params);
  return response.data.map((item) => ({
    code: item.dimension.code,
    name: item.dimension.name_vi,
    itemVolume: item.metrics.item_volume,
    percentage: item.metrics.percentage,
    negativeRate: item.metrics.negative_rate,
    activeHotspots: item.metrics.active_hotspots,
  }));
};

const toFilterOption = (item: ApiFilterOption): AnalyticsFilterOption => ({
  code: item.code,
  name: item.name_vi,
  ...(item.id ? { id: item.id } : {}),
});

export const getAnalyticsFilterOptions = async (
  filters: AnalyticsFilters,
): Promise<AnalyticsFilterOptions> => {
  const response = await request<ApiEnvelope<ApiFilterOptions>>('/filter-options', filterParams(filters));
  const data = response.data;
  return {
    sourceSystems: (data.source_systems ?? []).map(toFilterOption),
    intakeChannels: (data.intake_channels ?? []).map(toFilterOption),
    affectedChannels: (data.affected_channels ?? []).map(toFilterOption),
    locations: (data.locations ?? []).map(toFilterOption),
    journeyStages: (data.journey_stages ?? []).map(toFilterOption),
    journeySteps: (data.journey_steps ?? []).map(toFilterOption),
    touchpoints: (data.touchpoints ?? []).map(toFilterOption),
    serviceRequestSteps: (data.service_request_steps ?? []).map(toFilterOption),
    services: (data.services ?? []).map(toFilterOption),
    issues: (data.issues ?? []).map(toFilterOption),
    sentiments: (data.sentiments ?? []).map(toFilterOption),
    severities: (data.severities ?? []).map(toFilterOption),
  };
};
