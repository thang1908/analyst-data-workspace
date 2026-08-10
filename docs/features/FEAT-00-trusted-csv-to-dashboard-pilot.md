# FEAT-00 — Trusted CSV to Dashboard Pilot

- **Status:** Ready for refinement
- **Priority:** P0 — one-week staging MVP
- **Outcome owner:** Product Owner / Data Steward
- **Primary personas:** CX Analyst, CX Manager
- **Integration branch:** `dev`
- **Related:** [PRD](../PRD.md), [Service Taxonomy](../service_taxonomy.md), [Build Rules](../BUILD_RULES.md), [ADR-002](../architecture/adr/ADR-002-classification-model.md)
- **Child features:** [FEAT-01](./FEAT-01-data-foundation.md), [FEAT-02](./FEAT-02-csv-import.md), [FEAT-03](./FEAT-03-analytics-api.md), [FEAT-04](./FEAT-04-dashboard-ui.md), [FEAT-05](./FEAT-05-release-quality.md)

## 1. Outcome và timebox

Trong một tuần làm việc, user nội bộ có quyền có thể đưa một file CSV đã được mask và gắn nhãn tin cậy vào staging, xem kết quả validation/import, sau đó xem KPI, trend, breakdown và drill-down về đúng các feedback item tạo ra số liệu.

Đây là staging MVP để chứng minh luồng:

```text
Trusted CSV v1
→ validate + deduplicate
→ immutable source/canonical records
→ SOURCE_TRUSTED decision
→ analytics query
→ dashboard + drill-down
→ reconciliation + release evidence
```

Cam kết một tuần chỉ có hiệu lực khi Definition of Ready ở mục 13 hoàn tất trước kickoff. Không coi bản này là production-ready, không dùng cho dữ liệu chưa mask và không mở rộng scope giữa tuần.

## 2. Success boundary

Pilot được xem là đạt khi tất cả điều sau đúng trên staging:

- Một file tối đa 10.000 dòng theo đúng `trusted-feedback-csv/v1` được validate và execute bất đồng bộ.
- Mọi dòng có outcome rõ ràng `VALID`, `INVALID` hoặc `DUPLICATE`; không drop âm thầm.
- `total_rows = valid_rows + invalid_rows + duplicate_rows` và `committed_rows = valid_rows` sau một execution thành công.
- Retry cùng idempotency key hoặc upload lại cùng `source_reference` không tạo canonical record trùng.
- Dashboard và drill-down trả cùng tập `feedback_item_id` với cùng filter, `metric_definition_version` và snapshot token; import hoàn tất sau snapshot chỉ xuất hiện khi user refresh.
- User ngoài pilot project không đọc được import, item hoặc analytics của project đó.
- Log, metric và trace không chứa `content_masked`, nội dung file, email, số điện thoại hoặc secret.
- Với dữ liệu pilot 100.000 item, dashboard query chuẩn đạt p95 dưới 2 giây trên staging; ngưỡng release bắt buộc vẫn không được kém hơn NFR của PRD.

## 3. Scope cố định

### In scope

- Một project pilot, một location hierarchy đã seed và tối đa ba Service đã được Data Steward duyệt.
- Một CSV contract cố định, UTF-8, comma-delimited, dữ liệu đã mask và label do nguồn cung cấp.
- Upload, schema/row validation, preview counts, error download, execute, idempotency, duplicate detection và retry lỗi hệ thống.
- Immutable source lineage, một `feedback`, một `feedback_item` và một `SOURCE_TRUSTED` decision cho mỗi dòng hợp lệ.
- KPI item volume, negative rate, trend theo ngày và breakdown theo Service, Issue, Location, Sentiment, Operational Severity.
- Shared filters, stable pagination, dashboard states và drill-down về danh sách feedback masked.
- Minimal project-scoped authorization, audit, telemetry, reconciliation, feature flag, runbook và rollback.

### Out of scope

- XLSX, JSON, realtime API, webhook, social/hotline/app connector hoặc reusable column mapper.
- `content_raw`, attachment, customer name, phone, email, household ID hoặc dữ liệu PII thật.
- Manual classification/correction, AI prediction, review queue, lifecycle labeling, candidate cause, hotspot, ticket hoặc RCA.
- Taxonomy/location editor; pilot chỉ dùng seed/version đã publish.
- Saved view, export dashboard lớn, custom chart, comparison period hoặc scheduled report.
- Production HA, multi-region, historical backfill lớn hơn giới hạn file, SSO enterprise hoàn chỉnh hoặc fine-grained service scope.

