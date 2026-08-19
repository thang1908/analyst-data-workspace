import React, { useEffect, useState } from 'react';
import { Search, RotateCcw, SlidersHorizontal, ChevronDown } from 'lucide-react';
import { AnalyticsFilterOption, AnalyticsFilterOptions, AnalyticsFilters, getAnalyticsFilterOptions } from '../../api/analytics';

type FilterField = Exclude<keyof AnalyticsFilters, 'projectId'>;

interface FeedbackFilterToolbarProps {
  filters: AnalyticsFilters | null;
  activeFilterCount: number;
  query: string;
  onQueryChange: (query: string) => void;
  onChange: (field: FilterField, value: string | undefined) => void;
  onReset: () => void;
}

const FilterSelect: React.FC<{
  label: string;
  value?: string;
  options: AnalyticsFilterOption[];
  valueKey?: 'code' | 'id';
  onChange: (value: string | undefined) => void;
}> = ({ label, value, options, valueKey = 'code', onChange }) => (
  <div style={{ display: 'flex', flexDirection: 'column', gap: 4, minWidth: 140, flex: 1 }}>
    <span style={{ fontSize: 11, fontWeight: 600, color: '#64748b' }}>{label}</span>
    <select
      value={value ?? ''}
      onChange={(e) => onChange(e.target.value || undefined)}
      style={{
        width: '100%',
        padding: '7px 10px',
        borderRadius: 6,
        border: '1px solid #cbd5e1',
        background: '#ffffff',
        fontSize: 12,
        color: '#1e293b',
        fontWeight: value ? 600 : 400,
        cursor: 'pointer',
      }}
    >
      <option value="">Tất cả</option>
      {options.map((option) => {
        const optionVal = valueKey === 'id' ? (option.id ?? option.code) : option.code;
        return (
          <option key={`${option.id ?? option.code}`} value={optionVal}>
            {option.name}
          </option>
        );
      })}
    </select>
  </div>
);

const ELIGIBILITY_OPTIONS: AnalyticsFilterOption[] = [
  { code: 'INCLUDED', name: 'Hợp lệ đưa vào phân tích' },
  { code: 'EXCLUDED', name: 'Loại trừ (Spam / Test / Non-feedback)' },
];

