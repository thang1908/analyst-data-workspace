# FEAT-03 — Analytics API và Feedback Drill-down

- **Status:** Ready for refinement — build sau khi dependency contract freeze
- **Priority:** P0 — one-week pilot
- **Owner:** Backend/Data Engineer
- **Branch:** `codex/feat-analytics-api` từ `dev`; pull request merge về `dev`
- **Stack:** Python 3.12+, FastAPI, Python with type hints, Pydantic/OpenAPI contracts
- **Bounded contexts:** Analytics, Feedback Exploration
- **Related:** [PRD](../PRD.md), [Build Rules](../BUILD_RULES.md), [FEAT-01](./FEAT-01-data-foundation.md), [FEAT-02](./FEAT-02-csv-import.md), [FEAT-04](./FEAT-04-dashboard-ui.md)

## 1. Outcome

Người dùng có quyền xem được KPI, xu hướng, breakdown và danh sách feedback tạo ra từng con số từ dữ liệu CSV đã gắn nhãn `SOURCE_TRUSTED`; mọi endpoint dùng cùng filter, metric và authorization semantics.

## 2. Phạm vi

### In scope

- Read API cho summary, trend ngày, breakdown service/issue/location/sentiment/severity.
- Data-quality summary từ kết quả import.
- Feedback list/detail chỉ trả nội dung masked để drill-down.
- Shared filter contract, cursor pagination, stable sort và problem response.
- Authorization theo project pilot, reconciliation, test và telemetry; building/location là filter trong project, không phải authorization scope tuần đầu.

### Non-goal

- Ghi/sửa feedback, classification, taxonomy hoặc import job.
- AI, hotspot, realtime/streaming, saved dashboard, export hoặc BI cube.
- Pilot Web UI; thuộc FEAT-04.
- Raw PII/content, cross-project benchmark hoặc custom metric builder.
- Tạo materialized view/cache khi chưa có bằng chứng performance cần thiết.

## 3. Dependency và thứ tự merge

1. FEAT-01 cung cấp schema canonical, taxonomy/location seed, DB client và trusted classification projection.
2. FEAT-02 công bố contract import/job-terminal và sẽ ghi idempotent `feedback_item`, `classification_current` cùng import counts.
3. FEAT-03 có thể merge `dev` sau FEAT-01 khi public contract/read boundary với FEAT-02 đã freeze; runtime UAT và release vẫn chờ FEAT-02 tạo representative terminal import.
4. FEAT-04 generate client từ OpenAPI của FEAT-03; không copy type hoặc công thức metric.

Không đổi schema để unblock branch. Nếu thiếu field/index, mở change request cho owner FEAT-01 và cập nhật contract trước khi code.

## 4. Code ownership

### Owned paths

```text
apps/api/src/modules/analytics/**
apps/api/src/modules/feedback/**
packages/contracts/src/analytics/**
packages/contracts/src/feedback/**
```

Unit, contract và module integration test được co-locate trong các path trên. Cross-feature E2E/reconciliation/performance ở top-level `tests/**` thuộc FEAT-05.

### Integration seams được phép sửa tối thiểu

```text
apps/api/src/app.py                  # chỉ register FastAPI plugin
```

Contract được public bằng subpath export đã scaffold trong FEAT-01; không thêm central barrel dùng chung chỉ để export feature mới.

Nếu hai branch cùng chạm integration seam, để commit registration/export riêng nhằm cherry-pick hoặc resolve dễ dàng.

### Forbidden paths

```text
apps/worker/**
apps/web/**
packages/db/migrations/**
packages/db/seeds/**
packages/domain/**
packages/contracts/src/import/**
infra/**
```

Không query trực tiếp import table. Data-quality chỉ đi qua `TerminalImportOutcomeReader` do FEAT-01 công bố và FEAT-02 review semantics. Không ghi trực tiếp vào bất kỳ bảng nào.

## 5. Population và metric semantics

Đơn vị đếm duy nhất là `feedback_item.id`, không phải CSV row, source record hay feedback envelope.

Một item đủ điều kiện khi:

