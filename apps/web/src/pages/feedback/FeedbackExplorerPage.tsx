import React, { useCallback, useEffect, useState } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { UploadCloud, Download, RefreshCw, ChevronLeft, ChevronRight, ChevronsLeft, ChevronsRight } from 'lucide-react';
import TopBar from '../../components/layout/TopBar';
import AnalyticsState from '../../components/analytics/AnalyticsState';
import FeedbackDataTable from '../../components/feedback/FeedbackDataTable';
import FeedbackDetailModal from '../../components/feedback/FeedbackDetailModal';
import FeedbackFilterToolbar from '../../components/feedback/FeedbackFilterToolbar';
import { listFeedbackItems, FeedbackWorkspaceItem } from '../../api/feedback';
import { analyticsConfigurationError, getAnalyticsSummary, AnalyticsSummary } from '../../api/analytics';
import { useAnalyticsFilters } from '../../hooks/useAnalyticsFilters';

const FeedbackExplorerPage: React.FC = () => {
  const navigate = useNavigate();
  const { filters, setFilter, resetFilters, activeFilterCount } = useAnalyticsFilters();
  const [searchParams, setSearchParams] = useSearchParams();
  const [items, setItems] = useState<FeedbackWorkspaceItem[]>([]);
  const [total, setTotal] = useState(0);
  const [summary, setSummary] = useState<AnalyticsSummary | null>(null);
  const [selectedItem, setSelectedItem] = useState<FeedbackWorkspaceItem | null>(null);
  const [loading, setLoading] = useState(Boolean(filters));
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const query = searchParams.get('q') ?? '';

  const setQuery = useCallback((value: string) => {
    setPage(1);
    setSearchParams((current) => {
      const next = new URLSearchParams(current);
      if (value) next.set('q', value); else next.delete('q');
      return next;
    });
  }, [setSearchParams]);

  // Reset to page 1 whenever filters change
  const handleFilterChange = (field: any, value: string | undefined) => {
    setPage(1);
    setFilter(field, value);
  };

  const handleResetFilters = () => {
    setPage(1);
    resetFilters();
  };

  // Load summary metrics for tabs
  useEffect(() => {
    if (!filters) return;
    void getAnalyticsSummary({
      projectId: filters.projectId,
      dateFrom: filters.dateFrom,
      dateTo: filters.dateTo,
      sourceSystem: filters.sourceSystem,
      locationId: filters.locationId,
      serviceCode: filters.serviceCode,
      issueCode: filters.issueCode,
    })
      .then(setSummary)
      .catch(() => {});
  }, [filters?.projectId, filters?.dateFrom, filters?.dateTo, filters?.sourceSystem, filters?.locationId, filters?.serviceCode, filters?.issueCode]);

  const loadItems = useCallback(async () => {
    if (!filters) return;
    setLoading(true);
    setError(null);
    try {
      const hotspotId = searchParams.get('hotspot_id') ?? undefined;
      const result = await listFeedbackItems({
        projectId: filters.projectId,
        dateFrom: filters.dateFrom,
        dateTo: filters.dateTo,
        sourceSystem: filters.sourceSystem,
        intakeChannelCode: filters.intakeChannelCode,
        affectedChannelCode: filters.affectedChannelCode,
        locationId: filters.locationId,
        serviceCode: filters.serviceCode,
        issueCode: filters.issueCode,
        sentiment: filters.sentiment,
        operationalSeverity: filters.operationalSeverity,
        customerLifecycleStageCode: filters.customerLifecycleStageCode,
        customerLifecycleStepCode: filters.customerLifecycleStepCode,
        touchpointCode: filters.touchpointCode,
        hotspotId,
        analyticEligibility: filters.analyticEligibility,
        query,
        limit: pageSize,
        offset: (page - 1) * pageSize,
      });
      setItems(result.items);
      setTotal(result.total);
    } catch (loadError) {
      setError(loadError instanceof Error ? loadError.message : 'Không thể tải danh sách feedback.');
    } finally {
      setLoading(false);
    }
  }, [filters, query, searchParams, page, pageSize]);

  useEffect(() => { void loadItems(); }, [loadItems]);

  const handleSelectItem = (item: FeedbackWorkspaceItem) => {
    setSelectedItem(item);
  };

  // Sentiment counts
  const totalVolume = summary?.itemVolume ?? total;
  const negCount = summary ? Math.round(summary.itemVolume * summary.negativeRate) : 0;
  const posCount = summary ? Math.round(summary.itemVolume * summary.positiveRate) : 0;
  const neuCount = summary ? Math.max(0, summary.itemVolume - negCount - posCount) : 0;

  // Total pages
  const totalPages = Math.max(1, Math.ceil(total / pageSize));

  // Handle Export CSV
  const handleExportCSV = () => {
    if (!items.length) return;
    const csvRows = [
      ['ID', 'Noi dung da mask', 'Khu do thi', 'Dich vu', 'Van de', 'Cam xuc', 'Muc do', 'Kenh', 'Thoi gian'].join(','),
      ...items.map((it) => [
        `"${it.feedbackItemId}"`,
        `"${it.contentMasked.replace(/"/g, '""')}"`,
        `"${it.location.name || it.location.code || ''}"`,
        `"${it.currentClassification.service?.nameVi || ''}"`,
        `"${it.currentClassification.issue?.nameVi || ''}"`,
        `"${it.currentClassification.sentiment || ''}"`,
        `"${it.currentClassification.operationalSeverity || ''}"`,
        `"${it.sourceSystem || ''}"`,
        `"${it.reportedAt}"`,
      ].join(',')),
    ];
    const blob = new Blob([csvRows.join('\n')], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `danh_sach_phan_anh_${new Date().toISOString().slice(0, 10)}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <>
      <TopBar title="Tra cứu phản hồi" subtitle="Bằng chứng và phân loại dữ liệu" />
      <main className="page-content" style={{ padding: '20px 24px', width: '100%', maxWidth: '100%', boxSizing: 'border-box', minWidth: 0, display: 'flex', flexDirection: 'column', gap: 16 }}>
        {analyticsConfigurationError && (
          <AnalyticsState title="Chưa cấu hình Analytics" message={analyticsConfigurationError} />
        )}

        {!analyticsConfigurationError && (
          <>
            {/* Header: Title, Action buttons & Sentiment Quick Tabs */}
            <div className="card" style={{ padding: '18px 20px', borderRadius: 8 }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 14 }}>
                {/* Title */}
                <div>
                  <h2 style={{ fontSize: 18, fontWeight: 800, color: '#0f172a', margin: '0 0 12px 0', letterSpacing: '-0.2px' }}>
                    Danh sách phản ánh
                  </h2>

                  {/* Sentiment Segmented Tabs */}
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
                    <button
                      onClick={() => handleFilterChange('sentiment', undefined)}
                      style={{
                        padding: '6px 12px',
                        borderRadius: 6,
                        border: !filters?.sentiment ? '2px solid #2563eb' : '1px solid #e2e8f0',
                        background: !filters?.sentiment ? '#eff6ff' : '#ffffff',
                        color: !filters?.sentiment ? '#1d4ed8' : '#475569',
                        fontWeight: 700,
                        fontSize: 12,
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        gap: 6,
                      }}
                    >
                      <span>Tất cả</span>
                      <span style={{ background: !filters?.sentiment ? '#2563eb' : '#f1f5f9', color: !filters?.sentiment ? '#ffffff' : '#475569', padding: '1px 6px', borderRadius: 10, fontSize: 11 }}>
                        {totalVolume.toLocaleString()}
                      </span>
                    </button>

                    <button
                      onClick={() => handleFilterChange('sentiment', 'NEGATIVE')}
                      style={{
                        padding: '6px 12px',
                        borderRadius: 6,
                        border: filters?.sentiment === 'NEGATIVE' ? '2px solid #ef4444' : '1px solid #e2e8f0',
                        background: filters?.sentiment === 'NEGATIVE' ? '#fef2f2' : '#ffffff',
                        color: filters?.sentiment === 'NEGATIVE' ? '#b91c1c' : '#475569',
                        fontWeight: 700,
                        fontSize: 12,
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        gap: 6,
                      }}
                    >
                      <span style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                        <span style={{ width: 6, height: 6, borderRadius: '50%', background: '#ef4444' }} />
                        Tiêu cực
                      </span>
                      <span style={{ background: filters?.sentiment === 'NEGATIVE' ? '#ef4444' : '#fee2e2', color: filters?.sentiment === 'NEGATIVE' ? '#ffffff' : '#991b1b', padding: '1px 6px', borderRadius: 10, fontSize: 11 }}>
                        {negCount.toLocaleString()}
                      </span>
                    </button>

                    <button
                      onClick={() => handleFilterChange('sentiment', 'NEUTRAL')}
                      style={{
                        padding: '6px 12px',
                        borderRadius: 6,
                        border: filters?.sentiment === 'NEUTRAL' ? '2px solid #64748b' : '1px solid #e2e8f0',
                        background: filters?.sentiment === 'NEUTRAL' ? '#f8fafc' : '#ffffff',
                        color: filters?.sentiment === 'NEUTRAL' ? '#0f172a' : '#475569',
                        fontWeight: 700,
                        fontSize: 12,
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        gap: 6,
                      }}
                    >
                      <span style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                        <span style={{ width: 6, height: 6, borderRadius: '50%', background: '#94a3b8' }} />
                        Trung tính
                      </span>
                      <span style={{ background: filters?.sentiment === 'NEUTRAL' ? '#64748b' : '#f1f5f9', color: filters?.sentiment === 'NEUTRAL' ? '#ffffff' : '#475569', padding: '1px 6px', borderRadius: 10, fontSize: 11 }}>
                        {neuCount.toLocaleString()}
                      </span>
                    </button>

                    <button
                      onClick={() => handleFilterChange('sentiment', 'POSITIVE')}
                      style={{
                        padding: '6px 12px',
                        borderRadius: 6,
                        border: filters?.sentiment === 'POSITIVE' ? '2px solid #22c55e' : '1px solid #e2e8f0',
                        background: filters?.sentiment === 'POSITIVE' ? '#f0fdf4' : '#ffffff',
                        color: filters?.sentiment === 'POSITIVE' ? '#15803d' : '#475569',
                        fontWeight: 700,
                        fontSize: 12,
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        gap: 6,
                      }}
                    >
                      <span style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                        <span style={{ width: 6, height: 6, borderRadius: '50%', background: '#22c55e' }} />
                        Tích cực
                      </span>
                      <span style={{ background: filters?.sentiment === 'POSITIVE' ? '#22c55e' : '#dcfce7', color: filters?.sentiment === 'POSITIVE' ? '#ffffff' : '#166534', padding: '1px 6px', borderRadius: 10, fontSize: 11 }}>
                        {posCount.toLocaleString()}
                      </span>
                    </button>
                  </div>
                </div>

                {/* Right Action Buttons */}
                <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                  <button
                    onClick={() => navigate('/imports')}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: 6,
                      padding: '8px 14px',
                      borderRadius: 6,
                      background: '#eff6ff',
                      color: '#2563eb',
                      border: '1px solid #bfdbfe',
                      fontWeight: 600,
                      fontSize: 12,
                      cursor: 'pointer',
                    }}
                  >
                    <UploadCloud size={15} />
                    Nhập dữ liệu
                  </button>

                  <button
                    onClick={handleExportCSV}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: 6,
                      padding: '8px 14px',
                      borderRadius: 6,
                      background: '#ffffff',
                      color: '#475569',
                      border: '1px solid #cbd5e1',
                      fontWeight: 600,
                      fontSize: 12,
                      cursor: 'pointer',
                    }}
                  >
                    <Download size={15} />
                    Xuất CSV
                  </button>

                  <button
                    onClick={() => void loadItems()}
                    style={{
                      padding: '8px 10px',
                      borderRadius: 6,
                      background: '#ffffff',
                      border: '1px solid #cbd5e1',
                      color: '#475569',
                      cursor: 'pointer',
                    }}
                    title="Làm mới"
                  >
                    <RefreshCw size={14} className={loading ? 'spin' : ''} />
                  </button>
                </div>
              </div>
            </div>

            {/* Horizontal Filter Toolbar */}
            <FeedbackFilterToolbar
              filters={filters}
              activeFilterCount={activeFilterCount}
              query={query}
              onQueryChange={setQuery}
              onChange={handleFilterChange}
              onReset={handleResetFilters}
            />

            {/* Table Section */}
            {loading && (
              <AnalyticsState title="Đang tải danh sách phản ánh" message="Đang truy vấn dữ liệu theo trang và bộ lọc…" />
            )}

            {!loading && error && (
              <AnalyticsState title="Không tải được danh sách" message={error} onRetry={() => void loadItems()} />
            )}

            {!loading && !error && !items.length && (
              <AnalyticsState
                title="Không tìm thấy phản ánh nào"
                message="Hãy thử thay đổi từ khóa tìm kiếm hoặc đặt lại bộ lọc."
                onRetry={() => {
                  handleResetFilters();
                  setQuery('');
                }}
              />
            )}

            {!loading && !error && Boolean(items.length) && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                <FeedbackDataTable
                  items={items}
                  selectedId={selectedItem?.feedbackItemId}
                  onSelect={handleSelectItem}
                />

                {/* Modern Pagination Footer */}
                <div
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    flexWrap: 'wrap',
                    gap: 12,
                    background: '#ffffff',
                    padding: '12px 18px',
                    borderRadius: 8,
                    border: '1px solid #e2e8f0',
                    fontSize: 13,
                    color: '#475569',
                  }}
                >
                  {/* Left: Range Info & Page Size */}
                  <div style={{ display: 'flex', alignItems: 'center', gap: 14, flexWrap: 'wrap' }}>
                    <span>
                      Hiển thị <strong>{(page - 1) * pageSize + 1}</strong> -{' '}
                      <strong>{Math.min(page * pageSize, total).toLocaleString()}</strong> trong{' '}
                      <strong>{total.toLocaleString()}</strong> phản ánh
                    </span>

                    <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                      <span style={{ fontSize: 12, color: '#64748b' }}>Mỗi trang:</span>
                      <select
                        value={pageSize}
                        onChange={(e) => {
                          setPageSize(Number(e.target.value));
                          setPage(1);
                        }}
                        style={{
                          padding: '4px 8px',
                          borderRadius: 6,
                          border: '1px solid #cbd5e1',
                          background: '#ffffff',
                          fontSize: 12,
                          color: '#1e293b',
                          cursor: 'pointer',
                        }}
                      >
                        <option value={10}>10 mục</option>
                        <option value={20}>20 mục</option>
                        <option value={50}>50 mục</option>
                      </select>
                    </div>
                  </div>

                  {/* Right: Pagination Controls */}
                  <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                    <button
                      onClick={() => setPage(1)}
                      disabled={page === 1}
                      style={{
                        padding: '6px 8px',
                        borderRadius: 6,
                        border: '1px solid #cbd5e1',
                        background: page === 1 ? '#f8fafc' : '#ffffff',
                        color: page === 1 ? '#94a3b8' : '#334155',
                        cursor: page === 1 ? 'not-allowed' : 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                      }}
                      title="Trang đầu"
                    >
                      <ChevronsLeft size={15} />
                    </button>

                    <button
                      onClick={() => setPage((p) => Math.max(1, p - 1))}
                      disabled={page === 1}
                      style={{
                        padding: '6px 10px',
                        borderRadius: 6,
                        border: '1px solid #cbd5e1',
                        background: page === 1 ? '#f8fafc' : '#ffffff',
                        color: page === 1 ? '#94a3b8' : '#334155',
                        cursor: page === 1 ? 'not-allowed' : 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        gap: 4,
                        fontSize: 12,
                        fontWeight: 600,
                      }}
                    >
                      <ChevronLeft size={15} /> Trước
                    </button>

                    {/* Page Numbers */}
                    <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                      {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                        let pageNum = i + 1;
                        if (totalPages > 5 && page > 3) {
                          pageNum = page - 3 + i;
                          if (pageNum > totalPages) pageNum = totalPages - (4 - i);
                        }
                        if (pageNum < 1 || pageNum > totalPages) return null;

                        const isCurrent = page === pageNum;
                        return (
                          <button
                            key={pageNum}
                            onClick={() => setPage(pageNum)}
                            style={{
                              width: 32,
                              height: 32,
                              borderRadius: 6,
                              border: isCurrent ? '1px solid #2563eb' : '1px solid #cbd5e1',
                              background: isCurrent ? '#2563eb' : '#ffffff',
                              color: isCurrent ? '#ffffff' : '#334155',
                              fontWeight: isCurrent ? 700 : 500,
                              fontSize: 12,
                              cursor: 'pointer',
                            }}
                          >
                            {pageNum}
                          </button>
                        );
                      })}
                    </div>

                    <button
                      onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                      disabled={page >= totalPages}
                      style={{
                        padding: '6px 10px',
                        borderRadius: 6,
                        border: '1px solid #cbd5e1',
                        background: page >= totalPages ? '#f8fafc' : '#ffffff',
                        color: page >= totalPages ? '#94a3b8' : '#334155',
                        cursor: page >= totalPages ? 'not-allowed' : 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        gap: 4,
                        fontSize: 12,
                        fontWeight: 600,
                      }}
                    >
                      Sau <ChevronRight size={15} />
                    </button>

                    <button
                      onClick={() => setPage(totalPages)}
                      disabled={page >= totalPages}
                      style={{
                        padding: '6px 8px',
                        borderRadius: 6,
                        border: '1px solid #cbd5e1',
                        background: page >= totalPages ? '#f8fafc' : '#ffffff',
                        color: page >= totalPages ? '#94a3b8' : '#334155',
                        cursor: page >= totalPages ? 'not-allowed' : 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                      }}
                      title="Trang cuối"
                    >
                      <ChevronsRight size={15} />
                    </button>
                  </div>
                </div>
              </div>
            )}
          </>
        )}

        {/* Detail Modal */}
        {selectedItem && (
          <FeedbackDetailModal
            item={selectedItem}
            onClose={() => setSelectedItem(null)}
            onItemUpdated={(updated) => {
              setItems((prev) => prev.map((it) => (it.feedbackItemId === updated.feedbackItemId ? updated : it)));
              setSelectedItem(updated);
            }}
          />
        )}
      </main>
    </>
  );
};

export default FeedbackExplorerPage;
