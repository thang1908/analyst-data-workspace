export interface HotspotRef {
  id?: string;
  code?: string;
  name_vi?: string;
}

export interface HotspotItemData {
  hotspot_id: string;
  project_id: string;
  dimension_key: string;
  service: HotspotRef;
  issue: HotspotRef;
  location?: HotspotRef;
  status: 'CANDIDATE' | 'ACKNOWLEDGED' | 'INVESTIGATING' | 'RESOLVED' | 'DISMISSED' | 'REOPENED';
  action_priority: 'IMMEDIATE' | 'URGENT' | 'PLANNED' | 'MONITOR';
  operational_severity: 'SEV-1' | 'SEV-2' | 'SEV-3' | 'SEV-4';
  evidence_count: number;
  assigned_user_id?: string;
  assigned_team_key?: string;
  first_seen_at: string;
  last_seen_at: string;
  resolved_at?: string;
  resolution_summary?: string;
  window_start: string;
  window_end: string;
  version: number;
  created_at: string;
  updated_at: string;
}

export interface HotspotEvidence {
  feedback_item_id: string;
  reported_at: string;
  content_masked: string;
  sentiment: string;
  operational_severity: string;
  evidence_role: string;
}

export interface HotspotTimelineItem {
  timeline_event_id: string;
  hotspot_id: string;
  from_status?: string;
  to_status: string;
  action: string;
  actor_user_id: string;
  reason?: string;
  metadata_json?: Record<string, unknown>;
  correlation_id: string;
  created_at: string;
}

export interface HotspotDetailData {
  hotspot: HotspotItemData;
  evidence: HotspotEvidence[];
  timeline: HotspotTimelineItem[];
}

export interface HotspotListFilters {
  projectId: string;
  status?: string;
  actionPriority?: string;
  serviceCode?: string;
  issueCode?: string;
  locationId?: string;
  severity?: string;
  dateFrom?: string;
  dateTo?: string;
  limit?: number;
  offset?: number;
}

export interface HotspotListResponse {
  data: HotspotItemData[];
  meta: {
    total: number;
    limit: number;
    offset: number;
  };
}

export interface HotspotDetailResponse {
  data: HotspotDetailData;
}

const baseUrl = import.meta.env.VITE_API_URL ?? 'http://localhost:8000';

export const listHotspots = async (filters: HotspotListFilters): Promise<HotspotListResponse> => {
  const url = new URL(`${baseUrl}/api/v1/hotspots`);
  url.searchParams.set('project_id', filters.projectId);
  if (filters.status) url.searchParams.set('status', filters.status);
  if (filters.actionPriority) url.searchParams.set('action_priority', filters.actionPriority);
  if (filters.serviceCode) url.searchParams.set('service_code', filters.serviceCode);
  if (filters.issueCode) url.searchParams.set('issue_code', filters.issueCode);
  if (filters.locationId) url.searchParams.set('location_id', filters.locationId);
  if (filters.severity) url.searchParams.set('severity', filters.severity);
  if (filters.dateFrom) url.searchParams.set('date_from', filters.dateFrom);
  if (filters.dateTo) url.searchParams.set('date_to', filters.dateTo);
  if (filters.limit) url.searchParams.set('limit', String(filters.limit));
  if (filters.offset) url.searchParams.set('offset', String(filters.offset));

  const res = await fetch(url.toString());
  if (!res.ok) throw new Error(`Hotspot API error: ${res.status}`);
  return res.json() as Promise<HotspotListResponse>;
};

export const getHotspot = async (hotspotId: string): Promise<HotspotDetailData> => {
  const res = await fetch(`${baseUrl}/api/v1/hotspots/${hotspotId}`);
  if (!res.ok) throw new Error(`Hotspot API error: ${res.status}`);
  const json = await res.json() as HotspotDetailResponse;
  return json.data;
};

export const acknowledgeHotspot = async (
  hotspotId: string,
  data: { expected_version?: number; reason?: string }
): Promise<HotspotDetailData> => {
  const res = await fetch(`${baseUrl}/api/v1/hotspots/${hotspotId}/acknowledge`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error(`Acknowledge failed: ${res.status}`);
  const json = await res.json() as HotspotDetailResponse;
  return json.data;
};

export const assignHotspot = async (
  hotspotId: string,
  data: { expected_version?: number; owner_user_id?: string; owner_team_key?: string; reason?: string }
): Promise<HotspotDetailData> => {
  const res = await fetch(`${baseUrl}/api/v1/hotspots/${hotspotId}/assign`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error(`Assign failed: ${res.status}`);
  const json = await res.json() as HotspotDetailResponse;
  return json.data;
};

export const dismissHotspot = async (
  hotspotId: string,
  data: { expected_version?: number; reason: string }
): Promise<HotspotDetailData> => {
  const res = await fetch(`${baseUrl}/api/v1/hotspots/${hotspotId}/dismiss`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error(`Dismiss failed: ${res.status}`);
  const json = await res.json() as HotspotDetailResponse;
  return json.data;
};

export const resolveHotspot = async (
  hotspotId: string,
  data: { expected_version?: number; resolution_summary: string; reason?: string }
): Promise<HotspotDetailData> => {
  const res = await fetch(`${baseUrl}/api/v1/hotspots/${hotspotId}/resolve`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error(`Resolve failed: ${res.status}`);
  const json = await res.json() as HotspotDetailResponse;
  return json.data;
};

export const reopenHotspot = async (
  hotspotId: string,
  data: { expected_version?: number; reason: string }
): Promise<HotspotDetailData> => {
  const res = await fetch(`${baseUrl}/api/v1/hotspots/${hotspotId}/reopen`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error(`Reopen failed: ${res.status}`);
  const json = await res.json() as HotspotDetailResponse;
  return json.data;
};

export const detectHotspots = async (data: {
  project_id: string;
  window_days?: number;
  threshold_count?: number;
}): Promise<HotspotItemData[]> => {
  const res = await fetch(`${baseUrl}/api/v1/hotspots/detect`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error(`Detect failed: ${res.status}`);
  const json = await res.json() as HotspotListResponse;
  return json.data;
};
