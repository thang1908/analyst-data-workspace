import React, { useEffect, useState } from 'react';
import { RotateCcw, SlidersHorizontal, Filter } from 'lucide-react';
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

export const AnalyticsFilterBar: React.FC<AnalyticsFilterBarProps> = ({
  filters,
  activeFilterCount,
  onChange,
  onReset,
}) => {
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
    <div
      style={{
        background: '#ffffff',
        borderRadius: 8,
        border: '1px solid #e2e8f0',
        padding: '14px 18px',
        marginBottom: 20,
        boxShadow: '0 1px 3px rgba(0,0,0,0.03)',
        display: 'flex',
        flexDirection: 'column',
        gap: 12,
      }}
    >
      {/* Filter Bar Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 10 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontWeight: 700, color: '#0f172a', fontSize: 13 }}>
            <Filter size={15} color="#2563eb" />
            <span>Bộ lọc dữ liệu</span>
          </div>
          <span style={{ fontSize: 11, color: '#64748b', background: '#f1f5f9', padding: '2px 8px', borderRadius: 10 }}>
            {activeFilterCount ? `${activeFilterCount} điều kiện đang áp dụng` : 'Mặc định: Toàn thời gian'}
          </span>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          {/* Quick Date Inputs */}
          <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 12, color: '#64748b' }}>
            <span>Từ:</span>
            <input
              type="date"
              value={filters.dateFrom ?? ''}
              onChange={(e) => onChange('dateFrom', e.target.value || undefined)}
              style={{ padding: '5px 8px', borderRadius: 6, border: '1px solid #cbd5e1', fontSize: 12, background: '#ffffff' }}
            />
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 12, color: '#64748b' }}>
            <span>Đến:</span>
            <input
              type="date"
              value={filters.dateTo ?? ''}
              onChange={(e) => onChange('dateTo', e.target.value || undefined)}
              style={{ padding: '5px 8px', borderRadius: 6, border: '1px solid #cbd5e1', fontSize: 12, background: '#ffffff' }}
            />
          </div>

          <button
            onClick={() => setAdvanced((v) => !v)}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: 5,
              padding: '6px 11px',
              borderRadius: 6,
              background: advanced ? '#eff6ff' : '#f8fafc',
              color: advanced ? '#2563eb' : '#475569',
              border: '1px solid #cbd5e1',
              fontSize: 12,
              fontWeight: 600,
              cursor: 'pointer',
            }}
          >
            <SlidersHorizontal size={13} />
            {advanced ? 'Thu gọn' : 'Thêm bộ lọc'}
          </button>

          {activeFilterCount > 0 && (
            <button
              onClick={onReset}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: 4,
                padding: '6px 11px',
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
              Đặt lại
            </button>
          )}
        </div>
      </div>

      {/* Main Filter Dropdowns Row */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: 10, paddingTop: 2 }}>
        <FilterSelect
          label="Khu đô thị"
          value={filters.locationId}
          options={options?.locations ?? []}
          valueKey="id"
          onChange={(v) => onChange('locationId', v)}
        />
        <FilterSelect
          label="Giai đoạn hành trình"
          value={filters.customerLifecycleStageCode}
          options={options?.journeyStages ?? []}
          onChange={(v) => onChange('customerLifecycleStageCode', v)}
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
      </div>

      {/* Advanced Filters Row (Collapsible) */}
      {advanced && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: 10, paddingTop: 8, borderTop: '1px dashed #e2e8f0' }}>
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
            label="Cảm xúc"
            value={filters.sentiment}
            options={options?.sentiments ?? []}
            onChange={(v) => onChange('sentiment', v)}
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

export default AnalyticsFilterBar;
