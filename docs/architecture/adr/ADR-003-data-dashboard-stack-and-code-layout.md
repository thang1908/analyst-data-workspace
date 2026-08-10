
# ADR-003 — Data Dashboard Stack and Code Layout

- **Status:** Accepted
- **Date:** 2026-08-10
- **Decision owners:** Engineering Lead, Data Lead
- **Scope:** FEAT-00 đến FEAT-05
- **Related:** [PRD](../../PRD.md), [Build Rules](../../BUILD_RULES.md), [ADR-001](./ADR-001-journey-dimensions.md), [ADR-002](./ADR-002-classification-model.md)

## 1. Context

MVP một tuần cần đưa CSV đã phân loại vào hệ thống và hiển thị dashboard có thể đối soát về feedback nguồn.

Repository chưa có application scaffold. Nếu mỗi nhánh tự chọn framework, cấu trúc hoặc contract riêng, thời gian tích hợp sẽ lớn hơn thời gian build.

ADR này khóa stack, workspace layout, dependency direction và ranh giới runtime. Quy tắc domain, bảo mật, migration, test và release chi tiết vẫn tuân theo Build Rules.

## 2. Decision

Build một Python modular monolith, gồm ba runtime deployable:

```text
React/Vite web
      ↓ HTTP/OpenAPI
FastAPI backend
      ↓ application/domain
PostgreSQL

Python worker
      ↓ shared domain/database adapters
PostgreSQL
```

API và worker là hai process của cùng modular monolith. Chúng không phải microservice độc lập và không sở hữu domain model riêng.

## 3. Locked stack

| Concern               | Decision                                                 |
| --------------------- | -------------------------------------------------------- |
| Runtime               | Python 3.12+                                             |
| Dependency manager    | Poetry hoặc pip-tools với requirements.txt locked      |
| Language              | Python với type hints (mypy strict mode)                |
| Database              | PostgreSQL 16, current minor                             |
| SQL access/migrations | SQLAlchemy 2.0 + Alembic migrations                      |
| PostgreSQL driver     | psycopg3 (async)                                         |
| Runtime validation    | Pydantic v2                                              |
| HTTP contract         | OpenAPI generated from Pydantic models + FastAPI         |
| API                   | FastAPI 0.110+                                           |
| Worker                | Python process using shared domain and database packages |
| Web                   | React + Vite                                             |
| Test runner           | pytest cho unit/integration; Playwright cho browser E2E  |

Exact versions phải được pin bởi `poetry.lock` hoặc `requirements.txt` locked và container image digest hoặc immutable image tag.

Không dùng floating image tag hoặc dependency range để thay thế lockfile trong CI/release.

Thay framework, major version, database engine, ORM, contract mechanism hoặc workspace tool cần ADR mới thay thế ADR này.

## 4. Repository layout

Cấu trúc chuẩn là:

```text
/
├── apps/
│   ├── api/
│   │   ├── src/
│   │   │   ├── modules/
│   │   │   │   ├── imports/
│   │   │   │   ├── feedback/
│   │   │   │   └── analytics/
│   │   │   ├── app.py
│   │   │   └── main.py
│   │   ├── pyproject.toml
│   │   └── requirements.txt
│   ├── worker/
│   │   ├── src/
│   │   │   ├── modules/
│   │   │   │   └── imports/
│   │   │   └── worker.py
│   │   ├── pyproject.toml
│   │   └── requirements.txt
│   └── web/
│       ├── src/
│       │   ├── features/
│       │   │   ├── imports/
│       │   │   ├── dashboard/
│       │   │   └── feedback/
│       │   ├── app/
│       │   └── main.tsx
│       ├── package.json
│       └── tsconfig.json
├── packages/
│   ├── contracts/
│   │   ├── src/
│   │   │   ├── import/
│   │   │   ├── feedback/
│   │   │   └── analytics/
│   │   ├── pyproject.toml
│   │   └── __init__.py
│   ├── domain/
│   │   ├── src/
│   │   │   ├── import_domain.py
│   │   │   ├── feedback_domain.py
│   │   │   └── analytics_domain.py
│   │   ├── pyproject.toml
│   │   └── __init__.py
│   ├── db/
│   │   ├── alembic/
│   │   │   ├── versions/
│   │   │   └── env.py
│   │   ├── src/
│   │   │   ├── models/
│   │   │   ├── repositories/
│   │   │   └── session.py
│   │   ├── seeds/
│   │   │   ├── taxonomy.json
│   │   │   └── locations.json
│   │   ├── pyproject.toml
│   │   └── alembic.ini
│   └── test_fixtures/
│       └── import/
│           ├── valid.csv
│           └── invalid.csv
├── tests/
│   ├── e2e/
│   ├── integration/
│   └── performance/
├── infra/
│   ├── docker/
│   └── terraform/
├── docs/
├── pyproject.toml          # root workspace config
└── requirements.txt        # locked dependencies
```

