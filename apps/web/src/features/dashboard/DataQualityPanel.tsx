import React from 'react';
import { ShieldCheck, Info } from 'lucide-react';

export const DataQualityPanel: React.FC = () => {
  return (
    <div className="glass-panel" style={{ padding: 24, marginBottom: 24 }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 16 }}>
        <h3 className="heading-md" style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <ShieldCheck size={20} style={{ color: 'var(--accent-emerald)' }} /> Bảng Kiểm Tra Độ Tin Cậy Dữ Liệu (Data Quality)
        </h3>
        <span className="badge badge-pos">STATUS: COMMITTED & RECONCILED</span>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 16, marginBottom: 16 }}>
        <div style={{ background: 'rgba(255, 255, 255, 0.02)', padding: 16, borderRadius: 12, border: '1px solid var(--border-color)' }}>
          <div className="subtext" style={{ fontSize: '0.75rem' }}>DỮ LIỆU ĐÃ COMMIT</div>
          <div style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--accent-emerald)', marginTop: 4 }}>9,700 dòng</div>
        </div>
        <div style={{ background: 'rgba(255, 255, 255, 0.02)', padding: 16, borderRadius: 12, border: '1px solid var(--border-color)' }}>
          <div className="subtext" style={{ fontSize: '0.75rem' }}>DÒNG BỊ LOẠI (INVALID)</div>
          <div style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--sentiment-neg-text)', marginTop: 4 }}>150 dòng</div>
        </div>
        <div style={{ background: 'rgba(255, 255, 255, 0.02)', padding: 16, borderRadius: 12, border: '1px solid var(--border-color)' }}>
          <div className="subtext" style={{ fontSize: '0.75rem' }}>TỶ LỆ PASS VALIDATION</div>
          <div style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--text-primary)', marginTop: 4 }}>98.47%</div>
        </div>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: '0.8125rem', color: 'var(--text-muted)', background: 'rgba(15, 23, 42, 0.4)', padding: 12, borderRadius: 8 }}>
        <Info size={16} style={{ color: 'var(--accent-cyan)' }} />
        <span>Ghi chú: Thống kê Data Quality được tính theo <code>import_job.completed_at</code>. Các bộ lọc theo Service/Issue không áp dụng lên tổng dòng bị loại từ CSV.</span>
      </div>
    </div>
  );
};
