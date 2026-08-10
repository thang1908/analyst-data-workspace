# Build Rules — CX Intelligence & Operations Platform

- **Phiên bản:** 0.1
- **Trạng thái:** Active
- **Áp dụng cho:** Mọi feature, API, migration, job, dashboard, model và release
- **Tài liệu liên quan:** [START HERE](./00_START_HERE.md), [PRD](./PRD.md), [Service Taxonomy](./service_taxonomy.md)

## 1. Mục tiêu

Tài liệu này định nghĩa cách team biến PRD và taxonomy thành phần mềm có thể kiểm thử, quan sát, vận hành và thay đổi an toàn.

Mỗi thành viên có quyền dừng một feature nếu phát hiện domain assumption chưa được xác nhận, vi phạm security/privacy hoặc không có cách kiểm chứng acceptance criteria.

## 2. Các nguyên tắc không được phá vỡ

1. Build theo **vertical slice**, không bàn giao theo silo “DB xong”, “API xong”, “UI xong”.
2. Bắt đầu bằng **modular monolith + background worker**; chỉ tách service khi có bằng chứng về scale, ownership hoặc isolation.
3. Taxonomy, role, threshold, priority rule và handling unit là dữ liệu/config có version; không hard-code.
4. Raw feedback là bất biến. Correction tạo decision/version mới.
5. `prediction ≠ accepted decision`; `Candidate Cause ≠ Confirmed Root Cause`.
6. Mọi write từ client hoặc nguồn ngoài phải validate phía server, idempotent khi có retry và có audit phù hợp.
7. Mọi quyền đều enforce phía server theo scope; ẩn nút ở UI không phải authorization.
8. PII/raw content không xuất hiện trong log, metric, trace, fixture công khai hoặc prompt AI chưa được phê duyệt.
9. Mọi chart/KPI phải drill-down về tập record tạo ra số liệu; không có chart dead-end.
10. Migration, test, telemetry, runbook, feature flag và rollback là một phần của feature.
11. Không hard-delete dữ liệu có lịch sử nghiệp vụ hoặc taxonomy đã được tham chiếu.
12. Khi tài liệu mâu thuẫn, giải quyết bằng source-of-truth/ADR; không tự chọn cách hiểu thuận tiện.

## 3. Vertical slice

### 3.1 Định nghĩa

Một vertical slice là đơn vị delivery tạo ra một outcome có thể demo và kiểm chứng end-to-end, đi xuyên qua các lớp cần thiết:

```text
User/source action
→ authorization
→ API/job
→ domain rule
→ persistence/event
→ query/UI
→ audit/telemetry
→ automated test
→ controlled rollout
```

Một slice không bắt buộc phải có mọi màn hình hoặc mọi integration. Nó phải nhỏ nhất có thể nhưng vẫn tạo ra một vòng giá trị hoàn chỉnh.

### 3.2 Quy tắc slicing

- Slice theo outcome hoặc user decision, không theo technical component.
- Mỗi slice có một persona chính, một business owner và một trạng thái kết thúc đo được.
- Happy path, validation error, authorization failure, retry và audit phải nằm trong cùng scope nếu chúng cần thiết để dùng feature an toàn.
- Cross-cutting concern không được đẩy sang “hardening sau” nếu feature đã xử lý dữ liệu thật.
- Nếu slice lớn hơn khả năng review/demo trong một nhịp delivery, cắt theo source, actor, risk, service domain hoặc workflow state; không cắt UI/API/data thành các backlog độc lập.
- AI phải được thêm sau khi manual fallback hoạt động, trừ khi outcome không thể tồn tại nếu thiếu AI.

### 3.3 Ví dụ đúng

[FEAT-001](./features/FEAT-001-elevator-manual-slice.md) bao gồm CSV intake, validate, raw record, manual classification, workspace/filter, basic insight, audit và telemetry cho một use case elevator.

### 3.4 Ví dụ không được coi là vertical slice

- “Tạo tất cả database tables”.
- “Build toàn bộ REST API”.
- “Thiết kế dashboard trước khi metric definition được chốt”.
- “Tích hợp AI classifier” nhưng chưa có review queue, audit và manual fallback.

## 4. Kiến trúc và module boundary

### 4.1 Kiến trúc MVP

