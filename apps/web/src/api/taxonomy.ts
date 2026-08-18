export interface LifecycleStage {
  id: string;
  code: string;
  name_vi: string;
  name_en?: string;
  definition?: string;
  sort_order: number;
}

export interface LifecycleStep {
  id: string;
  code: string;
  stage: {
    id: string;
    code: string;
    name_vi: string;
  };
  name_vi: string;
  name_en?: string;
  definition?: string;
  sort_order: number;
}

export interface TouchpointService {
  id: string;
  code: string;
  name_vi: string;
  mapping_type: 'PRIMARY' | 'SECONDARY';
}

export interface Touchpoint {
  id: string;
  code: string;
  name_vi: string;
  name_en?: string;
  definition?: string;
  lifecycle_step: {
    id: string;
    code: string;
    name_vi: string;
  };
  services: TouchpointService[];
  sort_order: number;
  active: boolean;
}

export interface ServiceItem {
  id: string;
  code: string;
  name_vi: string;
  name_en?: string;
  default_severity: string;
  definition?: string;
  sort_order: number;
}

export interface IssueItem {
  id: string;
  code: string;
  service: {
    id: string;
    code: string;
    name_vi: string;
  };
  name_vi: string;
  name_en?: string;
  safety_critical: boolean;
  definition?: string;
  sort_order: number;
}

const baseUrl = (import.meta.env.VITE_API_BASE_URL ?? import.meta.env.VITE_API_URL ?? '').replace(/\/$/, '');

export const listCustomerLifecycleStages = async (): Promise<LifecycleStage[]> => {
  const res = await fetch(`${baseUrl}/api/v1/customer-lifecycle/stages`);
  if (!res.ok) throw new Error(`Taxonomy API error: ${res.status}`);
  return res.json() as Promise<LifecycleStage[]>;
};

export const listCustomerLifecycleSteps = async (stageCode?: string): Promise<LifecycleStep[]> => {
  const url = new URL(`${baseUrl}/api/v1/customer-lifecycle/steps`);
  if (stageCode) url.searchParams.set('stage_code', stageCode);
  const res = await fetch(url.toString());
  if (!res.ok) throw new Error(`Taxonomy API error: ${res.status}`);
  return res.json() as Promise<LifecycleStep[]>;
};

export const listCustomerLifecycleTouchpoints = async (
  stepCode?: string,
  serviceCode?: string
): Promise<Touchpoint[]> => {
  const url = new URL(`${baseUrl}/api/v1/customer-lifecycle/touchpoints`);
  if (stepCode) url.searchParams.set('step_code', stepCode);
  if (serviceCode) url.searchParams.set('service_code', serviceCode);
  const res = await fetch(url.toString());
  if (!res.ok) throw new Error(`Taxonomy API error: ${res.status}`);
  return res.json() as Promise<Touchpoint[]>;
};

export const listServices = async (): Promise<ServiceItem[]> => {
  const res = await fetch(`${baseUrl}/api/v1/services`);
  if (!res.ok) throw new Error(`Taxonomy API error: ${res.status}`);
  return res.json() as Promise<ServiceItem[]>;
};

export const listIssues = async (serviceCode?: string): Promise<IssueItem[]> => {
  const url = new URL(`${baseUrl}/api/v1/issues`);
  if (serviceCode) url.searchParams.set('service_code', serviceCode);
  const res = await fetch(url.toString());
  if (!res.ok) throw new Error(`Taxonomy API error: ${res.status}`);
  return res.json() as Promise<IssueItem[]>;
};
