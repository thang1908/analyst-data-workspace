# ADR-002 — Raw Feedback → Feedback Item → Prediction/Decision/Current

- **Status:** Accepted
- **Date:** 2026-08-10
- **Scope:** MVP baseline
- **Related:** [PRD](../../PRD.md), [Service Taxonomy](../../service_taxonomy.md), [Build Rules](../../BUILD_RULES.md), [ADR-001](./ADR-001-journey-dimensions.md)

## Context

PRD cần đồng thời:

- giữ raw content để audit;
- hỗ trợ một feedback có nhiều service/vấn đề;
- lưu AI suggestion + confidence + model version;
- cho human accept/correct/unknown;
- giữ correction history;
- query/filter/analytics nhanh;
- không coi AI prediction hoặc Candidate Cause là sự thật.

Nếu đặt toàn bộ field classification trực tiếp trên một `feedback` row, update sẽ làm mất history, prediction dễ bị nhầm với accepted label và feedback nhiều vấn đề bị ép vào một issue.

## Decision

Chọn pipeline và source-of-truth sau:

```text
feedback (immutable source evidence)
       │ 1
       └── N feedback_item (atomic classification unit)
                 ├── N classification_prediction (AI/rule output, append-only)
                 ├── N classification_decision (accepted human/policy decision, append-only)
                 └── 1 classification_current (rebuildable read projection)
```

### `feedback`

Lưu source lineage, original payload/content reference, reported/ingested time và raw context. Sau ingest không update nội dung gốc. Masking/redaction có representation/version riêng.

### `feedback_item`

Là đơn vị được phân loại và đưa vào issue-level analytics/hotspot. Một raw feedback có thể sinh một hoặc nhiều item. Item giữ link/offset hoặc evidence reference về raw feedback để không mất ngữ cảnh.


### `classification_prediction`

Là output append-only của AI/rule, không phải source of truth cho accepted analytics. Tối thiểu lưu:

```text
prediction_id
feedback_item_id
prediction_run_id
field_name
candidate_value_id
rank
confidence
model/provider/version
pipeline/prompt version
taxonomy_release_id
created_at
```

Prediction là immutable. Trạng thái review không update trên prediction row; `review_event` tham chiếu prediction và, khi action tạo accepted state mới, decision tương ứng.

### `classification_decision`

Là snapshot phân loại đã được chấp nhận tại một version. Tối thiểu lưu:

```text
decision_id
feedback_item_id
decision_version
customer_lifecycle_value_status
customer_lifecycle_step_id
service_request_value_status
service_request_step_id
primary_service_value_status
primary_service_id
issue_value_status
issue_id
sentiment
operational_severity
location_value_status
location_id
cause_determination_status
decision_source
taxonomy_release_id
decided_by
decided_at
reason
supersedes_decision_id
```

Secondary Service và Candidate Cause là các child relation versioned của decision snapshot, không phải chuỗi/JSON không kiểm soát. Correction không update decision cũ; tạo decision version mới chứa một trạng thái hợp lệ, nguyên tử cho toàn item.

`customer_lifecycle_stage_id` được derive/validate từ `customer_lifecycle_step_id` và có thể xuất hiện trong read projection; không lưu hai nguồn sự thật độc lập trong decision snapshot.

### `classification_current`

Là read projection trỏ/flatten accepted decision mới nhất để workspace/filter/analytics đọc nhanh. Nó không phải audit source of truth và phải rebuild được từ decision history.

## Decision sources

Stable values baseline:

```text
MANUAL
SOURCE_TRUSTED
HUMAN_ACCEPTED_AI
HUMAN_CORRECTED_AI
POLICY_AUTO_APPLIED
SYSTEM_MIGRATION
```

`SOURCE_TRUSTED` chỉ dùng khi source-trust policy đã được version, phê duyệt và audit. `POLICY_AUTO_APPLIED` chỉ dùng cho label low-risk khi policy đã được duyệt; không phải AI tự ghi decision tùy ý.

## Domain rules