Không thêm top-level application directory khác trong MVP nếu chưa cập nhật ADR.

## 5. Feature ownership map

| Feature | Primary owned paths | Outcome |
| --- | --- | --- |
| FEAT-00 Master | coordination/docs; không sở hữu business code | Điều phối scope và merge gates |
| FEAT-01 Platform & Data Foundation | root/app shell/platform config, `packages/contracts/src/{common,reference-data}`, `packages/domain`, `packages/db` | Scaffold, actor context, schema, reference data và persistence baseline |
| FEAT-02 CSV Import | `apps/api/src/modules/imports`, `apps/worker/src/modules/imports`, `packages/contracts/src/import`, `packages/test-fixtures/import` | Validate, import, lineage, fixtures và idempotency |
| FEAT-03 Analytics API | `apps/api/src/modules/feedback`, `apps/api/src/modules/analytics`, `packages/contracts/src/feedback`, `packages/contracts/src/analytics` | Query, metric và drill-down contract |
| FEAT-04 Pilot Web UI | `apps/web/src/features/{imports,dashboard,feedback}`, `apps/web/src/client/generated`, `apps/web/src/mocks/contracts` | Import control, dashboard, filter, list và detail |
| FEAT-05 Release Quality | `infra`, `.github/workflows`, `tests/e2e`, `tests/reconciliation`, `tests/performance`, `docs/runbooks` | Cross-feature quality gates, deploy verification và rollback evidence |

Unit, component, contract và module integration test được đặt cạnh code/contract của feature owner. Top-level `tests/**` chỉ chứa test xuyên nhiều feature và do FEAT-05 sở hữu.

Shared root configuration cần một integration owner review. Một feature không được sửa path của feature khác nếu chưa có handoff rõ trong PR.

## 6. Dependency direction

Dependency cho phép:

```text
apps/web    → packages/contracts (via OpenAPI generated types)
apps/api    → packages/contracts + packages/domain + packages/db
apps/worker → packages/contracts + packages/domain + packages/db
packages/db → packages/domain
packages/contracts → Pydantic/FastAPI libraries only
packages/domain    → platform-neutral libraries only
```

Các dependency bị cấm:

- `packages/domain` import FastAPI, React, SQLAlchemy hoặc psycopg3.
- `packages/contracts` import application, database hoặc UI code.
- `apps/web` import trực tiếp `packages/db` hoặc `packages/domain` implementation.
- API module ghi trực tiếp table do module khác sở hữu mà không qua application interface.
- Worker tự định nghĩa lại domain invariant hoặc HTTP contract.
- Một app import source code từ app khác.
- Circular dependency giữa package hoặc module.

## 7. Module boundaries

`imports` sở hữu upload request, import job, row validation result, dedupe orchestration và worker dispatch.

`feedback` sở hữu feedback query/detail use case và mapping từ domain read model sang contract.

