# Tài liệu Hệ thống — CX Intelligence & Operations Platform
> **Phiên bản tài liệu:** 2.0.0 (cập nhật theo code thực tế)
> **Cập nhật lần cuối:** 19/08/2026
> **Trạng thái:** Đã đồng bộ với codebase (Migration 020, API v1.1.0)

---

## 1. Tech Stack thực tế

| Layer | Technology | Version |
|---|---|---|
| Backend API | FastAPI | 0.141.1 |
| Database | PostgreSQL + SQLAlchemy async | 2.0.52 |
| DB Migrations | Alembic | 1.19.1 |
| DB Driver | psycopg v3 (async native) | 3.3.4 |
| Data Validation | Pydantic v2 | 2.13.4 |
| Frontend | React 18 + TypeScript | 18 / 5.2.2 |
| Frontend Build | Vite | 5.1.4 |
| Charts | Recharts | 3.10.1 |
| Icons | lucide-react | 0.350.0 |
| Routing | react-router-dom | 6.22.0 |
| Animation | framer-motion | 13.1.0 |
| ASGI Server | uvicorn + uvloop | 0.52.1 |

---

## 2. Cấu trúc thư mục

```
analyst-data-workspace/
├── apps/
│   ├── api/
│   │   ├── main.py                   # FastAPI entry point (v1.1.0)
│   │   ├── deps.py                   # Dependency injection
│   │   └── routers/
│   │       ├── analytics.py          # Analytics endpoints
│   │       ├── feedback.py           # Feedback workspace + direct-import-csv
│   │       ├── hotspot.py            # Hotspot CRUD & lifecycle
│   │       ├── taxonomy.py           # Taxonomy read endpoints
│   │       ├── import_pipeline.py    # Async CSV/XLSX import
│   │       └── ai_classification.py  # AI classification
│   ├── web/src/
│   │   ├── api/                      # Frontend API clients
│   │   ├── components/
│   │   │   ├── analytics/            # KPICard, Journey3DMatrix, TrendChart, PainPointsList, ChannelBreakdownCard, AnalyticsFilterBar
│   │   │   ├── feedback/             # FeedbackDataTable, FeedbackDetailModal, FeedbackFilterToolbar
│   │   │   ├── hotspot/              # HotspotDashboard (NEW), HotspotActionQueue, HotspotDetailModal
│   │   │   └── layout/               # Sidebar, TopBar
│   │   └── pages/
│   │       ├── OverviewPage.tsx      # /
│   │       ├── feedback/FeedbackExplorerPage.tsx  # /feedback
│   │       ├── hotspot/HotspotPage.tsx            # /hotspot
│   │       └── import/ImportWizardPage.tsx        # /import
│   └── worker/main.py                # Background import worker
├── packages/
│   ├── domain/
│   │   ├── shared/enums.py           # ALL domain enums
│   │   ├── feedback/                 # entities, masking, exceptions
│   │   ├── hotspot/engine.py         # Clustering engine + state machine
│   │   ├── taxonomy/                 # Taxonomy entities
│   │   └── import_pipeline/          # State machine, validation
│   └── infrastructure/
│       ├── db/repositories/          # DB repository implementations
│       ├── storage/s3.py
│       └── queue/postgres_queue.py
├── alembic/versions/                 # 20 migration files (001-020)
└── tests/unit + tests/integration    # 95 passed, 3 skipped
```

---

## 3. Database Schema — 20 Migrations

### Danh sách migrations

| File | Nội dung |
|---|---|
| 001 | PostgreSQL extensions (uuid-ossp, pg_trgm) + shared enums |
| 002 | taxonomy_release |
| 003 | customer_lifecycle_stage, customer_lifecycle_step, service_request_step |
| 004 | service, issue, cause_category |
| 005 | interaction_channel, location, owner_config |
| 006 | import_job, import_row, import_job_queue |
| 007 | feedback, feedback_item, feedback_affected_channel |
| 008 | classification_prediction (AI ledger) |
| 009 | classification_decision (decision ledger) |
| 010 | classification_current (current projection) |
| 011 | hotspot + hotspot_timeline + hotspot_evidence |
| 012 | analytics_feedback_item_v1 (semantic view) |
| 013-015 | Indexes + analytics view refinements |
| 016 | SEED Taxonomy v3.0.0: 6 stages, 36 steps, 10 services, 28 issues, 8 channels |
| 017 | Extend analytics view: intake_channel_code, affected_channel_codes (array) |
| 018 | SEED Taxonomy v3.0.1: dashboard display names ngắn gọn |
| 019 | touchpoint + touchpoint_service_map + action_priority on hotspot + touchpoint on classification_current |
| 020 | source_metadata_json -> JSONB + GIN index + B-tree indexes on location |

