# FEAT-001 — Elevator Manual Intake-to-Insight

- **Status:** Ready for refinement
- **Priority:** P0
- **Outcome owner:** CX Product Owner / CX Operations
- **Primary personas:** CX Analyst, Operator/CSKH
- **Bounded contexts:** Feedback Intake, Taxonomy & Location, Classification & Review, Feedback Exploration, Analytics
- **Related:** [PRD](../PRD.md), [Service Taxonomy](../service_taxonomy.md), [Build Rules](../BUILD_RULES.md), [ADR-001](../architecture/adr/ADR-001-journey-dimensions.md), [ADR-002](../architecture/adr/ADR-002-classification-model.md)

## 1. Outcome

CX Analyst có thể nhập một feedback elevator từ CSV, Operator có thể phân loại thủ công thành `RES-06 / SVC-17 / ELV-01 / S2`, và người dùng có quyền có thể tìm, lọc, xem chi tiết, xem số liệu cơ bản rồi drill-down về đúng feedback nguồn.

Feature này là vertical slice đầu tiên để kiểm chứng hợp đồng dữ liệu, phân quyền, audit và observability trước khi thêm AI hoặc hotspot.

## 2. Scenario chuẩn

Input:

```text
"Thang máy S2 sáng nào cũng phải chờ rất lâu."
```

Accepted classification sau manual review:

```text
Customer Lifecycle Status = KNOWN
Customer Lifecycle Stage  = Cư trú
Customer Lifecycle Step   = RES-06 — Di chuyển trong tòa
Service Request Status    = NOT_APPLICABLE
Service Request Step      = null
Primary Service Status    = KNOWN
Primary Service           = SVC-17 — Elevator / Vertical Transportation
Issue Status              = KNOWN
Issue                     = ELV-01 — Thời gian chờ thang máy lâu
Location Status           = KNOWN
Location                  = S2
Sentiment                 = NEGATIVE
Operational Severity      = SEV-2 (mapped from legacy P2 baseline)
Cause Status              = UNKNOWN
Candidate Causes          = []
Classification Source     = MANUAL
Review Status             = ACCEPTED
```

Không suy luận nguyên nhân kỹ thuật từ nội dung này.

## 3. Scope

### In scope

- Upload một file CSV UTF-8 theo template đã duyệt.
- Preview, validate từng dòng, hiển thị row error và chỉ commit khi user xác nhận.
- Import chạy qua job có status, count, idempotency và audit.
- Lưu source/raw feedback bất biến và tạo một feedback item cho scenario chuẩn.
- Lookup taxonomy/location từ dữ liệu có version; không hard-code label trong UI.
- Operator gán/sửa classification thủ công với reason và optimistic concurrency.
- Workspace list/filter theo date, project/building, customer journey, service, issue, location, sentiment và review status.
- Feedback detail hiển thị masked content, source context, accepted classification và audit history theo quyền.
- Insight cơ bản: item count/trend cho `SVC-17 + ELV-01 + S2`, có drill-down về cùng filtered list.
- Data-quality visibility cho invalid row, duplicate source key và unknown location.
- Authorization, audit, structured log, metric, trace, feature flag và rollback.

### Non-goal

- XLSX, realtime API, hotline/social integration hoặc attachment.
- AI prediction, confidence threshold hoặc AI review queue.
- Tự động tách một raw feedback thành nhiều feedback item.
- Secondary service hoặc nhiều issue cho cùng item.
- Hotspot detection, hard trigger, notification hoặc assignment.
- Ticket, SLA, asset, investigation, RCA hoặc root-cause confirmation.
- Taxonomy admin UI; slice này chỉ đọc taxonomy/location seed đã duyệt.
- Advanced dashboard, saved view hoặc export lớn.

## 4. Actors và permissions

| Actor | Scope | Được phép | Không được phép |
| --- | --- | --- | --- |
| CX Analyst | project/building được gán | upload, preview, commit import; xem masked workspace/detail/insight | xem ngoài scope; sửa taxonomy; xem raw PII nếu không có quyền riêng |
| Operator/CSKH | project/building/service được gán | mọi quyền đọc cần thiết; tạo/correct manual classification với reason | xác nhận root cause; sửa ngoài scope |
| Taxonomy Admin | taxonomy scope | đọc/kiểm chứng seed và mapping cho slice | taxonomy write không thuộc FEAT-001 |
| Platform Admin/Auditor | privileged scope được phê duyệt | xem operational/audit metadata | raw content chỉ khi có quyền PII riêng |

Quyền được enforce phía server ở mọi query/command. Record ngoài scope có hành vi `not found within scope` hoặc `forbidden` theo security policy, không làm rò rỉ sự tồn tại của dữ liệu.

## 5. Preconditions và DoR bổ sung

