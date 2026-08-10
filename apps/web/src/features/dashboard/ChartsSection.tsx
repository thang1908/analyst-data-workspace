import React, { useState } from 'react';
import { Table, BarChart2 } from 'lucide-react';
import { TrendResponse, BreakdownResponse } from '../../client/types';

interface ChartsSectionProps {
  trend: TrendResponse;
  breakdownService: BreakdownResponse;
  breakdownLocation: BreakdownResponse;
  breakdownSeverity: BreakdownResponse;
  onSegmentClick: (dimension: string, key: string) => void;
}

export const ChartsSection: React.FC<ChartsSectionProps> = ({
  trend,
  breakdownService,
  breakdownLocation,
  breakdownSeverity,
  onSegmentClick,
}) => {
  const [showTables, setShowTables] = useState(false);

  const maxTrend = Math.max(...trend.points.map(p => p.total_count), 1);

  return (
    <div style={{ marginBottom: 24 }}>
      {/* Header controls for charts accessibility */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <h2 className="heading-md" style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <BarChart2 size={20} style={{ color: 'var(--accent-cyan)' }} /> Phân Tích & Xu Hướng Dữ Liệu
        </h2>
        <button 
          className="btn-secondary" 
          onClick={() => setShowTables(!showTables)}
          style={{ fontSize: '0.8125rem' }}
        >
          <Table size={14} /> {showTables ? 'Xem Dạng Biểu Đồ' : 'Chuyển Sang Bảng Dữ Liệu (Accessible)'}
        </button>
      </div>

      {showTables ? (
        <div className="glass-panel" style={{ padding: 24, marginBottom: 24 }}>
          <h3 className="heading-md" style={{ marginBottom: 16 }}>Bảng Chi Tiết Xu Hướng Theo Ngày</h3>
          <div className="table-container" style={{ marginBottom: 32 }}>
            <table className="custom-table">
              <thead>
                <tr>
                  <th>Ngày</th>
                  <th>Tổng Volume</th>
                  <th>Số Tiêu Cực</th>
                  <th>Tỷ Lệ Tiêu Cực</th>
                </tr>
              </thead>
              <tbody>
                {trend.points.map((pt, idx) => (
                  <tr key={idx}>
                    <td>{pt.date}</td>
                    <td>{pt.total_count.toLocaleString()}</td>
                    <td>{pt.negative_count.toLocaleString()}</td>
                    <td>{(pt.negative_rate * 100).toFixed(1)}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <h3 className="heading-md" style={{ marginBottom: 16 }}>Bảng Phân Rã Theo Dịch Vụ (Service)</h3>
          <div className="table-container">
            <table className="custom-table">
              <thead>
                <tr>
                  <th>Mã Dịch Vụ</th>
                  <th>Tên Dịch Vụ</th>
                  <th>Tổng Volume</th>
                  <th>Tiêu Cực</th>
                </tr>
              </thead>
              <tbody>
                {breakdownService.segments.map((seg, idx) => (
                  <tr key={idx} style={{ cursor: 'pointer' }} onClick={() => onSegmentClick('service', seg.key)}>
                    <td><code>{seg.key}</code></td>
                    <td>{seg.label}</td>
                    <td>{seg.total_count.toLocaleString()}</td>
                    <td>{seg.negative_count.toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: 20 }}>
          {/* Daily Trend Chart Card */}
          <div className="glass-panel" style={{ padding: 24, gridColumn: '1 / -1' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 20 }}>
              <div>
                <h3 className="heading-md">Xu Hướng Feedback Theo Ngày</h3>
                <p className="subtext">Phân bố tổng volume và phản ánh tiêu cực theo mốc reported date</p>
              </div>
            </div>

            {/* Custom Bar Graph */}
            <div style={{ display: 'flex', alignItems: 'flex-end', gap: 16, height: 200, paddingTop: 20, borderBottom: '1px solid var(--border-color)' }}>
              {trend.points.map((pt, idx) => {
                const heightPct = (pt.total_count / maxTrend) * 100;
                const negHeightPct = (pt.negative_count / pt.total_count) * 100;

                return (
                  <div key={idx} style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', height: '100%', justifyContent: 'flex-end' }}>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: 4 }}>
                      {pt.total_count}
                    </div>
                    <div style={{
                      width: '100%',
                      maxWidth: 40,
                      height: `${heightPct}%`,
                      background: 'linear-gradient(180deg, var(--accent-primary), rgba(99, 102, 241, 0.3))',
                      borderRadius: '6px 6px 0 0',
                      position: 'relative',
                      overflow: 'hidden',
                      transition: 'height 0.3s ease'
                    }}>
                      {/* Negative overlay */}
                      <div style={{
                        position: 'absolute',
                        bottom: 0,
                        width: '100%',
                        height: `${negHeightPct}%`,
                        background: 'rgba(244, 63, 94, 0.7)'
                      }} />
                    </div>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: 8, transform: 'rotate(-25deg)', transformOrigin: 'top left' }}>
                      {pt.date.slice(5)}
                    </div>
                  </div>
                );
              })}
            </div>
            <div style={{ display: 'flex', gap: 24, justifyContent: 'center', marginTop: 24, fontSize: '0.75rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                <span style={{ width: 12, height: 12, borderRadius: 3, background: 'var(--accent-primary)' }} />
                <span>Tổng Volume</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                <span style={{ width: 12, height: 12, borderRadius: 3, background: '#f43f5e' }} />
                <span>Phản Ánh Tiêu Cực</span>
              </div>
            </div>
          </div>

          {/* Service Breakdown */}
          <div className="glass-panel" style={{ padding: 24 }}>
            <h3 className="heading-md" style={{ marginBottom: 4 }}>Phân Rã Theo Dịch Vụ (Service)</h3>
            <p className="subtext" style={{ marginBottom: 20 }}>Top dịch vụ nhận nhiều phản ánh nhất</p>

            <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
              {breakdownService.segments.map((seg, idx) => {
                const maxVol = breakdownService.segments[0]?.total_count || 1;
                const widthPct = (seg.total_count / maxVol) * 100;

                return (
                  <div key={idx} style={{ cursor: 'pointer' }} onClick={() => onSegmentClick('service', seg.key)}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.875rem', marginBottom: 4 }}>
                      <span style={{ fontWeight: 600 }}>{seg.label}</span>
                      <span style={{ color: 'var(--text-secondary)' }}>
                        {seg.total_count.toLocaleString()} (Tiêu cực: {seg.negative_count})
                      </span>
                    </div>
                    <div style={{ width: '100%', height: 10, background: 'rgba(255, 255, 255, 0.05)', borderRadius: 999, overflow: 'hidden' }}>
                      <div style={{ width: `${widthPct}%`, height: '100%', background: 'linear-gradient(90deg, var(--accent-cyan), var(--accent-primary))', borderRadius: 999 }} />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Location Breakdown */}
          <div className="glass-panel" style={{ padding: 24 }}>
            <h3 className="heading-md" style={{ marginBottom: 4 }}>Phân Rã Theo Vị Trí (Location)</h3>
            <p className="subtext" style={{ marginBottom: 20 }}>Phân bố phản ánh theo Tòa nhà / Khu vực</p>

            <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
              {breakdownLocation.segments.map((seg, idx) => {
                const maxVol = breakdownLocation.segments[0]?.total_count || 1;
                const widthPct = (seg.total_count / maxVol) * 100;

                return (
                  <div key={idx} style={{ cursor: 'pointer' }} onClick={() => onSegmentClick('location', seg.key)}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.875rem', marginBottom: 4 }}>
                      <span style={{ fontWeight: 600 }}>{seg.label}</span>
                      <span style={{ color: 'var(--text-secondary)' }}>
                        {seg.total_count.toLocaleString()}
                      </span>
                    </div>
                    <div style={{ width: '100%', height: 10, background: 'rgba(255, 255, 255, 0.05)', borderRadius: 999, overflow: 'hidden' }}>
                      <div style={{ width: `${widthPct}%`, height: '100%', background: 'linear-gradient(90deg, var(--accent-emerald), var(--accent-cyan))', borderRadius: 999 }} />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
