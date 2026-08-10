# FEAT-02 — Trusted CSV Import

- **Status:** Ready for refinement
- **Priority:** P0 — one-week staging MVP
- **Owner:** Backend/Data Engineer
- **Branch:** `codex/feat-csv-import`
- **Merge target:** `dev`, sau FEAT-01
- **Bounded context:** Feedback Intake
- **Related:** [FEAT-00](./FEAT-00-trusted-csv-to-dashboard-pilot.md), [FEAT-01](./FEAT-01-data-foundation.md), [Build Rules](../BUILD_RULES.md)

## 1. Outcome

CX Analyst có thể upload CSV `trusted-feedback-csv/v1`, validate và xem lỗi trước khi ghi canonical data, sau đó execute/retry một job bất đồng bộ. Mọi row có lineage, count đối soát được và retry không tạo duplicate.

Feature kết thúc ở canonical records + outbox event. Nó không build dashboard, analytics query hoặc manual classification.

## 2. Scope

### In scope

- Multipart CSV upload bằng streaming, file checksum, safe object-storage key và idempotent job create.
- Exact-header mapping, CSV parse/normalize, schema/reference validation và preview counts.
- Duplicate detection trong file, với canonical source key đã tồn tại và khi concurrent execute.
- Execute valid rows theo chunk, atomic canonical transaction, progress, retry và final reconciliation.
- Job/detail/error API, project-scoped authorization, audit và telemetry.
- JSON error pagination và downloadable safe CSV error report.
- Contract, unit, DB integration, worker resilience và import E2E tests.

### Out of scope

- XLSX, custom delimiter/header mapping, manual row edit, raw PII masking hoặc virus/content classification.
- Synchronous import, multi-file job, scheduled import hoặc generic connector framework.
- Update/delete feedback, manual decision, dashboard/analytics API hoặc export canonical dataset.
- Database schema/repository internals; thay đổi schema phải do FEAT-01 owner review và thực hiện.

## 3. Exclusive code ownership

FEAT-02 chỉ tạo/sửa product code tại:

```text
apps/api/src/modules/imports/**
apps/worker/src/modules/imports/**
packages/contracts/src/import/**
packages/test-fixtures/import/**
```

Suggested layout:

```text
packages/contracts/src/import/
  csv_v1.py
  import_job.py
  import_errors.py
  __init__.py

apps/api/src/modules/imports/
  routes.py
  handlers.py
  authorization.py
  source_file_store.py
  __init__.py

apps/worker/src/modules/imports/
  validate_job.py
  execute_job.py
  retry_policy.py
  worker_loop.py
  __init__.py

packages/test_fixtures/import/
  valid.csv
  invalid.csv
  duplicate.csv
  boundary/
```

Integration seams được phép sửa tối thiểu:

```text
apps/api/src/app.py          # chỉ register import router
apps/worker/src/worker.py    # chỉ register import worker module
```

Registration nằm trong commit riêng và cần FEAT-01 owner review để giảm conflict khi rebase.

Không sửa root config, `packages/domain/**`, `packages/db/**`, analytics/feedback routes hoặc web. Nếu public foundation thiếu capability, mở contract change cho FEAT-01 owner; không query SQLAlchemy table trực tiếp từ app module.

## 4. Preconditions và dependency

- FEAT-01 đã merge `dev`; branch này rebase lên commit đó trước code integration.
- `trusted-feedback-csv/v1`, pilot project/reference releases và source-trust policy đã ký.
- API có authenticated `ActorContext`; permission baseline là `imports:write`/`imports:read` và project scope.
- Source-file store cung cấp streaming put/get/delete-temp, server-side encryption và private key; API không trả storage key.
- Worker có cùng database, source store và secret config; queue có thể là DB-backed claim trong MVP.

## 5. CSV contract và normalization

FEAT-02 import nguyên văn contract mục 4 của FEAT-00 bằng `cx_contracts.import_pkg.csv_v1`; không copy schema vào handler/worker.

Exact header:

```text
source_reference,reported_at,project_code,location_code,service_code,issue_code,sentiment,operational_severity,content_masked
```

Normalization trước checksum/validation:

1. Strip một UTF-8 BOM; reject invalid UTF-8, NUL byte hoặc malformed CSV.
2. Header phải exact order; reject thiếu/thừa/duplicate column.
3. Bỏ duy nhất terminal empty row; row trống giữa file là `INVALID`.
4. Trim ASCII whitespace ở scalar trừ `content_masked`; không uppercase/sửa code.
5. Parse `reported_at` có offset, lưu UTC và offset gốc; reject timestamp không offset/không tồn tại.
6. Normalize CRLF bên trong `content_masked` thành LF; giữ các character còn lại sau CSV unescape.
7. Tạo canonical row JSON theo header order và SHA-256 `row_checksum`; không đưa payload vào log/error message.

