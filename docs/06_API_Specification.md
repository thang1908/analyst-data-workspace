# 06 — Đặc tả API

> **Cập nhật v2.0 (19/08/2026):**
> - Thêm endpoint `POST /feedback-items/direct-import-csv` — import CSV đồng bộ không cần worker
> - Thêm endpoint `POST /hotspots/{id}/reopen` — reopen về INVESTIGATING
> - Thêm endpoint `POST /hotspots/{id}/assign` — gán người xử lý, chuyển sang INVESTIGATING
> - Taxonomy: thêm `GET /customer-lifecycle/touchpoints` và `GET /touchpoints` (alias hidden)
> - Hotspot list filter thêm `action_priority`
> - Analytics breakdown thêm dimension `touchpoint`
> - `POST /hotspots/detect` body thêm field `safety_playbook_approved`
> - `data-quality` endpoint trả 501 Not Implemented
> - Channel codes (intake_channel_code, affected_channel_code) dùng lowercase: ch-app, ch-hotline...
> - Tất cả mutations hotspot yêu cầu `expected_version` (optimistic locking)



# Nền tảng Phân tích Hành trình CX, Dịch vụ & Nguyên nhân gốc rễ (CX Journey, Service & Root Cause Intelligence Platform)

**Phiên bản:** 2.0 — cập nhật 19/08/2026 khớp routers thực tế  
**Trạng thái:** Baseline Xây dựng Pilot P0  
**Nguồn gốc (Derived from):** `docs/PRD.md` v1.3, `05_Data_Model.md` v1.1, `docs/System_Design.md` v1.1, `docs/Business_Rules.md` v1.1, `docs/service_taxonomy.md` v3.0.0  
**Phong cách API (API style):** REST/JSON over HTTPS  
**Backend:** FastAPI + Pydantic v2  
**Đường dẫn cơ sở (Base path):** `/api/v1`

---

## 1. Mục đích

Tài liệu này xác định hợp đồng HTTP P0 được sử dụng bởi:

```text
apps/web
workers / internal clients
future approved connectors
```

API BẮT BUỘC phải bảo toàn các bất biến miền (domain invariants) thay vì công khai trực tiếp các thao tác CRUD cơ sở dữ liệu.

Các quy tắc chính:

- các client chọn các ID/mã phân loại (taxonomy IDs/codes) ổn định, không dùng nhãn đã bản địa hóa;
- CRUD cho các dòng phân loại (taxonomy row CRUD) không được công khai trong P0;
- Phản hồi thô (raw Feedback) là bất biến (immutable);
- Mục phản hồi (Feedback Item) là đơn vị xem xét (review) và phân tích (analytics);
- dự đoán (prediction) không thay đổi phân loại hiện tại (current classification);
- các thao tác ghi phân loại được chấp nhận sẽ tạo ra các phiên bản Quyết định (Decision) bất biến;
- các endpoint thay đổi dữ liệu (mutation endpoints) bắt buộc thực thi phân quyền (authorization), kiểm toán (audit) và kiểm soát truy cập đồng thời lạc quan (optimistic concurrency);
- các endpoint KPI/biểu đồ/đi sâu (drill-down) sử dụng một định nghĩa điều kiện hợp lệ phân tích (analytics eligibility definition) duy nhất.

---

# 2. Các quy ước chung

## 2.1 URL cơ sở (Base URL)

```text
/api/v1
```

Ví dụ:

```http
GET /api/v1/feedback-items
```

---

## 2.2 Loại nội dung (Content Type)

```http
Content-Type: application/json
Accept: application/json
```

Các endpoint tải lên tệp sử dụng `multipart/form-data`.

---

## 2.3 Xác thực (Authentication)

P0 sử dụng xác thực dựa trên SSO.

API nhận/rút ra ngữ cảnh chủ thể (principal context):

```json
{
  "user_id": "uuid",
  "role_ids": ["REVIEWER"],
  "privileges": [
    "feedback:read",
    "classification:review"
  ],
  "allowed_project_ids": ["uuid"],
  "raw_pii_allowed": false,
  "export_allowed": false
}
```

Các vai trò ứng dụng tối thiểu:

```text
PILOT_ADMIN
ANALYST
REVIEWER
VIEWER
```

Việc phân quyền BẮT BUỘC phải được thực thi ở phía máy chủ (server-side).

---

## 2.4 ID liên kết (Correlation ID)

Client CÓ THỂ gửi:

```http
X-Correlation-ID: <uuid-or-client-id>
```

Nếu vắng mặt, API sẽ tạo một ID mới.

Mỗi phản hồi NÊN trả về:

```http
X-Correlation-ID: ...
```

và bao gồm `request_id` trong metadata/lỗi của phản hồi.

---

## 2.5 Tính idempotent (Idempotency)

Các endpoint thay đổi dữ liệu có thể thử lại NÊN chấp nhận:

```http
Idempotency-Key: <client-generated-key>
```

Trường hợp sử dụng điển hình:

- tạo công việc nhập dữ liệu (import job);
- thực thi/thử lại việc nhập dữ liệu;
- tạo công việc dự đoán (prediction job);
- các thao tác thay đổi dữ liệu mà việc gửi trùng lặp có thể gây hại.

Tái sử dụng bị xung đột:

```text
409 IDEMPOTENCY_CONFLICT
```

---

## 2.6 Kiểm soát truy cập đồng thời lạc quan (Optimistic Concurrency)

Các tài nguyên vận hành có thể thay đổi sử dụng một trong các trường:

```text
expected_version
expected_current_decision_id
expected_projection_version
```

Một thao tác thay đổi dữ liệu bị lỗi thời sẽ trả về:

```text
409 VERSION_CONFLICT
```

Máy chủ BẮT BUỘC KHÔNG ĐƯỢC âm thầm áp dụng một bản cập nhật đánh giá (review) hoặc điểm nóng (hotspot) đã bị lỗi thời.