Baseline triển khai:

```text
Web application
       ↓
Modular application/API
       ├── synchronous domain use cases
       ├── PostgreSQL
       ├── object storage cho source file/attachment
       └── transactional outbox
                    ↓
             Background workers
             import / AI / projection / hotspot
```

Không tạo microservice chỉ để phản ánh sơ đồ domain. Module boundary được thiết kế rõ trong code và schema để có thể tách sau nếu cần.

### 4.2 Bounded modules

| Module | Sở hữu | Không được sở hữu |
| --- | --- | --- |
| Identity & Governance | user, role, scope, privileged audit policy | taxonomy và feedback business rule |
| Taxonomy & Location | journey, service, issue, cause group, mapping, version, location | prediction/review |
| Feedback Intake | source, batch/job, raw record, validation, dedupe, canonicalization | accepted classification logic |
| Classification & Review | feedback item, prediction, decision, current projection, correction | root-cause confirmation |
| Feedback Exploration | query/read model, search/filter/detail/export | authoritative write model |
| Analytics | metric definition, aggregate/read projection, drill-down keys | sửa feedback/classification |
| Hotspot Intelligence | rule, evaluation, hotspot candidate, membership | ticket/SLA/RCA |
| Case Operations — P1 | ticket, assignment, SLA, escalation | taxonomy ownership |
| Investigation & RCA — P1 | investigation, evidence, confirmed cause, action | AI auto-confirmation |

### 4.3 Boundary rules

- Mỗi module sở hữu schema/table write và domain service của mình.
- Module khác không ghi trực tiếp table do module này sở hữu.
- Cross-module command đi qua application interface; async propagation dùng versioned event/outbox.
- Read projection có thể denormalize nhưng không trở thành source of truth.
- Shared kernel chỉ gồm primitive chung như ID, time, money, pagination và correlation; không đặt domain entity dùng chung vào shared folder.
- Không tạo circular dependency. Dependency direction phải được ghi trong architecture test hoặc module rule.
- Background job phải idempotent, retryable, có dead-letter/failure visibility và correlation về source job/record.

## 5. Domain và data rules

### 5.1 Identity và time

- Business entity dùng stable opaque ID; business code như `SVC-17`, `ELV-01`, `RES-06` là unique, human-readable key và không tái sử dụng.
- Timestamp lưu UTC, ISO-8601 ở contract; UI hiển thị theo timezone cấu hình.
- Lưu riêng `reported_at`, `ingested_at`, `created_at`, `updated_at`; không thay thế lẫn nhau.
- Actor/system identity phải có trong mọi privileged write/audit event.

### 5.2 Raw feedback và classification

- Tuân theo [ADR-002](./architecture/adr/ADR-002-classification-model.md).
- Raw payload/content không update sau ingest. Masked/redacted representation có version riêng.
- Một raw feedback có thể tạo nhiều feedback item; mỗi item là đơn vị classification/analytics.
- Prediction là append-only và phải lưu model version, taxonomy version, confidence, input reference và thời điểm.
- Accepted decision là append-only; correction tạo decision version mới, có actor và reason.
- `classification_current` chỉ là projection đọc nhanh, có thể rebuild từ decision history.
- Một item có tối đa một primary service tại một decision version; secondary service dùng relation có role rõ.
- Issue phải thuộc primary service và mapping phải active tại taxonomy version tương ứng.
- Journey dimensions tuân theo [ADR-001](./architecture/adr/ADR-001-journey-dimensions.md).

### 5.3 Unknown, missing và not applicable

Không đồng nhất ba trạng thái:

- `UNKNOWN`: trường có ý nghĩa nhưng hiện chưa đủ bằng chứng.
- `MISSING`: nguồn lẽ ra phải cung cấp nhưng dữ liệu bị thiếu/invalid; phải xuất hiện trong data quality.
- `NOT_APPLICABLE`: trường không áp dụng cho loại record này.

Không dùng empty string, `0`, “N/A” tự do hoặc một ID giả cho các trạng thái trên.

Mỗi reference có thể chưa có giá trị phải dùng companion status, ví dụ `issue_value_status` và `issue_id`:

```text
value_status = KNOWN | UNKNOWN | MISSING | NOT_APPLICABLE
```

