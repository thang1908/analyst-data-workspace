# Stack Update: Python + PostgreSQL

**Date:** 2026-08-10  
**Status:** Updated in ADR-003 và FEAT-01

## Summary

Đã cập nhật stack từ **TypeScript/Node.js** sang **Python**, nhưng **giữ nguyên PostgreSQL** (phù hợp với relational data model).

## Changes

### Updated files
- ✅ `docs/architecture/adr/ADR-003-data-dashboard-stack-and-code-layout.md`
- ✅ `docs/features/FEAT-01-data-foundation.md`

### Stack comparison

| Component | Before (TypeScript) | After (Python) | Note |
| --- | --- | --- | --- |
| **Runtime** | Node.js 24 LTS | Python 3.12+ | ✅ Changed |
| **Language** | TypeScript strict | Python + type hints (mypy) | ✅ Changed |
| **Dependency manager** | pnpm workspace | Poetry / pip-tools | ✅ Changed |
| **Validation** | Zod | Pydantic v2 | ✅ Changed |
| **Database** | PostgreSQL 16 | PostgreSQL 16 | ✅ **Kept same** |
| **ORM** | Drizzle ORM | SQLAlchemy 2.0 | ✅ Changed |
| **Migrations** | Drizzle Kit | Alembic | ✅ Changed |
| **Driver** | node-postgres | psycopg3 (async) | ✅ Changed |
| **API Framework** | Fastify 5 | FastAPI 0.110+ | ✅ Changed |
| **Test runner** | Vitest | pytest | ✅ Changed |
| **Web (frontend)** | React + Vite | React + Vite | ✅ **Kept same** |
| **E2E tests** | Playwright | Playwright | ✅ **Kept same** |

## New stack locked

```python
# Backend
Runtime: Python 3.12+
Framework: FastAPI 0.110+
Database: PostgreSQL 16
ORM: SQLAlchemy 2.0
Migrations: Alembic
Driver: psycopg3 (async)
Validation: Pydantic v2
Testing: pytest

# Frontend (unchanged)
Framework: React + Vite
Language: TypeScript
E2E: Playwright
```

## Repository layout

```text
/
├── apps/
│   ├── api/                    # FastAPI backend
│   │   ├── src/
│   │   │   ├── modules/
│   │   │   ├── app.py
│   │   │   └── main.py
│   │   ├── pyproject.toml
│   │   └── requirements.txt
│   ├── worker/                 # Python worker
│   │   ├── src/
│   │   │   └── worker.py
│   │   └── pyproject.toml
│   └── web/                    # React frontend
│       ├── src/
│       └── package.json
├── packages/
│   ├── contracts/              # Pydantic models
│   ├── domain/                 # Pure domain logic
│   └── db/                     # SQLAlchemy + Alembic
├── tests/
│   ├── e2e/                    # Playwright tests
│   ├── integration/            # pytest integration
│   └── performance/
├── pyproject.toml              # Root workspace
└── requirements.txt            # Locked dependencies
```

## Why keep PostgreSQL?

✅ **Reasons to keep PostgreSQL:**
1. **Relational data model** - Feedback → Item → Decision → Taxonomy có foreign keys rõ ràng
2. **ACID transactions** - Import batch cần atomic commits
3. **Schema constraints** - Unique constraints, foreign keys enforce data integrity
4. **Complex queries** - Analytics drill-down cần JOINs
5. **Migration versioning** - Alembic có mature migration story
6. **Query reconciliation** - Dễ verify aggregate count = drill-down count

❌ **MongoDB would be harder:**
- Embedding vs referencing cho nested data
- Transaction semantics khác ACID
- Schema evolution phức tạp hơn
- Reconciliation queries khó hơn

## Benefits of Python + PostgreSQL

### ✅ Advantages
- **Team experience:** Python dễ học hơn TypeScript
- **Data processing:** pandas, numpy cho future CSV processing
- **ML/AI ready:** sklearn, transformers cho future AI features
- **Mature ecosystem:** FastAPI + SQLAlchemy + Alembic đã proven
- **Type safety:** Pydantic + mypy strict mode
- **Relational benefits:** PostgreSQL constraints, transactions, migrations

### ⚠️ Trade-offs
- **End-to-end typing:** Không type-safe từ backend → frontend (phải dùng OpenAPI codegen)
- **Language split:** Python backend + TypeScript frontend (2 languages)
- **Learning curve:** Team frontend cần biết 2 ngôn ngữ

### 🎯 Acceptable
- Frontend giữ TypeScript/React (không cần thay đổi)
- OpenAPI làm contract boundary giữa Python/TypeScript
- Playwright E2E tests language-agnostic

## Migration path (if needed from TypeScript codebase)

Nếu đã có TypeScript code:

1. **Database schema:** 
   - Drizzle schemas → SQLAlchemy models
   - Migration history có thể giữ (Alembic hỗ trợ existing DB)

2. **Validation schemas:**
   - Zod → Pydantic models
   - OpenAPI spec giữ nguyên contract

3. **API routes:**
   - Fastify routes → FastAPI routers
   - Request/response models tương tự

4. **Tests:**
   - Vitest → pytest
   - Test logic giữ nguyên

## What stays the same (domain rules)

✅ **Không đổi** (from BUILD_RULES):
- Raw feedback immutable
- Prediction ≠ Decision
- Idempotency (source + source_reference unique)
- Audit trail append-only
- No hard-delete
- CSV contract (`trusted-feedback-csv/v1`)
- Vertical slice principle
- Definition of Ready/Done
- Security rules, testing pyramid

## Next steps

### 1. FEAT-01 implementation checklist
- [ ] Setup Poetry workspace hoặc pip-tools
- [ ] Create FastAPI app shell (`apps/api/src/app.py`)
- [ ] Setup SQLAlchemy + Alembic migrations
- [ ] Define Pydantic contracts (`packages/contracts/`)
- [ ] Create domain models (`packages/domain/`)
- [ ] Setup pytest với PostgreSQL test fixtures
- [ ] Setup mypy strict mode
- [ ] Create seeds (JSON files) với validator
- [ ] Health/readiness endpoints
- [ ] Actor context from authentication

### 2. CI/CD updates
- [ ] Update Docker images (Python base image)
- [ ] Update dependency install commands (poetry install / pip install -r)
- [ ] Update test commands (pytest)
- [ ] Update linting (pylint, mypy, black)

### 3. Documentation
- [ ] Update FEAT-02, 03, 04 references nếu có TypeScript-specific
- [ ] Create Python code style guide (if needed)
- [ ] Update README.md với setup instructions

## References

- [ADR-003 Updated](./architecture/adr/ADR-003-data-dashboard-stack-and-code-layout.md)
- [FEAT-01 Updated](./features/FEAT-01-data-foundation.md)
- [BUILD_RULES](./BUILD_RULES.md) - Domain rules không đổi
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy 2.0 Documentation](https://docs.sqlalchemy.org/)
- [Pydantic v2 Documentation](https://docs.pydantic.dev/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)

---

**Decision approved:** Team consensus, Engineering Lead  
**Effective date:** 2026-08-10  
**Supersedes:** ADR-003 TypeScript stack (section 2, 3)