---

## 2.7 Các Enum chuẩn dùng chung giữa các tài liệu (Canonical Cross-document Enums)

```text
decision_source = MANUAL | SOURCE_TRUSTED | HUMAN_ACCEPTED_AI | HUMAN_CORRECTED_AI | POLICY_AUTO_APPLIED | SYSTEM_MIGRATION
cause_determination_status = NOT_ASSESSED | UNKNOWN | SUGGESTED | UNDER_INVESTIGATION | CONFIRMED | NOT_APPLICABLE
review_action = ACCEPT | CORRECT | MARK_UNKNOWN | MARK_MISSING | MARK_NOT_APPLICABLE | SPLIT_REQUIRED | SKIP
```

Các endpoint P0 từ chối `UNDER_INVESTIGATION` và `CONFIRMED`; các giá trị đó được dành riêng cho các endpoint Điều tra/RCA của P1. Các giá trị bí danh (alias) như `SOURCE`, `HUMAN`, `AI_ACCEPTED`, `CANDIDATE_AVAILABLE`, hoặc các hành động đánh giá viết kiểu Title Case là các giá trị truyền tải (wire values) không hợp lệ.

---

# 3. Bao bì phản hồi chuẩn (Standard Response Envelope)

Các endpoint tài nguyên CÓ THỂ trả về tài nguyên trực tiếp. Các endpoint bộ sưu tập/thao tác NÊN sử dụng:

```json
{
  "data": {},
  "meta": {
    "request_id": "uuid",
    "timestamp": "2026-08-11T09:00:00Z"
  }
}
```

Bộ sưu tập:

```json
{
  "data": [],
  "page": {
    "limit": 50,
    "next_cursor": "opaque-or-null",
    "total": 1200
  },
  "meta": {
    "request_id": "uuid"
  }
}
```

`total` CÓ THỂ được bỏ qua đối với các truy vấn con trỏ (cursor) tốn kém chi phí.

---

# 4. Hợp đồng lỗi chuẩn (Standard Error Contract)

```json
{
  "error": {
    "code": "DOMAIN_RULE_VIOLATION",
    "message": "Issue does not belong to selected Primary Service.",
    "field_errors": [
      {
        "field": "issue_id",
        "code": "ISSUE_SERVICE_MISMATCH",
        "message": "IS-07-01 must belong to SV-07 in the selected taxonomy release."
      }
    ],
    "details": {},
    "request_id": "uuid"
  }
}
```

Ánh xạ HTTP chuẩn:

| HTTP | Mã (Code) | Ý nghĩa (Meaning) |
|---:|---|---|
| 400 | VALIDATION_ERROR | yêu cầu bị sai định dạng / xác thực yêu cầu cơ bản thất bại |
| 401 | UNAUTHENTICATED | không có danh tính hợp lệ |
| 403 | FORBIDDEN | bị từ chối quyền / phạm vi dự án |
| 404 | NOT_FOUND | không tìm thấy tài nguyên / tài nguyên không nằm trong phạm vi |
| 409 | VERSION_CONFLICT | xung đột truy cập đồng thời lạc quan |
| 409 | IDEMPOTENCY_CONFLICT | tái sử dụng key với payload khác |
| 422 | DOMAIN_RULE_VIOLATION | JSON hợp lệ nhưng vi phạm bất biến miền |
| 429 | RATE_LIMITED | bị giới hạn tần suất yêu cầu (throttled) |
| 500 | INTERNAL_ERROR | lỗi máy chủ không mong muốn |

PII thô BẮT BUỘC KHÔNG ĐƯỢC phản hồi trong payload lỗi.

---

# 5. Phân trang, Sắp xếp và Lọc (Pagination, Sorting and Filtering)

## 5.1 Phân trang bằng Con trỏ (Cursor Pagination)

Được ưu tiên cho danh sách Feedback Item lớn:

```http
GET /feedback-items?limit=50&cursor=<opaque>
```

Mặc định:

```text
limit = 50
max   = 200
```

---

## 5.2 Sắp xếp (Sorting)

Cú pháp trong danh sách cho phép (allowlist):

```http
?sort=-reported_at
?sort=operational_severity,-reported_at
```

Client BẮT BUỘC KHÔNG ĐƯỢC truyền tên cột SQL tùy ý.

---

## 5.3 Các giá trị lọc ổn định (Stable Filter Values)

Sử dụng ID/mã:

```http
?service_code=SV-07
?issue_code=IS-07-01
?customer_lifecycle_step_code=RES-03
?service_request_step_code=SRV-02
```

Không lọc theo văn bản nhãn đã được dịch.

---

# 6. Các API Tham chiếu / Phân loại (Reference / Taxonomy APIs)

Tất cả các endpoint đọc thông thường đều trả về các giá trị đã xuất bản (published) trừ khi `taxonomy_release_id` được cung cấp một cách rõ ràng và bên gọi có quyền.

## 6.1 Các giai đoạn Vòng đời khách hàng (Customer Lifecycle Stages)

```http
GET /api/v1/customer-lifecycle/stages
```

Truy vấn:

```text
taxonomy_release_id?
active=true
```

Mục phản hồi:

```json
{
  "id": "uuid",
  "code": "RES",
  "name_vi": "Cư trú",
  "name_en": "Residence",
  "sort_order": 5
}
```

---

## 6.2 Các bước Vòng đời khách hàng (Customer Lifecycle Steps)

```http
GET /api/v1/customer-lifecycle/steps
```

Các bộ lọc:

```text
stage_code
taxonomy_release_id
active
```

Phản hồi:

```json
{
  "id": "uuid",
  "code": "RES-03",
  "stage": {
    "id": "uuid",
    "code": "RES"
  },
  "name_vi": "Ra vào & di chuyển",
  "definition": "..."
}
```

---

## 6.3 Các bước Vòng đời yêu cầu dịch vụ (Service Request Steps)