Yêu cầu ngoài danh sách này phải đi thành feature mới; không thêm vào child feature đang chạy.

## 4. Hợp đồng CSV dùng chung

Contract ID là `trusted-feedback-csv/v1`. Header phải đúng tên và đúng thứ tự:

```csv
source_reference,reported_at,project_code,location_code,service_code,issue_code,sentiment,operational_severity,content_masked
ELV-S2-0001,2026-08-10T08:00:00+07:00,PILOT_PROJECT,S2,SVC-17,ELV-01,NEGATIVE,SEV-2,"Thang máy S2 sáng nào cũng phải chờ rất lâu."
```

| Field | Required | Contract |
| --- | --- | --- |
| `source_reference` | Có | Operational non-PII key, không dùng tên/phone/email/unit ID; 1–128 ASCII characters; regex `^[A-Za-z0-9][A-Za-z0-9._:/-]{0,127}$`; unique logical key cùng source `PILOT_CSV_V1`. |
| `reported_at` | Có | ISO-8601 có offset hoặc `Z`; parse được thành thời điểm duy nhất; lưu UTC, giữ offset nguồn. |
| `project_code` | Có | Exact, case-sensitive code trong project seed đang active. |
| `location_code` | Có | Exact, case-sensitive code thuộc `project_code` trong location release đang active. |
| `service_code` | Có | Exact code trong taxonomy release được pin cho job. |
| `issue_code` | Có | Exact code active và mapped với `service_code` trong cùng taxonomy release. |
| `sentiment` | Có | Một trong `POSITIVE`, `NEUTRAL`, `NEGATIVE`, `MIXED`, `UNKNOWN`. |
| `operational_severity` | Có | Một trong `SEV-1`, `SEV-2`, `SEV-3`, `SEV-4`. |
| `content_masked` | Có | 1–4.000 Unicode code points sau CSV unescape; đã mask; không chứa line formula/action và không được log. |

File rules:

- MIME được chấp nhận: `text/csv` hoặc `application/vnd.ms-excel`; extension bắt buộc `.csv`.
- UTF-8; BOM đầu file được phép và bị loại trước khi so header. LF/CRLF đều hợp lệ.
- RFC 4180 quoting; delimiter là comma; không hỗ trợ tab, semicolon hoặc auto-detect.
- Tối đa 10 MiB và 10.000 data rows; chỉ một dòng trống cuối file được bỏ qua.
- Không cho phép thiếu, thừa, đổi tên hoặc đổi thứ tự column ở v1.
- Scalar trừ `content_masked` được trim ASCII whitespace trước validation; code không tự uppercase hoặc sửa.
- `content_masked` được giữ nguyên sau CSV unescape, chỉ chuẩn hóa CRLF nội bộ thành LF để checksum ổn định.
- Spreadsheet formula prefix `=`, `+`, `-`, `@` trong field text được escape khi xuất error file; không thực thi hoặc render như HTML.

Mỗi job pin `contract_version`, `taxonomy_release_id`, `location_release_id`, source trust policy version và SHA-256 của file. Child feature không được định nghĩa lại contract này.

## 5. Canonical semantics

Mỗi dòng `VALID` được execute thành đúng một chuỗi record:

```text
import_job + import_row
→ source_record
→ feedback
→ feedback_item(item_index=1)
→ classification_decision(decision_version=1, decision_source=SOURCE_TRUSTED)
→ classification_current
→ outbox_event(feedback.item.accepted.v1)
```

Decision v1 phải có:

```text
customer_lifecycle_value_status = UNKNOWN
customer_lifecycle_step_id      = null
service_request_value_status    = NOT_APPLICABLE
service_request_step_id         = null
primary_service_value_status    = KNOWN
primary_service_id              = resolved service_code
issue_value_status              = KNOWN
issue_id                        = resolved issue_code
sentiment                       = CSV value
operational_severity            = CSV value
location_value_status           = KNOWN
location_id                     = resolved project/location_code
cause_determination_status      = UNKNOWN
decision_source                 = SOURCE_TRUSTED
```

