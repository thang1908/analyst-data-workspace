import React from 'react';
import { PainPoint } from '../../mock/analyticsData';

interface PainPointsListProps {
  data: PainPoint[];
  onItemClick?: (item: PainPoint) => void;
}

const PainPointsList: React.FC<PainPointsListProps> = ({ data, onItemClick }) => {
  return (
    <div>
      {data.map((item) => (
        <div
          key={item.issueCode}
          className="pain-point-item"
          onClick={() => onItemClick?.(item)}
        >
          <div className="pain-rank">#{item.rank}</div>

          {item.hasHotspot && <div className="hotspot-dot" title="Đang có Hotspot" />}

          <div className="pain-info">
            <div className="pain-name">{item.issueName}</div>
            <div className="pain-service">{item.serviceName}</div>
          </div>

          <div style={{ textAlign: 'right', flexShrink: 0 }}>
            <div className="pain-count">{item.count.toLocaleString()}</div>
            <div className={`pain-trend ${item.trend > 0 ? 'up' : 'down'}`}>
              {item.trend > 0 ? '↑' : '↓'} {Math.abs(item.trend)}%
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};

export default PainPointsList;