```http
GET /api/v1/service-request-lifecycle/steps
```

---

## 6.4 Dịch vụ (Services)

```http
GET /api/v1/services
GET /api/v1/services/{service_id}
```

Mục phản hồi:

```json
{
  "id": "uuid",
  "code": "SV-07",
  "name_vi": "Kỹ thuật, tiện ích & tài sản chung",
  "name_en": "Engineering, Utilities & Common Assets",
  "default_severity": "SEV-3"
}
```

---

## 6.5 Vấn đề theo Dịch vụ (Issues by Service)

```http
GET /api/v1/services/{service_id}/issues
```

Bộ lọc thay thế:

```http
GET /api/v1/issues?service_code=SV-07
```

Mục phản hồi:

```json
{
  "id": "uuid",
  "code": "IS-07-01",
  "service_id": "uuid",
  "name_vi": "Hệ thống ngừng hoặc suy giảm",
  "safety_critical": false,
  "severity_override": null
}
```

---

## 6.6 Nguyên nhân ứng viên (Candidate Causes)

```http
GET /api/v1/issues/{issue_id}/candidate-causes
```

Phản hồi:

```json
{
  "data": [
    {
      "cause_id": "uuid",
      "cause_code": "CAUSE-ELEVATOR-CAPACITY",
      "name_vi": "...",
      "rank_hint": 1,
      "required_evidence": "..."
    }
  ]
}
```

Endpoint này chỉ trả về các giả thuyết có thể xảy ra.

---

## 6.7 Ánh xạ Vòng đời - Dịch vụ (Lifecycle-Service Mappings)

```http
GET /api/v1/lifecycle-service-mappings
```

Các bộ lọc:

```text
lifecycle_type
lifecycle_step_code
service_code
taxonomy_release_id
```

---

## 6.8 Vị trí (Locations)

```http
GET /api/v1/locations
```

Các bộ lọc:

```text
project_id   # bắt buộc trừ khi chủ thể có đúng một dự án
parent_id
location_type
q
active
```

---

## 6.9 Xác thực phiên bản phát hành Phân loại (Taxonomy Release Validation)

Chỉ dành cho Admin:

```http
POST /api/v1/taxonomy-versions/{taxonomy_release_id}/validate
```

Phản hồi:

```json
{
  "data": {
    "valid": true,
    "checks": [
      {"code": "SERVICE_COUNT", "status": "PASS", "actual": 10, "expected": 10},
      {"code": "ISSUE_COUNT", "status": "PASS", "actual": 28, "expected": 28}
    ],
    "checksum": "..."
  }
}
```

---

## 6.10 Xuất bản Phân loại (Publish Taxonomy)

Chỉ dành cho Admin:

```http
POST /api/v1/taxonomy-versions/{taxonomy_release_id}/publish
```

Yêu cầu:

```json
{
  "expected_status": "APPROVED",
  "effective_from": "2026-08-12T00:00:00Z",
  "reason": "Publish taxonomy 3.0.0 for P0 pilot."
}
```

Quy tắc:

- xác thực phải vượt qua;
- chuyển đổi trạng thái phải hợp lệ;
- kiểm toán là bắt buộc.

---

# 7. Các API Nhập dữ liệu (Import APIs)

## 7.1 Tạo công việc nhập dữ liệu (Create Import Job)

```http
POST /api/v1/import-jobs
Content-Type: multipart/form-data
Idempotency-Key: ...
```

Các trường:

```text
file
project_id
source_system
mapping_profile_id? 
```

Phản hồi `202 Accepted`:

```json
{
  "data": {
    "import_job_id": "uuid",
    "status": "UPLOADED",
    "filename": "feedback.xlsx",
    "file_size_bytes": 123456,
    "created_at": "..."
  }
}
```

---

## 7.2 Lưu/Cập nhật Ánh xạ (Save/Update Mapping)

```http
PUT /api/v1/import-jobs/{id}/mapping
```

Yêu cầu:

```json
{
  "expected_version": 1,
  "mapping": {
    "ticket_id": "source_record_key",
    "reported_date": "reported_at",
    "content_masked": "content",
    "project": "project",
    "channel": "intake_channel"
  }
}
```

Phản hồi chuyển công việc sang trạng thái `MAPPED`.

---

## 7.3 Xem trước Nhập dữ liệu (Preview Import)

```http
POST /api/v1/import-jobs/{id}/preview
```

Yêu cầu:

```json
{
  "sample_rows": 50
}
```

Phản hồi hiển thị bản xem trước đã chuẩn hóa mà không commit Feedback.

---

## 7.4 Xác thực Nhập dữ liệu (Validate Import)

```http
POST /api/v1/import-jobs/{id}/validate
Idempotency-Key: ...
```

Phản hồi:

```text
202 Accepted
```

```json
{
  "data": {
    "import_job_id": "uuid",
    "status": "VALIDATING"
  }
}
```

---

## 7.5 Lấy thông tin công việc Nhập dữ liệu (Get Import Job)

```http
GET /api/v1/import-jobs/{id}
```

Phản hồi:

```json
{
  "data": {
    "import_job_id": "uuid",
    "status": "VALIDATED",
    "total_rows": 18546,
    "valid_rows": 18110,
    "invalid_rows": 436,
    "committed_rows": 0,
    "version": 4
  }
}
```

---

## 7.6 Lỗi Nhập dữ liệu (Import Errors)

```http
GET /api/v1/import-jobs/{id}/errors
```

Các bộ lọc:

```text
field_name
error_code
limit
cursor
```

---

## 7.7 Thực thi Nhập dữ liệu (Execute Import)

```http
POST /api/v1/import-jobs/{id}/execute
Idempotency-Key: ...
```

Yêu cầu:

```json
{
  "expected_version": 4,
  "allow_partial": true
}
```

Phản hồi:

```text
202 Accepted
```

---

## 7.8 Thử lại Nhập dữ liệu (Retry Import)