`analytics` sở hữu metric semantics, aggregate query và drill-down filter normalization; không sửa authoritative feedback data.

`packages/domain` chứa entity, value object, invariant, use-case port và domain error dùng chung cho API/worker.

`packages/db` chứa SQLAlchemy models, repository adapter, transaction boundary, migration và seed; không chứa HTTP behavior.

`packages/contracts` chứa Pydantic request/response/error models, stable enum và OpenAPI metadata; không chứa persistence entity.

## 8. Contract-first workflow

Thứ tự thay đổi cho một capability là:

1. Chốt example input/output và error semantics.
2. Thêm hoặc sửa Pydantic models trong `packages/contracts`.
3. Generate/validate OpenAPI và review compatibility.
4. Chốt domain invariant và port trong `packages/domain`.
5. Thêm migration/repository trong `packages/db` nếu cần.
6. Implement API hoặc worker adapter.
7. Implement web client từ contract đã xuất bản.
8. Thêm contract, integration và E2E evidence phù hợp.

Frontend có thể phát triển song song bằng fixtures sinh từ contract; không tự tạo response shape riêng.

Breaking change không được merge âm thầm. Phải version contract hoặc cung cấp migration/compatibility window được duyệt.

## 9. Data and persistence decisions

PostgreSQL là source of truth duy nhất cho trạng thái canonical trong MVP.

Alembic migration đã merge là immutable. Sửa sai bằng migration mới, không rewrite migration đã chạy ở shared environment.

Mọi migration dùng quy trình `expand → migrate/backfill → verify → contract`.

Destructive `drop`, `rename` hoặc type narrowing không nằm trong cùng release với code bắt đầu phụ thuộc thay đổi đó.

Seed taxonomy/location phải có stable code, version và validator; application không hard-code label hoặc mapping.

Raw feedback/source lineage là bất biến. Dashboard chỉ đọc eligible feedback item/current projection, không aggregate trực tiếp raw import row.

Import retry phải dùng stable idempotency key và database constraint phù hợp; in-memory dedupe không đủ.

## 10. Runtime boundaries

FastAPI xử lý authentication context, validation, synchronous command/query và enqueue work.

Worker xử lý công việc import có thể retry; mỗi handler phải idempotent và trả trạng thái có thể quan sát.

Web không chứa business rule quyết định eligibility, metric denominator hoặc taxonomy validity.

API và worker dùng cùng domain/db package version từ một lockfile và cùng release artifact set.

Không tách message broker, cache hoặc search engine trong MVP nếu chưa có bằng chứng cần thiết. PostgreSQL-backed job mechanism có thể dùng cho pilot nếu đáp ứng retry, locking và visibility.

## 11. Release and rollback implications

Một commit release tạo web, API và worker artifacts từ cùng commit SHA và lockfile.

CI phải kiểm tra lockfile frozen, Python type hints (mypy strict), contract compatibility, migration trên database sạch, integration tests và production build.

Rollback application dùng artifact trước còn tương thích expanded schema. Dữ liệu đã ingest không bị xóa để rollback.

Migration lỗi được pause/forward-fix hoặc rollback bằng migration đã kiểm chứng khi thực sự reversible; không dùng destructive reset.

Projection analytics có thể rebuild từ authoritative records và phải có reconciliation check.

## 12. Consequences and compliance

Một ngôn ngữ, lockfile và shared contract giảm chi phí tích hợp, đổi lại team phải giữ dependency direction và backward compatibility giữa API/worker. ADR được thực thi bằng:

- workspace/import-boundary lint hoặc architecture test;
- Python type hints (mypy strict) ở root và từng package;
- frozen lockfile trong CI;
- contract compatibility test;
- clean-database migration test;
- aggregate-to-drill-down reconciliation test;
- CODEOWNERS/path review khi repository scaffold hỗ trợ.

Ngoại lệ phải ghi trong PR, có owner, thời hạn xử lý và ADR bổ sung nếu thay đổi quyết định lâu dài.
