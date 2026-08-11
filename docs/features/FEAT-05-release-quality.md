


# FEAT-05 — Release Quality, Staging và Rollback

- **Status:** Ready for refinement — build sau khi release dependencies có contract
- **Priority:** P0 — one-week pilot
- **Owner:** Release/QA Engineer
- **Branch:** `codex/feat-release-quality` từ `dev`; pull request merge về `dev`
- **Release flow:** feature branches → `dev` → verified release SHA → `main`
- **Stack:** Theo [ADR-003](../architecture/adr/ADR-003-data-dashboard-stack-and-code-layout.md)
- **Related:** [Build Rules](../BUILD_RULES.md), [Team Build Playbook](../TEAM_BUILD_PLAYBOOK.md), [FEAT-01](./FEAT-01-data-foundation.md), [FEAT-02](./FEAT-02-csv-import.md), [FEAT-03](./FEAT-03-analytics-api.md), [FEAT-04](./FEAT-04-dashboard-ui.md)

## 1. Outcome

Team có thể chứng minh một release SHA duy nhất cài đặt, migrate, build, deploy staging, nhập masked CSV, đối soát Data → Dashboard, quan sát lỗi và rollback an toàn trước khi merge `dev` vào `main`.

FEAT-05 sở hữu quality/release harness, không sở hữu business behavior. Defect trong product code phải quay lại branch của feature owner để sửa và mang evidence trở lại release candidate.

## 2. Phạm vi

### In scope

- CI gates cho pull request, `dev` và release candidate.
- PostgreSQL 16 test service, clean/upgrade migration verification và seed validation.
- Contract, integration, authorization, privacy, reconciliation và browser E2E suites.
- Immutable build artifacts cho web/API/worker từ cùng SHA và `poetry.lock or requirements.txt`.
- Staging deployment, secrets/auth setup, masked pilot dataset và smoke tests.
- Performance evidence, observability dashboard/alerts, feature flags và runbooks.
- Release checklist, approval evidence, rollback drill và post-deploy verification.

### Non-goal

- Sửa metric, import, UI, schema hoặc domain invariant để làm test pass.
- Mở rộng scope sản phẩm, refactor module hoặc đổi stack ADR-003.
- Production infrastructure hoàn chỉnh ngoài pilot đã phê duyệt.
- Dùng raw production data, bypass authentication hoặc bỏ gate để kịp lịch.
- Chạy destructive database reset trên shared staging/production.

## 3. Locked technical baseline

Quality harness dùng đúng ADR-003: Python 3.12+, Poetry workspace, Python with type hints, PostgreSQL 16, SQLAlchemy + Alembic, FastAPI, Pydantic/OpenAPI, React/Vite, pytest và Playwright. Exact versions đến từ committed lockfile; CI dùng `pip install -r requirements.txt`. Runtime/container dùng digest hoặc immutable tag, cấm floating `latest`. API, worker và web artifacts có cùng `release_sha`, build timestamp và contract version metadata.

## 4. Code ownership

### Owned paths

```text
infra/**
.github/workflows/**
tests/e2e/**
tests/reconciliation/**
tests/performance/**
docs/runbooks/**
```

### Minimal integration seams

Chỉ được sửa tối thiểu khi cần expose test/deploy interface:

```text
package.json                         # root quality scripts only
pyproject.toml                       # root workspace config only
apps/api/src/app.py                  # registration/health wiring only
apps/worker/src/worker.py            # health/shutdown wiring only
apps/web/src/app/**                  # flag/error-boundary wiring only
```

Mỗi integration-seam change phải ở commit riêng, có path owner review và không đổi business result.

### Forbidden ownership

FEAT-05 không tự sửa business code trong:

```text
apps/*/src/modules/**
apps/web/src/features/**
packages/contracts/src/**
packages/domain/src/**
packages/db/{migrations,seeds,src}/**
tests/contract/**
tests/integration/**
```

Contract/integration tests co-locate theo path owner của FEAT-01..040. FEAT-05 chạy và tổng hợp evidence nhưng không sở hữu hoặc sửa các test đó nếu chưa có handoff.