```http
POST /api/v1/import-jobs/{id}/retry
```

Chỉ thử lại các công việc bị lỗi/chưa commit theo các quy tắc idempotency.

---

## 7.9 Hủy Nhập dữ liệu (Cancel Import)

```http
POST /api/v1/import-jobs/{id}/cancel
```

Công việc đang trong hàng chờ/đang xử lý sẽ chuyển sang `CANCELLING` sau đó là `CANCELLED` khi dừng an toàn.

---

# 8. Các API Không gian làm việc Phản hồi (Feedback Workspace APIs)

## 8.1 Liệt kê các Mục phản hồi (List Feedback Items)

```http
GET /api/v1/feedback-items
```

Các bộ lọc chính:

```text
project_id
date_from
date_to

source_system
intake_channel_code
affected_channel_code
location_id

customer_lifecycle_stage_code
customer_lifecycle_step_code
service_request_step_code

service_code
issue_code
sentiment
operational_severity

classification_state
cause_determination_status
analytic_eligibility

has_prediction
needs_review
q

sort
limit
cursor
```

Phản hồi mục mặc định:

```json
{
  "feedback_item_id": "uuid",
  "feedback_id": "uuid",
  "reported_at": "2026-05-31T03:20:00Z",
  "source_system": "internal_csv",
  "content_masked": "S10512 hỗ trợ gọi KT sửa cửa",
  "location": {
    "id": "uuid",
    "code": "S10512",
    "name": "S10 / Unit 512"
  },
  "current_classification": {
    "service": {"id": "uuid", "code": "SV-07", "name_vi": "..."},
    "issue": {"id": "uuid", "code": "IS-07-03", "name_vi": "..."},
    "sentiment": "NEUTRAL",
    "operational_severity": "SEV-3",
    "classification_state": "ACCEPTED",
    "projection_version": 3
  },
  "review": {
    "needs_review": false,
    "latest_prediction_confidence": 0.91
  }
}
```

Nội dung thô không bao giờ được trả về bởi endpoint bộ sưu tập này.

---

## 8.2 Lấy Vỏ bọc Phản hồi (Get Feedback Envelope)

```http
GET /api/v1/feedback/{feedback_id}
```

Phản hồi mặc định trả về nội dung đã được che (masked content) và nguồn gốc dữ liệu (provenance).

Nội dung thô yêu cầu endpoint/quyền hạn rõ ràng; xem §8.5.

---

## 8.3 Lấy chi tiết Mục phản hồi (Get Feedback Item Detail)

```http
GET /api/v1/feedback-items/{feedback_item_id}
```

Bao gồm:

```text
văn bản đã che
nguồn gốc dữ liệu
vị trí
các kênh bị ảnh hưởng
phân loại hiện tại
tóm tắt các dự đoán mới nhất
tóm tắt quyết định/xem xét
liên kết điểm nóng
dòng dõi chia tách (split lineage)
```

---

## 8.4 Các kênh bị ảnh hưởng (Affected Channels)

```http
PUT /api/v1/feedback-items/{id}/affected-channels
```

Yêu cầu:

```json
{
  "expected_version": 2,
  "channel_ids": ["uuid", "uuid"]
}
```

Đây là ngữ cảnh vận hành; các nhãn phân loại không được tạo tại đây.

---

## 8.5 Xem nội dung thô có đặc quyền (Privileged Raw View)

```http
POST /api/v1/feedback/{feedback_id}/raw-view
```

Yêu cầu:

```json
{
  "reason": "Investigating source discrepancy for case #123."
}
```

Yêu cầu:

```text
raw_pii_allowed = true
yêu cầu lý do (reason required)
bắt buộc kiểm toán (audit mandatory)
```

Phản hồi:

```json
{
  "data": {
    "feedback_id": "uuid",
    "content_raw": "...",
    "view_token_expires_at": "..."
  }
}
```

Không công khai nội dung thô thông qua các endpoint GET dùng chung.

---

# 9. API Chia tách Mục phản hồi (Feedback Item Split API)

```http
POST /api/v1/feedback/{feedback_id}/items/split
```

Yêu cầu:

```json
{
  "source_feedback_item_id": "uuid",
  "expected_projection_version": 3,
  "reason": "Two independent observable failures.",
  "items": [
    {
      "item_text_masked": "Thang máy chậm vào buổi sáng",
      "symptom_detail": "Chờ thang máy lâu",
      "location_id": "uuid"
    },
    {
      "item_text_masked": "App cư dân không đăng nhập được",
      "symptom_detail": "OTP/login failure",
      "location_id": null
    }
  ]
}
```

Phản hồi `201 Created`:

```json
{
  "data": {
    "source_item": {
      "id": "uuid",
      "status": "SPLIT_PARENT"
    },
    "created_items": [
      {"id": "uuid", "item_index": 2},
      {"id": "uuid", "item_index": 3}
    ]
  }
}
```

Quy tắc:

- `content_raw` gốc không đổi;
- các quyết định lịch sử của mục nguồn vẫn được giữ nguyên;
- kiểm toán là bắt buộc.

---

# 10. Các API Dự đoán (Prediction APIs)

## 10.1 Tạo công việc dự đoán (Create Prediction Job)

```http
POST /api/v1/ai/prediction-jobs
Idempotency-Key: ...
```

Yêu cầu:

```json
{
  "project_id": "uuid",
  "taxonomy_release_id": "uuid",
  "selection": {
    "feedback_item_ids": ["uuid"],
    "or_filter": null
  },
  "fields": [
    "customer_lifecycle_step",
    "service_request_step",
    "primary_service",
    "issue",
    "sentiment"
  ]
}
```

Phản hồi:

```text
202 Accepted
```

---

## 10.2 Trạng thái công việc dự đoán (Prediction Job Status)

```http
GET /api/v1/ai/prediction-jobs/{job_id}
```

---

