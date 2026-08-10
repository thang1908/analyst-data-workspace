import React from 'react';
import { MessageSquare, AlertOctagon, TrendingDown, HelpCircle, ShieldAlert } from 'lucide-react';
import { AnalyticsMetrics } from '../../client/types';

interface KpiCardsProps {
  metrics: AnalyticsMetrics;
  onDrillDown: (filters: { sentiment?: string; severity?: string }) => void;
}

export const KpiCards: React.FC<KpiCardsProps> = ({ metrics, onDrillDown }) => {
  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: 16, marginBottom: 24 }}>
      {/* Total Volume Card */}
      <div className="glass-panel" style={{ padding: 20 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <div>
            <div className="subtext" style={{ fontSize: '0.75rem', fontWeight: 600 }}>TỔNG FEEDBACK</div>
            <div style={{ fontSize: '1.875rem', fontWeight: 800, marginTop: 4, color: 'var(--text-primary)' }}>
              {metrics.total_feedback_volume.toLocaleString('vi-VN')}
            </div>
          </div>
          <div style={{ background: 'rgba(99, 102, 241, 0.15)', padding: 10, borderRadius: 12, color: 'var(--accent-indigo)' }}>
            <MessageSquare size={20} />
          </div>
        </div>
        <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: 12 }}>
          Dữ liệu đã qua validate & dedupe
        </div>
      </div>

      {/* Negative Count Card */}
      <div 
        className="glass-panel" 
        style={{ padding: 20, cursor: 'pointer' }}
        onClick={() => onDrillDown({ sentiment: 'NEGATIVE' })}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <div>
            <div className="subtext" style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--sentiment-neg-text)' }}>FEEDBACK TIÊU CỰC</div>
            <div style={{ fontSize: '1.875rem', fontWeight: 800, marginTop: 4, color: 'var(--sentiment-neg-text)' }}>
              {metrics.negative_feedback_volume.toLocaleString('vi-VN')}
            </div>
          </div>
          <div style={{ background: 'rgba(244, 63, 94, 0.15)', padding: 10, borderRadius: 12, color: '#fb7185' }}>
            <AlertOctagon size={20} />
          </div>
        </div>
        <div style={{ fontSize: '0.75rem', color: '#fb7185', marginTop: 12, fontWeight: 500, display: 'flex', alignItems: 'center', gap: 4 }}>
          Click để drill-down danh sách →
        </div>
      </div>

      {/* Negative Rate Card */}
      <div className="glass-panel" style={{ padding: 20 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <div>
            <div className="subtext" style={{ fontSize: '0.75rem', fontWeight: 600 }}>TỶ LỆ TIÊU CỰC</div>
            <div style={{ fontSize: '1.875rem', fontWeight: 800, marginTop: 4, color: '#fb7185' }}>
              {(metrics.negative_rate * 100).toFixed(1)}%
            </div>
          </div>
          <div style={{ background: 'rgba(244, 63, 94, 0.15)', padding: 10, borderRadius: 12, color: '#fb7185' }}>
            <TrendingDown size={20} />
          </div>
        </div>
        <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: 12 }}>
          Không bao gồm Sentiment Unknown
        </div>
      </div>

      {/* Unknown Rate Card */}
      <div 
        className="glass-panel" 
        style={{ padding: 20, cursor: 'pointer' }}
        onClick={() => onDrillDown({ sentiment: 'UNKNOWN' })}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <div>
            <div className="subtext" style={{ fontSize: '0.75rem', fontWeight: 600 }}>CHƯA XÁC ĐỊNH</div>
            <div style={{ fontSize: '1.875rem', fontWeight: 800, marginTop: 4, color: 'var(--text-secondary)' }}>
              {(metrics.sentiment_unknown_rate * 100).toFixed(1)}%
            </div>
          </div>
          <div style={{ background: 'rgba(148, 163, 184, 0.15)', padding: 10, borderRadius: 12, color: '#94a3b8' }}>
            <HelpCircle size={20} />
          </div>
        </div>
        <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: 12, fontWeight: 500 }}>
          Click drill-down UNKNOWN →
        </div>
      </div>

      {/* High Severity Card */}
      <div 
        className="glass-panel" 
        style={{ padding: 20, cursor: 'pointer' }}
        onClick={() => onDrillDown({ severity: 'HIGH,CRITICAL' })}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <div>
            <div className="subtext" style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--sev-high-text)' }}>SEVERITY CAO / CRITICAL</div>
            <div style={{ fontSize: '1.875rem', fontWeight: 800, marginTop: 4, color: 'var(--sev-high-text)' }}>
              {metrics.high_severity_count.toLocaleString('vi-VN')}
            </div>
          </div>
          <div style={{ background: 'rgba(225, 29, 72, 0.2)', padding: 10, borderRadius: 12, color: '#fda4af' }}>
            <ShieldAlert size={20} />
          </div>
        </div>
        <div style={{ fontSize: '0.75rem', color: '#fda4af', marginTop: 12, fontWeight: 500 }}>
          Click drill-down SEV-1/SEV-2 →
        </div>
      </div>
    </div>
  );
};