- `KNOWN` bắt buộc ID khác null và resolve được trong taxonomy release.
- Ba trạng thái còn lại bắt buộc ID null; không dùng cùng một `null` để mang ba nghĩa.
- Item có field bắt buộc ở `MISSING/UNKNOWN` phải được đánh dấu data-quality/analytic eligibility theo metric policy, không âm thầm coi là hợp lệ.

### 5.4 Taxonomy và reference data

- Taxonomy/reference data có stable code, version, `active_from`, `active_to`, actor và change reason.
- Deactivate/supersede thay vì hard delete.
- Historical decision giữ taxonomy version đã dùng; báo cáo phải nói rõ dùng historical hay current taxonomy projection.
- Seed phải machine-readable, có checksum và validator cho uniqueness, foreign key, journey-service mapping, issue-service mapping và cause code.
- Thay đổi meaning của code hiện có là breaking semantic change; tạo version/code mới hoặc migration được duyệt.

### 5.5 Location

- Location là master data có hierarchy và stable code; không dùng raw text làm hotspot key.
- Raw location text được giữ để audit; normalization ghi mapping/method/confidence riêng.
- Granularity dùng trong filter/hotspot phải explicit.
- Record thiếu location không được âm thầm gán vào building mặc định; nó đi vào data-quality queue.

### 5.6 Idempotency, duplicate và consistency

- Source ingestion dùng `source + source_reference` hoặc idempotency key đã chốt; content hash chỉ là signal, không tự xóa record.
- Retry cùng key phải trả cùng logical result hoặc trạng thái hiện tại, không tạo duplicate.
- Duplicate business record được giữ lineage và đánh dấu/link; không xóa raw evidence.
- Constraint quan trọng được enforce cả trong database và domain layer khi khả thi.
- Concurrent edit dùng version/ETag; stale write trả conflict, không last-write-wins âm thầm.

### 5.7 Audit và retention

- Audit record là append-only và chứa actor, action, entity, old/new reference, reason, time, correlation ID.
- Audit không chứa raw PII ngoài phần được policy cho phép.
- Không hard-delete feedback, classification, ticket, taxonomy hoặc evidence đã có lịch sử.
- Retention/erasure phải có policy được duyệt trước production; anonymization phải giữ được integrity của operational metrics trong phạm vi pháp lý cho phép.

## 6. API rules

### 6.1 Contract

- OpenAPI-first; endpoint production phải có request, response, error, auth scope và example đã review.
- Prefix `/api/v1`; resource dùng danh từ số nhiều và stable ID.
- JSON field dùng một naming convention duy nhất; enum dùng stable machine value, label hiển thị tách riêng.
- Timestamp là ISO-8601 UTC; response có correlation/request ID.
- Không trả raw internal stack trace, SQL error hoặc secret.

### 6.2 Validation và errors

- Validate schema, domain invariant, authorization và reference version phía server.
- Error response dùng một problem schema thống nhất gồm `code`, `message`, `correlation_id` và `field_errors` khi có.
- Dùng status semantics nhất quán: `400` malformed, `401` unauthenticated, `403` unauthorized, `404` không thấy trong scope, `409` conflict/idempotency/concurrency, `422` domain validation, `429` rate limit.
- Import error phải chỉ rõ batch, row, column, error code và safe message; user tải được error rows.

### 6.3 Query API

- List endpoint có cursor pagination hoặc pagination strategy đã chốt, stable sort và bounded page size.
- Filter semantics, timezone, inclusive/exclusive boundary và default sort phải được tài liệu hóa.
- Search/filter không được trả record ngoài authorization scope.
- Export dùng cùng filter/query contract với workspace và được audit.

### 6.4 Write API

- Create/commit/retry endpoint quan trọng nhận idempotency key.
- Update nhận expected version/ETag; conflict trả trạng thái có thể xử lý.
- Manual override bắt buộc actor và reason theo policy.
- Long-running import/classification/aggregation trả job resource, không giữ HTTP request mở.
- Job API tối thiểu thể hiện state, progress/count, row errors, started/completed time và retryability.

### 6.5 Compatibility