- [ ] Project/building/location `S2` có stable ID/code và owner xác nhận meaning.
- [ ] `RES-06`, `SVC-17`, `ELV-01` và lifecycle-service mapping đang active trong cùng taxonomy release; cause status `UNKNOWN` được hỗ trợ nhưng không materialize thành cause record.
- [ ] CSV column contract, encoding, file/row limit và date/timezone được duyệt.
- [ ] Idempotency rule `source + source_reference` được duyệt.
- [ ] Role/scope matrix và quyền xem `content_raw`/`content_masked` được duyệt.
- [ ] Representative masked/synthetic CSV có valid, invalid và duplicate rows.
- [ ] Metric `feedback_item_count` và event-time rule được duyệt.
- [ ] OpenAPI và migration proposal được review cùng feature, không tách theo layer.

Feature chỉ chuyển sang `Ready for build` khi pass checklist trên và DoR chung trong [Build Rules](../BUILD_RULES.md).

## 6. End-to-end flow

1. CX Analyst upload CSV và cung cấp idempotency key.
2. System tạo import job, lưu file reference an toàn và bắt đầu validate async.
3. Preview hiển thị total/valid/invalid/duplicate rows; chưa tạo canonical feedback.
4. User sửa file hoặc commit valid rows theo policy đã duyệt.
5. Worker ghi raw source record bất biến và tạo `feedback` + một `feedback_item` cho dòng chuẩn.
6. Item xuất hiện trong Workspace với trạng thái `UNREVIEWED`, masked content và source lineage.
7. Operator mở detail, chọn `RES-06`, `SVC-17`, `ELV-01`, `S2`, sentiment và operational severity; cause status giữ `UNKNOWN`, candidate cause list rỗng.
8. Server validate mapping/version/scope và tạo `classification_decision` version 1; `classification_current` được project.
9. Correction sau đó tạo decision version mới với reason; raw content và decision cũ không đổi.
10. Workspace filter và insight đọc current projection; drill-down giữ nguyên filter context và trả đúng item.

## 7. State model

### Import job

```text
UPLOADED
→ MAPPED
→ VALIDATING
→ VALIDATED
→ QUEUED
→ PROCESSING
→ COMPLETED | PARTIAL | FAILED | CANCELLED
```

- User chỉ được execute từ `VALIDATED`; validation có row lỗi vẫn có thể commit valid rows nếu partial policy đã được duyệt, còn lỗi file/schema chuyển thẳng `FAILED`.
- Retry từ `FAILED` hoặc row thất bại trong `PARTIAL` chỉ khi error được đánh dấu retryable.
- Retry/commit cùng idempotency key không tạo thêm logical record.
- Job phải công bố count `total/valid/invalid/duplicate/committed`.

### Classification

```text
UNREVIEWED
→ ACCEPTED (manual decision v1)
→ CORRECTED (manual decision v2+)
```

`classification_current` trỏ tới accepted/corrected decision mới nhất. Không overwrite decision cũ.

## 8. Data contract

### CSV baseline

Các tên cột cuối cùng được khóa trong import contract/OpenAPI. Baseline của slice:

```csv
source,source_reference,reported_at,project_code,location_code,content_raw
pilot_csv,ELV-S2-0001,2026-08-10T08:00:00+07:00,PILOT_PROJECT,S2,"Thang máy S2 sáng nào cũng phải chờ rất lâu."
```

Không đặt tên, điện thoại, email hoặc mã căn thật trong fixture repository.

### Entity tối thiểu

| Entity | Mục đích |
| --- | --- |
| `import_job` | trạng thái, count, file ref, actor, idempotency, error summary |
| `source_record` | raw row/payload reference, source lineage, checksum, validation outcome |
| `feedback` | nội dung nguồn bất biến, reported/ingested time, project/location raw context |
| `feedback_item` | đơn vị manual classification và analytics |
| `classification_decision` | accepted snapshot có version, actor, reason, taxonomy version |
| `classification_current` | projection đọc nhanh, rebuild được |
| `audit_event` | privileged action/change lineage |

### Invariants

- `source + source_reference` là unique logical source key trong phạm vi đã chốt.
- `feedback.content_raw` không update; masked representation được tạo riêng.
- Một `feedback_item` của slice có tối đa một primary service và một issue trong current decision.
- `ELV-01` chỉ hợp lệ khi primary service là `SVC-17`.
- `RES-06 ↔ SVC-17` mapping phải active tại taxonomy version của decision.
- Customer Lifecycle và Service Request Lifecycle là hai dimension khác nhau theo ADR-001. Scenario này có `customer_lifecycle_value_status=KNOWN` và `RES-06`; Service Request dùng `service_request_value_status=NOT_APPLICABLE`, `service_request_step_id=null` trừ khi source workflow cung cấp bằng chứng.
- `S2` phải resolve về location master; raw text vẫn được giữ để audit.
- `cause_determination_status=UNKNOWN` và candidate cause list rỗng; không tạo confirmed root cause.
- `classification_decision.decision_version` tăng đơn điệu; stale update bị reject và `classification_current` trỏ tới decision mới nhất.