- source row đã commit thành công;
- source import job đã terminal `COMPLETED|PARTIAL`; canonical row thuộc job `PROCESSING|FAILED|CANCELLED` chưa eligible cho analytics;
- không phải duplicate import attempt;
- current classification trỏ tới decision có `decision_source=SOURCE_TRUSTED`;
- record nằm trong scope được server authorize;
- `reported_at` hợp lệ và thuộc khoảng ngày được chọn;
- `import_job.completed_at <= snapshot_at` được ký trong `snapshot_token` của request.

| Metric | Định nghĩa |
| --- | --- |
| `item_volume` | `count(distinct feedback_item.id)` sau authorization và filter |
| `negative_feedback_count` | item đủ điều kiện có sentiment `NEGATIVE` |
| `sentiment_known_count` | item có `sentiment <> UNKNOWN` |
| `sentiment_unknown_count` | item có `sentiment = UNKNOWN` |
| `negative_rate` | `negative_feedback_count / sentiment_known_count`; `null` nếu mẫu số bằng 0 |
| `sentiment_unknown_rate` | `sentiment_unknown_count / item_volume`; `null` nếu tổng bằng 0 |
| `high_severity_count` | item có operational severity `SEV-1` hoặc `SEV-2` |
| bucket `count` | distinct item trong bucket sau toàn bộ common filter |
| bucket `share` | bucket count chia `item_volume` của cùng query |

- Dùng `reported_at`, không fallback sang `ingested_at`.
- Date filter là ngày địa phương, hai đầu inclusive; server đổi thành `[00:00 date_from, 00:00 date_to+1)` theo timezone cấu hình pilot `Asia/Ho_Chi_Minh`.
- Default là hôm nay và 6 ngày trước; tối đa 90 ngày. `date_from > date_to` hoặc vượt 90 ngày trả `422`.
- Trend dùng bucket ngày, trả cả ngày bằng 0 và sắp xếp tăng dần.
- Breakdown sắp `count DESC, key ASC`; `limit` mặc định 10, tối đa 50; phần còn lại vào `other_count`.
- Label lấy từ taxonomy/reference API hoặc projection; không hard-code label trong response builder.
- Data quality bucket/filter theo `import_job.completed_at` của terminal execution, không dùng `feedback.ingested_at` vì invalid/duplicate row không tạo feedback; UI phải ghi rõ đây là cửa sổ hoàn tất nhập liệu.

## 6. Shared filter contract

Các endpoint analytics và feedback list dùng chung `AnalyticsFilterSchema`:

```text
date_from, date_to
project_code[], building_code[], location_code[]
service_code[], issue_code[]
sentiment[], operational_severity[]
snapshot_token
```

- Array encode bằng query param lặp lại, ví dụ `service_code=SVC-17&service_code=SVC-18`.
- OR trong cùng field; AND giữa các field.
- Mỗi field tối đa 50 giá trị; trim, reject empty và duplicate được normalize.
- Enum/code sai trả `422 INVALID_FILTER_VALUE`; combination hợp lệ nhưng không có dữ liệu trả tập rỗng.
- Server intersect filter với scope. Request rõ ràng ngoài scope trả `403 SCOPE_NOT_ALLOWED` mà không tiết lộ record count.
- `snapshot_token` là token opaque do context endpoint cấp, chứa `snapshot_at`, metric version và project-scope fingerprint; client không tự tạo/chỉnh token.
- Response trả `applied_filters`, `timezone`, `metric_definition_version`, `snapshot_token` và `snapshot_at` để UI hiển thị/đối soát.
- Summary, trend, mọi breakdown và feedback list trong một dashboard interaction bắt buộc dùng cùng token. Token hết hạn/sai scope trả `409 SNAPSHOT_EXPIRED_OR_INVALID`; UI lấy context mới và refresh toàn bộ widgets.

Data-quality dùng contract riêng vì invalid/duplicate row không có Service/Issue/Sentiment:

```text
completed_from, completed_to
project_code[]
snapshot_token
```

`DataQualityFilter` chỉ áp dụng project authorization và `import_job.completed_at`; không nhận building/location/service/issue/sentiment/severity filter.

## 7. API contract

