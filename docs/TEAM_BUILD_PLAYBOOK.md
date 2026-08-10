# Team Build Playbook — One-week Data-to-Dashboard MVP

- **Version:** 0.1
- **Status:** Active for pilot build
- **Base branch:** `dev`
- **Release branch:** `main`
- **Architecture:** [ADR-003](./architecture/adr/ADR-003-data-dashboard-stack-and-code-layout.md)
- **Engineering rules:** [Build Rules](./BUILD_RULES.md)

## 1. Purpose

Playbook này điều phối FEAT-00 đến FEAT-05 để nhiều người build song song mà không làm lệch contract, schema hoặc số liệu dashboard.

Mục tiêu tuần đầu là vertical slice CSV trusted data → canonical feedback item → analytics API → dashboard/drill-down → staging evidence.

Stack, runtime và repository layout đã khóa trong ADR-003. Tài liệu này không thay thế domain rules hoặc Definition of Ready/Done trong Build Rules.

Named owners và decision evidence được theo dõi trong [Pilot Kickoff Checklist](./PILOT_KICKOFF_CHECKLIST.md); role label trong tài liệu không thay thế tên người chịu trách nhiệm.

## 2. Feature and branch map

Mỗi feature có đúng một integration owner và một nhánh chuẩn:

| ID | Name | Branch | Base | Primary paths |
| --- | --- | --- | --- | --- |
| FEAT-00 | Master | `dev` | `main` sau release gate | coordination/docs; không sở hữu business code |
| FEAT-01 | Platform & Data Foundation | `codex/feat-data-foundation` | `dev` | app shells/platform, `packages/domain`, `packages/db/{migrations,seeds,src}` |
| FEAT-02 | CSV Import | `codex/feat-csv-import` | `dev` | `apps/api/src/modules/imports`, `apps/worker/src/modules/imports`, `packages/contracts/src/import` |
| FEAT-03 | Analytics API | `codex/feat-analytics-api` | `dev` | `apps/api/src/modules/{feedback,analytics}`, `packages/contracts/src/{feedback,analytics}` |
| FEAT-04 | Pilot Web UI | `codex/feat-pilot-web-ui` | `dev` | `apps/web/src/features/{imports,dashboard,feedback}` |
| FEAT-05 | Release Quality | `codex/feat-release-quality` | `dev` | `infra`, `.github/workflows`, `tests/{e2e,reconciliation,performance}`, `docs/runbooks` |

Không tạo tên nhánh thay thế cho cùng feature. Hotfix ngoài bảng dùng `codex/fix-<short-slug>` và cần FEAT-00 owner gán phạm vi trước khi code.

## 3. Checkout commands

Checkout remote feature branch đã được tạo sẵn:

```bash
git fetch origin --prune
git switch --track origin/codex/feat-data-foundation
```

Thay tên branch bằng đúng branch trong bảng cho FEAT-02 đến FEAT-05. Không tạo branch trùng với tên khác.

Mở lại feature branch đã tồn tại:

```bash
git fetch origin
git switch <feature-branch>
git rebase origin/dev
```

Không dùng `git checkout --`, `git reset --hard` hoặc thao tác xóa thay đổi để xử lý worktree chung.

## 4. Code ownership

| Path | Accountable owner | Required reviewers |
| --- | --- | --- |
| `packages/domain/**` | FEAT-01 | FEAT-00; feature sử dụng invariant |
| `packages/contracts/src/{common,reference-data}/**` và package config | FEAT-01 | FEAT-02/030; FEAT-00 |
| App package config, `apps/{api,worker}/src/platform/**`, `apps/web/src/app/**` và base entrypoints | FEAT-01 | FEAT-02/030/040/050 theo consumer |
| `packages/db/migrations/**` | FEAT-01 | FEAT-00; FEAT-02/030 khi bị ảnh hưởng |
| `packages/db/seeds/**` | FEAT-01 | Product/Data owner |
| `packages/db/src/**` | FEAT-01 | Consumer feature owner |
| `packages/contracts/src/import/**` | FEAT-02 | FEAT-01; FEAT-00 |
| `packages/contracts/src/feedback/**` | FEAT-03 | FEAT-01; FEAT-04 |
| `packages/contracts/src/analytics/**` | FEAT-03 | FEAT-04; Product/Data owner |
| `apps/api/src/modules/imports/**` | FEAT-02 | FEAT-01 |
| `apps/worker/src/modules/imports/**` | FEAT-02 | FEAT-01; FEAT-05 |
| `apps/api/src/modules/feedback/**` | FEAT-03 | FEAT-01; FEAT-04 |
| `apps/api/src/modules/analytics/**` | FEAT-03 | Product/Data owner; FEAT-04 |
| `apps/web/src/features/dashboard/**` | FEAT-04 | FEAT-03; Product owner |
| `apps/web/src/features/feedback/**` | FEAT-04 | FEAT-03; Product owner |
| `apps/web/src/features/imports/**` | FEAT-04 | FEAT-02; Product owner |
| `apps/web/src/client/generated/**`, `apps/web/src/mocks/contracts/**` | FEAT-04 | FEAT-02/030; FEAT-05 |
| `packages/test-fixtures/**` | FEAT-02 | FEAT-01; FEAT-03/040; FEAT-05 |
| `tests/{e2e,reconciliation,performance}/**`, `infra/**`, `.github/workflows/**`, `docs/runbooks/**` | FEAT-05 | FEAT-00; affected feature owner |
| Root workspace/config | FEAT-01 | FEAT-00; tất cả owner bị ảnh hưởng |

