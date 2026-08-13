import React from 'react';

interface AnalyticsStateProps {
  title?: string;
  message: string;
  onRetry?: () => void;
}

const AnalyticsState: React.FC<AnalyticsStateProps> = ({ title, message, onRetry }) => (
  <div className="analytics-state" role="status">
    {title && <strong>{title}</strong>}
    <span>{message}</span>
    {onRetry && <button className="section-action" onClick={onRetry}>Thử lại</button>}
  </div>
);

export default AnalyticsState;