## 9. API behavior baseline

Tên endpoint cuối cùng nằm trong OpenAPI. Feature cần các capability sau:

```http
POST /api/v1/import-jobs
GET  /api/v1/import-jobs/{id}
POST /api/v1/import-jobs/{id}/validate
POST /api/v1/import-jobs/{id}/execute
POST /api/v1/import-jobs/{id}/retry
GET  /api/v1/import-jobs/{id}/errors

GET   /api/v1/feedback-items
GET   /api/v1/feedback-items/{id}
POST  /api/v1/feedback-items/{id}/decisions

GET /api/v1/insights/feedback-count
```

Rules:

- Upload/execute nhận idempotency key; decision command nhận `expected_version` và `reason`.
- Invalid service/issue/journey mapping trả `422` với stable error code.
- Stale classification update trả `409` cùng current version an toàn.
- List/insight dùng cùng filter semantics và authorization scope.
- Async job response không chứa local file path, raw storage credential hoặc stack trace.

## 10. UX behavior

- Upload có file constraints, progress, cancel khi an toàn và retry guidance.
- Preview hiển thị total/valid/invalid/duplicate, sample rows và downloadable error rows.
- Workspace có loading, empty, partial error, no-permission và retry state.
- Detail phân biệt rõ source/raw-masked content, current accepted classification và history.
- Selector Issue được scope theo primary Service; invalid combination không thể submit.
- Correction hiển thị current version, yêu cầu reason và xử lý `409` bằng refresh/compare, không âm thầm ghi đè.
- Insight segment mở Workspace với cùng date/project/service/issue/location filter trong URL.
- Confidence/AI UI không xuất hiện trong slice này.

## 11. Acceptance criteria

### AC-01 — Preview không ghi canonical data

**Given** CX Analyst có scope phù hợp và upload CSV hợp lệ<br>
**When** validation hoàn tất nhưng chưa commit<br>
**Then** preview hiển thị count chính xác và chưa có `feedback`/`feedback_item` mới.

### AC-02 — Commit tạo lineage end-to-end

**Given** row scenario chuẩn ở trạng thái valid<br>
**When** user commit import<br>
**Then** system tạo đúng một source record, một immutable raw feedback, một feedback item `UNREVIEWED` và audit/correlation đầy đủ.

### AC-03 — Idempotency

**Given** import/commit trước đã thành công<br>
**When** request được retry với cùng idempotency key/source reference<br>
**Then** system trả logical result hiện có và không tạo duplicate canonical record.

### AC-04 — Row error có thể xử lý

**Given** CSV có một row invalid date hoặc unknown location<br>
**When** validation chạy<br>
**Then** job nêu row/column/error code an toàn; invalid row không được commit và xuất hiện trong data-quality/error output.

### AC-05 — Manual classification hợp lệ

**Given** Operator có scope và item `UNREVIEWED`<br>
**When** lưu classification `RES-06/SVC-17/ELV-01/S2`, sentiment `NEGATIVE`, operational severity `SEV-2`, cause status `UNKNOWN` và candidate cause list rỗng<br>
**Then** system tạo decision version 1 `ACCEPTED`, cập nhật current projection và ghi audit actor/reason/time/taxonomy version.

### AC-06 — Reject mapping không hợp lệ

**Given** Operator chọn issue không thuộc `SVC-17` hoặc lifecycle-service mapping inactive<br>
**When** submit<br>
**Then** API trả `422`, không tạo decision/current change và UI chỉ rõ field cần sửa.

### AC-07 — Correction không overwrite history

**Given** item có accepted decision version 1<br>
**When** Operator có quyền correct với expected version và reason<br>
**Then** system tạo version 2, giữ version 1/raw feedback bất biến và audit được old/new decision reference.

### AC-08 — Concurrent correction

**Given** hai Operator mở cùng version 1<br>
**When** người thứ hai submit sau khi version 2 đã tồn tại<br>
**Then** API trả `409`; không last-write-wins và UI yêu cầu refresh/compare.

### AC-09 — Authorization

**Given** user không có scope building/location chứa S2<br>
**When** query list/detail/insight hoặc submit classification<br>
**Then** record không bị lộ và action bị từ chối/audit theo policy.

### AC-10 — Filter và drill-down đối soát

**Given** item đã accepted<br>
**When** filter `SVC-17 + ELV-01 + S2` và mở insight segment<br>
**Then** workspace và insight có cùng count theo metric definition; drill-down trả đúng item và giữ filter context.