## 10.3 Các dự đoán của Mục phản hồi (Feedback Item Predictions)

```http
GET /api/v1/feedback-items/{id}/predictions
```

Các bộ lọc:

```text
field_name
prediction_run_id
latest_only
```

Phản hồi nhóm các ứng viên theo trường và giữ nguyên phiên bản mô hình/phân loại.

---

# 11. Các API Quyết định Phân loại (Classification Decision APIs)

## 11.1 Lịch sử Quyết định (Decision History)

```http
GET /api/v1/feedback-items/{id}/decisions
```

Trả về các phiên bản bất biến, phiên bản mới nhất xếp trước.

---

## 11.2 Phân loại hiện tại (Current Classification)

```http
GET /api/v1/feedback-items/{id}/current-classification
```

Phản hồi:

```json
{
  "data": {
    "feedback_item_id": "uuid",
    "current_decision_id": "uuid",
    "current_decision_version": 3,
    "projection_version": 3,
    "taxonomy_release_id": "uuid",
    "customer_lifecycle": {
      "value_status": "KNOWN",
      "stage": {"id": "uuid", "code": "RES", "name_vi": "Cư trú"},
      "step": {"id": "uuid", "code": "RES-03", "name_vi": "Ra vào & di chuyển"}
    },
    "service_request": {
      "value_status": "NOT_APPLICABLE",
      "step": null
    },
    "primary_service": {
      "value_status": "KNOWN",
      "service": {"id": "uuid", "code": "SV-07"}
    },
    "issue": {
      "value_status": "KNOWN",
      "issue": {"id": "uuid", "code": "IS-07-01"}
    },
    "sentiment": "NEGATIVE",
    "operational_severity": "SEV-3",
    "cause_determination_status": "UNKNOWN",
    "candidate_causes": []
  }
}
```

---

## 11.3 Tạo Quyết định Phân loại (Create Classification Decision)

Ghi đánh giá chuẩn hóa (canonical review write):

```http
POST /api/v1/feedback-items/{id}/decisions
```

Yêu cầu:

```json
{
  "expected_current_decision_id": "uuid-or-null",
  "expected_projection_version": 3,
  "taxonomy_release_id": "uuid",

  "customer_lifecycle": {
    "value_status": "KNOWN",
    "step_id": "uuid"
  },

  "service_request": {
    "value_status": "NOT_APPLICABLE",
    "step_id": null
  },

  "primary_service": {
    "value_status": "KNOWN",
    "service_id": "uuid"
  },

  "issue": {
    "value_status": "KNOWN",
    "issue_id": "uuid"
  },

  "sentiment": "NEGATIVE",
  "operational_severity": "SEV-3",

  "cause_determination_status": "SUGGESTED",
  "candidate_causes": [
    {
      "cause_id": "uuid",
      "rank": 1,
      "confidence": 0.72,
      "rationale_masked": "..."
    }
  ],

  "other_reason": null,
  "prediction_refs": ["prediction_event_uuid"],
  "decision_source": "HUMAN_CORRECTED_AI",
  "decision_reason": "Accepted service/issue; corrected lifecycle."
}
```

Hành vi phía máy chủ:

```text
xác thực phiên bản kỳ vọng (expected version)
xác thực phiên bản phát hành phân loại (taxonomy release)
rút ra giai đoạn vòng đời từ bước
xác thực issue thuộc về service
xác thực cặp value_status/FK
xác thực quy tắc SV-10
chèn quyết định bất biến
cập nhật chiếu hiện tại (current projection)
ghi thông tin xem xét + kiểm toán
commit
```

Phản hồi `201 Created` trả về decision và projection mới.

---

## 11.4 Phím tắt Xem xét Dự đoán (Review Prediction Shortcut)

Thiết kế hệ thống công khai:

```http
POST /api/v1/ai/predictions/{prediction_id}/review
```

Endpoint này chỉ là sự tiện lợi cho giao diện người dùng (UI convenience). Nó BẮT BUỘC phải gọi nội bộ cùng một dịch vụ áp dụng quyết định (decision application service) như `POST /feedback-items/{id}/decisions`.

Yêu cầu:

```json
{
  "action": "ACCEPT",
  "expected_projection_version": 3,
  "overrides": {},
  "comment": "Prediction is correct."
}
```

Các hành động được phép:

```text
ACCEPT
CORRECT
MARK_UNKNOWN
MARK_MISSING
MARK_NOT_APPLICABLE
SPLIT_REQUIRED
SKIP
```

`ACCEPT`, `CORRECT`, `MARK_UNKNOWN`, `MARK_MISSING`, `MARK_NOT_APPLICABLE` tạo ra một ClassificationDecision bất biến cộng với ReviewEvent. `SPLIT_REQUIRED` và `SKIP` chỉ tạo ReviewEvent; việc chia tách thực tế sử dụng endpoint chia tách riêng biệt. Không một "trạng thái xem xét dự đoán" có thể thay đổi (mutable prediction review state) nào được phép trở thành một nguồn sự thật (source of truth) thay thế.

---

# 12. Các API Hàng chờ Xem xét (Review Queue APIs)

Abstraction truy vấn P0 được khuyến nghị:

```http
GET /api/v1/review-queue
```

Các bộ lọc:

```text
project_id
field_name
confidence_lt
service_code
severity
age_gt_minutes
q
limit
cursor
```

Mục hàng chờ:

```json
{
  "feedback_item_id": "uuid",
  "reported_at": "...",
  "content_masked": "...",
  "prediction": {
    "service": {"code": "SV-07", "confidence": 0.93},
    "issue": {"code": "IS-07-01", "confidence": 0.81}
  },
  "current_projection_version": 2,
  "risk_flags": ["LOW_CONFIDENCE"]
}
```

Baseline thứ tự ưu tiên:

```text
an toàn / kích hoạt cứng (safety/hard trigger)
→ mức độ nghiêm trọng (severity)
→ đánh giá chờ xử lý cũ nhất (oldest pending review)
→ độ tin cậy thấp hơn (lower confidence)
```

