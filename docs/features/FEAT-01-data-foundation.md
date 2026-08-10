# FEAT-01 — Platform & Data Foundation

- **Status:** Ready for refinement
- **Priority:** P0 — integration gate ngày 1
- **Owner:** Platform/Data Engineer
- **Branch:** `codex/feat-data-foundation`
- **Merge target:** `dev`
- **Bounded contexts:** Shared Kernel, Taxonomy & Location, Feedback Intake, Classification & Review
- **Related:** [FEAT-00](./FEAT-00-trusted-csv-to-dashboard-pilot.md), [Build Rules](../BUILD_RULES.md), [ADR-002](../architecture/adr/ADR-002-classification-model.md)

## 1. Outcome

Team có một Python monorepo chạy được, app shells/API actor context thống nhất, một canonical PostgreSQL schema có migration/constraint/repository, và một pilot reference seed có validator. FEAT-02/03/04 có thể build song song trên public contracts mà không tự tạo app bootstrap, entity, enum hoặc database access riêng.

PR này là dependency đầu tiên phải merge vào `dev`. Nó tạo nền, không tạo upload endpoint, analytics endpoint hay dashboard.

## 2. Stack được khóa

| Concern | Baseline |
| --- | --- |
| Runtime | Python 3.12+; pin exact patch trong container image. |
| Dependency manager | Poetry hoặc pip-tools; commit lockfile (`poetry.lock` hoặc `requirements.txt`). |
| Language | Python với type hints; mypy `strict` mode; không `Any` không có justification. |
| Validation | Pydantic v2; models là nguồn cho runtime validation và OpenAPI schema. |
| Database | PostgreSQL 16 current minor; SQLAlchemy 2.0 + Alembic migrations. |
| API/runtime consumers | FastAPI 0.110+ API; worker là Python process. FEAT-01 chỉ cung cấp foundation/wiring contract. |
| Test | pytest cho unit/integration; PostgreSQL thật trong integration test, không mock SQL semantics. |

Không tự nâng major trong feature branch. Security/bugfix patch được cập nhật qua lockfile/image có CI evidence.

## 3. Scope

### In scope

- Root workspace scaffold, scripts và Python/lint/test conventions.
- API/worker/web app shells, configuration boundary, health wiring, HTTP problem handler và minimal authentication adapter tạo `ActorContext` cho module.
- Common IDs, time, error/problem, actor/scope và reference-release contracts.
- Pure domain invariants cho import state, trusted source classification và immutable feedback chain.
- PostgreSQL client, schema, migrations, indexes, repositories và unit-of-work transaction.
- Pilot project/location/taxonomy/source-trust seed machine-readable, checksum và validator.
- DB integration tests, architecture dependency tests và migration smoke test.
- Health/readiness primitives và structured telemetry ports; không chứa content.

### Out of scope

- HTTP route, multipart parsing, source-file adapter hoặc worker polling loop của import.
- Analytics/filter/query endpoint và frontend.
- Custom enterprise SSO provisioning/admin, taxonomy editor, AI/manual classification hoặc production provisioning. Staging issuer/client/secrets do FEAT-05 cấu hình trên adapter đã có.
- Full taxonomy import từ Markdown. Pilot seed chỉ chứa subset đã ký cho FEAT-00.

## 4. Exclusive code ownership

FEAT-01 được phép tạo/sửa:

```text
pyproject.toml
poetry.lock / requirements.txt
pytest.ini
mypy.ini
.pylintrc
apps/api/pyproject.toml
apps/api/src/app.py
apps/api/src/main.py
apps/api/src/platform/**
apps/worker/pyproject.toml
apps/worker/src/worker.py
apps/worker/src/platform/**
apps/web/package.json
apps/web/pyproject.toml
apps/web/vite.config.py
apps/web/src/main.pyx
apps/web/src/app/**
apps/web/src/client/index.py
packages/contracts/pyproject.toml
packages/contracts/src/common/**
packages/contracts/src/reference_data/**
packages/domain/**
packages/db/**
```
prettier.config.mjs
pytest.ini
.env.example
apps/api/pyproject.toml
apps/api/pyproject.toml
apps/api/src/app.py
apps/api/src/server.py
apps/api/src/platform/**
apps/worker/pyproject.toml
apps/worker/pyproject.toml
apps/worker/src/worker.py
apps/worker/src/platform/**
apps/web/package.json
apps/web/pyproject.toml
apps/web/vite.config.py
apps/web/src/main.pyx
apps/web/src/app/**
apps/web/src/client/index.py
packages/pyproject.toml
packages/contracts/pyproject.toml
packages/contracts/src/common/**
packages/contracts/src/reference-data/**
packages/domain/**
packages/db/**
```

Public package exports dùng subpath wildcard, ví dụ `@cx/contracts/import`, `@cx/contracts/analytics`; không dùng một central barrel buộc mọi feature cùng sửa. FEAT-01 sở hữu package config, `common` và `reference-data`; FEAT-02/030 sở hữu folder contract riêng theo feature spec.

Không tạo file trong `apps/api/src/modules/**`, `apps/worker/src/modules/**`, `apps/web/src/features/**`, `apps/web/src/client/generated/**`, `apps/web/src/mocks/**` hoặc `packages/test-fixtures/**`. Root script và cả ba app shell phải hoạt động khi workspace được cài fresh.

Authentication baseline validate token/session từ issuer được cấu hình và tạo `ActorContext` gồm actor, permissions, project scopes và correlation ID. Test adapter chỉ được bật khi `APP_ENV=test`; staging/production phải fail closed nếu issuer hoặc key validation thiếu/sai. FEAT-01 không tự provision identity provider hoặc hard-code pilot user.

## 5. Dependency rules

```text
packages/contracts  ← packages/domain
        ↑                    ↑
        └──────── packages/db
                             ↑
                         apps/* wiring
```

- `contracts` chỉ phụ thuộc Pydantic và platform-neutral libs.
- `domain` không biết database hoặc HTTP; chỉ invariant logic.
- `db` biết SQLAlchemy models, repositories và migrations; dùng domain types.
- `apps/*` wire platform (FastAPI/worker runtime) với domain/db; không chứa business logic.

FEAT-01 không được tạo import business endpoint, analytics query hoặc UI component; chúng thuộc FEAT-02/03/04.

Authentication baseline validate token/session từ issuer được cấu hình và tạo `ActorContext` gồm actor, permissions, project scopes và correlation ID. Test adapter chỉ được bật khi `APP_ENV=test`; staging/production phải fail closed nếu issuer hoặc key validation thiếu/sai. FEAT-01 không tự provision identity provider hoặc hard-code pilot user.
```

- `contracts` không import domain, DB hoặc app.
- `domain` chỉ import common/reference contract và không import SQLAlchemy/PostgreSQL/FastAPI.
- `db` implement domain repository ports; SQL/SQLAlchemy type không rò ra public domain interface.
- App module gọi use case/repository public API; không query table trực tiếp.
- Không circular dependency; CI architecture test kiểm tra import boundary.
- Clock, ID generator, transaction và actor context được inject để test deterministic.

## 6. Shared contract

### Identity, time và error

- Entity ID là UUIDv7 tạo ở application boundary, lưu PostgreSQL `uuid`.
- Timestamp contract là ISO-8601 UTC; DB dùng `timestamptz`; test dùng fixed clock.
- Business code là case-sensitive stable string, không tái sử dụng.
- Request principal tối thiểu: `actor_id`, `permissions[]`, `project_ids[]`, `correlation_id`.
- Problem response foundation: `code`, `message`, `correlation_id`, optional `field_errors[]` gồm `path`, `code`, `message` an toàn.

Stable common enums:

```text
ValueStatus       = KNOWN | UNKNOWN | MISSING | NOT_APPLICABLE
DecisionSource    = MANUAL | SOURCE_TRUSTED | HUMAN_ACCEPTED_AI |
                    HUMAN_CORRECTED_AI | POLICY_AUTO_APPLIED |
                    SYSTEM_MIGRATION
Sentiment         = POSITIVE | NEUTRAL | NEGATIVE | MIXED | UNKNOWN
Severity          = SEV-1 | SEV-2 | SEV-3 | SEV-4
ImportJobState    = UPLOADED | MAPPED | VALIDATING | VALIDATED |
                    QUEUED | PROCESSING | COMPLETED | PARTIAL |
                    FAILED | CANCELLED
ImportRowOutcome  = VALID | INVALID | DUPLICATE
```

Không thêm `UNKNOWN` giả vào bảng taxonomy. Reference field dùng `ValueStatus` và nullable ID theo ADR-002.

Schema/domain enum giữ đủ stable values của ADR-002 để không cần migration enum khi mở rộng. FEAT-00/020 chỉ được tạo `SOURCE_TRUSTED`; các writer cho value khác nằm ngoài pilot và không được expose trong API tuần đầu.

## 7. Database contract

Tên table/column dùng `snake_case`; mọi table có `created_at`; mutable operational table có `updated_at` và optimistic `version` khi có concurrent write.

| Table | Cột/constraint bắt buộc |
| --- | --- |
| `project` | `id`, unique `code`, `name`, `active`, timestamps. |
| `reference_release` | `id`, `kind=TAXONOMY|LOCATION|SOURCE_TRUST`, unique `(kind, version)`, `status=PUBLISHED`, `checksum_sha256`, `published_at`. |
| `location_node` | `id`, `release_id`, `project_id`, `code`, `name`, `node_type`, `parent_id`; unique `(release_id, project_id, code)`; parent cùng release/project. |
| `taxonomy_service` | `id`, `release_id`, `code`, `name`, `active`; unique `(release_id, code)`. |
| `taxonomy_issue` | `id`, `release_id`, `code`, `name`, `active`; unique `(release_id, code)`. |
| `taxonomy_service_issue` | `release_id`, `service_id`, `issue_id`, `active`; primary key ba cột; composite FK bảo đảm cùng release. |
| `source_trust_policy` | `id`, `release_id`, `source`, `project_id`, `allowed_contract_version`, `active_from`, `active_to`, `approved_by`, `approved_at`; unique `(release_id, source, project_id)` và không có effective interval chồng lấn cho cùng `(source, project_id, allowed_contract_version)`. |
| `import_job` | `id`, `actor_id`, `project_id`, `idempotency_key`, `contract_version`, pinned release IDs, `file_name`, `file_sha256`, `storage_key`, state/counts, safe failure fields, timestamps; unique `(actor_id, idempotency_key)`. |
| `import_row` | `id`, `import_job_id`, `row_number`, `row_checksum`, immutable `normalized_payload` JSONB, `outcome`, safe `errors` JSONB, duplicate/canonical refs; unique `(import_job_id, row_number)`. |
| `source_record` | `id`, `source`, `source_reference`, `import_job_id`, `import_row_id`, `payload_checksum`, timestamps; unique `(source, source_reference)` và unique `import_row_id`. |
| `feedback` | `id`, unique `source_record_id`, `reported_at`, `reported_offset`, `project_id`, `source_location_text`, `content_masked`, `content_raw=NULL`, `ingested_at`; immutable. |
| `feedback_item` | `id`, `feedback_id`, `item_index=1`, `item_text_masked`, `analytic_eligibility=INCLUDED`; unique `(feedback_id, item_index)`; immutable trong pilot. |
| `classification_decision` | `id`, `feedback_item_id`, `decision_version`, all companion statuses/IDs, sentiment, severity, release IDs, `decision_source`, policy ID, reason, actor/time; unique `(feedback_item_id, decision_version)`; append-only. |
| `classification_current` | PK `feedback_item_id`, unique `current_decision_id`, flattened current fields, `projection_version`, `last_decision_at`; rebuildable. |
| `outbox_event` | `id`, unique `dedupe_key`, `event_type`, `schema_version`, `aggregate_id`, payload JSONB không content, `occurred_at`, publish attempt/state fields. |
| `audit_event` | `id`, actor/action/entity refs, outcome, reason/code, correlation ID, timestamp; append-only và không copy payload/content. |

### Required database invariants

- Count columns của `import_job` không âm; terminal states có `completed_at`; state transition đi qua compare-and-set repository.
- `KNOWN` yêu cầu ID khác null; mọi status khác yêu cầu ID null bằng check constraint.
- Service/Issue/Location/Project phải resolve trong releases pin trên job/decision; mapping Service–Issue active.
- Trusted decision v1 có semantics đúng mục 5 của FEAT-00, `decision_version=1`, không có superseded decision.
- `source_record`, `feedback`, `feedback_item`, `classification_decision`, `audit_event` không expose update/delete repository. DB role của app không có hard-delete path; migration/admin role tách riêng.
- Một row commit là một DB transaction tạo source → feedback → item → decision → current → audit → outbox và cập nhật row/job count.
- Unique conflict do retry được đọc lại thành logical existing result; conflict khác trả typed domain error, không nuốt SQL error.

## 8. Repository/public port

`packages/domain` khai báo, `packages/db` implement tối thiểu:

```ts
ReferenceDataReader.resolveTrustedCodes(input)
ImportJobRepository.createOrGetByIdempotencyKey(input)
ImportJobRepository.compareAndSetState(input)
ImportJobRepository.saveValidationBatch(input)
TrustedFeedbackUnitOfWork.commitValidatedRow(input)
ImportJobRepository.reconcile(jobId)
TerminalImportOutcomeReader.summarize(input) // terminal COMPLETED|PARTIAL by project/completed_at/snapshot
ClassificationProjectionRepository.rebuild(itemIds)
OutboxRepository.claimBatch(input)
AuditRepository.append(input)
```

Mỗi public method nhận `correlation_id`/actor context cần thiết, trả domain type, và map lỗi sang stable code. Không trả SQLAlchemy row hoặc database connection cho app.

## 9. Pilot seed

Machine-readable source đặt tại:

```text
packages/db/seeds/pilot/project-location.v1.json
packages/db/seeds/pilot/taxonomy.v1.json
packages/db/seeds/pilot/source-trust-policy.v1.json
packages/db/seeds/pilot/validate-seed.py
```

Baseline tối thiểu gồm `PILOT_PROJECT`, location `S2`, taxonomy release `1.0.0`, Services `SVC-17`/`SVC-18`, Issues `ELV-01`/`ELV-02`/`ELV-06`/`PKG-01` và các mapping đúng Service active. `PKG-01` có trong seed để fixture chứng minh pair `SVC-17 + PKG-01` bị reject là `INVALID_SERVICE_ISSUE`, không phải `UNKNOWN_ISSUE`. Mở rộng Service/Issue chỉ bằng seed change được Data Steward ký.

Validator phải fail khi duplicate code/ID, parent location sai project/release, Issue không có Service, mapping inactive/missing, release chưa `PUBLISHED`, checksum sai hoặc source-trust contract không phải `trusted-feedback-csv/v1`. Seed chạy idempotent và không update meaning của release đã publish.

## 10. Acceptance criteria

### AC-010-01 — Fresh setup

**Given** clean checkout và PostgreSQL 16 trống<br>
**When** chạy documented install, migrate, seed và verify commands<br>
**Then** workspace build được, schema/constraints/indexes tồn tại và seed checksum pass mà không thao tác tay.

### AC-010-02 — Contract boundary

**Given** package graph<br>
**When** CI chạy typecheck/architecture test<br>
**Then** không có circular/import ngược, app có thể import public subpaths và không cần import source nội bộ.

### AC-010-03 — Reference integrity

**Given** valid và tampered seed fixtures<br>
**When** seed validator chạy<br>
**Then** valid fixture idempotent; tampered mapping/checksum/release bị reject bằng stable safe error.

### AC-010-04 — Atomic trusted row

**Given** một normalized valid row và pinned releases<br>
**When** `commitValidatedRow` thành công<br>
**Then** toàn canonical chain/outbox/audit được tạo một lần trong một transaction với đúng SOURCE_TRUSTED semantics.

### AC-010-05 — Failure/idempotency

**Given** transaction fail ở bất kỳ write hoặc cùng row được gọi lại<br>
**When** unit-of-work rollback/retry<br>
**Then** không có partial chain; retry trả logical record cũ và canonical counts không tăng.

### AC-010-06 — Immutable history

**Given** source/feedback/decision đã commit<br>
**When** app repository cố update/delete hoặc stale state transition<br>
**Then** operation không tồn tại hoặc bị reject; current projection có thể xóa/rebuild mà history không đổi.

### AC-010-07 — App shell và actor context

**Given** web/API/worker build từ clean checkout và request có token hợp lệ/không hợp lệ<br>
**When** chạy health/auth smoke<br>
**Then** ba app start được; API tạo đúng scoped `ActorContext` cho token hợp lệ, fail closed cho token lỗi và không cho test adapter chạy ngoài `APP_ENV=test`.

## 11. Test và CI

| Layer | Gate |
| --- | --- |
| Unit | Value objects, state transitions, status/ID invariants, mapping validation, typed error mapping. |
| Database integration | Fresh migration, constraints/FK/unique, atomic rollback, concurrent idempotency, projection rebuild, outbox claim. |
| Seed | Golden checksum, invalid reference/mapping/release, idempotent rerun. |
| Architecture | Dependency direction, public exports, forbidden app/DB imports. |
| Compatibility | Migration up từ supported baseline; app rollback tương thích expanded schema. |

Root commands phải có ít nhất `pip lint`, `pip typecheck`, `pip test`, `pip db:migrate`, `pip db:seed`, `pip db:verify`. CI dùng `pip install -r requirements.txt`.

## 12. Telemetry

- Migration/seed log chỉ gồm migration/release/checksum/outcome/duration; không log seed payload tự do.
- DB operations trace bằng `correlation_id`, operation name và duration; không ghi SQL bindings có content.
- Metrics tối thiểu: DB pool saturation/query errors, migration/seed outcome, outbox unpublished count/oldest age, transaction conflict và reconciliation mismatch.
- Readiness fail khi DB unavailable hoặc migrations chưa đạt expected version; seed/reference validation failure chặn pilot enable, không nhất thiết làm API process crash.

## 13. DoR

- [ ] Stack/boundary/table contract được Tech Lead và owners FEAT-02/030 review.
- [ ] Pilot project/location/Service/Issue codes và source-trust approver được cung cấp.
- [ ] PostgreSQL 16 integration environment và CI service sẵn sàng.
- [ ] Migration naming/deploy command và application DB role policy được chốt.
- [ ] Không còn open decision đổi ID, unique source key hoặc canonical transaction boundary.

## 14. DoD và handoff

- [ ] AC-010-01 đến AC-010-07 pass; lint/typecheck/unit/integration/architecture gates xanh.
- [ ] Fresh DB và upgrade smoke test pass; down/reset không được dùng làm production rollback.
- [ ] Seed checksum/validator pass và được Data Steward sign off.
- [ ] Public contract/repository examples đủ để FEAT-02/030 dùng mà không đọc DB table trực tiếp.
- [ ] Không có content/PII/secret trong log, fixture hoặc telemetry snapshot.
- [ ] Merge `dev`, owners FEAT-02/030/040 được thông báo commit SHA và rebase thành công.

Rollback code về commit trước chỉ khi version trước tương thích expanded schema. Migration đã áp dụng được giữ lại; correction bằng forward migration. Không drop canonical/history table trong rollback.