`SOURCE_TRUSTED` chỉ hợp lệ khi source trust policy `pilot-csv-v1` đã được Product Owner và Data Steward phê duyệt. Nếu chưa phê duyệt, chỉ được chạy synthetic fixture; không tự coi label nguồn là accepted decision.

## 6. Child feature và branch ownership

| Thứ tự | Feature | Branch | Build outcome | Exclusive write paths |
| --- | --- | --- | --- | --- |
| 1 | FEAT-01 Platform & Data Foundation | `codex/feat-data-foundation` | Monorepo/app shells chạy được, actor context, common contracts/domain, PostgreSQL schema/migration/repository và pilot seed. | Root/app-shell/platform config; `packages/domain/**`; `packages/db/**`; shared foundation trong `packages/contracts/**`. |
| 2 | FEAT-02 CSV Import | `codex/feat-csv-import` | Upload/validate/preview/execute/retry và row lineage hoàn chỉnh. | `apps/api/src/modules/imports/**`; `apps/worker/src/modules/imports/**`; `packages/contracts/src/import/**`; `packages/test-fixtures/import/**`. |
| 3 | FEAT-03 Analytics API | `codex/feat-analytics-api` | Metric/filter contract, aggregate query và drill-down API đối soát được. | Paths ghi trong FEAT-03; không sửa import module. |
| 4 | FEAT-04 Pilot Web UI | `codex/feat-pilot-web-ui` | Import control, dashboard responsive, shared filters, states và drill-down. | Paths ghi trong FEAT-04; không sửa API/domain trực tiếp. |
| 5 | FEAT-05 Release Quality | `codex/feat-release-quality` | E2E, CI/reconciliation, runbook, staging rollout và release evidence. | Paths ghi trong FEAT-05; product code fix quay về owner feature. |

Một file chỉ có một feature owner. Nếu cần thay contract hoặc schema của feature khác, mở change request nhỏ và để owner của path thực hiện; không sửa chéo trong PR của mình.

## 7. Dependency và integration order

```text
FEAT-01 platform/contract/schema freeze
        ├── FEAT-02 import API/worker ─┐
        └── FEAT-03 analytics API ─────┤
                                        ├── FEAT-04 Pilot Web UI
                                        ↓
                                  FEAT-05 E2E/release
```

Quy tắc để vẫn làm song song:

1. `codex/feat-data-foundation` được merge vào `dev` sớm nhất sau khi migration, seed validator và package public API pass; mục tiêu là nửa đầu ngày 1.
2. Trước thời điểm đó, FEAT-02/030/040 chỉ viết test, mock và code trong exclusive paths dựa trên contract đã review trong spec.
3. Sau khi FEAT-01 merge, từng branch rebase trên `dev`, bỏ mọi local stub trùng shared package và chạy full gate.
4. FEAT-02 và FEAT-03 có thể merge độc lập sau FEAT-01. FEAT-04 chỉ merge khi contract test với cả FEAT-02 và FEAT-03 pass; mock chỉ dùng cho test/dev story.
5. FEAT-05 merge cuối; defect product code phải được sửa ở branch/path owner hoặc follow-up commit có owner review.

Không merge feature branch vào feature branch khác và không push thẳng lên `dev`. Mỗi PR phải squash/rebase sạch, link feature ID và liệt kê AC đã đạt.

## 8. End-to-end flow

1. CX Analyst có permission `imports:write` tải CSV v1 lên với `Idempotency-Key`.
2. API stream file tới source-file store, tính SHA-256, tạo `import_job=UPLOADED`, sau đó auto-map exact header thành `MAPPED`.
3. Analyst yêu cầu validate; worker pin reference releases, parse từng row và tạo immutable validation result.
4. Job `VALIDATED` công bố total/valid/invalid/duplicate; UI cho tải error CSV nhưng chưa có canonical feedback.
5. Analyst execute job. Worker claim job, commit mỗi chunk trong transaction idempotent và phát outbox event.
6. Job kết thúc `COMPLETED` hoặc `PARTIAL`; count được reconcile với canonical rows.
7. Analytics query nhìn thấy item committed sau freshness budget; dashboard refresh hiển thị KPI/chart.
8. User đổi filter hoặc click chart segment; API trả list được tạo bởi cùng normalized filter và `metric_definition_version`.
9. Auditor có thể truy từ item về decision, feedback, source row, import job và file checksum mà không cần log nội dung.

