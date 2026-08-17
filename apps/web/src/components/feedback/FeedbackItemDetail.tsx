import React from 'react';
import { FileSearch, GitBranch, MapPin, ShieldCheck } from 'lucide-react';
import { FeedbackWorkspaceItem } from '../../api/feedback';

const formatDate = (value: string) => new Intl.DateTimeFormat('vi-VN', { dateStyle: 'full', timeStyle: 'short' }).format(new Date(value));
const valueOrFallback = (value: string | null | undefined) => value || 'Chưa xác định';

const DetailRow: React.FC<{ label: string; value: React.ReactNode }> = ({ label, value }) => <div className="feedback-detail-row"><dt>{label}</dt><dd>{value}</dd></div>;

const FeedbackItemDetail: React.FC<{ item: FeedbackWorkspaceItem | null }> = ({ item }) => {
  if (!item) return <div className="feedback-detail-empty"><FileSearch size={30} /><strong>Chọn một feedback</strong><span>Chi tiết bằng chứng và phân loại hiện tại sẽ xuất hiện ở đây.</span></div>;
  const classification = item.currentClassification;
  return <div className="feedback-detail-content">
    <section className="feedback-evidence">
      <div className="feedback-detail-section-title"><FileSearch size={16} /><span>Bằng chứng đã mask</span></div>
      <blockquote>{item.contentMasked}</blockquote>
      <div className="feedback-detail-metadata"><span>{formatDate(item.reportedAt)}</span><span>{item.sourceSystem}</span></div>
    </section>
    <section>
      <div className="feedback-detail-section-title"><ShieldCheck size={16} /><span>Phân loại hiện tại</span></div>
      <dl className="feedback-detail-list">
        <DetailRow label="Dịch vụ" value={valueOrFallback(classification.service?.nameVi)} />
        <DetailRow label="Vấn đề" value={valueOrFallback(classification.issue?.nameVi)} />
        <DetailRow label="Cảm xúc" value={valueOrFallback(classification.sentiment)} />
        <DetailRow label="Mức độ" value={valueOrFallback(classification.operationalSeverity)} />
        <DetailRow label="Trạng thái" value={valueOrFallback(classification.classificationState)} />
      </dl>
    </section>
    <section>
      <div className="feedback-detail-section-title"><MapPin size={16} /><span>Ngữ cảnh</span></div>
      <dl className="feedback-detail-list">
        <DetailRow label="Vị trí" value={valueOrFallback(item.location.name ?? item.location.code)} />
        <DetailRow label="Kênh bị ảnh hưởng" value={item.affectedChannelCodes.length ? item.affectedChannelCodes.join(', ') : 'Chưa ghi nhận'} />
        <DetailRow label="Điều kiện phân tích" value={item.analyticEligibility} />
      </dl>
    </section>
    <section>
      <div className="feedback-detail-section-title"><GitBranch size={16} /><span>Dòng tách ý định</span></div>
      <p className="feedback-lineage">{item.parentItemId ? `Item con của feedback item ${item.parentItemId.slice(0, 8)}…` : 'Đây là feedback item gốc; chưa có dòng tách ý định cha.'}</p>
    </section>
  </div>;
};

export default FeedbackItemDetail;
