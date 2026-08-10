# ADR-001 — Tách hai chiều Lifecycle độc lập

- **Status:** Accepted
- **Date:** 2026-08-10
- **Scope:** MVP baseline
- **Related:** [PRD](../../PRD.md), [Service Taxonomy](../../service_taxonomy.md), [Build Rules](../../BUILD_RULES.md), [FEAT-001](../../features/FEAT-001-elevator-manual-slice.md)

## Context

Journey Dictionary hiện chứa hai loại khái niệm khác bản chất:

1. `Customer Lifecycle`: Nhận thức, Xem xét, Giao dịch, Nhận nhà, Cư trú với các step `A*`, `C*`, `TR-*`, `HO-*`, `RES-*`.
2. `Service Request Lifecycle`: Tìm thông tin, Gửi yêu cầu, Phê duyệt, Thanh toán, Được phục vụ, Theo dõi, Hoàn tất, Đánh giá với các step `SRV-*`.

Hai loại này không loại trừ nhau. Một feedback có thể đồng thời nói về trải nghiệm “Di chuyển trong tòa” (`RES-06`) và được ghi nhận ở bước “Gửi yêu cầu” (`SRV-02`). Nếu đặt `Dịch vụ` ngang hàng như một customer-journey stage duy nhất, hệ thống buộc phải mất một chiều hoặc tạo label mơ hồ.

## Decision

Hệ thống mô hình hóa hai dimension trực giao:

### Dimension A — Customer Lifecycle

```text
customer_lifecycle_stage
customer_lifecycle_step
```

Bao gồm:

- Nhận thức — `A*`
- Xem xét — `C*`
- Giao dịch — `TR-*`
- Nhận nhà — `HO-*`
- Cư trú — `RES-*`

Dimension này trả lời: **khách đang ở đâu trong hành trình/lifecycle trải nghiệm?**

### Dimension B — Service Request Lifecycle

```text
service_request_step
```

Bao gồm `SRV-01..SRV-08` và trả lời: **yêu cầu/dịch vụ đang ở bước nào trong vòng đời phục vụ?**

Mỗi feedback item có thể có tối đa một step ở mỗi dimension và có thể có cả hai. Không ép một dimension từ dimension còn lại.

## Domain rules

1. `customer_lifecycle_step` phải thuộc đúng `customer_lifecycle_stage`.
2. `service_request_step` không được lưu như Customer Lifecycle Stage.
3. `Journey Step ↔ Service` vẫn là N:N, nhưng mapping phải mang `journey_dimension` hoặc dùng hai relation rõ tên.
4. Field chưa đủ bằng chứng dùng `UNKNOWN`; field không áp dụng dùng `NOT_APPLICABLE`; không gán một step mặc định để tăng coverage.
5. Classification decision và prediction lưu taxonomy version của cả hai dimension.
6. Filter, API và metric phải đặt tên dimension rõ; không dùng một field chung `journey_step` mà không có dimension type.
7. Dashboard không cộng Customer Lifecycle và Service Request Lifecycle vào cùng hierarchy/tổng số.
8. Service Request Lifecycle có thể đến từ workflow/source metadata; không bắt buộc suy luận từ content.

## Application to FEAT-001

Với feedback:

```text
"Thang máy S2 sáng nào cũng phải chờ rất lâu."
```

accepted Customer Lifecycle là:

```text
Stage = Cư trú
Step  = RES-06 — Di chuyển trong tòa
```

Service Request Lifecycle để `UNKNOWN` hoặc `NOT_APPLICABLE` nếu source không chứng minh feedback đang ở bước nào của workflow. Không tự gán `SRV-02` chỉ vì nội dung là một lời phàn nàn.

## Data/API implications

Tên field baseline:

```text
customer_lifecycle_stage_id
customer_lifecycle_step_id
service_request_step_id
taxonomy_release_id
```

API filter/UI label phải dùng:

- `customer_lifecycle_stage`
- `customer_lifecycle_step`
- `service_request_step`

Nếu dùng một bảng lifecycle step chung, mỗi row bắt buộc có `dimension_type = CUSTOMER_LIFECYCLE | SERVICE_REQUEST_LIFECYCLE`; database constraint bảo đảm prefix/stage relationship hợp lệ.

## Alternatives considered

### Một hierarchy có sáu stage

Rejected vì “Dịch vụ” không phải một lifecycle stage loại trừ “Cư trú/Giao dịch”; một feedback có thể thuộc cả hai.

### Chỉ giữ Customer Lifecycle

Rejected vì mất thông tin vòng đời phục vụ, khó phân tích friction ở bước gửi/phê duyệt/theo dõi/hoàn tất.

### Một field multi-label không định type

Rejected vì API/filter/metric mơ hồ, constraint yếu và dễ double-count.

## Consequences

### Positive

- Giữ được cả trải nghiệm lifecycle và workflow phục vụ.
- Filter/analytics có semantics rõ.
- AI có thể abstain từng dimension độc lập.
- Tránh biến `SRV-*` thành stage cạnh tranh với `RES-*`.

### Cost

- Schema/API/UI có thêm field/filter.
- Taxonomy mapping và training/evaluation cần biết dimension type.
- Dataset hoặc tài liệu lịch sử đang mã hóa sáu stage cần compatibility mapping/migration theo decision này.

## Migration/validation

- Gán `A/C/TR/HO/RES` vào dimension `CUSTOMER_LIFECYCLE`, `SRV` vào `SERVICE_REQUEST_LIFECYCLE`.
- Validator reject row có prefix/dimension không khớp.
- Dữ liệu lịch sử ở “Dịch vụ” được chuyển sang `service_request_step_id`, không ghi thành Customer Lifecycle Stage.
- Reconciliation báo số record trước/sau theo từng dimension; không xóa historical classification.
