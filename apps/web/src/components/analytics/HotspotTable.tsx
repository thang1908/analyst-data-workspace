import React from 'react';
import { HotspotRow } from '../../mock/analyticsData';

interface HotspotTableProps {
  data: HotspotRow[];
  onRowClick?: (row: HotspotRow) => void;
}

const SEV_COLOR: Record<string, string> = {
  'SEV-1': 'sev-1',
  'SEV-2': 'sev-2',
  'SEV-3': 'sev-3',
  'SEV-4': 'sev-4',
};

const STATUS_CLASS: Record<string, string> = {
  INVESTIGATING: 'investigating',
  CANDIDATE:     'candidate',
  CONFIRMED:     'confirmed',
  RESOLVED:      'resolved',
};

const STATUS_LABEL: Record<string, string> = {
  INVESTIGATING: 'Đang điều tra',
  CANDIDATE:     'Ứng viên',
  CONFIRMED:     'Xác nhận',
  RESOLVED:      'Đã giải quyết',
};

const HotspotTable: React.FC<HotspotTableProps> = ({ data, onRowClick }) => {
  return (
    <table className="hotspot-table">
      <thead>
        <tr>
          <th>Mức độ</th>
          <th>Vấn đề khách hàng</th>
          <th>Dịch vụ / Sự cố</th>
          <th>Vị trí</th>
          <th style={{ textAlign: 'right' }}>Bằng chứng</th>
          <th style={{ textAlign: 'right' }}>Xu hướng</th>
          <th>Trạng thái</th>
          <th>Phụ trách</th>
        </tr>
      </thead>
      <tbody>
        {data.map((row) => (
          <tr key={row.id} onClick={() => onRowClick?.(row)}>
            <td>
              <span className={`sev-badge ${SEV_COLOR[row.severity]}`}>
                ● {row.severity}
              </span>
            </td>
            <td style={{ color: 'var(--text-primary)', fontWeight: 500, maxWidth: 200 }}>
              {row.customerPain}
            </td>
            <td>
              <span style={{ color: 'var(--text-accent)', fontSize: 11, fontWeight: 600 }}>
                {row.serviceCode}
              </span>
              {' / '}
              <span style={{ fontSize: 11 }}>{row.issueCode}</span>
            </td>
            <td>{row.location}</td>
            <td style={{ textAlign: 'right', fontWeight: 700, color: 'var(--text-primary)' }}>
              {row.evidenceCount}
            </td>
            <td style={{ textAlign: 'right' }}>
              <span className={row.trendPercent > 0 ? 'trend-positive' : 'trend-negative'}>
                {row.trendPercent > 0 ? '↑' : '↓'}{Math.abs(row.trendPercent)}%
              </span>
            </td>
            <td>
              <span className={`status-badge ${STATUS_CLASS[row.status]}`}>
                {STATUS_LABEL[row.status]}
              </span>
            </td>
            <td style={{ fontSize: 12 }}>{row.owner}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
};

export default HotspotTable;
