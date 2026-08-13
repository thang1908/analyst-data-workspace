import React from 'react';
import { HotspotRow } from '../../mock/analyticsData';

interface HotspotTableProps {
  data: HotspotRow[];
  onRowClick?: (row: HotspotRow) => void;
}

// Map serviceCode → tên đầy đủ
const SERVICE_NAME: Record<string, string> = {
  'SV-01': 'Hạ tầng kỹ thuật',
  'SV-02': 'App & Hệ thống số',
  'SV-03': 'Giao tiếp & CSKH',
  'SV-04': 'Môi trường sống',
  'SV-05': 'Tiếp cận & Di chuyển',
  'SV-06': 'Thanh toán & Phí',
  'SV-07': 'Kỹ thuật & Tài sản',
  'SV-08': 'An ninh',
};

const SEV_LABEL: Record<string, string> = {
  'SEV-1': 'Nghiêm trọng',
  'SEV-2': 'Cao',
  'SEV-3': 'Trung bình',
  'SEV-4': 'Thấp',
};

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
  CANDIDATE:     'Nghi vấn',
  CONFIRMED:     'Đã xác nhận',
  RESOLVED:      'Đã giải quyết',
};

const HotspotTable: React.FC<HotspotTableProps> = ({ data, onRowClick }) => {
  return (
    <table className="hotspot-table">
      <thead>
        <tr>
          <th>Mức độ</th>
          <th>Vấn đề khách hàng gặp phải</th>
          <th>Dịch vụ liên quan</th>
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
                ● {SEV_LABEL[row.severity]}
              </span>
            </td>
            <td style={{ color: 'var(--text-primary)', fontWeight: 500, maxWidth: 220 }}>
              {row.customerPain}
            </td>
            <td style={{ color: 'var(--text-secondary)', fontSize: 12 }}>
              {SERVICE_NAME[row.serviceCode] ?? row.serviceCode}
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