export const FeedbackFilterToolbar: React.FC<FeedbackFilterToolbarProps> = ({
  filters,
  activeFilterCount,
  query,
  onQueryChange,
  onChange,
  onReset,
}) => {
  const [options, setOptions] = useState<AnalyticsFilterOptions | null>(null);
  const [showAdvanced, setShowAdvanced] = useState(false);

  useEffect(() => {
    if (!filters) return;
    void getAnalyticsFilterOptions({ projectId: filters.projectId })
      .then(setOptions)
      .catch(() => {});
  }, [filters?.projectId]);

  if (!filters) return null;

  return (
    <div
      style={{
        background: '#ffffff',
        borderRadius: 8,
        border: '1px solid #e2e8f0',
        padding: '14px 16px',
        display: 'flex',
        flexDirection: 'column',
        gap: 12,
        boxShadow: '0 1px 3px rgba(0,0,0,0.03)',
      }}
    >
      {/* Top Search & Action Bar */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 12, flexWrap: 'wrap' }}>
        {/* Search Box */}
        <div style={{ position: 'relative', flex: '1 1 320px', minWidth: 260 }}>
          <Search size={15} color="#94a3b8" style={{ position: 'absolute', left: 11, top: '50%', transform: 'translateY(-50%)' }} />
          <input
            type="text"
            placeholder="Tìm kiếm nội dung phản hồi đã mask..."
            value={query}
            onChange={(e) => onQueryChange(e.target.value)}
            style={{
              width: '100%',
              padding: '8px 12px 8px 34px',
              borderRadius: 6,
              border: '1px solid #cbd5e1',
              fontSize: 13,
              background: '#f8fafc',
            }}
          />
        </div>

        {/* Date Inputs */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 12, color: '#64748b' }}>
            <span>Từ:</span>
            <input
              type="date"
              value={filters.dateFrom ?? ''}
              onChange={(e) => onChange('dateFrom', e.target.value || undefined)}
              style={{ padding: '6px 8px', borderRadius: 6, border: '1px solid #cbd5e1', fontSize: 12, background: '#ffffff' }}
            />
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 12, color: '#64748b' }}>
            <span>Đến:</span>
            <input
              type="date"
              value={filters.dateTo ?? ''}
              onChange={(e) => onChange('dateTo', e.target.value || undefined)}
              style={{ padding: '6px 8px', borderRadius: 6, border: '1px solid #cbd5e1', fontSize: 12, background: '#ffffff' }}
            />
          </div>

          <button
            onClick={() => setShowAdvanced((v) => !v)}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: 5,
              padding: '7px 11px',
              borderRadius: 6,
              background: showAdvanced ? '#eff6ff' : '#f8fafc',
              color: showAdvanced ? '#2563eb' : '#475569',
              border: '1px solid #cbd5e1',
              fontSize: 12,
              fontWeight: 600,
              cursor: 'pointer',
            }}
          >
            <SlidersHorizontal size={13} />
            {showAdvanced ? 'Thu gọn' : 'Thêm bộ lọc'}
          </button>

          {activeFilterCount > 0 && (
            <button
              onClick={onReset}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: 4,
                padding: '7px 11px',
                borderRadius: 6,
                background: '#fef2f2',
                color: '#dc2626',
                border: '1px solid #fecaca',
                fontSize: 12,
                fontWeight: 600,
                cursor: 'pointer',
              }}
            >
              <RotateCcw size={13} />
              Đặt lại ({activeFilterCount})
            </button>
          )}
        </div>
      </div>

      {/* Main Filter Dropdowns Row */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))', gap: 10, paddingTop: 4 }}>
        <FilterSelect
          label="Khu đô thị"
          value={filters.locationId}
          options={options?.locations ?? []}
          valueKey="id"
          onChange={(v) => onChange('locationId', v)}
        />
        <FilterSelect
          label="Dịch vụ"
          value={filters.serviceCode}
          options={options?.services ?? []}
          onChange={(v) => onChange('serviceCode', v)}
        />
        <FilterSelect
          label="Vấn đề"
          value={filters.issueCode}
          options={options?.issues ?? []}
          onChange={(v) => onChange('issueCode', v)}
        />
        <FilterSelect
          label="Tính hợp lệ"
          value={filters.analyticEligibility}
          options={ELIGIBILITY_OPTIONS}
          onChange={(v) => onChange('analyticEligibility', v)}
        />
      </div>

      {/* Advanced Filter Row (Collapsible) */}
      {showAdvanced && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))', gap: 10, paddingTop: 8, borderTop: '1px dashed #e2e8f0' }}>
          <FilterSelect
            label="Giai đoạn hành trình"
            value={filters.customerLifecycleStageCode}
            options={options?.journeyStages ?? []}
            onChange={(v) => onChange('customerLifecycleStageCode', v)}
          />
          <FilterSelect
            label="Bước hành trình"
            value={filters.customerLifecycleStepCode}
            options={options?.journeySteps ?? []}
            onChange={(v) => onChange('customerLifecycleStepCode', v)}
          />
          <FilterSelect
            label="Điểm chạm (Touchpoint)"
            value={filters.touchpointCode}
            options={options?.touchpoints ?? []}
            onChange={(v) => onChange('touchpointCode', v)}
          />
          <FilterSelect
            label="Kênh tiếp nhận"
            value={filters.intakeChannelCode}
            options={options?.intakeChannels ?? []}
            onChange={(v) => onChange('intakeChannelCode', v)}
          />
          <FilterSelect
            label="Mức độ nghiêm trọng"
            value={filters.operationalSeverity}
            options={options?.severities ?? []}
            onChange={(v) => onChange('operationalSeverity', v)}
          />
        </div>
      )}
    </div>
  );
};

export default FeedbackFilterToolbar;