1. Raw content/payload là bất biến; correction chỉ thay decision/projection.
2. Mỗi item có thể có nhiều prediction và decision, nhưng chỉ một current accepted decision.
3. Decision version tăng đơn điệu; concurrent stale write bị reject.
4. Field reference chưa có giá trị dùng companion `*_value_status = KNOWN | UNKNOWN | MISSING | NOT_APPLICABLE`; `KNOWN` yêu cầu ID hợp lệ, các status khác yêu cầu ID null.
5. Khi primary Service ở trạng thái `KNOWN`, decision có đúng một primary Service; secondary Service dùng relation có `role` rõ.
6. Khi Issue ở trạng thái `KNOWN`, Issue phải thuộc primary Service đã biết tại taxonomy release tương ứng.
7. Lifecycle fields tuân theo ADR-001 và mapping active.
8. Prediction không được dùng như accepted label nếu chưa qua human/policy decision.
9. `UNKNOWN`, `MISSING`, `NOT_APPLICABLE` có semantics khác nhau.
10. Candidate cause có thể zero-to-many và chỉ là hypothesis; `UNKNOWN` là `cause_determination_status`, không phải một cause record. Confirmed Root Cause thuộc Investigation/RCA context riêng.
11. Audit event tham chiếu decision/prediction ID, actor, reason và correlation; không copy raw PII vào audit.
12. Analytics theo issue mặc định đếm `feedback_item`, không mặc định đếm raw feedback; metric catalog phải công bố unit.
13. Duplicate source record giữ lineage/status; không xóa evidence.

## Write flow

### Manual

```text
Create feedback/item
→ Operator submits labels + expected current version + reason
→ server validates scope/taxonomy/invariants
→ append classification_decision
→ update projection in same transaction hoặc reliable outbox
→ write audit event
```

### AI-assisted

```text
Create feedback_item
→ append prediction
→ human/policy review
→ append decision
→ update current projection
```

AI timeout/invalid output không chặn manual workflow.

## Read flow

- Workspace/filter/detail summary đọc `classification_current` và masked content projection.
- Audit/history đọc decision/prediction append-only theo quyền.
- Analytics/hotspot đọc accepted current hoặc versioned analytical projection theo metric definition.
- Raw content chỉ được fetch qua permission riêng; không join mặc định vào analytics query.

## Consistency and failure handling

- Decision write và outbox event phải atomic.
- Projection consumer idempotent và chấp nhận duplicate event.
- Projection lag được đo; UI có thể hiển thị processing state nếu chưa cập nhật.
- Rebuild projection phải tạo cùng result; có reconciliation job so decision latest với current row.
- Không sửa history để “khớp dashboard”; correction dùng decision/event mới.

## Alternatives considered

### Classification fields trực tiếp trên feedback row

Rejected vì mất history, trộn raw/canonical/accepted state và khó xử lý multi-issue.

### Một bảng dùng chung cho prediction và decision

Rejected vì semantics/authority khác nhau, dễ để AI output lọt vào analytics như fact.

### Chỉ phân loại toàn raw feedback

Rejected vì một message có thể có nhiều issue/service và làm sai hotspot/count.

### Current row là source of truth duy nhất

Rejected vì overwrite không đáp ứng audit/correction lineage và không rebuild được.

## Consequences

### Positive

- Raw evidence, AI output và accepted human decision được phân biệt rõ.
- Hỗ trợ correction/audit, multi-issue và model/taxonomy versioning.
- Query nhanh qua projection nhưng vẫn có history chuẩn.
- Manual-first và AI-assisted dùng cùng downstream model.

### Cost

- Nhiều entity/job/projection hơn một bảng CRUD đơn giản.
- Cần optimistic concurrency, outbox và reconciliation.
- Metric phải nói rõ đếm raw feedback hay feedback item.

## Migration/implementation notes

- Không duy trì hai writable source cùng lúc. Nếu schema cũ có classification trên `feedback`, coi chúng là migration input hoặc projection tạm thời.
- Tạo stable IDs, decision version constraint và unique current row per item.
- Backfill history bằng `SYSTEM_MIGRATION`, giữ original timestamps/source khi biết và ghi migration lineage.
- Chạy reconciliation trước khi chuyển query/analytics sang current projection.
- Không drop field cũ trong cùng release; áp dụng expand → backfill/verify → switch read → contract.
