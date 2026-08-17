import { AnalyticsBreakdownItem, AnalyticsFilterOption } from '../../api/analytics';

/**
 * Keep the dashboard structure aligned with the published taxonomy.  A
 * breakdown contains only dimensions that have matching feedback, whereas a
 * journey should still show its zero-volume stages and steps.
 */
export const mergeTaxonomyBreakdown = (
  taxonomy: AnalyticsFilterOption[],
  breakdown: AnalyticsBreakdownItem[],
): AnalyticsBreakdownItem[] => {
  const metricsByCode = new Map(breakdown.map((item) => [item.code, item]));
  return taxonomy.map((option) => metricsByCode.get(option.code) ?? {
    code: option.code,
    name: option.name,
    itemVolume: 0,
    percentage: 0,
    negativeRate: 0,
    activeHotspots: 0,
  });
};
