import React, { useEffect, useState } from 'react';
import { RotateCcw, SlidersHorizontal } from 'lucide-react';
import {
  AnalyticsFilterOption,
  AnalyticsFilterOptions,
  AnalyticsFilters,
  getAnalyticsFilterOptions,
} from '../../api/analytics';
import AnalyticsState from './AnalyticsState';

type FilterField = Exclude<keyof AnalyticsFilters, 'projectId'>;

interface AnalyticsFilterBarProps {
  filters: AnalyticsFilters | null;
  activeFilterCount: number;
  onChange: (field: FilterField, value: string | undefined) => void;
  onReset: () => void;
}

const FilterSelect: React.FC<{
  label: string;
  value?: string;
  options: AnalyticsFilterOption[];
  onChange: (value: string | undefined) => void;
}> = ({ label, value, options, onChange }) => (
  <label className="analytics-filter-control">
    <span>{label}</span>
    <select value={value ?? ''} onChange={(event) => onChange(event.target.value || undefined)}>
      <option value="">Tất cả</option>
      {options.map((option) => <option key={`${option.id ?? option.code}`} value={option.id ?? option.code}>{option.name}</option>)}
    </select>
  </label>
);

const AnalyticsFilterBar: React.FC<AnalyticsFilterBarProps> = ({ filters, activeFilterCount, onChange, onReset }) => {
  const [options, setOptions] = useState<AnalyticsFilterOptions | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [advanced, setAdvanced] = useState(activeFilterCount > 0);

  useEffect(() => {
    if (!filters) return;
    const baseFilters: AnalyticsFilters = {
      projectId: filters.projectId,
      dateFrom: filters.dateFrom,
      dateTo: filters.dateTo,
    };
    void getAnalyticsFilterOptions(baseFilters)
      .then(setOptions)
      .catch((loadError) => setError(loadError instanceof Error ? loadError.message : 'Không thể tải lựa chọn bộ lọc.'));
  }, [filters?.projectId, filters?.dateFrom, filters?.dateTo]);

  if (!filters) return null;
  if (error) return <AnalyticsState title="Không tải được bộ lọc" message={error} />;

  return (
    <section className="analytics-filter-bar" aria-label="Bộ lọc analytics">
      <div className="analytics-filter-heading">
        <div><SlidersHorizontal size={16} /><strong>Bộ lọc dữ liệu</strong><span>{activeFilterCount ? `${activeFilterCount} đang áp dụng` : 'Mặc định: 30 ngày gần nhất'}</span></div>
        <div className="analytics-filter-actions">
          <button className="section-action" onClick={() => setAdvanced((value) => !value)}>{advanced ? 'Thu gọn' : 'Bộ lọc nâng cao'}</button>
          <button className="section-action" onClick={onReset} disabled={!activeFilterCount}><RotateCcw size={14} /> Xóa bộ lọc</button>
        </div>
      </div>
      <div className="analytics-filter-grid">
        <label className="analytics-filter-control"><span>Từ ngày</span><input type="date" value={filters.dateFrom ?? ''} onChange={(event) => onChange('dateFrom', event.target.value || undefined)} /></label>
        <label className="analytics-filter-control"><span>Đến ngày</span><input type="date" value={filters.dateTo ?? ''} onChange={(event) => onChange('dateTo', event.target.value || undefined)} /></label>
        <FilterSelect label="Hành trình" value={filters.customerLifecycleStageCode} options={options?.journeyStages ?? []} onChange={(value) => onChange('customerLifecycleStageCode', value)} />
        <FilterSelect label="Dịch vụ" value={filters.serviceCode} options={options?.services ?? []} onChange={(value) => onChange('serviceCode', value)} />
        <FilterSelect label="Vấn đề" value={filters.issueCode} options={options?.issues ?? []} onChange={(value) => onChange('issueCode', value)} />
        <FilterSelect label="Vị trí" value={filters.locationId} options={options?.locations ?? []} onChange={(value) => onChange('locationId', value)} />
      </div>
      {advanced && (
        <div className="analytics-filter-grid analytics-filter-advanced">
          <FilterSelect label="Nguồn dữ liệu" value={filters.sourceSystem} options={options?.sourceSystems ?? []} onChange={(value) => onChange('sourceSystem', value)} />
          <FilterSelect label="Kênh tiếp nhận" value={filters.intakeChannelCode} options={options?.intakeChannels ?? []} onChange={(value) => onChange('intakeChannelCode', value)} />
          <FilterSelect label="Kênh bị ảnh hưởng" value={filters.affectedChannelCode} options={options?.affectedChannels ?? []} onChange={(value) => onChange('affectedChannelCode', value)} />
          <FilterSelect label="Phạm vi vị trí" value={filters.locationScope} options={options?.locations ?? []} onChange={(value) => onChange('locationScope', value)} />
          <FilterSelect label="Bước hành trình" value={filters.customerLifecycleStepCode} options={options?.journeySteps ?? []} onChange={(value) => onChange('customerLifecycleStepCode', value)} />
          <FilterSelect label="Bước yêu cầu dịch vụ" value={filters.serviceRequestStepCode} options={options?.serviceRequestSteps ?? []} onChange={(value) => onChange('serviceRequestStepCode', value)} />
          <FilterSelect label="Cảm xúc" value={filters.sentiment} options={options?.sentiments ?? []} onChange={(value) => onChange('sentiment', value)} />
          <FilterSelect label="Mức độ" value={filters.operationalSeverity} options={options?.severities ?? []} onChange={(value) => onChange('operationalSeverity', value)} />
        </div>
      )}
    </section>
  );
};

export default AnalyticsFilterBar;
