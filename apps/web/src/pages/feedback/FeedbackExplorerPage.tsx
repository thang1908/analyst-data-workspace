import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import TopBar from '../../components/layout/TopBar';
import AnalyticsState from '../../components/analytics/AnalyticsState';
import FeedbackFilters from '../../components/feedback/FeedbackFilters';
import FeedbackItemDetail from '../../components/feedback/FeedbackItemDetail';
import FeedbackItemList from '../../components/feedback/FeedbackItemList';
import { getFeedbackItem, listFeedbackItems, FeedbackWorkspaceItem } from '../../api/feedback';
import { analyticsConfigurationError } from '../../api/analytics';
import { useAnalyticsFilters } from '../../hooks/useAnalyticsFilters';

const FeedbackExplorerPage: React.FC = () => {
  const { filters, setFilter, resetFilters, activeFilterCount } = useAnalyticsFilters();
  const [searchParams, setSearchParams] = useSearchParams();
  const [items, setItems] = useState<FeedbackWorkspaceItem[]>([]);
  const [total, setTotal] = useState(0);
  const [selectedId, setSelectedId] = useState<string | undefined>();
  const [selectedItem, setSelectedItem] = useState<FeedbackWorkspaceItem | null>(null);
  const [loading, setLoading] = useState(Boolean(filters));
  const [detailLoading, setDetailLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const query = searchParams.get('q') ?? '';

  const setQuery = useCallback((value: string) => {
    setSearchParams((current) => {
      const next = new URLSearchParams(current);
      if (value) next.set('q', value); else next.delete('q');
      return next;
    });
  }, [setSearchParams]);

  const loadItems = useCallback(async () => {
    if (!filters) return;
    setLoading(true);
    setError(null);
    try {
      const result = await listFeedbackItems({
        projectId: filters.projectId, dateFrom: filters.dateFrom, dateTo: filters.dateTo,
        sourceSystem: filters.sourceSystem, intakeChannelCode: filters.intakeChannelCode,
        affectedChannelCode: filters.affectedChannelCode, locationId: filters.locationId, query,
      });
      const clientFiltered = result.items.filter((item) => {
        const current = item.currentClassification;
        return (!filters.serviceCode || current.service?.code === filters.serviceCode)
          && (!filters.issueCode || current.issue?.code === filters.issueCode)
          && (!filters.sentiment || current.sentiment === filters.sentiment)
          && (!filters.operationalSeverity || current.operationalSeverity === filters.operationalSeverity);
      });
      setItems(clientFiltered);
      setTotal(result.total);
      setSelectedId((current) => clientFiltered.some((item) => item.feedbackItemId === current) ? current : clientFiltered[0]?.feedbackItemId);
    } catch (loadError) {
      setError(loadError instanceof Error ? loadError.message : 'Không thể tải feedback.');
    } finally {
      setLoading(false);
    }
  }, [filters, query]);

  useEffect(() => { void loadItems(); }, [loadItems]);

  useEffect(() => {
    if (!selectedId) { setSelectedItem(null); return; }
    setDetailLoading(true);
    void getFeedbackItem(selectedId)
      .then(setSelectedItem)
      .catch((detailError) => setError(detailError instanceof Error ? detailError.message : 'Không thể tải chi tiết feedback.'))
      .finally(() => setDetailLoading(false));
  }, [selectedId]);

  const resultLabel = useMemo(() => {
    if (items.length === total) return `${total.toLocaleString()} feedback items`;
    return `${items.length.toLocaleString()} / ${total.toLocaleString()} feedback items`;
  }, [items.length, total]);

  return <>
    <TopBar title="Feedback Explorer" subtitle="Khoan sâu từ vấn đề đến bằng chứng đã mask" />
    <main className="page-content feedback-explorer-page">
      {analyticsConfigurationError && <AnalyticsState title="Chưa cấu hình Analytics" message={analyticsConfigurationError} />}
      {!analyticsConfigurationError && <>
        <FeedbackFilters
          filters={filters}
          activeFilterCount={activeFilterCount}
          query={query}
          onQueryChange={setQuery}
          onChange={setFilter}
          onReset={() => { resetFilters(); setQuery(''); }}
        />
        <div className="feedback-workspace" aria-label="Feedback Explorer workspace">
          <section className="card feedback-list-panel">
            <div className="feedback-panel-heading"><div><span className="section-title">Feedback items</span><p>Bằng chứng khớp bộ lọc hiện tại</p></div><strong>{resultLabel}</strong></div>
            {loading && <AnalyticsState title="Đang tải feedback" message="Đang truy vấn các bằng chứng đã mask…" />}
            {!loading && error && <AnalyticsState title="Không tải được feedback" message={error} onRetry={() => void loadItems()} />}
            {!loading && !error && !items.length && <AnalyticsState title="Không có feedback khớp bộ lọc" message="Hãy nới bộ lọc hoặc thử cụm từ tìm kiếm khác." onRetry={() => { resetFilters(); setQuery(''); }} />}
            {!loading && !error && Boolean(items.length) && <FeedbackItemList items={items} selectedId={selectedId} onSelect={(item) => setSelectedId(item.feedbackItemId)} />}
          </section>
          <aside className="card feedback-detail-panel" aria-live="polite">
            <div className="feedback-panel-heading"><div><span className="section-title">Chi tiết feedback</span><p>Evidence và phân loại hiện tại</p></div>{detailLoading && <span className="panel-count">Đang tải…</span>}</div>
            <FeedbackItemDetail item={selectedItem} />
          </aside>
        </div>
      </>}
    </main>
  </>;
};

export default FeedbackExplorerPage;