- Additive change được ưu tiên.
- Không rename/remove field hoặc đổi enum meaning trong cùng API version.
- Event consumer phải chấp nhận additive field và xử lý duplicate/out-of-order theo contract.
- Deprecation có owner, consumer inventory và thời điểm loại bỏ được thông báo.

## 7. UX rules

- Màn hình phải có loading, empty, partial error, retry, permission denied và success feedback phù hợp.
- Raw/accepted label/AI suggestion/confidence/review status phải được phân biệt bằng ngôn ngữ và thị giác, không chỉ màu sắc.
- Filter state được giữ trong URL hoặc saved query để drill-down/back không mất context.
- Chart segment mở đúng filtered feedback list; danh sách mở feedback detail và audit.
- Không hiển thị action user không có quyền, nhưng authorization vẫn phải enforce phía server.
- Destructive/deactivate/bulk action cần scope preview, confirmation và kết quả từng record.
- UI dùng taxonomy label từ API; không copy enum/label vào source code.
- Các control chính phải dùng được bằng bàn phím, có accessible name và trạng thái focus/error rõ.

## 8. Security và privacy rules

### 8.1 Authentication và authorization

- SSO/RBAC tối thiểu là P0 cho dữ liệu thật.
- Least privilege theo role và scope `project/building/service`; deny by default.
- Authorization được kiểm tra ở query và command; không chỉ route/menu.
- Privileged action, export, xem raw PII, role/scope change và taxonomy change phải audit.
- Service account có identity riêng, scope hẹp, rotation và không dùng chung user credential.

### 8.2 Data protection

- Phân loại field theo public/internal/confidential/PII/sensitive trước khi production.
- Encrypt in transit và at rest theo platform standard.
- Analytics và AI mặc định dùng `content_masked`; quyền xem `content_raw` tách riêng.
- Attachment dùng signed URL ngắn hạn, kiểm tra authorization trước khi ký.
- Secret nằm trong secret manager/environment được quản lý; không commit hoặc log.
- Lower environment dùng synthetic hoặc masked data; không copy raw production PII tùy tiện.

### 8.3 Logging và incident response

- Không log content, phone, email, unit-owner identity, token hoặc attachment URL có chữ ký.
- Security event có correlation, actor, target, action và outcome nhưng không chứa secret/PII không cần thiết.
- Feature xử lý dữ liệu nhạy cảm phải có threat review, abuse cases và runbook trước pilot.

## 9. AI rules

- AI tạo `classification_prediction`; không tự ghi đè accepted decision.
- Auto-apply chỉ được thực hiện bởi policy engine cho label low-risk đã được duyệt, đủ threshold theo label và có kill switch.
- Không AI nào được auto-confirm Root Cause, safety/legal responsibility hoặc gửi operational dispatch.
- Khi AI lỗi, timeout hoặc output invalid, record vẫn đi qua manual workflow.
- Output phải validate theo schema và taxonomy version; label ngoài candidate set bị reject.
- Lưu model/provider/version, prompt/pipeline version, taxonomy version, confidence per field, latency và review outcome.
- Prompt/input gửi ra ngoài phải được mask/minimize theo privacy policy và hợp đồng nhà cung cấp.
- Không dùng correction làm training data nếu chưa có lineage, consent/policy và data-quality check.
- Evaluation dùng frozen, versioned, stratified gold set; báo Macro-F1, per-label support, unknown/abstain rate, override rate và confidence calibration.
- Không dùng metric tổng hợp để che label safety/rare có chất lượng thấp.
- Model/rule rollout có feature flag, shadow/canary option, monitoring drift và rollback độc lập với application release.

## 10. Testing rules

### 10.1 Test bắt buộc theo risk

| Loại test | Mục tiêu tối thiểu |
| --- | --- |
| Unit/domain | Invariant, state transition, priority/rule calculation, time boundary |
| Database/integration | Constraint, transaction, migration, retry, idempotency, concurrency |
| Contract | OpenAPI request/response/error; event schema compatibility |
| End-to-end | Critical user flow từ source/UI tới persistence/query/audit |
| Authorization | Allowed/denied theo role và project/building/service scope |
| Data quality | Missing, invalid mapping, duplicate, unknown location, malformed encoding |
| Resilience | Worker retry, partial failure, timeout, duplicate/out-of-order event |
| Performance | Data volume/query mix đã chốt trong feature DoR |
| AI evaluation | Frozen gold set, per-label metric, abstain/fallback, invalid output |