```http
GET /api/v1/analytics/context
GET /api/v1/analytics/summary
GET /api/v1/analytics/trend
GET /api/v1/analytics/breakdowns/{dimension}
GET /api/v1/analytics/data-quality
GET /api/v1/feedback-items
GET /api/v1/feedback-items/{id}
```

`dimension` chỉ nhận `service|issue|location|sentiment|operational_severity`.

Context response trả timezone, `metric_definition_version`, `snapshot_token`, `snapshot_at`, allowed project và filter options có code/label cho building/location/service/issue/sentiment/severity. Issue option kèm `service_code`; location option kèm parent/building code. Options đã intersect project scope và lấy từ reference release, không hard-code hoặc suy ra từ UI. Snapshot token có TTL 30 phút và không chứa PII/filter values.

Summary response tối thiểu:

```json
{
  "data": {
    "item_volume": 120,
    "negative_feedback_count": 36,
    "sentiment_known_count": 120,
    "sentiment_unknown_count": 0,
    "negative_rate": 0.3,
    "sentiment_unknown_rate": 0,
    "high_severity_count": 12
  },
  "meta": {
    "timezone": "Asia/Ho_Chi_Minh",
    "metric_definition_version": "feedback-dashboard-v1",
    "snapshot_token": "opaque-signed-token",
    "snapshot_at": "2026-08-10T08:00:00Z",
    "applied_filters": {}
  }
}
```

Data-quality response có `total_rows`, `committed_rows`, `invalid_rows`, `duplicate_rows`; invariant trong cùng cửa sổ là `total_rows = committed_rows + invalid_rows + duplicate_rows`. Chỉ tính execution terminal `COMPLETED|PARTIAL`; job mới validate/chưa execute, `FAILED` trước execute hoặc `CANCELLED` được theo dõi ở operational import view, không trộn vào reconciliation dashboard. Partial/retry không được double-count logical row.

Feedback list:

- default `limit=25`, max 100;
- sort cố định `reported_at DESC, id DESC`;
- cursor opaque chứa sort key, filter hash và snapshot hash; cursor dùng với filter/snapshot khác trả `400 CURSOR_FILTER_MISMATCH`;
- item trả ID, reported time, project/building/location, trusted labels, severity, sentiment và `content_masked`;
- không trả `content_raw`, storage key, internal actor data hoặc import payload.

Feedback detail áp dụng cùng scope và chỉ trả masked source context. Response được phép trả `source_reference` vì contract v1 yêu cầu đây là operational non-PII key đã được source-trust policy duyệt; không trả source payload/storage key. ID không tồn tại hoặc ngoài scope trả generic `404 FEEDBACK_ITEM_NOT_FOUND`.

Mọi lỗi dùng problem schema chung gồm `code`, `message`, `correlation_id`, `field_errors`; không trả SQL, stack trace hoặc raw filter data nhạy cảm.

## 8. Implementation rules

- FastAPI route chỉ parse/auth/serialize; công thức nằm trong analytics application/query service.
- Repository nhận normalized filter object; không nhận raw query string.
- Dùng parameterized SQL/query builder; mọi aggregate và drill-down dùng cùng population predicate helper.
- Scope predicate luôn được thêm trong repository, không phụ thuộc caller nhớ truyền.
- Không N+1 khi resolve label; load/join theo batch.
- Không cache trong pilot. `snapshot_at` đóng băng eligibility population cho một interaction; UI refresh rõ ràng bằng cách lấy context/token mới.
- OpenAPI sinh từ Pydantic contract; implementation và generated spec phải pass contract test.

## 9. Acceptance criteria