Owner chịu trách nhiệm contract và backward compatibility, không có nghĩa là owner duy nhất được code. Cross-path change cần handoff trong PR trước khi sửa.

## 5. Dependency graph and merge order

Dependency và integration gate bắt buộc:

```text
FEAT-00 scope/contracts gate
          ↓
FEAT-01 Platform & Data Foundation
     ┌────┴───────────────┐
     ↓                    ↓
FEAT-02 CSV Import   FEAT-03 Analytics API
                          ↓
                 FEAT-04 Pilot Web UI
     └────────────┬───────┘
                  ↓
FEAT-05 Release Quality
                  ↓
dev acceptance → main release
```

Development có thể song song bằng contract/fixtures. FEAT-01 merge đầu tiên; FEAT-02 và FEAT-03 có thể merge độc lập sau FEAT-01; FEAT-04 chỉ merge sau khi contract FEAT-02 và FEAT-03 pass; FEAT-05 merge cuối khi import, API và UI đã có trên `dev`.

FEAT-03 không merge query dựa trên bảng tạm của FEAT-02. FEAT-04 không merge client type tự định nghĩa thay cho shared contract. FEAT-05 có thể chuẩn bị CI sớm nhưng phải rebase trên `dev` mới nhất và merge cuối.

Sau mỗi merge upstream, owner downstream phải rebase, chạy gate liên quan và xác nhận contract diff trước khi tiếp tục review.

## 6. Rebase policy

- Chỉ rebase feature branch do một owner/team kiểm soát.
- Không rebase hoặc force-push `dev` và `main`.
- Không rebase shared feature branch khi collaborator chưa xác nhận checkpoint.
- Rebase lên `origin/dev` trước khi yêu cầu final review và sau mỗi upstream dependency merge.
- Resolve conflict theo source of truth; không chọn `ours/theirs` hàng loạt.
- Sau rebase, chạy lại contract, typecheck, migration và test bị ảnh hưởng.
- Chỉ dùng `git push --force-with-lease` trên feature branch sau khi owner xác nhận; không dùng `--force`.
- Nếu branch đã có review active, thông báo commit SHA cũ/mới trong PR sau rebase.

Luồng chuẩn:

```bash
git fetch origin
git switch <feature-branch>
git rebase origin/dev
<run-required-checks>
git push --force-with-lease origin <feature-branch>
```

`<run-required-checks>` là placeholder cho tới khi root scripts được scaffold và khóa.

## 7. Contract-first workflow

Mỗi capability đi theo thứ tự:

1. Product/Data owner chốt example, eligibility và error semantics.
2. Contract owner thêm Pydantic models tại `packages/contracts/src/<area>`.
3. Thêm request, response, error examples và OpenAPI compatibility test.
4. FEAT-01 xác nhận domain invariant, stable IDs và schema impact.
5. Migration/repository được review trước implementation phụ thuộc.
6. API/worker implement contract; không trả shape ngoài contract.
7. Web dùng generated/shared types hoặc fixtures được validate bởi contract.
8. Mỗi feature co-locate unit/contract/module-integration test trong path mình sở hữu; FEAT-05 thêm cross-feature E2E/reconciliation/performance evidence.
9. Product/Data owner đối soát aggregate với drill-down records.

Contract PR phải được merge trước hoặc trong cùng atomic integration change với consumer. Không merge UI/API assumption chưa được biểu diễn trong contract.

Breaking enum/field meaning cần version mới hoặc compatibility plan; đổi tên để “dễ code hơn” không phải lý do hợp lệ.

