# Đặc tả API — Bản nháp v1

Base path: `/api/v1`

## 1. Quy ước chung

- Dùng JSON, trừ endpoint upload multipart và tải tệp.
- Mọi request cần xác thực; máy chủ kiểm tra quyền theo workspace và dataset.
- Mutation phải gửi `Idempotency-Key: <uuid>` và `base_version_id`, trừ thao tác tạo mới ban đầu.
- Thời gian dùng ISO 8601 UTC; ID là chuỗi opaque, client không suy luận cấu trúc ID.
- Tác vụ dự kiến quá 3 giây trả `202 Accepted` kèm `job_id`.
- Danh sách có phân trang và giới hạn tối đa do máy chủ cấu hình.

## 2. Nhập bộ dữ liệu

### `POST /datasets/imports`

Nhận multipart upload hoặc thông báo hoàn tất upload qua pre-signed URL.

```json
{
  "import_id": "imp_123",
  "status": "analyzing"
}
```

### `GET /datasets/imports/{import_id}`

Trả danh sách sheet, 50 dòng xem trước, schema suy luận, ước lượng số dòng và cảnh báo.

### `POST /datasets/imports/{import_id}/commit`

```json
{
  "sheet_names": ["Feedback"],
  "header_row": 1,
  "schema_overrides": {
    "reported_date": "date"
  }
}
```

Mỗi sheet đã chọn tạo một dataset. Response trả `201 Created` nếu hoàn tất đồng bộ hoặc `202 Accepted` nếu chạy nền.

## 3. Metadata bộ dữ liệu

### `GET /datasets/{dataset_id}`

### `GET /datasets/{dataset_id}/columns`

### `PATCH /datasets/{dataset_id}`

Chỉ đổi tên hoặc archive metadata; không dùng endpoint này để sửa dữ liệu bảng.

## 4. Đọc dòng dữ liệu

### `GET /datasets/{dataset_id}/rows`

Query:

```text
offset=0
limit=200
view_id=...
version_id=ver_10
```

`version_id` mặc định là phiên bản hiện tại. Khi filter/sort phức tạp, dùng endpoint `POST .../query` để tránh URL quá dài.

```json
{
  "dataset_id": "ds_1",
  "version_id": "ver_10",
  "offset": 0,
  "limit": 200,
  "total_rows": 18546,
  "filtered_rows": 3421,
  "rows": [
    {
      "_row_id": "r_1",
      "ticket_id": "T001",
      "building": "S1"
    }
  ]
}
```

## 5. Truy vấn view

### `POST /datasets/{dataset_id}/query`

```json
{
  "version_id": "ver_10",
  "filters": [
    {"column_id": "col_priority", "operator": "EQ", "value": "High"}
  ],
  "sorts": [
    {"column_id": "col_reported_date", "direction": "DESC"}
  ],
  "offset": 0,
  "limit": 200
}
```

Đây là truy vấn không phá hủy dữ liệu. Response dùng cùng cấu trúc với endpoint đọc dòng.

## 6. Sửa ô

Mọi lần sửa ô đều được ghi nội bộ thành một operation.

### `PATCH /datasets/{dataset_id}/cells`

Header:

```text
Idempotency-Key: <uuid>
```

Body:

```json
{
  "base_version_id": "ver_10",
  "changes": [
    {
      "row_id": "r_152",
      "column_id": "col_sentiment",
      "value": "Negative"
    }
  ]
}
```

Response:

```json
{
  "operation_id": "op_201",
  "result_version_id": "ver_11",
  "status": "succeeded",
  "affected_rows": 1
}
```

## 7. Xem trước operation

### `POST /datasets/{dataset_id}/operations/preview`

```json
{
  "base_version_id": "ver_11",
  "operation_type": "REMOVE_NULL_ROWS",
  "parameters": {
    "column_ids": ["col_reported_date"],
    "mode": "ANY"
  },
  "scope": {"type": "ALL_ROWS"}
}
```

Response:

```json
{
  "preview_token": "pvt_123",
  "expires_at": "2026-08-08T10:15:00Z",
  "base_version_id": "ver_11",
  "valid": true,
  "affected_rows": 231,
  "before_row_count": 18546,
  "after_row_count": 18315,
  "warnings": [],
  "sample_before": [],
  "sample_after": []
}
```