### 10.2 Test data

- Fixture có stable ID và không chứa PII thật.
- Mỗi feature có golden happy-path record và negative/boundary cases.
- Taxonomy fixture phải được validate cùng rule như production seed.
- Time-dependent test dùng fixed clock; không phụ thuộc timezone/máy chạy.
- Test import phải bao gồm duplicate key, invalid row, partial batch, retry và resumable behavior.

### 10.3 CI gate

Pull request không merge khi:

- lint/typecheck/test liên quan fail;
- migration không chạy được từ version đang hỗ trợ;
- OpenAPI/event compatibility check fail;
- secret/PII scan hoặc dependency security gate fail theo policy;
- coverage của critical domain branch bị bỏ mà không có lý do review;
- acceptance criteria không có test hoặc bằng chứng kiểm chứng tương ứng.

## 11. Observability rules

### 11.1 Correlation

Mỗi request/job/event phải truyền các ID phù hợp:

```text
correlation_id
request_id
job_id / batch_id
source_record_id
feedback_id / feedback_item_id
model_version
taxonomy_release_id
rule_version
```

Không đưa raw content/PII vào label metric hoặc trace attribute.

### 11.2 Structured logs

- Log theo event/action/outcome, structured và queryable.
- Error log có safe error code, retryability, dependency và correlation.
- Không dùng log làm audit source of truth.
- Sampling không được làm mất security event hoặc job terminal failure.

### 11.3 Metrics và SLI

Mỗi feature chọn SLI phù hợp và ghi target trong feature spec, ví dụ:

- API latency/error/authorization-denied rate;
- import rows processed/failed/duplicate, job duration và retry count;
- queue depth/lag/dead-letter;
- classification prediction latency, abstain, review backlog, override rate;
- missing/unknown/invalid mapping rate;
- analytics freshness và drill-down reconciliation;
- hotspot evaluation lag, candidate count, reopen/false-positive review.

### 11.4 Dashboard, alert và runbook

- Mỗi production alert có owner, severity, actionable threshold và runbook.
- Không alert chỉ vì metric “trông lạ”; phải nói operator cần kiểm tra/hành động gì.
- Dashboard release/pilot phải cho phép đối soát source count → canonical count → accepted classification → aggregate.

## 12. Release rules

### 12.1 Change flow

- Dùng protected main/trunk, short-lived branch và reviewed pull request.
- PR link feature/ADR, nêu scope, test evidence, migration, security, telemetry và rollback.
- Feature flag mặc định off cho thay đổi chưa rollout.
- Taxonomy, AI model và hotspot rule có version/release note riêng, dù được phát hành cùng application.

### 12.2 Database migration

- Dùng `expand → migrate/backfill → verify → contract` qua các release tương thích.
- Không drop/rename destructive hoặc đổi meaning dữ liệu trong cùng deploy với code phụ thuộc.
- Backfill retryable, observable và không khóa bảng vượt budget đã chốt.
- Rollback application phải chạy được với expanded schema; data correction ưu tiên forward-fix có audit.

### 12.3 Environment và pilot

- Dev/test dùng synthetic fixture; staging dùng representative masked dataset.
- Trước pilot: reconcile record count, error count, permissions, audit, metric và query performance.
- Rollout theo project/building/role bằng feature flag; có owner theo dõi và tiêu chí stop/continue.
- Không mở rộng pilot khi data-quality hoặc authorization incident chưa được xử lý.

### 12.4 Rollback

Mỗi release phải xác định:

- flag/kill switch nào tắt behavior;
- worker/job nào cần pause và cách resume an toàn;
- model/rule/taxonomy version nào quay lại;
- dữ liệu nào đã ghi và cách reconcile/forward-correct;
- owner quyết định rollback và kênh thông báo.

Không rollback bằng cách xóa raw feedback, decision history hoặc chạy destructive reset.

## 13. Definition of Ready — DoR

Feature chỉ có trạng thái `Ready for build` khi tất cả mục sau đã đạt hoặc có exception được phê duyệt:

