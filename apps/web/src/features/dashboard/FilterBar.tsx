import React, { useState, useEffect } from 'react';
import { Filter, RotateCcw, Check, X } from 'lucide-react';
import { AnalyticsFilterParams } from '../../client/types';

interface FilterBarProps {
  initialFilters: AnalyticsFilterParams;
  onApply: (filters: AnalyticsFilterParams) => void;
  onReset: () => void;
}

export const FilterBar: React.FC<FilterBarProps> = ({ initialFilters, onApply, onReset }) => {
  const [fromDate, setFromDate] = useState(initialFilters.from_date || '2026-08-01');
  const [toDate, setToDate] = useState(initialFilters.to_date || '2026-08-10');
  const [serviceId, setServiceId] = useState(initialFilters.service_ids || '');
  const [locationId, setLocationId] = useState(initialFilters.location_ids || '');
  const [sentiment, setSentiment] = useState(initialFilters.sentiments || '');
  const [severity, setSeverity] = useState(initialFilters.severities || '');

  useEffect(() => {
    setFromDate(initialFilters.from_date || '2026-08-01');
    setToDate(initialFilters.to_date || '2026-08-10');
    setServiceId(initialFilters.service_ids || '');
    setLocationId(initialFilters.location_ids || '');
    setSentiment(initialFilters.sentiments || '');
    setSeverity(initialFilters.severities || '');
  }, [initialFilters]);

  const handleApply = (e: React.FormEvent) => {
    e.preventDefault();
    onApply({
      from_date: fromDate,
      to_date: toDate,
      service_ids: serviceId || undefined,
      location_ids: locationId || undefined,
      sentiments: sentiment || undefined,
      severities: severity || undefined,
    });
  };

  const activeChips = [
    fromDate && toDate ? { key: 'date', label: `Từ ${fromDate} đến ${toDate}` } : null,
    serviceId ? { key: 'service', label: `Dịch vụ: ${serviceId}` } : null,
    locationId ? { key: 'location', label: `Vị trí: ${locationId}` } : null,
    sentiment ? { key: 'sentiment', label: `Sentiment: ${sentiment}` } : null,
    severity ? { key: 'severity', label: `Severity: ${severity}` } : null,
  ].filter(Boolean);

  return (
    <div className="glass-panel" style={{ padding: 20, marginBottom: 24 }}>
      <form onSubmit={handleApply} style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: 16, alignItems: 'end' }}>
        <div>
          <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: 6 }}>
            TỪ NGÀY
          </label>
          <input 
            type="date" 
            value={fromDate}
            onChange={e => setFromDate(e.target.value)}
            style={{
              width: '100%',
              padding: '8px 12px',
              borderRadius: 'var(--radius-sm)',
              background: 'rgba(15, 23, 42, 0.6)',
              border: '1px solid var(--border-color)',
              color: 'var(--text-primary)',
              fontFamily: 'inherit'
            }}
          />
        </div>

        <div>
          <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: 6 }}>
            ĐẾN NGÀY
          </label>
          <input 
            type="date" 
            value={toDate}
            onChange={e => setToDate(e.target.value)}
            style={{
              width: '100%',
              padding: '8px 12px',
              borderRadius: 'var(--radius-sm)',
              background: 'rgba(15, 23, 42, 0.6)',
              border: '1px solid var(--border-color)',
              color: 'var(--text-primary)',
              fontFamily: 'inherit'
            }}
          />
        </div>

        <div>
          <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: 6 }}>
            DỊCH VỤ (SERVICE)
          </label>
          <select 
            value={serviceId} 
            onChange={e => setServiceId(e.target.value)}
            style={{
              width: '100%',
              padding: '8px 12px',
              borderRadius: 'var(--radius-sm)',
              background: 'rgba(15, 23, 42, 0.6)',
              border: '1px solid var(--border-color)',
              color: 'var(--text-primary)',
              fontFamily: 'inherit'
            }}
          >
            <option value="">Tất cả dịch vụ</option>
            <option value="SRV_SUPPORT">Hỗ Trợ Khách Hàng</option>
            <option value="SRV_BILLING">Thanh Toán & Hóa Đơn</option>
            <option value="SRV_FACILITY">Bảo Trì Tòa Nhà</option>
            <option value="SRV_SECURITY">An Ninh</option>
          </select>
        </div>

        <div>
          <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: 6 }}>
            SENTIMENT
          </label>
          <select 
            value={sentiment} 
            onChange={e => setSentiment(e.target.value)}
            style={{
              width: '100%',
              padding: '8px 12px',
              borderRadius: 'var(--radius-sm)',
              background: 'rgba(15, 23, 42, 0.6)',
              border: '1px solid var(--border-color)',
              color: 'var(--text-primary)',
              fontFamily: 'inherit'
            }}
          >
            <option value="">Tất cả Sắc Thái</option>
            <option value="NEGATIVE">Tiêu Cực (NEGATIVE)</option>
            <option value="NEUTRAL">Trung Tính (NEUTRAL)</option>
            <option value="POSITIVE">Tích Cực (POSITIVE)</option>
            <option value="UNKNOWN">Chưa Xác Định (UNKNOWN)</option>
          </select>
        </div>

        <div>
          <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: 6 }}>
            MỨC ĐỘ (SEVERITY)
          </label>
          <select 
            value={severity} 
            onChange={e => setSeverity(e.target.value)}
            style={{
              width: '100%',
              padding: '8px 12px',
              borderRadius: 'var(--radius-sm)',
              background: 'rgba(15, 23, 42, 0.6)',
              border: '1px solid var(--border-color)',
              color: 'var(--text-primary)',
              fontFamily: 'inherit'
            }}
          >
            <option value="">Tất cả Severity</option>
            <option value="HIGH,CRITICAL">Mức Cao (HIGH & CRITICAL)</option>
            <option value="MEDIUM">Mức Trung Bình (MEDIUM)</option>
            <option value="LOW">Mức Thấp (LOW)</option>
          </select>
        </div>

        <div style={{ display: 'flex', gap: 8 }}>
          <button type="submit" className="btn-primary" style={{ flex: 1 }}>
            <Check size={16} /> Áp Dụng
          </button>
          <button type="button" className="btn-secondary" onClick={onReset} title="Xóa lọc">
            <RotateCcw size={16} />
          </button>
        </div>
      </form>

      {/* Active Filter Chips */}
      {activeChips.length > 0 && (
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, marginTop: 16, paddingTop: 16, borderTop: '1px solid var(--border-color)' }}>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: 4 }}>
            <Filter size={12} /> Đang lọc:
          </span>
          {activeChips.map((chip, idx) => (
            <span key={idx} className="badge badge-neu" style={{ textTransform: 'none', fontWeight: 500 }}>
              {chip?.label}
            </span>
          ))}
        </div>
      )}
    </div>
  );
};