### Bảng chính

#### feedback
- feedback_id UUID PK
- project_id UUID
- source_system text ('direct-csv', tên nguồn)
- source_record_key text
- intake_channel_id UUID FK
- external_ticket_id text
- reported_at, ingested_at timestamptz
- content_raw, content_masked text
- source_metadata_json JSONB  ← migration 020 (document store)
- raw_content_checksum text (SHA-256)

#### feedback_item
- feedback_item_id UUID PK
- feedback_id UUID FK
- item_index int (1..N, hỗ trợ split)
- item_text_masked text
- location_id UUID FK
- status: ACTIVE / SPLIT_PARENT / RETIRED
- analytic_eligibility: INCLUDED / EXCLUDED / PENDING
- parent_item_id UUID FK (nullable)

#### classification_decision (ledger bất biến)
Mỗi quyết định phân loại thêm 1 dòng mới.
- Fields chính: taxonomy_release_id, customer_lifecycle_step_id, primary_service_id, issue_id, sentiment, operational_severity, classification_state, decision_source, decided_by, decided_at

#### classification_current (projection)
- customer_lifecycle_stage_id (tính từ step)
- customer_lifecycle_step_id
- touchpoint_id ← THÊM MỚI migration 019
- touchpoint_value_status ← THÊM MỚI migration 019
- primary_service_id, issue_id, sentiment, operational_severity
- projection_version int

#### hotspot
- hotspot_id UUID PK
- dimension_key text: '{service_id}:{issue_id}:{location_id}:{rule_version}'
- status: CANDIDATE / ACKNOWLEDGED / INVESTIGATING / RESOLVED / DISMISSED / REOPENED
- action_priority: IMMEDIATE / URGENT / PLANNED / MONITOR  ← THÊM MỚI migration 019
- operational_severity text (max severity của cluster)
- evidence_count int
- assigned_user_id UUID, assigned_team_key text
- first_seen_at, last_seen_at, resolved_at timestamptz
- resolution_summary text
- window_start, window_end timestamptz
- version int (optimistic locking)

#### hotspot_timeline (audit log bất biến)
- from_status, to_status, action text
- actor_user_id UUID, reason text
- metadata_json JSONB, correlation_id text

#### touchpoint (THÊM MỚI migration 019)
- touchpoint_id UUID PK
- taxonomy_release_id UUID FK
- touchpoint_code, name_vi, name_en, definition text
- lifecycle_step_id UUID FK
- sort_order int, active bool

#### touchpoint_service_map (THÊM MỚI migration 019)
- touchpoint_id, service_id UUID PKs
- mapping_type: PRIMARY / SECONDARY

#### analytics_feedback_item_v1 (SQL View)
Grain: 1 row / feedback_item. Chỉ INCLUDED items.
Join tất cả classification, taxonomy, location, feedback, hotspot aggregates.
Expose: intake_channel_code, affected_channel_codes (text[])

---

## 4. Domain Business Logic

### Hotspot Engine (packages/domain/hotspot/engine.py)

#### calculate_action_priority() — Quy tắc ưu tiên
| Điều kiện | Priority |
|---|---|
| SEV-1 + is_safety_critical + safety_playbook_approved=True | IMMEDIATE |
| SEV-1 + is_safety_critical + playbook chưa duyệt | URGENT |
| SEV-1 hoặc SEV-2 hoặc count >= 10 | URGENT |
| SEV-3 hoặc SEV-4 + count >= 2 | PLANNED |
| Còn lại | MONITOR |

#### calculate_operational_severity()
Lấy max severity của tất cả items trong cluster.

#### generate_dimension_key() — Idempotency key
"{service_id}:{issue_id}:{location_id_or_GLOBAL}:{rule_version}"

#### State transitions hợp lệ
CANDIDATE → ACKNOWLEDGED, INVESTIGATING, DISMISSED
ACKNOWLEDGED → INVESTIGATING, RESOLVED, DISMISSED
INVESTIGATING → RESOLVED, DISMISSED
RESOLVED → REOPENED (→ INVESTIGATING)
DISMISSED → REOPENED (→ INVESTIGATING)