| AC | Given / When / Then |
| --- | --- |
| AC-01 Summary | **Given** 10 committed items, một duplicate retry và hai invalid rows; **When** gọi summary; **Then** total là 10 và negative rate dùng đúng known denominator. |
| AC-02 Filter | **Given** filter date/service/issue/location và một snapshot token; **When** gọi summary, trend, breakdown và list; **Then** tất cả dùng cùng normalized filter, timezone, snapshot và population. |
| AC-03 Drill-down | **Given** bucket count `N` và import mới hoàn tất sau `snapshot_at`; **When** thêm bucket key rồi paginate hết list bằng cùng token; **Then** vẫn có đúng `N` distinct item; refresh token mới mới được thấy item mới. |
| AC-04 Date | **Given** item quanh biên ngày `Asia/Ho_Chi_Minh`; **When** query một ngày; **Then** chỉ item trong half-open UTC interval tương ứng được tính. |
| AC-05 Auth | **Given** user không có pilot project scope; **When** query aggregate/list/detail; **Then** không lộ count/existence và nhận error theo policy. |
| AC-06 Privacy | **Given** item có raw và masked content; **When** đọc list/detail; **Then** chỉ masked content được trả và log/trace không chứa content. |
| AC-07 Quality | **Given** import completed/partial/retried; **When** gọi data-quality; **Then** count không double-count và invariant tổng khớp. |
| AC-08 Empty/error | **Given** filter hợp lệ không có item hoặc filter sai; **When** query; **Then** trường hợp đầu trả `200` zero/empty, trường hợp sau trả stable `422`. |
| AC-09 Context | **Given** authorized pilot user; **When** gọi context; **Then** options chỉ gồm code/label/mapping trong project scope và token dùng được đồng nhất cho analytics/list. |
| AC-10 Snapshot expiry | **Given** token hết hạn/sai scope; **When** query widget/list; **Then** API trả stable `409`, không trả partial mixed-snapshot data. |

## 10. Test strategy

| Loại | Cases bắt buộc |
| --- | --- |
| Unit | normalize analytics/DQ filter; snapshot sign/verify/expiry; date boundary/DST-safe conversion; rate null denominator; bucket sort/share |
| Integration | snapshot population under concurrent import; duplicate exclusion; zero-fill trend; pagination; terminal-import data-quality reader |
| Contract | context/options, Pydantic/OpenAPI success và `400/403/404/409/422`; unknown additive response field |
| Authorization | allowed, mixed-scope, out-of-scope aggregate/list/detail |
| Reconciliation | summary ↔ trend ↔ bucket ↔ paginated list trên frozen fixture |
| Privacy | response/log/trace snapshot không có raw content, PII, SQL hoặc storage key |
| Performance | 100k items pilot, 90 ngày, common filters: p95 mỗi endpoint dưới 2 giây trên staging |

Fixture phải có positive/negative, unknown sentiment, SEV-1..4, midnight boundary, duplicate source key và invalid row. Authorization suite dùng một record thuộc synthetic project ngoài pilot để chứng minh project denial; không giả lập fine-grained building scope trong tuần đầu.

## 11. Telemetry và SLI

Structured log fields: `correlation_id`, `request_id`, `route`, `actor_id`, scope count, filter-field count, outcome, safe error code, duration. Không log content hoặc toàn bộ filter values.

Metrics:

```text
analytics_requests_total{route,outcome}
analytics_request_duration_seconds{route}
analytics_reconciliation_error_total
feedback_query_requests_total{route,outcome}
feedback_query_duration_seconds{route}
```

Không dùng project/building/user/code làm metric label. Trace gồm auth → normalize filter → repository → serialize. Alert p95/error/reconciliation chỉ bật khi FEAT-05 cung cấp owner và runbook.

## 12. Rollout, rollback và DoD

- Flag `trusted_csv_analytics_api`, mặc định off ngoài test.
- Deploy sau migration/seed FEAT-01 và representative import FEAT-02; reconcile source → committed item → summary → list trước khi bật pilot.
- Stop rollout nếu có scope leak, raw-content exposure, reconciliation mismatch hoặc p95 vượt 2 giây liên tục theo release rule.
- Rollback bằng tắt flag và rollback application tương thích schema; không xóa canonical data.

Feature Done khi mọi AC có automated evidence, contract/client generation pass, authorization/privacy tests pass, reconciliation bằng 0 trên frozen fixture, performance budget đạt và FEAT-04 có thể dùng OpenAPI mà không cần type/formula riêng.

## 13. Open decisions không chặn build

- Index bổ sung sau performance run — owner FEAT-01; chỉ thêm qua migration riêng.
- Mở rộng date range trên 90 ngày — Product quyết định sau pilot evidence.
- Cache/materialized projection — Architecture quyết định nếu p95 không đạt sau query/index tuning.
