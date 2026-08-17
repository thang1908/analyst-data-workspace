import { useCallback, useMemo } from 'react';
import { useSearchParams } from 'react-router-dom';
import { AnalyticsFilters, defaultAnalyticsFilters } from '../api/analytics';

type FilterField = Exclude<keyof AnalyticsFilters, 'projectId'>;

const queryNames: Record<FilterField, string> = {
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

const filterFields = Object.keys(queryNames) as FilterField[];

export const useAnalyticsFilters = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const defaults = defaultAnalyticsFilters();

  const filters = useMemo<AnalyticsFilters | null>(() => {
    if (!defaults) return null;
    const values: AnalyticsFilters = { ...defaults };
    for (const field of filterFields) {
      const value = searchParams.get(queryNames[field]);
      if (value) values[field] = value;
    }
    return values;
  }, [defaults?.projectId, searchParams]);

  const setFilter = useCallback((field: FilterField, value: string | undefined) => {
    setSearchParams((current) => {
      const next = new URLSearchParams(current);
      if (value) next.set(queryNames[field], value);
      else next.delete(queryNames[field]);
      if (field === 'customerLifecycleStageCode') {
        next.delete(queryNames.customerLifecycleStepCode);
        next.delete(queryNames.touchpointCode);
      }
      if (field === 'customerLifecycleStepCode') {
        next.delete(queryNames.touchpointCode);
      }
      if (field === 'serviceCode') next.delete(queryNames.issueCode);
      return next;
    });
  }, [setSearchParams]);

  const resetFilters = useCallback(() => setSearchParams({}), [setSearchParams]);
  const activeFilterCount = filterFields.filter((field) => {
    if (field === 'dateFrom' || field === 'dateTo') return false;
    return Boolean(searchParams.get(queryNames[field]));
  }).length;

  return { filters, setFilter, resetFilters, activeFilterCount };
};
