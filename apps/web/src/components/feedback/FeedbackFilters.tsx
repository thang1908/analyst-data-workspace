import React, { useEffect, useState } from 'react';
import { RotateCcw, Search, SlidersHorizontal } from 'lucide-react';
import AnalyticsState from '../analytics/AnalyticsState';
import { AnalyticsFilterOption, AnalyticsFilterOptions, AnalyticsFilters, getAnalyticsFilterOptions } from '../../api/analytics';

type FilterField = Exclude<keyof AnalyticsFilters, 'projectId'>;

interface FeedbackFiltersProps {
  filters: AnalyticsFilters | null;
  activeFilterCount: number;
  query: string;
  onQueryChange: (value: string) => void;
  onChange: (field: FilterField, value: string | undefined) => void;
  onReset: () => void;
}

const SelectFilter: React.FC<{ label: string; value?: string; options: AnalyticsFilterOption[]; onChange: (value: string | undefined) => void }> = ({ label, value, options, onChange }) => (
  <label className="analytics-filter-control">
    <span>{label}</span>
    <select value={value ?? ''} onChange={(event) => onChange(event.target.value || undefined)}>
      <option value="">Tất cả</option>
      {options.map((option) => <option key={`${option.id ?? option.code}`} value={option.id ?? option.code}>{option.name}</option>)}
    </select>
  </label>
);

const FeedbackFilters: React.FC<FeedbackFiltersProps> = ({ filters, activeFilterCount, query, onQueryChange, onChange, onReset }) => {
  const [options, setOptions] = useState<AnalyticsFilterOptions | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [advanced, setAdvanced] = useState(activeFilterCount > 0);

  useEffect(() => {
    if (!filters) return;
    void getAnalyticsFilterOptions({ projectId: filters.projectId, dateFrom: filters.dateFrom, dateTo: filters.dateTo })
      .then(setOptions)
      .catch((loadError) => setError(loadError instanceof Error ? loadError.message : 'Không tải được lựa chọn bộ lọc.'));
  }, [filters?.projectId, filters?.dateFrom, filters?.dateTo]);

  if (!filters) return null;
  if (error) return <AnalyticsState title="Không tải được bộ lọc" message={error} />;

  return (
    <section className="analytics-filter-bar feedback-filter-bar" aria-label="Bộ lọc Feedback Explorer">
      <div className="analytics-filter-heading">
        <div><SlidersHorizontal size={16} /><strong>Lọc bằng chứng</strong><span>{activeFilterCount ? `${activeFilterCount} điều kiện đang áp dụng` : 'Lọc để tìm feedback cụ thể'}</span></div>
        <div className="analytics-filter-actions">
          <button className="section-action" onClick={() => setAdvanced((value) => !value)}>{advanced ? 'Thu gọn' : 'Thêm bộ lọc'}</button>
          <button className="section-action" onClick={onReset} disabled={!activeFilterCount && !query}><RotateCcw size={14} /> Xóa bộ lọc</button>
        </div>
      </div>
      <div className="feedback-filter-grid">
        <label className="feedback-search"><Search size={15} /><input value={query} onChange={(event) => onQueryChange(event.target.value)} placeholder="Tìm trong feedback đã mask…" /></label>
        <label className="analytics-filter-control"><span>Từ ngày</span><input type="date" value={filters.dateFrom ?? ''} onChange={(event) => onChange('dateFrom', event.target.value || undefined)} /></label>
        <label className="analytics-filter-control"><span>Đến ngày</span><input type="date" value={filters.dateTo ?? ''} onChange={(event) => onChange('dateTo', event.target.value || undefined)} /></label>
        <SelectFilter label="Dịch vụ" value={filters.serviceCode} options={options?.services ?? []} onChange={(value) => onChange('serviceCode', value)} />
        <SelectFilter label="Vấn đề" value={filters.issueCode} options={options?.issues ?? []} onChange={(value) => onChange('issueCode', value)} />
      </div>
      {advanced && <div className="feedback-filter-grid feedback-filter-advanced">
        <SelectFilter label="Hành trình" value={filters.customerLifecycleStageCode} options={options?.journeyStages ?? []} onChange={(value) => onChange('customerLifecycleStageCode', value)} />
        <SelectFilter label="Bước hành trình" value={filters.customerLifecycleStepCode} options={options?.journeySteps ?? []} onChange={(value) => onChange('customerLifecycleStepCode', value)} />
        <SelectFilter label="Điểm chạm" value={filters.touchpointCode} options={options?.touchpoints ?? []} onChange={(value) => onChange('touchpointCode', value)} />
        <SelectFilter label="Cảm xúc" value={filters.sentiment} options={options?.sentiments ?? []} onChange={(value) => onChange('sentiment', value)} />
        <SelectFilter label="Mức độ" value={filters.operationalSeverity} options={options?.severities ?? []} onChange={(value) => onChange('operationalSeverity', value)} />
        <SelectFilter label="Nguồn dữ liệu" value={filters.sourceSystem} options={options?.sourceSystems ?? []} onChange={(value) => onChange('sourceSystem', value)} />
        <SelectFilter label="Kênh bị ảnh hưởng" value={filters.affectedChannelCode} options={options?.affectedChannels ?? []} onChange={(value) => onChange('affectedChannelCode', value)} />
        <SelectFilter label="Vị trí" value={filters.locationId} options={options?.locations ?? []} onChange={(value) => onChange('locationId', value)} />
      </div>}
    </section>
  );
};

export default FeedbackFilters;