Giới hạn được enforce trước và trong stream: `.csv`, MIME allowlist, 10 MiB, 10.000 data rows và 4.000 Unicode code points cho content. File vượt giới hạn dừng stream, xóa temp object theo runbook và không tạo validation row.

## 6. Validation và row outcome

Validation chạy theo batch tối đa 500 rows, pin releases đã lưu trên job và ghi đúng một `import_row` mỗi data row.

Thứ tự rule:

1. Required/type/length/enum/time validation.
2. Tất cả `project_code` phải bằng project của job và actor có scope.
3. Location resolve trong pinned location release và thuộc project.
4. Service/Issue resolve active trong pinned taxonomy release; mapping pair active.
5. Nếu còn hợp lệ, duplicate check theo `(source=PILOT_CSV_V1, source_reference)`.

Outcome precedence: row có schema/reference error là `INVALID`; nếu không invalid nhưng key lặp trong file hoặc đã canonical là `DUPLICATE`; còn lại là `VALID`. Với duplicate trong cùng file, row number nhỏ nhất là candidate valid và các row sau trỏ về row đầu. Không dựa vào content hash để loại record.

Stable error codes tối thiểu:

```text
INVALID_ENCODING, INVALID_CSV_SYNTAX, INVALID_HEADER,
FILE_TOO_LARGE, ROW_LIMIT_EXCEEDED, REQUIRED_FIELD,
INVALID_FORMAT, VALUE_TOO_LONG, INVALID_TIMESTAMP,
PROJECT_SCOPE_MISMATCH, UNKNOWN_PROJECT, UNKNOWN_LOCATION,
UNKNOWN_SERVICE, UNKNOWN_ISSUE, INVALID_SERVICE_ISSUE,
INVALID_SENTIMENT, INVALID_SEVERITY,
DUPLICATE_IN_FILE, DUPLICATE_SOURCE_REFERENCE
```

Error item chỉ gồm `row_number`, optional `column`, `code`, safe message và duplicate reference an toàn; không echo `content_masked`.

## 7. Job state machine

```text
UPLOADED
→ MAPPED
→ VALIDATING
→ VALIDATED
→ QUEUED
→ PROCESSING
→ COMPLETED | PARTIAL | FAILED | CANCELLED
```

- Create stream thành công tạo `UPLOADED`; exact header mapping tự động chuyển `MAPPED`. File-level lỗi chuyển `FAILED` với `retryable=false`.
- Validate chỉ từ `MAPPED`; compare-and-set sang `VALIDATING`. Row errors vẫn kết thúc `VALIDATED`; parser/storage/system failure kết thúc `FAILED`.
- Execute chỉ từ `VALIDATED` khi `valid_rows>0`; chuyển `QUEUED`, worker claim sang `PROCESSING`.
- `COMPLETED` khi mọi final `VALID` row committed, kể cả khi có duplicate skips và không có invalid row.
- `PARTIAL` trong contract v1 chỉ khi mọi final `VALID` row đã committed nhưng job có ít nhất một `INVALID` row; data error không retryable và job không còn row chờ xử lý.
- Retryable execution/system failure, kể cả sau khi một số chunk đã committed, kết thúc `FAILED` và giữ persisted progress; retry chỉ chạy final `VALID` row chưa có canonical reference.
- Nếu không có valid row, execute trả `422 NO_VALID_ROWS`; job giữ `VALIDATED` để user xem lỗi.
- `CANCELLED` trong pilot chỉ được phép trước `PROCESSING` (`UPLOADED|MAPPED|VALIDATED|QUEUED`). Sau khi worker claim `PROCESSING`, job phải hoàn tất hoặc chuyển `FAILED` retryable; không cancel sau canonical commit đầu tiên.
- Retry chỉ cho `FAILED` có `retryable=true`; validation/data error và `PARTIAL` yêu cầu file mới nếu user muốn sửa row, không retry mù.
- Retry validation thực hiện compare-and-set `FAILED → VALIDATING`; retry execution thực hiện `FAILED → QUEUED`. Mỗi retry tăng attempt/version, giữ cùng job/file/releases và không reset row/canonical record đã hoàn tất.

Worker claim dùng repository compare-and-set/lease. Lease expiry cho phép reclaim; duplicate delivery phải an toàn. Chunk size mặc định 200, config bounded 50–500.

## 8. Idempotency, concurrency và counts