---

# 13. Các API Phân tích (Analytics APIs)

Các endpoint phân tích BẮT BUỘC phải đọc từ lớp nghĩa quản trị (governed semantic layer).

## 13.1 Hợp đồng bộ lọc chung (Shared Filter Contract)

Tất cả các endpoint bảng điều khiển đều chấp nhận một ngữ cảnh bộ lọc được tuần tự hóa (serialized filter context) chung:

```text
project_id
date_from
date_to
source_system
intake_channel_code
affected_channel_code
location_id/location_scope
customer_lifecycle_stage_code
customer_lifecycle_step_code
service_request_step_code
service_code
issue_code
sentiment
operational_severity
```

Persona không được chấp nhận như một bộ lọc P0 hoặc chiều chi tiết (breakdown dimension).

Cùng một đối tượng bộ lọc BẮT BUỘC phải tái sử dụng được cho việc đi sâu (drill-down) tới `/feedback-items`.

---

## 13.2 Tóm tắt Bảng điều khiển (Dashboard Summary)

```http
GET /api/v1/analytics/summary
```

Phản hồi:

```json
{
  "data": {
    "item_volume": 18546,
    "negative_rate": 0.342,
    "unknown_rate": 0.074,
    "active_hotspots": 7,
    "top_service": {
      "code": "SV-07",
      "name_vi": "Kỹ thuật, tiện ích & tài sản chung",
      "count": 3620
    },
    "top_issue": {
      "code": "IS-07-01",
      "count": 1490
    },
    "top_location": {
      "id": "uuid",
      "name": "S2",
      "count": 620
    },
    "eligibility_definition_version": "v1"
  }
}
```

---

## 13.3 Xu hướng (Trend)

```http
GET /api/v1/analytics/trend
```

Truy vấn:

```text
metric=item_volume|negative_rate|unknown_rate|active_hotspots
grain=day|week|month
<shared filters>
```

---

## 13.4 Chi tiết theo chiều (Breakdown)

```http
GET /api/v1/analytics/breakdown
```

Truy vấn:

```text
dimension=service|issue|location|journey_stage|journey_step|service_request_step|intake_channel|affected_channel|sentiment|severity
metrics=item_volume,negative_rate,active_hotspots,trend
limit=20
<shared filters>
```

Mỗi bucket trả về tất cả các chỉ số được yêu cầu. `trend` là một chuỗi time-bucket trong cùng một ngữ cảnh chiều/bộ lọc; P0 không tính toán so sánh WoW/MoM/YoY.

Ví dụ cho `dimension=journey_step`:

```json
{
  "data": [
    {
      "dimension": {"code": "RES-03", "name_vi": "Ra vào & di chuyển"},
      "metrics": {
        "item_volume": 620,
        "negative_rate": 0.41,
        "active_hotspots": 2,
        "trend": [
          {"bucket": "2026-08-10", "item_volume": 88, "negative_rate": 0.43, "active_hotspots": 2}
        ]
      }
    }
  ],
  "meta": {"metric_definition_version": "v1", "filter_context": "opaque"}
}
```

---

## 13.5 Chất lượng Dữ liệu (Data Quality)

```http
GET /api/v1/analytics/data-quality
```

Trả về:

```text
thiếu/không xác định theo trường
tỷ lệ sử dụng SV-10
số lượng không hợp lệ
số lượng chưa phân loại
số lượng dự đoán độ tin cậy thấp
số lượng hàng chờ xem xét bị lỗi thời
```

---

## 13.6 Tính nhất quán khi Đi sâu (Drill-down Consistency)

Mỗi kết quả phân tích CÓ THỂ trả về:

```json
{
  "drilldown": {
    "resource": "/api/v1/feedback-items",
    "filter_context": "opaque-or-json-safe-filter"
  }
}
```

UI BẮT BUỘC phải tái sử dụng ngữ cảnh này thay vì dựng lại logic bộ lọc từ các nhãn biểu đồ.

---

# 14. Các API Điểm nóng (Hotspot APIs)

## 14.1 Liệt kê các Điểm nóng (List Hotspots)

```http
GET /api/v1/hotspots
```

Các bộ lọc:

```text
project_id
status
service_code
issue_code
location_id
severity
assigned_to_me
date_from
date_to
sort
limit
cursor
```

---

## 14.2 Chi tiết Điểm nóng (Hotspot Detail)

```http
GET /api/v1/hotspots/{id}
```

Phản hồi bao gồm:

```text
các chiều (dimensions)
quy tắc/phiên bản (rule/version)
trạng thái (status)
mức độ nghiêm trọng (severity)
người phụ trách (owner)
thời điểm thấy lần đầu/lần cuối (first_seen/last_seen)
số lượng bằng chứng (evidence_count)
các mục phản hồi bằng chứng (evidence feedback items)
dòng thời gian (timeline)
các nguyên nhân ứng viên nếu có (candidate causes if available)
```

---

## 14.3 Xác nhận (Acknowledge)

```http
POST /api/v1/hotspots/{id}/acknowledge
```

Yêu cầu:

```json
{
  "expected_version": 4,
  "reason": "Operations team has accepted triage."
}
```

---

## 14.4 Phân công (Assign)

```http
POST /api/v1/hotspots/{id}/assign
```

```json
{
  "expected_version": 5,
  "owner_user_id": "uuid",
  "owner_team_key": null,
  "reason": "Assign to engineering duty manager."
}
```

---

## 14.5 Bác bỏ (Dismiss)

```http
POST /api/v1/hotspots/{id}/dismiss
```

Lý do là bắt buộc.

---

## 14.6 Giải quyết (Resolve)

```http
POST /api/v1/hotspots/{id}/resolve
```

Yêu cầu:

```json
{
  "expected_version": 8,
  "reason": "Observed hotspot is no longer active after operational handling.",
  "resolution_summary": "P0 operational resolution; this does not assert a confirmed root cause."
}
```

---

## 14.7 Mở lại (Reopen)

```http
POST /api/v1/hotspots/{id}/reopen
```

Được phép từ:

```text
RESOLVED
DISMISSED
```

Yêu cầu lý do.

---

# 15. Chỉ dành cho P1 — Các API Điều tra / Nguyên nhân gốc rễ (Investigation / Root Cause APIs)

Tất cả các endpoint trong phần này đều bị loại khỏi tài liệu OpenAPI, bảng định tuyến (routing table), ma trận phân quyền (authorization matrix) và tiêu chí nghiệm thu (acceptance gate) của P0. P0 dừng lại ở bằng chứng/người phụ trách/trạng thái điểm nóng và Nguyên nhân ứng viên cơ bản.

## 15.1 Chi tiết Điều tra (Investigation Detail)

```http
GET /api/v1/investigations/{id}
```

---

## 15.2 Thêm bằng chứng (Add Evidence)

```http
POST /api/v1/investigations/{id}/evidence
```

Có thể sử dụng tham chiếu bên ngoài bằng JSON hoặc tải lên multipart.

---

## 15.3 Xác nhận Nguyên nhân gốc rễ (Confirm Root Cause)

Quyền hạn bị hạn chế:

```http
POST /api/v1/investigations/{id}/root-causes
```

Yêu cầu:

```json
{
  "expected_version": 3,
  "cause_id": "uuid-or-null",
  "root_cause_text": "Door sensor calibration drift caused repeated abnormal stops.",
  "evidence_summary": "Maintenance logs + inspection result + reproduced failure.",
  "corrective_actions": [
    {
      "description": "Recalibrate affected sensors",
      "owner_user_id": "uuid",
      "due_at": "..."
    }
  ],
  "preventive_actions": [
    {
      "description": "Add calibration check to preventive maintenance",
      "owner_team_key": "ENGINEERING",
      "due_at": "..."
    }
  ]
}
```

AI BẮT BUỘC KHÔNG ĐƯỢC gọi endpoint này với vai trò là bên xác nhận tự động.

---

# 16. Các API Kiểm toán (Audit APIs)

Admin/kiểm toán viên:

```http
GET /api/v1/audit-events
```

Các bộ lọc:

```text
project_id
actor_user_id
action
resource_type
resource_id
date_from
date_to
limit
cursor
```

PII thô mặc định không được trả về trong metadata kiểm toán.

---

# 17. Các API Xuất dữ liệu (Export APIs)

Các thao tác xuất dữ liệu P0 NÊN là bất đồng bộ đối với các tập dữ liệu lớn.

```http
POST /api/v1/exports
GET  /api/v1/exports/{id}
```

Yêu cầu:

```json
{
  "resource": "feedback_items",
  "filters": {},
  "columns": [
    "reported_at",
    "service_code",
    "issue_code",
    "location_code",
    "sentiment"
  ],
  "include_raw_content": false
}
```

Quy tắc:

- bắt buộc có `export_allowed`;
- `include_raw_content=true` yêu cầu thêm `raw_pii_allowed`;
- lý do xuất dữ liệu thô là bắt buộc;
- việc xuất dữ liệu thô sẽ được kiểm toán;
- đối tượng kết quả sử dụng URL tải xuống được ký có thời hạn ngắn.

---

# 18. Ma trận Quyền hạn API (API Permission Matrix)

| Khả năng / Quyền hạn (Capability) | VIEWER | ANALYST | REVIEWER | PILOT_ADMIN |
|---|:---:|:---:|:---:|:---:|
| Xem bảng điều khiển | ✓ | ✓ | ✓ | ✓ |
| Xem phản hồi đã che | ✓ | ✓ | ✓ | ✓ |
| Chạy các bộ lọc phân tích | ✓ | ✓ | ✓ | ✓ |
| Xuất dữ liệu đã che | policy | ✓ | ✓ | ✓ |
| Xem nội dung thô | — | policy | policy | policy |
| Chạy dự đoán AI | — | ✓ | ✓ | ✓ |
| Tạo quyết định phân loại | — | — | ✓ | ✓ |
| Chia tách Mục phản hồi | — | — | ✓ | ✓ |
| Quản lý điểm nóng | — | policy | ✓ | ✓ |
| Xác nhận nguyên nhân gốc rễ [Chỉ P1] | — | — | privilege | ✓ |
| Xác thực/xuất bản phân loại | — | — | — | ✓ |
| Xem kiểm toán | — | — | — | ✓ |

`policy` có nghĩa là vẫn bắt buộc phải có quyền hạn (privilege) và phạm vi dự án (project scope) rõ ràng.

---

# 19. Ánh xạ API sang Cơ sở dữ liệu (API-to-Database Mapping)

| Tài nguyên API (API Resource) | Nguồn dữ liệu chính (Primary Data Source) |
|---|---|
| `/feedback-items` | `analytics_feedback_item_v1` + workspace joins |
| `/feedback/{id}` | `feedback` |
| `/feedback-items/{id}` | `feedback_item` + projection + ledgers |
| `/predictions` | `prediction_event` |
| `/decisions` | `classification_decision` |
| `/current-classification` | `classification_current` |
| `/analytics/*` | governed semantic layer |
| `/hotspots` | `hotspot` + evidence/timeline |
| `/investigations` [chỉ P1] | investigation/RCA tables |
| `/audit-events` | `audit_event` |
| các truy vấn đọc phân loại | các bảng tham chiếu đã xuất bản |

---

# 20. Các yêu cầu OpenAPI (OpenAPI Requirements)

Đầu ra OpenAPI của FastAPI BẮT BUỘC phải định nghĩa:

- tất cả request/response schema;
- các enum;
- các ràng buộc xác thực (validation constraints);
- bao bì lỗi đã được ghi chép tài liệu;
- cơ chế xác thực (authentication scheme);
- hợp đồng phân trang;
- các payload mẫu;
- các operation ID đủ ổn định cho việc sinh client phía frontend.

Các operation ID được khuyến nghị:

```text
listFeedbackItems
getFeedbackItem
splitFeedbackItem
createClassificationDecision
listServices
listIssues
createImportJob
executeImportJob
getAnalyticsSummary
listHotspots
acknowledgeHotspot
```

Không công khai các mô hình ORM trực tiếp dưới dạng response schema.

---

# 21. Các mục tiêu hiệu năng (Performance Targets)

Tùy thuộc vào quy mô pilot:

```text
GET /feedback-items                 p95 < 3s
GET /feedback-items/{id}            p95 < 2s
GET /analytics/summary              p95 < 5s
GET /analytics/breakdown            p95 < 5s
các truy vấn đọc phân loại đơn giản p95 < 1s
```

Các endpoint thay đổi dữ liệu đưa công việc vào hàng chờ bất đồng bộ nên trả về nhanh chóng với `202 Accepted`.

---

# 22. Các yêu cầu bảo mật (Security Requirements)

1. Chỉ sử dụng HTTPS ngoài môi trường phát triển cục bộ.
2. Thực thi phạm vi dự án phía máy chủ.
3. Không đưa PII thô vào log/lỗi.
4. Việc xem/xuất dữ liệu thô yêu cầu quyền hạn rõ ràng và được kiểm toán.
5. Các URL đối tượng đã ký phải có thời hạn hết hạn.
6. Giới hạn tần suất (rate-limit) cho các endpoint tìm kiếm/xuất dữ liệu/dự đoán tốn kém chi phí.
7. Xác thực loại/kích thước/checksum của tệp được tải lên.
8. Từ chối các biểu thức sắp xếp/lọc tùy ý không an toàn.
9. Không tin tưởng các vai trò (role claims) do giao diện frontend cung cấp.
10. ID liên kết là định danh, không phải là token phân quyền.

---

# 23. Kiểm thử Hợp đồng (Contract Tests)

Các bài kiểm thử hợp đồng P0 BẮT BUỘC phải chứng minh:

1. truy cập dự án không có thẩm quyền trả về 403/404 theo chính sách;
2. các truy vấn đọc phân loại trả về các ID/mã ổn định đã xuất bản;
3. việc không khớp giữa issue và service trả về 422;
4. thao tác ghi quyết định lỗi thời trả về 409;
5. việc xem xét dự đoán tạo ra một Decision, không phải một bản ghi sự thật thay thế;
6. việc chia tách không làm thay đổi Feedback thô;
7. endpoint nội dung thô thực thi phân quyền và kiểm toán;
8. thử lại việc nhập dữ liệu idempotent không làm trùng lặp Feedback;
9. ngữ cảnh bộ lọc đi sâu (drill-down) phân tích tái tạo lại đúng số liệu của biểu đồ;
10. chuyển đổi trạng thái điểm nóng không hợp lệ trả về 422;
11. SV-10 mà không có `other_reason` sẽ trả về 422;
12. `KNOWN` với tham chiếu null sẽ trả về 422;
13. thao tác bất đồng bộ lớn trả về 202 cùng tài nguyên công việc;
14. API không bao giờ trả về PII thô trong các lỗi chuẩn.

---

# 24. Thứ tự xây dựng P0 (P0 Build Order)

Thứ tự triển khai được khuyến nghị:

```text
1. chủ thể xác thực + bao bì lỗi + ID liên kết
2. các endpoint đọc phân loại
3. các endpoint công việc nhập dữ liệu
4. danh sách/chi tiết phản hồi
5. các endpoint công việc/đọc dự đoán
6. các endpoint quyết định/phân loại hiện tại
7. hàng chờ xem xét
8. tóm tắt/chi tiết/xu hướng phân tích
9. danh sách/chi tiết/thay đổi điểm nóng
10. luồng công việc chia tách
11. xem/xuất dữ liệu thô có đặc quyền
12. các endpoint admin xác thực/xuất bản phân loại
13. endpoint truy vấn kiểm toán
```

---

# 25. Tiêu chí nghiệm thu API (API Acceptance Criteria)

API P0 đã sẵn sàng xây dựng khi:

- Các OpenAPI schema khớp với `05_Data_Model.md`;
- Không có endpoint nào cho phép thay đổi dữ liệu vi phạm sổ cái chỉ ghi thêm (append-only ledgers);
- Tất cả các thao tác ghi phân loại đều sử dụng cùng một dịch vụ ứng dụng;
- Hành vi xung đột phiên bản được chuẩn hóa;
- Các ID/mã ổn định được sử dụng trong các bộ lọc;
- Phân loại không bị mã hóa cứng trong UI/handler phía backend;
- Phân tích và đi sâu (drill-down) dùng chung một ngữ nghĩa bộ lọc;
- Phân tích chi tiết (breakdown) hỗ trợ `item_volume`, `negative_rate`, `active_hotspots`, và `trend` cho Hành trình/Dịch vụ và hỗ trợ bộ lọc/chiều `affected_channel`;
- Persona bị từ chối như một bộ lọc/chiều phân tích của P0;
- Tất cả các thao tác ghi xem xét đều sử dụng 7 hành động chuẩn hóa với hành vi Quyết định-so với-Sự kiện xem xét (Decision-versus-ReviewEvent) chính xác;
- P0 không công khai bất kỳ thao tác thay đổi dữ liệu nào về Điều tra/Nguyên nhân gốc rễ đã xác nhận/Hành động khắc phục/Hành động phòng ngừa;
- Ranh giới PII thô rõ ràng và được kiểm toán;
- Các bài kiểm thử hợp đồng vượt qua;
- UI có thể triển khai mọi luồng P0 bắt buộc mà không cần các giả định trực tiếp về cơ sở dữ liệu.