Khi gate phát hiện defect:

1. Lưu failed command, release SHA, safe log/correlation ID, expected/actual và minimal reproduction.
2. Gán FEAT-01 cho schema/domain, FEAT-02 cho import, FEAT-03 cho API/metric, FEAT-04 cho UI.
3. Owner sửa trên branch của họ và mở PR vào `dev`.
4. FEAT-05 rebase/re-run gates; không cherry-pick sửa tạm không có owner.

Nếu chính test/harness sai, FEAT-05 sửa trong owned path và ghi lý do.

## 5. CI workflow và required gates

### Pull request fast gates

```bash
pip install -r requirements.txt
make lint
make typecheck
make test
make test-contract
make build
```

Gates bổ sung:

- workspace dependency-direction/architecture test theo ADR-003;
- OpenAPI generation có clean diff và compatibility check;
- secret scan, dependency/license/security policy và fixture PII scan;
- changed migration lint: immutable filename/checksum, không destructive change chưa duyệt;
- no focused/skipped test (`.only`, unauthorized `.skip`) trong critical suite.

### `dev` integration gates

```bash
make db-migrate
make db-seed
make db-verify
make test-integration
make test-e2e
```

- Chạy migration trên database sạch và upgrade fixture từ version đang hỗ trợ.
- Dùng PostgreSQL 16 thật trong isolated ephemeral environment, không mock SQL semantics.
- Chạy API/worker/web từ artifacts vừa build, không dùng dev server thay release artifact.
- Fail-fast với setup lỗi; vẫn upload safe logs, reports, traces và screenshots khi test lỗi.

### Release candidate gates

- Toàn bộ gates chạy lại trên exact SHA dự kiến merge `main`.
- Artifacts được ký/ghi checksum và promote; không rebuild giữa staging và release.
- Required checks protected, không được admin bypass nếu chưa có exception có owner, expiry và risk approval.
- Một rerun chỉ hợp lệ khi ghi nguyên nhân flaky/infrastructure; không rerun đến khi “xanh”.

## 6. Test environment và data safety

- Test/dev chỉ dùng synthetic fixtures; staging dùng representative masked dataset đã duyệt/checksum.
- Cấm raw name, phone, email, apartment identity, token, signed URL hoặc production dump trong repository/artifact/log.
- Secrets đến từ managed secret store/CI environment; short-lived credential, least privilege, rotation và không echo.
- CI service account tách khỏi human account. Staging web/API dùng auth thật theo pilot, không hidden bypass route.
- E2E có tối thiểu Analyst allowed, CX Manager allowed và out-of-scope user denied.
- Browser trace/video/screenshot được coi là sensitive artifact, retention giới hạn và chỉ upload khi đã mask.
- Log scan sau suite phải fail nếu thấy known fixture canary raw value hoặc secret pattern.

## 7. Contract, integration và E2E coverage

Contract tests khóa:

- import job states/count/error/idempotency;
- analytics filter/metric/error/pagination schemas;
- generated web client tương thích OpenAPI;
- additive compatibility và stable machine enum/error code.

Integration tests khóa:

- migration/constraints/seed checksum;
- valid, invalid, duplicate, partial và retry import;
- trusted classification eligibility;
- authorization ở query/detail/aggregate;
- timezone boundary, filter composition và cursor stability.

Critical Playwright flow:

```text
sign in
→ upload masked CSV
→ validate counts
→ execute and wait terminal job
→ open dashboard
→ apply filters
→ click KPI/chart segment bằng cùng snapshot token
→ verify feedback list count
→ open masked detail
→ Back giữ URL/filter
```

E2E còn cover empty, partial widget error, `403`, invalid filter, worker retry và browser refresh. Test không phụ thuộc order hoặc shared mutable record; mỗi run dùng unique namespace/idempotency key.

## 8. Reconciliation gates

Với frozen pilot fixture và baseline một valid row → một feedback item:

```text
total_rows = committed_rows + invalid_rows + duplicate_rows
committed_rows = distinct canonical source keys
committed_rows = eligible SOURCE_TRUSTED item count
eligible SOURCE_TRUSTED item count = analytics `item_volume`
dashboard item volume = analytics `item_volume`
sum(trend daily buckets) = dashboard total
bucket count = count of complete paginated drill-down under same filters
```

`top buckets + other_count = total` chỉ áp dụng khi dimension known-status policy trong FEAT-03 nói toàn population được bucket hóa.

- Checker xuất JSON evidence gồm fixture checksum, release SHA, metric version, filter/timezone, `snapshot_at`/token hash, expected/actual và safe IDs; không lưu token thật.
- Bất kỳ mismatch khác 0 là release blocker; không sửa bằng rounding hoặc UI override.
- Retry cùng file/key phải giữ canonical/dashboard counts không đổi.

## 9. Performance và resilience

- Seed representative volume: 100k feedback items, 90 ngày, distribution có skew theo issue/sentiment/time trong project pilot; authorization denial dùng synthetic project ngoài scope.
- FEAT-03 endpoints: p95 dưới 2 giây trên staging profile.
- FEAT-04 useful dashboard content: p75 dưới 2.5 giây theo budget đã chốt; không tính auth redirect.
- Import throughput/duration dùng budget FEAT-02; retry không duplicate và worker resume được sau restart.
- Load mix gồm summary, trend, breakdown, list pagination và detail; không chỉ benchmark query đơn.
- Capture dataset checksum, machine/service size, concurrency, warm/cold state và query plan cho regression.
- Performance smoke chạy mỗi release; full benchmark có thể scheduled nhưng phải chạy trước pilot.
- Worker kill/restart, API timeout, duplicate delivery và transient DB failure có automated resilience evidence.

## 10. Staging deployment

1. Build/sign artifacts từ release SHA bằng frozen lockfile.
2. Provision/verify PostgreSQL 16, object storage và network policy bằng code trong `infra/**`.
3. Inject secrets; chạy preflight connectivity mà không print credentials.
4. Deploy expand migration và verify; không contract/drop trong pilot deploy.
5. Deploy API/worker/web cùng artifact set với feature flags off.
6. Load validated taxonomy/location seed và masked fixture.
7. Chạy auth/scope smoke, import, reconciliation và critical E2E.
8. Bật flags tuần tự cho internal pilot; quan sát error, latency, queue và count.
9. Ghi staging URL, SHA, artifact checksums, migration version và evidence vào release record.

Staging không tự fallback sang mock API. Health endpoint chỉ báo process/dependency readiness, không trả secret, config hoặc PII.

## 11. Observability và runbooks

Dashboard vận hành tối thiểu:

- API request rate/error/p95 theo route;
- import queue depth/lag, job terminal states, row outcomes và retry;
- DB connection/error/slow query và migration version;
- web client errors/web vitals theo route;
- reconciliation mismatch và feature-flag state/change audit.

Trace truyền `correlation_id` qua API → worker → DB/read query; browser error hiển thị correlation ID an toàn. Metric labels không dùng user/project/building/code/content.

Mỗi production/pilot alert phải có owner, severity, actionable threshold và link runbook. Tạo tối thiểu `import-job-failure.md`, `analytics-reconciliation.md`, `staging-deploy.md` và `pilot-rollback.md` trong `docs/runbooks/`.

Không alert chỉ vì metric “khác thường” nếu chưa có hành động cụ thể.

## 12. Feature flags và release policy

Flags tối thiểu là `trusted_csv_import`, `trusted_csv_analytics_api` và `trusted_csv_dashboard`.

- Default off; config theo environment và pilot scope, deny-safe khi provider lỗi.
- Bật theo dependency order import → analytics API → dashboard; tắt theo thứ tự ngược khi có UI/API incident, hoặc tắt import trước khi dữ liệu ghi sai.
- Server vẫn enforce auth khi UI flag off/on; flag không phải authorization.
- Flag change có actor, time, scope, reason và correlation audit.

