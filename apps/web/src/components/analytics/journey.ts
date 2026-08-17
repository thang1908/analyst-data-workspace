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
  return taxonomy.map((option) => {
    const metrics = metricsByCode.get(option.code);
    return {
      code: option.code,
      // The active taxonomy owns display labels. Metrics can originate from
      // an older release, while the stable code keeps the meaning unchanged.
      name: option.name,
      itemVolume: metrics?.itemVolume ?? 0,
      percentage: metrics?.percentage ?? 0,
      negativeRate: metrics?.negativeRate ?? 0,
      activeHotspots: metrics?.activeHotspots ?? 0,
    };
  });
};