### AC-11 — PII/log safety

**Given** import có content được policy coi là sensitive<br>
**When** job/API/UI flow chạy<br>
**Then** user thường chỉ thấy masked content; log/metric/trace không chứa raw content hoặc PII.

### AC-12 — Candidate cause an toàn

**Given** nội dung chỉ nói thời gian chờ lâu<br>
**When** classification hoàn tất<br>
**Then** `cause_determination_status` vẫn là `UNKNOWN`, không có cause record được chọn; system không tạo root cause/evidence hoặc khẳng định lỗi thiết bị.

## 12. Test strategy

| Loại | Case tối thiểu |
| --- | --- |
| Unit/domain | issue-service/lifecycle-service constraint; state transition; version conflict; unknown semantics |
| Integration | CSV parsing/encoding; transaction; idempotent retry; partial invalid rows; current projection rebuild |
| Contract | job states/count/errors; list filters; `422/409/403`; safe error body |
| E2E | upload → preview → commit → manual classify → filter → insight drill-down → audit |
| Authorization | Analyst/Operator allowed; outside project/building/service denied; raw-vs-masked access |
| Resilience | worker timeout/retry; duplicate delivery; resume failed job; projection retry |
| Performance | representative file size và list/filter query mix được chốt trong DoR |
| Privacy | fixture không có PII thật; log/trace snapshot không chứa content/raw identifier nhạy cảm |

## 13. Telemetry và SLI

### Structured events/log fields

```text
correlation_id, request_id, job_id, source_record_id,
feedback_id, feedback_item_id, taxonomy_release_id,
actor_id, action, outcome, safe_error_code
```

Không log `content_raw`, phone/email, signed URL hoặc file content.

### Metrics

- `import_jobs_total{state}`
- `import_rows_total{outcome=valid|invalid|duplicate|committed}`
- `import_job_duration_seconds`
- `manual_classification_total{outcome}`
- `classification_conflict_total`
- `feedback_query_duration_seconds`
- `feedback_unknown_location_total`
- `insight_drilldown_reconciliation_error_total`

### Trace

Trace được chuỗi hóa từ upload request → validation worker → commit worker → feedback creation → manual decision → projection → query/insight.

Alert chỉ được bật khi có owner/runbook; tối thiểu cần visibility cho terminal job failure, queue backlog và reconciliation mismatch.

## 14. Rollout

Feature flags baseline:

```text
feedback_csv_import
manual_classification
feedback_basic_insight
```

Quy trình:

1. Deploy expanded schema và code với flags off.
2. Load/validate taxonomy-location seed và checksum trên staging.
3. Chạy synthetic/representative masked CSV; đối soát source → raw → item → decision → insight.
4. Bật cho role nội bộ và một project/building pilot có owner.
5. Theo dõi job error, unknown location, authorization denial bất thường, latency và reconciliation.
6. Chỉ mở rộng scope sau khi Product/Domain Owner chấp nhận và không có security/data-quality incident nghiêm trọng.

Không gắn timeline cứng; mở rộng dựa trên release gate và evidence.

## 15. Rollback

- Tắt ba feature flag để chặn upload/edit/insight mới theo phạm vi cần thiết.
- Pause worker bằng cơ chế vận hành; không kill giữa transaction. Job retryable được resume sau fix.
- Rollback application chỉ về version còn tương thích expanded schema.
- Không xóa raw feedback, source record, decision hoặc audit đã tạo.
- Projection sai được rebuild; classification sai được forward-correct bằng decision mới có reason.
- Reconcile job/count trước khi mở lại feature.

## 16. Feature-specific Definition of Done

Ngoài DoD chung:

- [ ] Scenario chuẩn tạo đúng `RES-06/SVC-17/ELV-01/S2`, `SEV-2`, cause status `UNKNOWN`, candidate list rỗng và không suy luận root cause.
- [ ] Import retry/duplicate không làm tăng canonical count.
- [ ] Raw feedback và decision history chứng minh được tính bất biến.
- [ ] Workspace count bằng insight/drill-down count theo metric definition.
- [ ] Authorization tests cover project/building/service và raw/masked content.
- [ ] Pilot dashboard đối soát được source → item → accepted decision → insight.

## 17. Open decisions

Phải đóng trước `Ready for build`:

- Stable `project_code`, meaning/granularity của `S2` và location hierarchy — owner: Data Steward/BQL.
- CSV column names, maximum size/rows, encoding và partial-commit policy — owner: Product + Engineering.
- Role/scope matrix và raw-content permission — owner: Security + Product.
- `feedback_item_count` event-time/timezone/exclusion rule — owner: Data Steward.
- Manual correction reason bắt buộc dạng free text hay reason code — owner: CX Operations.
