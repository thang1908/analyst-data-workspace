# API Contracts Specification — Trusted CSV to Dashboard Pilot

- **Status:** Approved Draft / Contract Frozen
- **Target Audience:** Backend Engineers (FEAT-02, FEAT-03), Frontend Engineers (FEAT-04)
- **Base Path:** `/api/v1/projects/{project_id}`
- **Related Specs:** [ADR-003](./adr/ADR-003-data-dashboard-stack-and-code-layout.md), [FEAT-02](../features/FEAT-02-csv-import.md), [FEAT-03](../features/FEAT-03-analytics-api.md), [FEAT-04](../features/FEAT-04-dashboard-ui.md)

---

## 1. Shared Filter Contract (Query Parameters)

Mọi API Analytics và Feedback Drill-down đều sử dụng chung một cấu trúc Query Filter để đảm bảo tính đồng nhất (Consistency) giữa số liệu Dashboard và danh sách Feedback chi tiết.

### Filter Schema (`AnalyticsFilterParams`)
| Parameter | Type | Required | Description | Example |
| :--- | :--- | :--- | :--- | :--- |
| `from_date` | `string` (ISO-8601 Date) | Yes | Ngày bắt đầu | `2026-08-01` |
| `to_date` | `string` (ISO-8601 Date) | Yes | Ngày kết thúc | `2026-08-10` |
| `service_ids` | `string` (Comma-separated) | No | Danh sách mã Service | `SRV_SUPPORT,SRV_BILLING` |
| `location_ids` | `string` (Comma-separated) | No | Danh sách mã Location | `LOC_BLDG_A` |
| `sentiments` | `string` (Comma-separated) | No | Sentiment filter (`POSITIVE`, `NEUTRAL`, `NEGATIVE`) | `NEGATIVE` |
| `severities` | `string` (Comma-separated) | No | Severity filter (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`) | `HIGH,CRITICAL` |

---

## 2. API Endpoints Specification

### 2.1. CSV Import API (FEAT-02 Context)

#### Endpoint 1: Upload CSV File
- **Method & Path**: `POST /api/v1/projects/{project_id}/imports/upload`
- **Content-Type**: `multipart/form-data`
- **Response `202 Accepted`**:
```json
{
  "import_job_id": "job_9842a1b7",
  "status": "VALIDATING",
  "filename": "feedback_july.csv",
  "total_rows": 10000,
  "uploaded_at": "2026-08-10T14:00:00Z"
}
```

#### Endpoint 2: Get Import Validation Progress & Summary
- **Method & Path**: `GET /api/v1/projects/{project_id}/imports/{job_id}`
- **Response `200 OK`**:
```json
{
  "import_job_id": "job_9842a1b7",
  "status": "VALIDATED",
  "counts": {
    "total_rows": 10000,
    "valid_rows": 9850,
    "invalid_rows": 150,
    "duplicate_rows": 0
  },
  "errors_sample": [
    {
      "row_number": 42,
      "column_name": "created_at",
      "error_code": "INVALID_TIMESTAMP",
      "message": "Timestamp must be ISO-8601 compliant"
    }
  ],
  "can_execute": true
}
```

#### Endpoint 3: Execute Import Job (Idempotent)
- **Method & Path**: `POST /api/v1/projects/{project_id}/imports/{job_id}/execute`
- **Request Body**:
```json
{
  "idempotency_key": "exec_key_8849201"
}
```
- **Response `200 OK`**:
```json
{
  "import_job_id": "job_9842a1b7",
  "status": "COMMITTED",
  "committed_rows": 9850,
  "committed_at": "2026-08-10T14:05:00Z"
}
```

---

### 2.2. Analytics API (FEAT-03 Context)

#### Endpoint 4: Get KPI Analytics Summary
- **Method & Path**: `GET /api/v1/projects/{project_id}/analytics/summary`
- **Query Params**: Shared Filter Contract (`from_date`, `to_date`, etc.)
- **Response `200 OK`**:
```json
{
  "snapshot_token": "snap_20260810_150000",
  "metrics": {
    "total_feedback_volume": 9850,
    "negative_feedback_volume": 1398,
    "negative_rate": 0.1419,
    "validation_pass_rate": 0.985
  }
}
```

#### Endpoint 5: Get Daily Trend Analytics
- **Method & Path**: `GET /api/v1/projects/{project_id}/analytics/trend`
- **Query Params**: Shared Filter Contract
- **Response `200 OK`**:
```json
{
  "snapshot_token": "snap_20260810_150000",
  "points": [
    { "date": "2026-08-01", "total_count": 950, "negative_count": 120, "negative_rate": 0.1263 },
    { "date": "2026-08-02", "total_count": 1100, "negative_count": 180, "negative_rate": 0.1636 }
  ]
}
```

#### Endpoint 6: Get Breakdown Analytics
- **Method & Path**: `GET /api/v1/projects/{project_id}/analytics/breakdown`
- **Query Params**: Shared Filter Contract + `dimension=service|location|issue|severity`
- **Response `200 OK`**:
```json
{
  "dimension": "service",
  "snapshot_token": "snap_20260810_150000",
  "segments": [
    { "key": "SRV_SUPPORT", "label": "Customer Support", "total_count": 4812, "negative_count": 820 },
    { "key": "SRV_BILLING", "label": "Billing Services", "total_count": 3540, "negative_count": 410 }
  ]
}
```

---

### 2.3. Feedback Drill-Down API (FEAT-03 Context)

#### Endpoint 7: List Masked Feedback Items (Cursor Pagination)
- **Method & Path**: `GET /api/v1/projects/{project_id}/feedback/items`
- **Query Params**: Shared Filter Contract + `limit=20` + `cursor=string`
- **Response `200 OK`**:
```json
{
  "items": [
    {
      "feedback_item_id": "fb_item_98214",
      "created_at": "2026-08-10T14:20:00Z",
      "service_name": "Customer Support",
      "location_name": "Building A - Floor 3",
      "sentiment": "NEGATIVE",
      "severity": "HIGH",
      "masked_text": "Khách hàng phản ánh nhân viên *** chậm trễ hỗ trợ đơn hàng..."
    }
  ],
  "next_cursor": "cursor_eyJpZCI6OTgyMTR9",
  "has_more": true
}
```

#### Endpoint 8: Get Single Feedback Detail & Provenance
- **Method & Path**: `GET /api/v1/projects/{project_id}/feedback/items/{item_id}`
- **Response `200 OK`**:
```json
{
  "feedback_item_id": "fb_item_98214",
  "created_at": "2026-08-10T14:20:00Z",
  "service_name": "Customer Support",
  "issue_name": "Slow Response",
  "location_name": "Building A - Floor 3",
  "sentiment": "NEGATIVE",
  "severity": "HIGH",
  "masked_text": "Khách hàng phản ánh nhân viên *** chậm trễ hỗ trợ đơn hàng...",
  "provenance": {
    "import_job_id": "job_9842a1b7",
    "source_reference": "feedback_july.csv",
    "row_index": 42,
    "decision": "SOURCE_TRUSTED",
    "committed_at": "2026-08-10T14:05:00Z"
  }
}
```

---

## 3. Standard Error Model & Error Codes

Mọi API lỗi đều phải tuân thủ chuẩn RFC-7807 (Problem Details).

### Error Schema
```json
{
  "type": "https://errors.cx-platform.domain/VALIDATION_ERROR",
  "title": "Invalid Request Parameters",
  "status": 400,
  "detail": "Date '2026-13-45' is not a valid ISO-8601 date string",
  "instance": "/api/v1/projects/proj_01/analytics/summary",
  "code": "INVALID_PARAM"
}
```

### Standard Error Codes Enum
- `INVALID_PARAM`: Tham số đầu vào sai định dạng.
- `UNAUTHORIZED_PROJECT_ACCESS`: User không có quyền trên project.
- `IMPORT_JOB_NOT_FOUND`: Import Job ID không tồn tại.
- `FILE_TOO_LARGE`: File CSV vượt quá kích thước 15MB.
- `IDEMPOTENCY_CONFLICT`: Thao tác Execute Import bị gọi lặp lại.
- `SERVER_INTERNAL_ERROR`: Lỗi không xác định ở hệ thống backend.