### Direct CSV Import Logic
- Auto-detect delimiter (,  ;  TAB)
- Fuzzy location match, auto-create nếu không khớp
- Keyword heuristics cho service/issue matching
- Sentiment + severity từ CSV hoặc heuristics từ nội dung
- Batch flush mỗi 1000 rows
- Lưu toàn bộ raw CSV vào source_metadata_json (JSONB)

---

## 5. API Endpoints (v1.1.0)

### Health
GET /health
GET /api/v1/health

### Analytics — /api/v1/analytics
GET /summary          → KPI: item_volume, rates, active_hotspots
GET /trend            → Time series (grain: day/week/month)
GET /breakdown        → Dimension breakdown (11 dimensions: service, issue, location, journey_stage, journey_step, touchpoint, service_request_step, intake_channel, affected_channel, sentiment, severity)
GET /filter-options   → Filter dropdown options
GET /data-quality     → 501 Not Implemented

Filter params (15 chiều): project_id*, date_from, date_to, source_system, intake_channel_code, affected_channel_code, location_id, location_scope, customer_lifecycle_stage_code, customer_lifecycle_step_code, touchpoint_code, service_request_step_code, service_code, issue_code, sentiment, operational_severity

### Feedback — /api/v1/feedback-items
GET    /                        → listFeedbackItems (15+ filters, limit/offset, default limit=50, max=100)
GET    /{id}                    → getFeedbackItem
PATCH  /{id}                    → updateFeedbackItem (correction: service, issue, sentiment, severity, eligibility, location, symptom_detail)
POST   /direct-import-csv       → Import CSV đồng bộ (multipart/form-data)
POST   /{id}/split              → splitFeedbackItem (tách multi-intent)

Headers cho mutations: X-Actor-ID, X-Actor-Role, X-Correlation-ID

### Hotspot — /api/v1/hotspots
GET  /                    → listHotspots (filters: status, action_priority, service_code, issue_code, location_id, severity, date_from, date_to)
GET  /{id}                → getHotspot (detail + evidence + timeline)
POST /{id}/acknowledge    → CANDIDATE → ACKNOWLEDGED
POST /{id}/assign         → → INVESTIGATING + assign owner_user_id + owner_team_key
POST /{id}/dismiss        → → DISMISSED
POST /{id}/resolve        → → RESOLVED + resolution_summary (required)
POST /{id}/reopen         → → INVESTIGATING (từ RESOLVED/DISMISSED)
POST /detect              → Run detection engine

Detect body: {project_id, window_days=180, threshold_count=3, rule_version="v1.0.0", safety_playbook_approved=false, window_start?, window_end?}

Error codes: 404 Not Found, 409 Conflict (version mismatch), 422 Invalid state transition

### Taxonomy — /api/v1
GET /customer-lifecycle/stages         → 6 stages
GET /customer-lifecycle/steps          → 36 steps (filter: stage_code)
GET /customer-lifecycle/touchpoints    → Touchpoints (filter: step_code, service_code)
GET /touchpoints                       → Alias (hidden from OpenAPI schema)
GET /services                          → 10 services
GET /services/{service_id}/issues      → Issues của 1 service
GET /issues                            → 28 issues (filter: service_code)

### Import Pipeline — /api/v1/import-jobs
POST /           → Upload file (202 Accepted)
POST /upload     → Alias
POST /{id}/map   → Map columns
POST /{id}/execute → Queue to worker
GET  /{id}       → Check status

---

## 6. Taxonomy v3.0.1

### 6 Customer Lifecycle Stages (36 steps total)
A (Nhận biết): A1, A2, A3
C (Xem xét): C1..C6
TR (Giao dịch): TR-01..TR-06
HO (Nhận nhà): HO-01..HO-05
RES (Cư trú): RES-01..RES-08
OPS (Vận hành): OPS-01..OPS-08

### 8 Service Request Steps
SRV-01..SRV-08

### 10 Primary Services
SV-01 Quản lý hợp đồng & hồ sơ
SV-02 Tài chính & thanh toán
SV-03 Giao nhận nhà & bàn giao
SV-04 An ninh & kiểm soát ra vào
SV-05 Vệ sinh & môi trường
SV-06 Cây xanh & cảnh quan
SV-07 Kỹ thuật, tiện ích & tài sản chung
SV-08 Dịch vụ cư dân & cộng đồng
SV-09 App & nền tảng số
SV-10 Khác

