import React, { useEffect, useState } from 'react';
import { Filter, RotateCcw, Calendar, ChevronDown } from 'lucide-react';
import { AnalyticsFilterOption, AnalyticsFilterOptions, AnalyticsFilters, getAnalyticsFilterOptions } from '../../api/analytics';

type FilterField = Exclude<keyof AnalyticsFilters, 'projectId'>;

interface FeedbackSidebarFiltersProps {
  filters: AnalyticsFilters | null;
  activeFilterCount: number;
  onChange: (field: FilterField, value: string | undefined) => void;
  onReset: () => void;
}

export const FeedbackSidebarFilters: React.FC<FeedbackSidebarFiltersProps> = ({
  filters,
  activeFilterCount,
  onChange,
  onReset,
}) => {
  const [options, setOptions] = useState<AnalyticsFilterOptions | null>(null);
  const [dateMode, setDateMode] = useState<'all' | '30d' | '7d' | 'today' | 'custom'>('all');

  useEffect(() => {
    if (!filters) return;
    void getAnalyticsFilterOptions({ projectId: filters.projectId })
      .then(setOptions)
      .catch(() => {});
  }, [filters?.projectId]);

  const handleDateModeChange = (mode: 'all' | '30d' | '7d' | 'today' | 'custom') => {
    setDateMode(mode);
    const today = new Date();
    const formatDate = (d: Date) => d.toISOString().split('T')[0];

    if (mode === 'all') {
      onChange('dateFrom', undefined);
      onChange('dateTo', undefined);
    } else if (mode === 'today') {
      const todayStr = formatDate(today);
      onChange('dateFrom', todayStr);
      onChange('dateTo', todayStr);
    } else if (mode === '7d') {
      const past = new Date(today);
      past.setDate(past.getDate() - 7);
      onChange('dateFrom', formatDate(past));
      onChange('dateTo', formatDate(today));
    } else if (mode === '30d') {
      const past = new Date(today);
      past.setDate(past.getDate() - 30);
      onChange('dateFrom', formatDate(past));
      onChange('dateTo', formatDate(today));
    }
  };

  if (!filters) return null;

  return (
    <div
      style={{
        background: '#ffffff',
        borderRadius: 8,
        border: '1px solid #e2e8f0',
        padding: 16,
        display: 'flex',
        flexDirection: 'column',
        gap: 16,
        fontSize: 13,
      }}
    >
      {/* Sidebar Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderBottom: '1px solid #f1f5f9', paddingBottom: 10 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontWeight: 700, color: '#0f172a', fontSize: 14 }}>
          <Filter size={16} color="#2563eb" />
          <span>Bộ lọc</span>
          {activeFilterCount > 0 && (
            <span style={{ fontSize: 11, background: '#eff6ff', color: '#2563eb', padding: '1px 6px', borderRadius: 10, fontWeight: 700 }}>
              {activeFilterCount}
            </span>
          )}
        </div>
        {activeFilterCount > 0 && (
          <button
            onClick={onReset}
            style={{
              fontSize: 11,
              color: '#ef4444',
              background: 'none',
              border: 'none',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: 3,
              fontWeight: 600,
            }}
          >
            <RotateCcw size={11} /> Đặt lại
          </button>
        )}
      </div>

      {/* Khu đô thị (Location) */}
      <div>
        <label style={{ fontWeight: 600, color: '#475569', fontSize: 12, marginBottom: 4, display: 'block' }}>
          Khu đô thị
        </label>
        <select
          value={filters.locationId ?? ''}
          onChange={(e) => onChange('locationId', e.target.value || undefined)}
          style={{
            width: '100%',
            padding: '7px 10px',
            borderRadius: 6,
            border: '1px solid #cbd5e1',
            background: '#ffffff',
            fontSize: 12,
            color: '#1e293b',
          }}
        >
          <option value="">Tất cả</option>
          {options?.locations.map((loc) => (
            <option key={loc.id ?? loc.code} value={loc.id ?? loc.code}>
              {loc.name}
            </option>
          ))}
        </select>
      </div>

      {/* Thời gian (Time Range Options) */}
      <div>
        <label style={{ fontWeight: 600, color: '#475569', fontSize: 12, marginBottom: 6, display: 'block' }}>
          Thời gian
        </label>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 6, fontSize: 12, color: '#334155' }}>
          {[
            { key: 'all', label: 'Toàn thời gian' },
            { key: '30d', label: '30 ngày trước' },
            { key: '7d', label: '7 ngày trước' },
            { key: 'today', label: 'Hôm nay' },
            { key: 'custom', label: 'Ngày tùy chỉnh' },
          ].map((item) => (
            <label
              key={item.key}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: 8,
                cursor: 'pointer',
                fontWeight: dateMode === item.key ? 700 : 400,
                color: dateMode === item.key ? '#2563eb' : '#334155',
              }}
            >
              <input
                type="radio"
                name="dateMode"
                checked={dateMode === item.key}
                onChange={() => handleDateModeChange(item.key as any)}
                style={{ accentColor: '#2563eb' }}
              />
              {item.label}
            </label>
          ))}
        </div>

        {dateMode === 'custom' && (
          <div style={{ marginTop: 8, display: 'flex', flexDirection: 'column', gap: 6 }}>
            <input
              type="date"
              value={filters.dateFrom ?? ''}
              onChange={(e) => onChange('dateFrom', e.target.value || undefined)}
              style={{ padding: '5px 8px', borderRadius: 4, border: '1px solid #cbd5e1', fontSize: 11 }}
            />
            <input
              type="date"
              value={filters.dateTo ?? ''}
              onChange={(e) => onChange('dateTo', e.target.value || undefined)}
              style={{ padding: '5px 8px', borderRadius: 4, border: '1px solid #cbd5e1', fontSize: 11 }}
            />
          </div>
        )}
      </div>

      {/* Kênh đánh giá (Intake Channel) */}
      <div>
        <label style={{ fontWeight: 600, color: '#475569', fontSize: 12, marginBottom: 4, display: 'block' }}>
          Kênh đánh giá
        </label>
        <select
          value={filters.intakeChannelCode ?? ''}
          onChange={(e) => onChange('intakeChannelCode', e.target.value || undefined)}
          style={{ width: '100%', padding: '7px 10px', borderRadius: 6, border: '1px solid #cbd5e1', background: '#ffffff', fontSize: 12 }}
        >
          <option value="">Tất cả</option>
          {options?.intakeChannels.map((c) => (
            <option key={c.code} value={c.code}>{c.name}</option>
          ))}
        </select>
      </div>

      {/* Giai đoạn trải nghiệm (Journey Stage) */}
      <div>
        <label style={{ fontWeight: 600, color: '#475569', fontSize: 12, marginBottom: 4, display: 'block' }}>
          Giai đoạn trải nghiệm
        </label>
        <select
          value={filters.customerLifecycleStageCode ?? ''}
          onChange={(e) => onChange('customerLifecycleStageCode', e.target.value || undefined)}
          style={{ width: '100%', padding: '7px 10px', borderRadius: 6, border: '1px solid #cbd5e1', background: '#ffffff', fontSize: 12 }}
        >
          <option value="">Tất cả</option>
          {options?.journeyStages.map((s) => (
            <option key={s.code} value={s.code}>{s.name}</option>
          ))}
        </select>
      </div>

      {/* Loại điểm chạm (Touchpoint) */}
      <div>
        <label style={{ fontWeight: 600, color: '#475569', fontSize: 12, marginBottom: 4, display: 'block' }}>
          Loại điểm chạm
        </label>
        <select
          value={filters.touchpointCode ?? ''}
          onChange={(e) => onChange('touchpointCode', e.target.value || undefined)}
          style={{ width: '100%', padding: '7px 10px', borderRadius: 6, border: '1px solid #cbd5e1', background: '#ffffff', fontSize: 12 }}
        >
          <option value="">Tất cả</option>
          {options?.touchpoints.map((tp) => (
            <option key={tp.code} value={tp.code}>{tp.name}</option>
          ))}
        </select>
      </div>

      {/* Nhóm dịch vụ (Service) */}
      <div>
        <label style={{ fontWeight: 600, color: '#475569', fontSize: 12, marginBottom: 4, display: 'block' }}>
          Nhóm dịch vụ
        </label>
        <select
          value={filters.serviceCode ?? ''}
          onChange={(e) => onChange('serviceCode', e.target.value || undefined)}
          style={{ width: '100%', padding: '7px 10px', borderRadius: 6, border: '1px solid #cbd5e1', background: '#ffffff', fontSize: 12 }}
        >
          <option value="">Tất cả</option>
          {options?.services.map((svc) => (
            <option key={svc.code} value={svc.code}>{svc.name}</option>
          ))}
        </select>
      </div>

      {/* Vấn đề (Issue) */}
      <div>
        <label style={{ fontWeight: 600, color: '#475569', fontSize: 12, marginBottom: 4, display: 'block' }}>
          Vấn đề phát sinh
        </label>
        <select
          value={filters.issueCode ?? ''}
          onChange={(e) => onChange('issueCode', e.target.value || undefined)}
          style={{ width: '100%', padding: '7px 10px', borderRadius: 6, border: '1px solid #cbd5e1', background: '#ffffff', fontSize: 12 }}
        >
          <option value="">Tất cả</option>
          {options?.issues.map((iss) => (
            <option key={iss.code} value={iss.code}>{iss.name}</option>
          ))}
        </select>
      </div>
    </div>
  );
};

export default FeedbackSidebarFilters;
