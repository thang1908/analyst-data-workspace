# Mô hình dữ liệu logic

Các tên bảng, trường và giá trị enum được giữ bằng tiếng Anh để có thể dùng trực tiếp khi triển khai.

## 1. Workspace

```text
workspace
- id UUID PK
- name
- created_at
- updated_at
```

## 2. Thành viên workspace

```text
workspace_member
- workspace_id UUID FK
- user_id UUID FK
- role ENUM(owner, editor, viewer)
- created_at
```

Khóa chính ghép: `(workspace_id, user_id)`.

## 3. Bộ dữ liệu

```text
dataset
- id UUID PK
- workspace_id UUID FK
- name
- source_type ENUM(csv, xlsx, database, warehouse)
- source_filename
- raw_object_uri
- current_version_id UUID FK nullable
- row_count bigint
- column_count integer
- status ENUM(importing, ready, failed, archived)
- created_by UUID FK
- created_at
- updated_at
```

`database` và `warehouse` là giá trị dành cho Giai đoạn 1.3; MVP chỉ tạo `csv` và `xlsx`.

## 4. Cột dữ liệu

```text
dataset_column
- id UUID PK
- dataset_id UUID FK
- stable_key
- name
- display_name
- logical_type ENUM(text, integer, decimal, boolean, date, datetime)
- nullable
- ordinal integer
- inferred_type nullable
- inference_confidence decimal nullable
- created_at
- updated_at
```

Không nhận diện cột chỉ bằng tên hiện tại vì thao tác đổi tên phải giữ được lineage. `stable_key` không đổi trong suốt vòng đời cột.

## 5. Phiên bản bộ dữ liệu

```text
dataset_version
- id UUID PK
- dataset_id UUID FK
- parent_version_id UUID FK nullable
- version_number bigint
- snapshot_uri nullable
- originating_operation_id UUID FK nullable
- row_count bigint
- column_count integer
- materialized bool
- created_by UUID FK
- created_at
```

Phiên bản nhập đầu tiên không bắt buộc có `parent_version_id`. Mỗi phiên bản sau chỉ có một phiên bản cha trong MVP; branching đầy đủ chưa thuộc phạm vi.

## 6. Thao tác

```text
operation
- id UUID PK
- dataset_id UUID FK
- base_version_id UUID FK
- result_version_id UUID FK nullable until success
- operation_type
- parameters JSONB
- scope JSONB nullable
- affected_rows bigint nullable
- status ENUM(pending, running, succeeded, failed, reverted)
- reversible bool
- idempotency_key
- error_code nullable
- created_by UUID FK
- created_at
- completed_at nullable
```

Quan hệ chuẩn: một thao tác đọc một `base_version_id` và khi thành công tạo đúng một `result_version_id`; một phiên bản kết quả chỉ do tối đa một thao tác tạo. Hai khóa tham chiếu chéo phải được tạo bằng migration có thứ tự hoặc ràng buộc deferred.

## 7. View đã lưu

```text
saved_view
- id UUID PK
- dataset_id UUID FK
- name
- filters JSONB
- sorts JSONB
- visible_columns JSONB
- column_layout JSONB
- created_by UUID FK
- created_at
- updated_at
```

View chỉ chứa trạng thái trình bày/truy vấn, không làm thay đổi dữ liệu.

## 8. Tác vụ xuất

```text
export_job
- id UUID PK
- dataset_id UUID FK
- version_id UUID FK
- format ENUM(csv, xlsx)
- scope JSONB
- status ENUM(pending, running, succeeded, failed, expired)
- output_uri nullable
- row_count bigint nullable
- error_code nullable
- created_by UUID FK
- created_at
- completed_at nullable
- expires_at nullable
```

## 9. Ràng buộc quan trọng

- tên cột và `stable_key` là duy nhất trong một dataset;
- `(dataset_id, version_number)` là duy nhất;
- idempotency key là duy nhất trong ngữ cảnh `(dataset_id, created_by)`;
- `base_version_id` và `result_version_id` phải thuộc cùng dataset với operation;
- `current_version_id` phải thuộc chính dataset đó;
- một phiên bản kết quả chỉ tham chiếu tối đa một operation nguồn;
- `inference_confidence` nằm trong khoảng 0–1;
- không được ghi đè URI nguồn thô qua đường xử lý thông thường;
- các bản ghi metadata quan trọng nên dùng soft delete/audit thay vì xóa vật lý;
- mọi thời gian được lưu ở UTC và chuyển đổi theo múi giờ khi hiển thị.