## 8. Commit rules

- Một commit chứa một thay đổi logic có thể review và revert độc lập.
- Không trộn formatting toàn repository với feature change.
- Không commit generated artifact nếu build policy chưa xác định artifact đó là source.
- Không commit `.env`, credential, raw PII, production dump hoặc local OS file.
- Không commit code fail lint/typecheck/test thuộc scope.
- Commit message dùng imperative, có area rõ.

Ví dụ: `feat(import): validate trusted CSV rows`, `feat(analytics): add item-volume query`, `test(release): verify import-to-dashboard reconciliation`.

Commit sửa migration đã chạy không được phép; tạo migration forward mới.

## 9. Pull request rules

Mỗi PR phải:

- ghi FEAT ID, outcome và acceptance criteria liên quan;
- chỉ ra base branch `dev` và upstream dependency SHA;
- liệt kê path ngoài ownership nếu có cùng handoff/reviewer;
- nêu contract, migration, security/PII và telemetry impact;
- có test evidence và lệnh đã chạy;
- có screenshot hoặc recording cho UI behavior;
- nêu feature flag, rollout, rollback/forward-fix;
- không có unrelated file, secret hoặc fixture chứa dữ liệu thật;
- được rebase trên `origin/dev` mới nhất trước merge;
- dùng squash merge trừ khi FEAT-00 owner duyệt giữ commit history.

PR checklist tối thiểu:

```text
[ ] Contract/example được review trước consumer
[ ] Python with type hints, lint và typecheck pass
[ ] Unit/contract/integration test liên quan pass
[ ] Migration chạy được trên database sạch
[ ] Authorization và PII/log path đã kiểm tra
[ ] Aggregate khớp drill-down nếu có metric
[ ] Feature flag và rollback đã mô tả
[ ] Không sửa path ngoài ownership chưa được đồng ý
```

## 10. Prohibited changes

- Dashboard query trực tiếp raw CSV/import table.
- Hard-code taxonomy label, mapping, timezone hoặc metric denominator trong UI.
- Update/delete raw feedback hoặc applied migration.
- Dùng prediction hoặc row chưa accepted/source-trusted làm eligible analytics item.
- Cross-module write trực tiếp table do module khác sở hữu.
- Copy contract/type giữa web, API và worker.
- Đổi stack/major version đã khóa trong ADR-003 mà không có ADR thay thế.
- Thêm microservice, broker, cache hoặc search engine chỉ để “chuẩn bị scale”.
- Tắt validation/test/security gate để kịp demo mà không có exception được duyệt.
- Force-push shared integration/release branch.

## 11. Environment and secrets

- Commit `.env.example` chỉ với tên biến và safe placeholder.
- `.env`, `.env.local` và secret thật phải ignored.
- CI/staging lấy secret từ managed secret store; không ghi secret vào workflow YAML.
- Tách `APP_ENV`; không dùng production credential ở dev/test.
- Fixture chỉ synthetic/masked và nằm trong `packages/test-fixtures`.
- Log không chứa `content_raw`, email, phone, token, signed URL hoặc database URL.
- Secret leak làm PR/release dừng ngay; rotate trước khi tiếp tục, không chỉ xóa commit mới nhất.

## 12. Migration rules

- FEAT-01 là accountable owner của mọi migration.
- Mỗi migration có purpose, forward path, verification query và rollback/forward-fix note.
- Dùng `expand → migrate/backfill → verify → contract`.
- Không drop/rename/narrow type trong cùng release với consumer mới.
- Migration đã chạy trên shared environment là immutable.
- Constraint cho stable ID, foreign key và idempotency phải nằm ở database khi khả thi.
- Seed có version/checksum; thay meaning tạo version/migration mới.
- PR migration phải chạy trên database sạch và từ supported previous state.
- Rollback application không được xóa feedback, lineage, decision hoặc audit đã ghi.

## 13. Test pyramid and CI gates

Pyramid ưu tiên nhiều test nhanh ở đáy, ít E2E nhưng phủ đúng critical path:

```text
             E2E
       integration/contract
    unit/domain/schema validation
```

| Layer | Required evidence |
| --- | --- |
| Unit/domain | invariant, state, eligibility, metric boundary, invalid mapping |
| Contract | Pydantic/OpenAPI examples, error schema, backward compatibility |
| Integration | PostgreSQL migration, transaction, idempotency, query reconciliation |
| E2E | upload → import → dashboard → filtered feedback drill-down |
| Security/privacy | denied scope, masked fixture, log/trace scan |