- `POST import-jobs` yêu cầu `Idempotency-Key` 16–128 characters. Cùng actor/key và cùng file SHA trả job cũ; cùng key khác SHA trả `409 IDEMPOTENCY_KEY_REUSED`.
- Validate/execute/retry command yêu cầu `expected_version`; stale command trả `409 JOB_VERSION_CONFLICT` với current safe state/version.
- Repeated command ở state đã đạt trả current job, không enqueue duplicate work.
- Canonical transaction do FEAT-01 cung cấp quyết định unique `(source, source_reference)`.
- Nếu một key trở thành duplicate sau preview do concurrent job, execute atomically đổi row `VALID→DUPLICATE`, giảm `valid_rows`, tăng `duplicate_rows` và tăng `counts_revision`; final count là authoritative.
- Sau successful terminal `COMPLETED|PARTIAL`: `total=valid+invalid+duplicate`, `committed=valid`, và canonical lineage count của job bằng `committed`. `FAILED|CANCELLED` giữ progress/count thực tế nhưng không được dùng cho dashboard reconciliation.
- Progress/count lấy từ persisted state, không giữ chỉ trong memory.

## 9. API contract

Mọi endpoint dưới `/api/v1`, trả `correlation_id`, enforce project scope server-side và dùng problem schema chung.

```http
POST /api/v1/import-jobs
GET  /api/v1/import-jobs/{job_id}
POST /api/v1/import-jobs/{job_id}/validate
POST /api/v1/import-jobs/{job_id}/execute
POST /api/v1/import-jobs/{job_id}/retry
GET  /api/v1/import-jobs/{job_id}/errors
```

### Create

`POST` là `multipart/form-data` gồm `project_code` và `file`; header `Idempotency-Key` bắt buộc. Response `202`:

```json
{
  "data": {
    "job_id": "uuid",
    "state": "MAPPED",
    "version": 2,
    "contract_version": "trusted-feedback-csv/v1",
    "file_sha256": "hex",
    "counts": null
  },
  "correlation_id": "uuid"
}
```

Không trả original path, storage key, signed URL hoặc file content.

### Commands và query

- Validate body: `{ "expected_version": 2 }`; trả `202` current job.
- Execute body: `{ "expected_version": 4, "commit_policy": "VALID_ROWS_ONLY" }`; đây là policy duy nhất v1.
- Retry body: `{ "expected_version": 7, "phase": "VALIDATION" | "EXECUTION" }`; chỉ hợp lệ với job `FAILED` retryable đúng phase.
- GET job trả state/version, pinned contract/release versions, counts, progress, safe failure, retryability và timestamps.
- GET errors hỗ trợ `format=json|csv`; JSON dùng cursor, stable sort `row_number ASC, column ASC`, max page 200. CSV luôn thêm `'=`, `'+`, `'-`, `'@` escape cho formula-leading cells và không có content column.
- `404` dùng cho ID ngoài scope để không lộ existence; `403` cho action trên resource trong scope nhưng thiếu permission theo policy.

OpenAPI/Pydantic schema được export từ `packages/contracts/src/import`; handler không định nghĩa inline DTO khác contract.

## 10. End-to-end implementation flow

1. API authorize project, stream file qua size/hash guard vào private store và create-or-get job.
2. Header probe exact; lưu sanitized display filename, checksum/storage key; emit audit `IMPORT_UPLOADED`.
3. Validate command CAS state và tạo work claim. Worker stream file, parse/normalize, batch resolve reference data và persist row results.
4. Worker reconcile counts, chuyển `VALIDATED`, emit audit/metrics; không tạo canonical record.
5. Execute worker claim job, đọc `VALID` rows theo row number, gọi `commitValidatedRow` từng chunk.
6. Sau mỗi chunk persist progress/lease. Retry đọc row chưa có canonical reference; không lặp row đã commit.
7. Reconcile persisted row/canonical counts, set terminal state và emit audit/outbox operational event không có content.
8. API error report đọc persisted outcomes; không parse lại file để tránh drift.

## 11. Acceptance criteria

### AC-020-01 — Upload an toàn

**Given** authorized Analyst và valid CSV<br>
**When** upload với idempotency key<br>
**Then** file được stream/checksum, job đạt `MAPPED`, release versions được pin và response/log không lộ storage/content.

### AC-020-02 — Preview không ghi canonical

**Given** file có valid/invalid/duplicate rows<br>
**When** validation hoàn tất<br>
**Then** job `VALIDATED`, count/error đúng từng row và số source/feedback/item/decision mới bằng 0.

### AC-020-03 — Exact contract validation

**Given** wrong header, timestamp thiếu offset, unknown code và invalid Service–Issue pair<br>
**When** validate<br>
**Then** file/rows bị reject bằng stable error tương ứng; system không sửa dữ liệu âm thầm.

### AC-020-04 — Atomic execute

**Given** 80 valid, 10 invalid, 10 duplicate<br>
**When** execute `VALID_ROWS_ONLY`<br>
**Then** 80 complete canonical chains được tạo, job `PARTIAL`, count reconcile và mỗi chain truy ngược job/row được.

### AC-020-05 — Idempotent retry