## 9. Shared invariants

- `source=PILOT_CSV_V1` cùng `source_reference` là unique logical source key.
- Preview/validation không tạo `source_record`, `feedback`, `feedback_item` hoặc decision.
- Execute một row là atomic: tạo đủ canonical chain và outbox event, hoặc không tạo phần nào.
- Source row, feedback envelope và decision snapshot là append-only; không có API update/delete trong pilot.
- Mỗi feedback của contract v1 có đúng một feedback item với `item_index=1`.
- `KNOWN` bắt buộc foreign key resolve trong release đã pin; `UNKNOWN/NOT_APPLICABLE` bắt buộc ID null.
- Issue phải mapped với Service; Location phải thuộc Project; mọi check được enforce cả domain và DB khi khả thi.
- `classification_current` là projection rebuildable, không phải audit source of truth.
- Metric unit mặc định là distinct `feedback_item_id`; event time là `reported_at` theo timezone filter được gửi rõ ràng.
- Chart, KPI và drill-down bắt buộc dùng cùng normalized filter hash và metric version.
- Không dùng content hash để tự xóa business duplicate; duplicate được xác định bởi source key và giữ lineage.

## 10. Pilot acceptance criteria

### AC-000-01 — Happy path end-to-end

**Given** CSV v1 gồm 100 dòng hợp lệ và user có project scope<br>
**When** user upload, validate và execute job<br>
**Then** có 100 source records, feedback, feedback items, source-trusted decisions/current projections; dashboard item volume là 100 và drill-down trả đúng 100 distinct item.

### AC-000-02 — Count reconciliation

**Given** file có 80 valid, 10 invalid và 10 duplicate rows<br>
**When** validation và partial execute hoàn tất<br>
**Then** count thỏa `100=80+10+10`, `committed=80`, error output có 20 row outcomes và canonical count chỉ tăng 80.

### AC-000-03 — Retry/idempotency

**Given** execute response timeout sau khi worker đã commit<br>
**When** client retry cùng idempotency key và worker nhận duplicate delivery<br>
**Then** logical job/result cũ được trả, không tăng canonical/decision count và audit cho biết retry outcome.

### AC-000-04 — Trusted mapping safety

**Given** row có Issue không thuộc Service hoặc code không nằm trong pinned release<br>
**When** validate<br>
**Then** row `INVALID` với stable safe error code; không có accepted decision và không tự sửa code.

### AC-000-05 — Dashboard consistency

**Given** job đã commit và analytics freshness budget đã qua<br>
**When** user filter date/project/service/issue/location/sentiment/severity rồi click một segment<br>
**Then** KPI, chart và list dùng cùng filter context; aggregate count bằng distinct item trong drill-down.

### AC-000-06 — Authorization/privacy

**Given** user không có pilot project scope<br>
**When** truy cập job, dashboard hoặc item detail bằng ID đã biết<br>
**Then** server không trả dữ liệu; denial được ghi an toàn và mọi telemetry không chứa file/content/PII.

### AC-000-07 — Failure recovery

**Given** worker chết giữa hai chunks<br>
**When** job được retry sau restart<br>
**Then** committed chunk không lặp, phần còn lại tiếp tục, state/count cuối đúng và có correlation xuyên suốt.

### AC-000-08 — Performance

**Given** staging có 100.000 feedback items và file có 10.000 rows<br>
**When** chạy query mix/ingestion benchmark đã chốt<br>
**Then** dashboard p95 dưới 2 giây, import hoàn tất dưới 5 phút, không request HTTP dài chờ worker và không có mismatch.

## 11. Shared telemetry và reconciliation

Correlation tối thiểu:

```text
correlation_id, request_id, actor_id, project_id,
job_id, import_row_id, source_record_id,
feedback_id, feedback_item_id, taxonomy_release_id,
location_release_id, metric_definition_version
```

Release dashboard tối thiểu:

- Job count/duration/state, row outcomes, retry, queue lag và terminal failures.
- Source → feedback → item → current decision → analytics eligible count.
- Dashboard API latency/error/denied rate và reconciliation mismatch.
- Frontend load/error/empty/drill-down outcome không kèm filter value nhạy cảm.