### 28 Issues (3 per SV-01..SV-09, 1 for SV-10)
IS-01-01, IS-01-02, IS-01-03 ... IS-09-01, IS-09-02, IS-09-03, IS-10-01

### 8 Interaction Channels
ch-app, ch-hotline, ch-web, ch-email, ch-frontdesk, ch-social, ch-zalo, ch-other

---

## 7. Domain Enums (packages/domain/shared/enums.py)

ValueStatus          = KNOWN | UNKNOWN | MISSING | NOT_APPLICABLE
TaxonomyReleaseStatus = DRAFT | APPROVED | PUBLISHED | RETIRED
ClassificationState  = PENDING_REVIEW | ACCEPTED | REJECTED | SUPERSEDED
DecisionSource       = MANUAL | SOURCE_TRUSTED | HUMAN_ACCEPTED_AI | HUMAN_CORRECTED_AI | POLICY_AUTO_APPLIED | SYSTEM_MIGRATION
Sentiment            = POSITIVE | NEUTRAL | NEGATIVE | UNKNOWN
OperationalSeverity  = SEV-1 | SEV-2 | SEV-3 | SEV-4
CauseDeterminationStatus = NOT_ASSESSED | UNKNOWN | SUGGESTED | UNDER_INVESTIGATION | CONFIRMED | NOT_APPLICABLE
AnalyticEligibility  = INCLUDED | EXCLUDED | PENDING
FeedbackItemStatus   = ACTIVE | SPLIT_PARENT | RETIRED
ImportJobStatus      = UPLOADED | MAPPED | VALIDATING | VALIDATED | QUEUED | PROCESSING | COMPLETED | PARTIAL | FAILED | CANCELLING | CANCELLED
HotspotStatus        = CANDIDATE | ACKNOWLEDGED | INVESTIGATING | RESOLVED | DISMISSED | REOPENED
ActionPriority       = IMMEDIATE | URGENT | PLANNED | MONITOR
MappingType          = PRIMARY | SECONDARY
ReviewAction         = ACCEPT | CORRECT | MARK_UNKNOWN | MARK_MISSING | MARK_NOT_APPLICABLE | SPLIT_REQUIRED | SKIP

---

## 8. Môi trường & Triển khai

### Environment Variables
DATABASE_URL=postgresql+psycopg://user:password@localhost:5432/cx_db
VITE_API_BASE_URL=http://localhost:8000

### Chạy local
alembic upgrade head
uvicorn apps.api.main:app --reload --port 8000
# Frontend:
cd apps/web && npm run dev -- --port 3000
# Tests:
pytest tests/unit tests/integration

### OpenAPI
Swagger UI: http://localhost:8000/docs
ReDoc:      http://localhost:8000/redoc
JSON:       http://localhost:8000/openapi.json

---

## 9. Delta — Thay đổi so với tài liệu cũ

| Hạng mục | Tài liệu cũ | Thực tế |
|---|---|---|
| API version | Chưa định nghĩa | v1.1.0 |
| action_priority trên hotspot | Không có | Implement migration 019 |
| Touchpoints | Chưa có | Đầy đủ: table + API + analytics (migration 019) |
| Analytics dimensions | Chưa đầy đủ | 11 dimensions (thêm touchpoint, service_request_step, affected_channel) |
| Direct CSV import | Không có | POST /feedback-items/direct-import-csv |
| Document store JSONB | Không có | source_metadata_json JSONB + GIN index (migration 020) |
| Dynamic location | Không có | Auto-create location khi CSV import không khớp |
| HotspotDashboard | Không có | Component mới: 4 KPI + 2 Donut + Bar chart |
| ChannelBreakdownCard | Không có | Component mới trong OverviewPage |
| Taxonomy version | v3.0.0 | v3.0.1 (labels ngắn gọn hơn cho dashboard) |
| Default pagination FeedbackExplorer | Chưa định nghĩa | 10 items/page |
| data-quality endpoint | Planned | 501 Not Implemented |
| REOPEN hotspot | Không có | POST /{id}/reopen |
| ASSIGN hotspot | Không có | POST /{id}/assign với owner_user_id + owner_team_key |
| HotspotStatus REOPENED | Không có | Enum value mới |
| Sidebar nav label | "Điểm nóng & Căn nguyên" | "Điểm nóng" |
