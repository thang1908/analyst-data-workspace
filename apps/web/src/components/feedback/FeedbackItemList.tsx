import React from 'react';
import { FeedbackWorkspaceItem } from '../../api/feedback';

interface FeedbackItemListProps {
  items: FeedbackWorkspaceItem[];
  selectedId?: string;
  onSelect: (item: FeedbackWorkspaceItem) => void;
}

const sentimentClass = (value: string | null) => value ? `feedback-sentiment ${value.toLowerCase()}` : 'feedback-sentiment';
const formatDate = (value: string) => new Intl.DateTimeFormat('vi-VN', { dateStyle: 'medium', timeStyle: 'short' }).format(new Date(value));

const FeedbackItemList: React.FC<FeedbackItemListProps> = ({ items, selectedId, onSelect }) => (
  <div className="feedback-item-list" role="listbox" aria-label="Danh sách feedback items">
    {items.map((item) => (
      <button key={item.feedbackItemId} role="option" aria-selected={selectedId === item.feedbackItemId} className={`feedback-item-row${selectedId === item.feedbackItemId ? ' selected' : ''}`} onClick={() => onSelect(item)}>
        <div className="feedback-item-row-top"><span>{formatDate(item.reportedAt)}</span><span>{item.sourceSystem}</span></div>
        <p>{item.contentMasked}</p>
        <div className="feedback-item-tags">
          {item.currentClassification.service?.nameVi && <span>{item.currentClassification.service.nameVi}</span>}
          {item.currentClassification.issue?.nameVi && <span>{item.currentClassification.issue.nameVi}</span>}
          <span className={sentimentClass(item.currentClassification.sentiment)}>{item.currentClassification.sentiment ?? 'Chưa phân loại'}</span>
          {item.currentClassification.operationalSeverity && <span className="feedback-severity">{item.currentClassification.operationalSeverity}</span>}
        </div>
      </button>
    ))}
  </div>
);

export default FeedbackItemList;