**Given** response timeout, duplicate worker delivery hoặc process chết giữa chunks<br>
**When** command/job được retry<br>
**Then** không tăng canonical count cho row đã commit, phần còn lại tiếp tục và terminal counts đúng.

### AC-020-06 — Concurrent duplicate

**Given** hai jobs preview cùng source key là valid<br>
**When** execute đồng thời<br>
**Then** chỉ một canonical chain tồn tại; job còn lại chuyển row thành duplicate và final counts revision phản ánh thay đổi.

### AC-020-07 — Authorization

**Given** actor thiếu permission hoặc project scope<br>
**When** create/read/command/error download bằng ID biết trước<br>
**Then** request bị từ chối không lộ data; không có work được enqueue và denial được audit an toàn.

### AC-020-08 — Boundary/performance

**Given** 10.000-row/10-MiB boundary fixture và over-limit fixtures<br>
**When** xử lý trên staging shape<br>
**Then** boundary job hoàn tất dưới 5 phút; over-limit dừng sớm, cleanup được quan sát và API không giữ connection chờ worker.

## 12. Test strategy

| Layer | Cases bắt buộc |
| --- | --- |
| Unit | BOM/UTF-8/RFC4180, normalization/checksum, exact header, timestamp/enum/length, state/retry rules, safe CSV escaping. |
| Contract | Multipart, all job responses, error pagination, `400/403/404/409/422`, OpenAPI examples và generated consumer compatibility. |
| DB integration | Batch persistence, CAS/lease, unique source key, atomic row commit, count reconciliation, concurrent execute. |
| Worker resilience | Crash before/after commit, lease expiry, duplicate delivery, storage timeout, DB timeout và retry exhaustion. |
| Authorization/privacy | Role/project matrix, guessed IDs, logs/traces/error files không có content/PII/storage key. |
| E2E | Upload → validate → error download → execute → terminal lineage; duplicate upload/retry. |
| Performance | 10.000 rows, mixed 80/10/10, 100% duplicate và max content length. |

Fixture phải synthetic, stable và không có PII thật. Large fixture được generate deterministically trong test, không commit file khổng lồ.

## 13. Telemetry và operations

Structured fields:

```text
correlation_id, request_id, actor_id, project_id, job_id,
state_from, state_to, row_number, outcome, safe_error_code,
retryable, attempt, lease_id, duration_ms
```

Không log filename nguyên bản nếu policy coi nhạy cảm, payload, `content_masked`, source reference raw, SQL binding hoặc storage key.

Metrics tối thiểu:

- `import_jobs_total{state,phase,outcome}` và `import_job_duration_seconds{phase}`.
- `import_rows_total{outcome,error_code}` nhưng không label theo project/source reference.
- `import_worker_queue_depth`, lease age, retries, retry exhausted và cleanup failures.
- `import_reconciliation_mismatch_total` và concurrent duplicate count.

Alert terminal system failure/retry exhausted, queue oldest age vượt 2 phút trong pilot, cleanup failure và bất kỳ reconciliation mismatch nào. Mỗi alert link runbook FEAT-05 và có owner.

## 14. Rollout, rollback và DoR

Flag: `trusted_csv_import`, default off. Deploy sau FEAT-01 migration/seed, smoke bằng synthetic file, bật internal role rồi pilot project. Stop khi có unauthorized access, content/PII leak, duplicate canonical, mismatch hoặc repeated terminal failure.

Rollback: tắt flag, ngừng nhận command mới, pause worker ở chunk boundary; không xóa committed history. Resume/retry sau forward-fix; application rollback chỉ về version tương thích schema/job states.

DoR bổ sung:

- [ ] FEAT-01 public repositories/contracts đã merge và owner xác nhận không còn schema gap.
- [ ] CSV golden/negative/boundary fixtures và expected outcomes được Data Steward duyệt.
- [ ] Source-file retention/cleanup, auth permissions và source-trust approval đã chốt.
- [ ] Max file/row, chunk/lease/retry budgets và staging volume sẵn sàng test.
- [ ] OpenAPI/error codes được FEAT-04/050 owners review.

## 15. Feature-specific DoD

- [ ] AC-020-01 đến AC-020-08 pass và map tới automated test/evidence.
- [ ] Lint/typecheck/unit/contract/DB integration/E2E/security/performance gates xanh.
- [ ] Không có direct DB query ngoài FEAT-01 repositories và không có schema change trong PR.
- [ ] Retry/crash/concurrent duplicate chứng minh canonical count không tăng sai.
- [ ] Error CSV an toàn với spreadsheet formula; log/trace snapshot không có content/PII/secret.
- [ ] OpenAPI/generated client published trong workspace; FEAT-04 consumer contract pass.
- [ ] Metrics/alerts/runbook hooks chạy trên staging; source → canonical reconciliation mismatch bằng 0.
- [ ] PR merge `dev` sau rebase, không sửa path owner của feature khác.
