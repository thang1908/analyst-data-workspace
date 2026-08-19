import React, { useCallback, useEffect, useState } from 'react';
import TopBar from '../../components/layout/TopBar';
import { HotspotActionQueue } from '../../components/hotspot/HotspotActionQueue';
import { HotspotDashboard } from '../../components/hotspot/HotspotDashboard';
import { HotspotItemData, listHotspots } from '../../api/hotspots';
import { useAnalyticsFilters } from '../../hooks/useAnalyticsFilters';
import AnalyticsFilterBar from '../../components/analytics/AnalyticsFilterBar';
import AnalyticsState from '../../components/analytics/AnalyticsState';

export const HotspotPage: React.FC = () => {
  const { filters, setFilter, resetFilters, activeFilterCount } = useAnalyticsFilters();
  const [hotspots, setHotspots] = useState<HotspotItemData[]>([]);
  const [loading, setLoading] = useState(Boolean(filters));
  const [error, setError] = useState<string | null>(null);

  const loadHotspots = useCallback(async () => {
    if (!filters?.projectId) return;
    setLoading(true);
    setError(null);
    try {
      const res = await listHotspots({
        projectId: filters.projectId,
        serviceCode: filters.serviceCode,
        issueCode: filters.issueCode,
        locationId: filters.locationId,
        dateFrom: filters.dateFrom,
        dateTo: filters.dateTo,
      });
      setHotspots(res.data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Không thể tải danh sách điểm nóng.');
    } finally {
      setLoading(false);
    }
  }, [filters]);

  useEffect(() => {
    void loadHotspots();
  }, [loadHotspots]);

  return (
    <>
      <TopBar title="Quản lý Điểm nóng" />
      <div className="page-content">
        <AnalyticsFilterBar
          filters={filters}
          activeFilterCount={activeFilterCount}
          onChange={setFilter}
          onReset={resetFilters}
        />
        {error ? (
          <AnalyticsState title="Lỗi tải dữ liệu" message={error} onRetry={() => void loadHotspots()} />
        ) : (
          filters && (
            <>
              {/* Visual Dashboard: KPIs + Charts */}
              {!loading && hotspots.length > 0 && (
                <HotspotDashboard hotspots={hotspots} />
              )}

              {/* Action Queue: scrollable cards */}
              <HotspotActionQueue
                projectId={filters.projectId}
                hotspots={hotspots}
                loading={loading}
                onRefresh={() => void loadHotspots()}
              />
            </>
          )
        )}
      </div>
    </>
  );
};

export default HotspotPage;