`preview_token` ràng buộc với người dùng, dataset, base version và payload đã chuẩn hóa. Apply phải bị từ chối nếu token hết hạn hoặc phiên bản đã thay đổi. Với thao tác không bắt buộc xem trước, token có thể bỏ qua.

## 8. Áp dụng operation

### `POST /datasets/{dataset_id}/operations`

Gửi cùng payload đã xem trước, thêm `preview_token` khi bắt buộc, và header idempotency.

Response đồng bộ (`200 OK`):

```json
{
  "operation_id": "op_202",
  "status": "succeeded",
  "result_version_id": "ver_12",
  "affected_rows": 231,
  "duration_ms": 842,
  "warnings": []
}
```

Response chạy nền (`202 Accepted`):

```json
{
  "operation_id": "op_202",
  "status": "running",
  "job_id": "job_1001"
}
```

## 9. Lịch sử

### `GET /datasets/{dataset_id}/operations?cursor=...&limit=50`

### `GET /datasets/{dataset_id}/operations/{operation_id}`

Danh sách sắp xếp mới nhất trước; chi tiết có tham số, phạm vi, actor, cảnh báo và mẫu trước/sau đã được giới hạn.

## 10. Undo/redo

### `POST /datasets/{dataset_id}/undo`

```json
{
  "base_version_id": "ver_12",
  "operation_id": "op_202"
}
```

MVP chỉ cho undo thao tác có thể hoàn tác gần nhất; `operation_id` giúp client và server xác nhận cùng một mục tiêu.

### `POST /datasets/{dataset_id}/redo`

```json
{
  "base_version_id": "ver_13",
  "operation_id": "op_202"
}
```

Redo bị từ chối nếu đã phát sinh nhánh chỉnh sửa mới. Cả hai endpoint cần header idempotency và trả hợp đồng operation chuẩn.

## 11. Profiling

### `GET /datasets/{dataset_id}/profile?version_id=ver_12`

### `GET /datasets/{dataset_id}/columns/{column_id}/profile?version_id=ver_12`

Response luôn nêu `version_id`, `computed_at` và trạng thái `fresh`, `stale` hoặc `computing`.

## 12. Xuất dữ liệu

### `POST /datasets/{dataset_id}/exports`

```json
{
  "version_id": "ver_12",
  "format": "xlsx",
  "scope": {"type": "ALL_ROWS"}
}
```

Với dữ liệu đã lọc, `scope` phải chứa biểu thức filter đã chuẩn hóa hoặc `saved_view_id`; không chỉ gửi chuỗi `filtered` không thể tái lập.

### `GET /exports/{export_id}`

```json
{
  "export_id": "exp_100",
  "status": "succeeded",
  "version_id": "ver_12",
  "row_count": 18315,
  "download_url": "<short-lived-signed-url>",
  "expires_at": "2026-08-08T11:00:00Z"
}
```

## 13. Trạng thái tác vụ nền

### `GET /jobs/{job_id}`

```json
{
  "job_id": "job_1001",
  "type": "operation",
  "status": "running",
  "progress": {"completed": 60000, "total": 100000, "unit": "rows"},
  "result": null,
  "error": null
}
```

Trạng thái cuối: `succeeded`, `failed` hoặc `cancelled`. Client nên dùng backoff khi polling; hỗ trợ SSE/WebSocket là phần tối ưu sau MVP.

## 14. Response lỗi

Status HTTP phải phù hợp với mã lỗi, ví dụ `400` payload sai, `401` chưa xác thực, `403` thiếu quyền, `404` không tồn tại, `409` xung đột phiên bản/idempotency và `422` lỗi kiểm tra dữ liệu.

```json
{
  "error": {
    "code": "VERSION_CONFLICT",
    "message": "Bộ dữ liệu đã thay đổi kể từ khi thao tác này được tạo.",
    "request_id": "req_...",
    "details": {
      "expected_version": "ver_11",
      "current_version": "ver_12"
    }
  }
}
```

Không đưa stack trace, dữ liệu ô nhạy cảm hoặc thông tin nội bộ vào response lỗi.