Root CI interface sau scaffold phải cung cấp tương đương:

```bash
pip install -r requirements.txt
pnpm lint
pnpm typecheck
pnpm test
pnpm test:contract
pnpm test:integration
pnpm test:e2e
pnpm build
pnpm db:migrate
pnpm db:verify
```

Tên script là placeholder cho tới khi scaffold PR khóa root `package.json`; sau đó đổi tên cần approval của FEAT-00 và FEAT-05.

## 14. Five-day coordination

| Day | Integration goal | Merge gate |
| --- | --- | --- |
| 1 | Khóa CSV/metric/contracts; scaffold; FEAT-01 merge `dev`; mọi team rebase | Clean migration/seed/app-shell/auth smoke và public contracts pass |
| 2 | FEAT-02 import và FEAT-03 analytics làm song song; FEAT-04 import/dashboard bằng mock contract | Row outcome/idempotency và aggregate/drill-down module tests pass |
| 3 | FEAT-02/030 merge độc lập; FEAT-04 nối generated clients và representative data | Import terminal counts, API reconciliation và UI contract pass |
| 4 | FEAT-04 merge; FEAT-05 full E2E, authorization/privacy, resilience, reconciliation/performance | Critical flow và mọi release blocker gate pass |
| 5 | Deploy staging flags off, smoke/UAT, rollback drill, enable pilot scope | Acceptance evidence; `dev` approved để release `main` |

Checkpoint hằng ngày: 09:00 chốt target/dependency/blocker; 12:00 cutoff contract/schema; 16:00 bàn giao merge candidate/test evidence; 17:00 FEAT-00 cập nhật gate và merge order. Không mở feature mới sau ngày 3.

## 15. RACI

Vai trò: Product/Data Owner (`PDO`), FEAT-00 Integration Lead (`IL`), feature owner (`FO`), FEAT-05 Release/QA (`RQ`).

| Activity | PDO | IL | FO | RQ |
| --- | --- | --- | --- | --- |
| Scope, CSV và metric semantics | A/R | C | C | I |
| Contract/change order | C | A | R | C |
| Domain/schema/migration | C | A | R — FEAT-01 | C |
| Import implementation | I | A | R — FEAT-02 | C |
| Analytics API | C | A | R — FEAT-03 | C |
| Pilot web/import/dashboard UX | A | C | R — FEAT-04 | C |
| CI, integration/E2E, staging | I | A | C | R — FEAT-05 |
| Acceptance and release decision | A | R | C | C |
| Incident/rollback coordination | I | A | C | R |

`R` thực hiện, `A` chịu trách nhiệm cuối, `C` được tham vấn, `I` được thông báo. Mỗi dòng chỉ có một `A`.

## 16. Conflict protocol

Khi có conflict về file, contract hoặc domain meaning:

1. Dừng sửa vùng conflict; không overwrite thay đổi đang có.
2. Ghi hai branch/SHA, file, contract hoặc invariant bị ảnh hưởng.
3. Path owner đề xuất resolution; FEAT-00 owner quyết định merge order.
4. Domain/metric ambiguity chuyển Product/Data owner; kiến trúc lâu dài dùng ADR.
5. Merge upstream owner trước, downstream rebase và adapt.
6. Schema conflict giải bằng migration forward mới, không rewrite migration đã dùng.
7. Chạy lại contract/migration/integration tests và thông báo evidence cho consumer.

Nếu chưa quyết định kịp cutoff, giữ feature flag off và giảm scope; không tự chọn behavior để kịp merge.

## 17. Ready and Done gates

Mọi feature phải pass [Definition of Ready trong Build Rules](./BUILD_RULES.md#13-definition-of-ready--dor) trước khi chuyển sang `Ready for build`.

Ngoài DoR chung, tuần này cần khóa CSV sample, expected volume, taxonomy/location seed, trusted-source policy, metric examples, branch/path owner và downstream consumer.

Mọi feature phải pass [Definition of Done trong Build Rules](./BUILD_RULES.md#14-definition-of-done--dod) cùng feature-specific DoD trước merge hoàn tất.

Release `dev → main` chỉ được phép khi:

- FEAT-01 đến FEAT-05 đã merge đúng dependency order;
- import count đối soát source → canonical → eligible item;
- dashboard KPI/chart khớp filtered drill-down;
- CI, migration, build và critical E2E pass trên release SHA;
- staging dùng masked/synthetic data và không có P0/P1 defect trong scope;
- rollback drill có owner, artifact và verification evidence;
- Product/Data Owner chấp nhận outcome.
