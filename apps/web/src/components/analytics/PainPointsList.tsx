import React from 'react';

export interface PainPoint {
  code: string;
  name: string;
  count: number;
  percentage: number;
  negativeRate: number;
  activeHotspots: number;
}

interface PainPointsListProps {
  data: PainPoint[];
  onItemClick?: (item: PainPoint) => void;
}

const PainPointsList: React.FC<PainPointsListProps> = ({ data, onItemClick }) => {
  return (
    <div>
      {data.map((item, index) => (
        <div
          key={item.code}
          className="pain-point-item"
          onClick={() => onItemClick?.(item)}
        >
          <div className="pain-rank">#{index + 1}</div>

          <div className="pain-info">
            <div className="pain-name">{item.name}</div>
            <div className="pain-service">Tiêu cực: {(item.negativeRate * 100).toFixed(1)}%{item.activeHotspots ? ` · ${item.activeHotspots} hotspot đang mở` : ''}</div>
          </div>

          <div style={{ textAlign: 'right', flexShrink: 0 }}>
            <div className="pain-count">{item.count.toLocaleString()}</div>
            <div className="pain-trend">{(item.percentage * 100).toFixed(1)}% phản hồi</div>
          </div>
        </div>
      ))}
    </div>
  );
};

export default PainPointsList;