Merge `dev → main` chỉ khi exact release SHA pass gates, staging evidence còn hiệu lực, không có defect P0/P1, Product/Data Owner accept outcome và Integration Lead approve release.

## 13. Rollback

- Dừng rollout/tắt flag liên quan; pause worker tại safe boundary và giữ job retryable.
- Promote artifact trước còn tương thích expanded schema; không rebuild rollback artifact.
- Không xóa raw feedback, canonical data, history hoặc audit; correction là forward-fix có evidence.
- Migration chỉ rollback khi đã chứng minh reversible; mặc định forward migration mới.
- Sau rollback chạy auth smoke, health, import-job visibility và read-only reconciliation.
- Release record ghi trigger, decision owner, timestamps, artifact/schema/flag versions và follow-up owner.

Rollback drill trên staging là required gate, không chỉ là tài liệu.

## 14. Acceptance criteria

| AC                   | Given / When / Then                                                                                                                                                                            |
| -------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| AC-01 Frozen build   | **Given** clean runner; **When** install/build cùng SHA; **Then** frozen lockfile pass và artifacts có cùng release metadata.                                            |
| AC-02 Migration      | **Given** clean và supported-old DB; **When** migrate/seed/verify; **Then** cả hai đạt expected schema/checksum, không destructive reset.                               |
| AC-03 Critical flow  | **Given** masked fixture và allowed user; **When** chạy E2E intake-to-dashboard; **Then** flow hoàn tất và masked detail đúng.                                        |
| AC-04 Authorization  | **Given** out-of-scope user; **When** query dashboard/list/detail; **Then** không lộ data/count và audit/error an toàn.                                                  |
| AC-05 Reconciliation | **Given** frozen fixture; **When** chạy checker; **Then** mọi source/canonical/aggregate/drill-down invariant mismatch bằng 0.                                            |
| AC-06 Idempotency    | **Given** successful import; **When** retry cùng key/file; **Then** canonical và dashboard counts không tăng.                                                            |
| AC-07 Privacy        | **Given** canary raw/secret patterns; **When** chạy CI/E2E; **Then** scan fail nếu pattern xuất hiện trong log/report/DOM/trace.                                         |
| AC-08 Performance    | **Given** representative 100k dataset; **When** chạy release profile; **Then** budgets FEAT-02/030/040 đạt và evidence reproducible.                                     |
| AC-09 Flags          | **Given** flags off/on theo thứ tự; **When** smoke test; **Then** behavior thay đổi đúng, auth không bypass và change được audit.                                 |
| AC-10 Rollback       | **Given** staging release đang chạy; **When** thực hiện drill; **Then** artifact trước hoạt động với schema hiện tại, data giữ nguyên và reconciliation pass. |

## 15. DoR và feature-specific DoD

### DoR

- [ ] ADR-003, root scripts, merge order, environment owner và release approver đã khóa.
- [ ] FEAT-01..040 có contract, AC, flags, fixtures, budgets và owner xử lý defect.
- [ ] Staging access, secret store, masked dataset và test identities đã sẵn sàng.
- [ ] Supported migration starting version và rollback-compatible artifact được xác định.
- [ ] Required checks/protected branches có quyền cấu hình được duyệt.

### DoD

- [ ] PR/`dev`/release workflows chạy xanh trên exact SHA, không bypass hoặc unexplained rerun.
- [ ] Clean/upgrade migration, seed checksum, contract, integration, critical E2E và privacy scans pass.
- [ ] Reconciliation mismatch bằng 0; retry giữ counts ổn định.
- [ ] Staging deploy từ immutable artifacts; auth/scope và masked-data smoke pass.
- [ ] Performance/resilience budgets có reproducible evidence.
- [ ] Observability dashboards, actionable alerts và bốn runbook tối thiểu được review.
- [ ] Feature flags, staged rollout và rollback drill pass; release record đầy đủ.
- [ ] Product defects được sửa/merge bởi đúng owner branch; FEAT-05 không chứa business-code workaround.
- [ ] Product/Data Owner và Integration Lead ký chấp nhận trước `dev → main`.
