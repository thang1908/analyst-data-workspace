# CX Intelligence & Operations Platform

> **Nền tảng Phân tích & Vận hành Trải nghiệm Cư dân**
> API version 1.1.0 | Taxonomy v3.0.1 | Migration 020

## Tài liệu

| File | Nội dung | Trạng thái |
|---|---|---|
| [SYSTEM_DOCUMENTATION.md](docs/SYSTEM_DOCUMENTATION.md) | **Tài liệu kỹ thuật cập nhật nhất** — Tech stack, DB schema, API endpoints, Frontend components, Business logic | ✅ Đồng bộ với code |
| [01_PRD.md](docs/01_PRD.md) | Product Requirements Document | ⚠️ Cũ (tham khảo) |
| [02_Business_Rules.md](docs/02_Business_Rules.md) | Business Rules | ⚠️ Cũ (tham khảo) |
| [03_service_taxonomy.md](docs/03_service_taxonomy.md) | Taxonomy chi tiết | ⚠️ Cũ (tham khảo) |
| [04_System_Design.md](docs/04_System_Design.md) | System Design | ⚠️ Cũ (tham khảo) |
| [05_Data_Model.md](docs/05_Data_Model.md) | Data Model | ⚠️ Cũ (tham khảo) |
| [06_API_Specification.md](docs/06_API_Specification.md) | API Specification | ⚠️ Cũ (tham khảo) |
| [07_UI_UX_Spec.md](docs/07_UI_UX_Spec.md) | UI/UX Specification | ⚠️ Cũ (tham khảo) |
| [08_Operating_Dashboard_Spec.md](docs/08_Operating_Dashboard_Spec.md) | Dashboard Spec | ⚠️ Cũ (tham khảo) |

> Sử dụng `SYSTEM_DOCUMENTATION.md` làm nguồn truth duy nhất. Các file cũ để lại để tham khảo lịch sử thiết kế ban đầu.

## Chạy nhanh

```bash
# 1. Migrate DB
alembic upgrade head

# 2. Start API (port 8000)
uvicorn apps.api.main:app --reload --port 8000

# 3. Start Frontend (port 3000)
cd apps/web && npm run dev -- --port 3000

# 4. Run tests
pytest tests/unit tests/integration
```

## Tính năng chính

- **Hợp nhất đa kênh**: 8 kênh tiếp nhận (App, Hotline, Lễ tân, Zalo, Email, Web, Social, Khác)
- **Taxonomy chuẩn hóa**: 6 stages / 36 steps / 10 services / 28 issues / Touchpoints
- **Phát hiện Điểm nóng**: Rolling window algorithm, 4 mức ưu tiên, đầy đủ audit trail
- **Dashboard thời gian thực**: KPI, ma trận hành trình, kênh phản ánh, xu hướng
- **Kho phản hồi**: 15+ bộ lọc, full-text search, drill-down
- **Import linh hoạt**: Direct CSV (đồng bộ) + Async pipeline

## OpenAPI Docs

- Swagger: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