- [ ] Business outcome, persona chính và accountable owner rõ.
- [ ] Link tới PRD story, taxonomy và ADR liên quan.
- [ ] Scope và non-goal rõ; không che giấu dependency ngoài MVP.
- [ ] Acceptance criteria Given/When/Then gồm happy path, validation, permission, retry và audit phù hợp.
- [ ] Domain invariant, state machine và source of truth được xác định.
- [ ] Sample data representative, expected volume/query mix và edge cases có sẵn.
- [ ] API/schema/event impact đã review; migration/backfill approach rõ.
- [ ] UX flow có loading/empty/error/permission/concurrency state.
- [ ] Role/scope, PII classification, retention và audit requirement rõ.
- [ ] Test strategy và telemetry/SLI được định nghĩa.
- [ ] Rollout, feature flag, rollback và owner theo dõi được định nghĩa.
- [ ] Không còn open decision có thể thay đổi acceptance criteria hoặc data model trong scope.

## 14. Definition of Done — DoD

Feature chỉ có trạng thái `Done` khi:

- [ ] Tất cả acceptance criteria có automated test hoặc evidence kiểm chứng được duyệt.
- [ ] Code review, lint, typecheck, unit, integration, contract, E2E và security gate liên quan pass.
- [ ] Database constraint/migration/backfill được test trên representative volume.
- [ ] OpenAPI, event schema, feature spec, ADR và changelog liên quan đã cập nhật.
- [ ] Authorization enforce server-side; privileged action và export có audit.
- [ ] Không log PII/raw content/secret; security/privacy review theo risk đã pass.
- [ ] Structured logs, metrics, trace, dashboard/alert cần thiết hoạt động với correlation ID.
- [ ] Performance/reliability budget của feature đạt trên staging.
- [ ] Loading/empty/error/permission/accessibility states đã kiểm tra.
- [ ] Feature flag, runbook, release note, rollout/rollback plan đã sẵn sàng.
- [ ] Dữ liệu pilot được reconcile source → canonical → decision → aggregate.
- [ ] Product/Domain Owner chấp nhận outcome; không còn defect P0/P1 trong scope.

## 15. Feature-spec template

Mỗi file `docs/features/FEAT-xxx-name.md` dùng cấu trúc sau:

```markdown
# FEAT-XXX — Tên outcome

- **Status:** Proposed | Ready for refinement | Ready for build | In delivery | Pilot | Done
- **Priority:** P0 | P1 | P2
- **Owner:**
- **Personas:**
- **Bounded contexts:**
- **Related:** PRD stories, taxonomy, ADR, OpenAPI

## 1. Outcome

Một câu mô tả thay đổi quan sát được cho user/business.

## 2. Scope

- In scope
- Non-goal

## 3. Actors và permissions

Role, scope, allowed/denied action, raw/masked access.

## 4. Preconditions / DoR additions

Data, owner decision, sample, dependency riêng của feature.

## 5. End-to-end flow

Happy path và state transitions.

## 6. Domain/data contract

Entities, IDs, invariants, example, taxonomy/rule version.

## 7. API/event behavior

Commands, queries, errors, idempotency, concurrency, async job/event.

## 8. UX behavior

Screen/state/filter/drill-down/loading/error/permission/accessibility.

## 9. Acceptance criteria

Given / When / Then, đánh số AC-01...

## 10. Test strategy

Unit, integration, contract, E2E, authorization, resilience, performance.

## 11. Telemetry và SLI

Logs, metrics, traces, dashboard, alert/runbook.

## 12. Rollout và rollback

Flags, scope, reconciliation, stop criteria, rollback/forward-fix.

## 13. Feature-specific DoD

Các gate ngoài DoD chung.

## 14. Open decisions

Câu hỏi, owner, due-before-build/release.
```

## 16. Pull-request checklist tối thiểu

- [ ] Link feature ID và AC được implement.
- [ ] Không mở rộng scope ngoài feature/non-goal.
- [ ] Domain/API/data/security assumption mới đã vào spec hoặc ADR.
- [ ] Tests chứng minh invariant và failure path chính.
- [ ] Migration backward-compatible; seed/config có validator/version.
- [ ] Authorization và PII/logging đã kiểm tra.
- [ ] Telemetry đủ để biết feature đang chạy đúng hay sai.
- [ ] Rollout/rollback và backward compatibility được mô tả.