Mỗi mismatch khác 0 phải có sample ID an toàn, owner và runbook; không log payload để debug.

## 12. Kế hoạch một tuần

| Ngày | Gate bắt buộc |
| --- | --- |
| Ngày 1 | Freeze CSV/OpenAPI/filter contract; FEAT-01 migration, seed validator và shared package merge `dev`; các team rebase. |
| Ngày 2 | FEAT-02 validate/preview; FEAT-03 query skeleton; FEAT-04 import/dashboard bằng contract mock. |
| Ngày 3 | Import execute/idempotency; analytics/drill-down integration; UI nối API. |
| Ngày 4 | Full E2E, authorization/privacy, resilience, reconciliation và representative performance test. |
| Ngày 5 | Fix P0/P1, deploy staging flags off, smoke test, UAT, enable pilot scope và lưu release evidence. |

Nếu FEAT-01 chưa merge hết ngày 1 hoặc CSV/source-trust/seed chưa được duyệt, giảm cam kết thành synthetic demo; không bỏ validation, idempotency, authorization hoặc reconciliation để giữ lịch.

## 13. Definition of Ready

- [ ] Product Owner ký scope/non-goal, một project và danh sách tối đa ba Service.
- [ ] Data Steward cung cấp taxonomy/location release đã publish, checksum và mapping sample.
- [ ] Source owner ký `pilot-csv-v1`: labels là trusted, dữ liệu đã mask và source reference ổn định.
- [ ] Có bốn fixture: valid, invalid mapping, duplicate và 10.000-row performance; không có PII thật.
- [ ] Actor/permission/project-scope matrix và staging test accounts sẵn sàng.
- [ ] PostgreSQL, source-file store và staging runtime đã được cấp; secret không đi vào repository.
- [ ] Metric v1, timezone/filter boundary và expected dashboard wireframe được duyệt.
- [ ] Branch owner, reviewer, merge order và daily integration window được gán tên.
- [ ] Không còn decision có thể đổi CSV header, unique key, canonical chain hoặc metric unit.

## 14. Definition of Done

- [ ] Mọi child feature đạt DoD riêng và DoD chung trong Build Rules.
- [ ] AC-000-01 đến AC-000-08 có automated test/evidence liên kết trong release record.
- [ ] Fresh database migrate + seed + validate được bằng một documented command; rollback app không phá schema.
- [ ] OpenAPI/generated client và runtime không drift; contract compatibility gate pass.
- [ ] E2E chạy trên build artifact, không chỉ dev server hoặc mock.
- [ ] Authorization/privacy/security scan pass; logs/traces được kiểm tra không có content/PII/secret.
- [ ] Representative import/performance và source-to-dashboard reconciliation pass với mismatch bằng 0.
- [ ] Feature flags, owner dashboard, alerts, runbook, stop criteria và forward-fix procedure sẵn sàng.
- [ ] Product Owner và Data Steward chấp nhận staging outcome; không còn defect P0/P1 trong scope.

## 15. Rollout và rollback

Flags tối thiểu:

```text
trusted_csv_import
trusted_csv_analytics_api
trusted_csv_dashboard
```

Deploy schema expand và code với flags off; seed/validate reference releases; chạy synthetic E2E; bật tuần tự cho internal admin rồi pilot project. Dừng rollout khi có unauthorized access, PII exposure, canonical duplicate, count mismatch, terminal job failure không retry được hoặc p95 vượt PRD budget liên tục.

Rollback bằng flag và pause worker ở chunk boundary. Application rollback phải tương thích expanded schema. Không xóa job/source/feedback/decision/audit đã ghi; sửa projection bằng rebuild và sửa dữ liệu bằng forward-fix có audit.

## 16. Open decisions

Các quyết định này phải đóng trước `Ready for build`:

- Project/location codes, tối đa ba Service và danh sách Issue mapping tương ứng — **Owner:** Data Steward.
- Ai phê duyệt source-trust policy và thời hạn hiệu lực — **Owner:** Product + Governance.
- Source-file retention và quyền tải lại file — **Owner:** Security + Data Owner.
- Staging identity provider và exact project-scope claims — **Owner:** Platform/Security.
- Hạ tầng PostgreSQL/source-file store và performance shape — **Owner:** Tech Lead.
