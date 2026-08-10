# FEAT-04 — Pilot Web UI: Import to Dashboard

- **Status:** Ready for refinement — build với contract mock đã duyệt
- **Priority:** P0 — one-week pilot
- **Owner:** Frontend Engineer
- **Branch:** `codex/feat-pilot-web-ui` từ `dev`; pull request merge về `dev`
- **Stack:** React, Vite, TypeScript; không dùng Next.js trong pilot
- **Personas:** CX Analyst, CX Manager
- **Bounded contexts:** Feedback Intake, Analytics, Feedback Exploration
- **Related:** [PRD](../PRD.md), [Build Rules](../BUILD_RULES.md), [FEAT-01](./FEAT-01-data-foundation.md), [FEAT-02](./FEAT-02-csv-import.md), [FEAT-03](./FEAT-03-analytics-api.md), [FEAT-05](./FEAT-05-release-quality.md)

## 1. Outcome

Người dùng có quyền có thể xem dữ liệu CSV trusted dưới dạng KPI và biểu đồ, áp dụng filter nhất quán, click mọi segment để drill-down về đúng feedback masked tạo ra con số và quay lại mà không mất context.

## 2. Phạm vi

### In scope

- Dashboard overview với KPI, trend và breakdown.
- Import control tối thiểu: upload CSV, theo dõi validate, xem counts/error và execute/retry theo capability FEAT-02.
- Filter theo ngày, project, building, service, issue, location, sentiment và severity.
- Feedback drill-down list và masked detail.
- URL là source of truth cho filter, pagination context và điều hướng back.
- Contract mock để build trước API, sau đó thay bằng generated clients FEAT-02/030.
- Loading, refreshing, empty, partial error, fatal error, permission và offline state.
- Responsive layout, keyboard support, accessible chart alternative, tests và telemetry.

### Non-goal

- Reusable column mapper, spreadsheet row editor, drag-drop nhiều file, sửa classification/taxonomy hoặc xem raw content.
- Tính metric, aggregate hoặc authorization ở browser.
- AI, hotspot, alert, saved dashboard, export, custom chart và realtime push.
- User-configurable timezone; pilot hiển thị timezone từ API.
- Native mobile app hoặc pixel-perfect support cho legacy browser.

## 3. Dependency và cách build song song

1. FEAT-02 là source of truth cho import endpoint, job state/capability, counts, errors và command concurrency.
2. FEAT-03 là source of truth cho analytics context/options, filter, metric, snapshot và feedback read contract.
3. Frontend bắt đầu bằng contract fixtures có cùng success/problem schema; MSW/mock adapter chỉ thay transport.
4. Khi OpenAPI FEAT-02/030 sẵn sàng, generate client/types vào path quy định và chạy cùng bộ mock/contract tests.
5. Không merge `dev` nếu generated clients khác mock schema hoặc import/drill-down reconciliation chưa pass.
6. FEAT-01/020 phải có representative masked dataset trước staging UAT.

Mock không được thêm field “tạm” ngoài contract. Mỗi mock response phải validate bằng generated/Pydantic schema; không dùng `as unknown as` để ép kiểu.

## 4. Code ownership

### Owned paths

```text
apps/web/src/features/dashboard/**
apps/web/src/features/feedback/**
apps/web/src/features/imports/**
apps/web/src/client/generated/**       # chỉ output của generator
apps/web/src/mocks/contracts/import/**
apps/web/src/mocks/contracts/analytics/**
apps/web/src/mocks/contracts/feedback/**
```

Unit/component/contract-mock test được co-locate trong các path trên. Cross-feature E2E ở top-level `tests/e2e/**` thuộc FEAT-05; FEAT-04 cung cấp scenario và selector ổn định cho test đó.

### Integration seams được phép sửa tối thiểu

```text
apps/web/src/app/router.tsx            # chỉ register routes/lazy modules
apps/web/src/client/index.ts           # configure base URL/auth/correlation
apps/web/src/mocks/browser.ts          # chỉ register feature handlers
```

Giữ registration/export trong commit riêng nếu có nguy cơ conflict khi merge `dev`.

### Forbidden paths

```text
apps/api/**
apps/worker/**
packages/db/**
packages/domain/**
packages/contracts/**
infra/**
```

- Không hand-edit file trong `client/generated`; thay đổi phải bắt đầu từ OpenAPI FEAT-02/030 tương ứng rồi regenerate.
- Không copy API type, taxonomy label, enum hoặc metric formula vào feature source.
- Không đọc database, CSV hay import state trực tiếp từ web.
- Không thêm global state/library hoặc đổi design-system token ngoài PR riêng đã được thống nhất.

## 5. Routes và URL state

```text
/imports
/imports/new
/imports/:importJobId
/dashboard
/feedback
/feedback/:feedbackItemId
```

URL query dùng đúng tên filter FEAT-03:

```text
date_from, date_to
project_code, building_code, location_code
service_code, issue_code
sentiment, operational_severity
cursor
```

- Multi-select encode bằng query param lặp lại; serialize theo thứ tự ổn định.
- Default lần đầu: 7 ngày gồm hôm nay theo timezone API; default phải xuất hiện trong URL sau hydrate.
- Form giữ draft local; chỉ request và update URL khi user chọn **Áp dụng**.
- **Xóa bộ lọc** trở về default 7 ngày và bỏ cursor.
- Mọi thay đổi filter bỏ cursor; pagination chỉ thay cursor.
- Unknown/invalid URL value được loại an toàn, hiển thị notice và không crash.
- Dashboard → list truyền nguyên common filter rồi thêm bucket key được click.
- List → detail giữ search string. Back từ detail/list trở về đúng filter; direct bookmark detail có fallback về `/feedback`.
- `snapshot_token` không được đưa vào shareable route URL. Runtime lấy token từ analytics context, giữ token cho mọi widget/list request trong interaction và lấy token mới khi reload/explicit refresh.
- Nếu reload/share URL có `cursor` nhưng không còn matching snapshot token, UI bỏ cursor, lấy context mới và tải lại trang đầu với notice an toàn.
- Không đưa actor, content, token hoặc internal ID nhạy cảm vào URL/telemetry.

## 6. Import UI

- `/imports/new` chỉ nhận một `.csv`, hiển thị constraints `trusted-feedback-csv/v1`, project pilot và progress upload; không đọc/render toàn file trong browser.
- Sau upload, UI chuyển tới `/imports/:importJobId`. Chỉ poll có backoff khi state là `VALIDATING|QUEUED|PROCESSING`; dừng ở action-required `MAPPED|VALIDATED`, mọi terminal state hoặc khi route unmount.
- Job detail hiển thị state, version, total/valid/invalid/duplicate/committed counts, safe error summary, taxonomy/location release và timestamps từ API.
- Nút **Validate**, **Execute valid rows** và **Retry** chỉ bật khi capability/state từ FEAT-02 cho phép; command luôn gửi `expected_version` mới nhất.
- `409 JOB_VERSION_CONFLICT` buộc refresh job trước khi thử lại; không tự gửi command với version đoán.
- Error download dùng endpoint FEAT-02; UI không reconstruct CSV và không hiển thị `content_masked` trong error table.
- Trước Execute, user phải xác nhận valid/invalid/duplicate counts và policy `VALID_ROWS_ONLY`.
- Khi job `COMPLETED|PARTIAL`, CTA mở dashboard với project/date context; khi `FAILED`, hiển thị safe error code, retryability và correlation ID.
- Refresh browser không upload lại file hoặc tạo job mới. Double submit/upload được chặn ở UI nhưng idempotency server vẫn là source of truth.
- Import screen có loading, no-permission, validation error, processing, partial, failed, cancelled và terminal success states; không dùng mock fallback trên staging.

## 7. Dashboard view

### Header và filter bar

- Tiêu đề, timezone, `snapshot_at`, nút refresh và trạng thái đang cập nhật; refresh lấy context/token mới rồi refresh mọi widget cùng token.
- Date range bắt buộc; các selector còn lại lấy code/label/mapping từ `GET /api/v1/analytics/context`.
- Issue selector được thu hẹp theo service nếu mapping có sẵn; server vẫn là nơi validate cuối.
- Active filters hiển thị dạng chip có accessible remove button.
- Filter bar dùng được hoàn toàn bằng bàn phím và không auto-submit mỗi keystroke.

### KPI cards

| Card | Giá trị từ API | Hiển thị |
| --- | --- | --- |
| Tổng feedback | `item_volume` | số nguyên, không suy ra từ chart |
| Feedback tiêu cực | `negative_feedback_count` | count và link drill-down sentiment `NEGATIVE` |
| Tỷ lệ tiêu cực | `negative_rate` | phần trăm; hiển thị “Chưa đủ dữ liệu” khi `null` |
| Sentiment chưa xác định | `sentiment_unknown_rate` | phần trăm và link drill-down `UNKNOWN`; không gộp vào denominator tỷ lệ tiêu cực |
| Mức độ cao | `high_severity_count` | count của `SEV-1/SEV-2`, click drill-down với hai filter values |

UI không tự đổi denominator, cộng buckets hoặc suy diễn count khi endpoint lỗi.

### Charts

- Trend feedback theo ngày: line/bar với zero bucket giữ nguyên từ API.
- Breakdown theo Service, Issue và Location: horizontal bar, top buckets và “Khác” nếu API trả `other_count`.
- Sentiment và Operational Severity: bar/donut nếu chart library đáp ứng accessibility.
- Sort, percentage và label dùng nguyên response FEAT-03; không sort lại theo label trừ view table.
- Click/keyboard activate bucket mở `/feedback` với cùng filter và bucket key.
- Segment “Khác” không drill-down nếu API không trả tập keys; hiển thị explanatory tooltip/text.
- Mỗi chart có heading, concise summary và nút chuyển sang accessible data table.

### Data-quality panel

- Hiển thị `total_rows`, `committed_rows`, `invalid_rows`, `duplicate_rows` của execution terminal `COMPLETED|PARTIAL` theo ingest window.
- Ghi rõ data-quality dùng `import_job.completed_at`, khác với chart dùng `reported_at`.
- Panel chỉ áp dụng completed-date/project filter; Service/Issue/Location/Sentiment/Severity filter không áp dụng và UI phải nói rõ thay vì làm người dùng hiểu nhầm.
- Không trộn invalid/duplicate rows vào `item_volume`.
- Nếu invariant tổng không khớp, hiển thị warning an toàn và phát telemetry; không tự sửa số.

## 8. Feedback drill-down và detail

Feedback list hiển thị:

- reported time theo timezone API;
- project/building/location;
- service, issue, sentiment, severity;
- `content_masked` có giới hạn hiển thị và nút mở detail;
- pagination Next/Previous theo opaque cursor, không tự tạo page number.

List heading mô tả filter nguồn, `snapshot_at` và tổng context. Dùng cùng token thì `N` từ bucket phải giữ đúng dù import mới hoàn tất; chỉ explicit refresh/token mới được đổi số.

Detail hiển thị masked content, source reference an toàn, trusted classification labels và reported time. Không có nút reveal raw content. `404` hiển thị “Không tìm thấy hoặc bạn không có quyền”, không phân biệt hai trường hợp.

## 9. Async và failure states

| State | Hành vi bắt buộc |
| --- | --- |
| Initial loading | skeleton giữ layout, `aria-busy=true`, status text cho screen reader |
| Filter refresh | giữ dữ liệu cũ nhưng đánh dấu stale/đang cập nhật; disable submit trùng; cancel request cũ |
| Empty | `200` và total 0: giải thích không có dữ liệu, cho xóa filter; không render chart giả |
| Widget error | widget có safe message/retry riêng; phần còn lại vẫn dùng được |
| Fatal error | summary/filter bootstrap lỗi: page error với correlation ID và Retry |
| `401` | chuyển qua auth flow chuẩn, không loop |
| `403` | full no-permission state, không render count/charts cũ |
| `404` detail | generic not-found-within-scope và link quay lại list |
| `409` | job version conflict: refresh job; snapshot invalid/expired: lấy context mới và refresh toàn dashboard |
| `422` | map `field_errors` về filter, focus field đầu tiên |
| Offline/timeout | giữ URL/filter, nêu kết nối lỗi và cho retry |

Response cũ không được overwrite response mới. Query key gồm normalized URL filters; request abort khi filters đổi/unmount. Error UI không hiển thị stack trace hoặc raw response body.

## 10. Responsive và accessibility

- Desktop ≥1280px: filter bar và tối đa 4 KPI/row; charts 2 cột.
- Tablet 768–1279px: KPI/charts 2 cột; filter panel có thể collapse.
- Mobile 360–767px: một cột, không horizontal page scroll; tables có labelled scroll region.
- Đạt WCAG 2.2 AA cho contrast, focus-visible và target size phù hợp.
- Có skip link; landmark/heading order đúng; mọi form control có label/instruction/error association.
- Không dùng màu làm tín hiệu duy nhất; severity/sentiment có text/icon label.
- Chart usable bằng keyboard và có data table tương đương; tooltip không chứa thông tin duy nhất.
- Focus chuyển tới page heading khi route đổi, tới error summary khi submit lỗi và trở lại trigger khi đóng dialog/drawer.
- Tôn trọng `prefers-reduced-motion`; number/chart transition không cản screen reader.
- Format số theo `vi-VN`; timestamp luôn kèm timezone/context, không format bằng machine local timezone.

## 11. Acceptance criteria

| AC | Given / When / Then |
| --- | --- |
| AC-01 Render | **Given** valid summary/trend/breakdown fixtures; **When** mở dashboard; **Then** KPI/chart hiển thị nguyên giá trị, labels và timezone từ contract. |
| AC-02 URL filter | **Given** user chọn nhiều filter; **When** Apply, refresh hoặc share URL; **Then** state/request được khôi phục giống nhau và cursor được reset đúng. |
| AC-03 Drill-down | **Given** bucket count `N` và import mới sau snapshot; **When** activate bằng click/keyboard; **Then** list mở với nguyên filter, cùng snapshot cộng bucket key và vẫn reconcile đúng `N`. |
| AC-04 Back | **Given** dashboard → list → detail; **When** Back hai lần; **Then** filter, scroll/context và route hợp lý được giữ. |
| AC-05 Empty | **Given** API trả zero/empty; **When** render; **Then** có empty guidance, không chart giả, không coi là lỗi. |
| AC-06 Partial error | **Given** một breakdown lỗi; **When** endpoint khác thành công; **Then** widget lỗi retry độc lập và KPI/chart khác vẫn dùng được. |
| AC-07 Permission | **Given** `403`; **When** response đến sau dữ liệu cũ; **Then** dữ liệu cũ bị xóa và chỉ no-permission state xuất hiện. |
| AC-08 Privacy | **Given** list/detail fixture; **When** render và telemetry chạy; **Then** không có raw content/PII/token trong DOM, URL, event hoặc console. |
| AC-09 A11y | **Given** keyboard và screen reader; **When** filter, đọc chart, drill-down, retry; **Then** mọi outcome thực hiện được không cần chuột/màu. |
| AC-10 Responsive | **Given** viewport 360/768/1280; **When** dashboard/list/detail render; **Then** nội dung không che khuất và không có page-level horizontal overflow. |
| AC-11 Import flow | **Given** authorized Analyst và CSV mixed fixture; **When** upload → validate → xác nhận → execute; **Then** UI hiển thị đúng counts/state/error download, không double-submit và mở dashboard sau terminal job. |
| AC-12 Context/snapshot | **Given** context có options/token và token hết hạn sau đó; **When** load/refresh dashboard; **Then** mọi widget dùng cùng token, options đúng mapping và expiry làm refresh toàn bộ thay vì trộn dữ liệu cũ/mới. |

## 12. Test strategy

| Loại | Cases bắt buộc |
| --- | --- |
| Unit | import command enablement/version; polling stop/backoff; context/snapshot lifecycle; URL parse/serialize; filter draft/apply/reset; formatter timezone/percent/null; query keys |
| Component | upload/job states; KPI/chart/table; masked list/detail; loading/empty/error/permission; stale response |
| Contract mock | mọi fixture validate FEAT-02/030 schema; success và `401/403/404/409/422/500` |
| Integration | generated client + MSW; upload/validate/execute/poll; abort/race; repeated query params; cursor transition |
| E2E | upload → validate → execute → dashboard; filter → chart/KPI drill-down → detail → back; refresh/share URL |
| Accessibility | axe không có critical/serious issue; keyboard order; name/role/value; table alternative |
| Visual/responsive | screenshots ở 360, 768, 1280 cho normal, empty, error, permission |
| Privacy | DOM/URL/console/telemetry scan không có `content_raw`, PII hoặc auth token |

Test dùng CSV fixture FEAT-02 và frozen response fixture FEAT-03 gồm valid/mixed import, zero data, all-negative, null rate, long Vietnamese labels, `other_count`, multi-page list, mixed scope và midnight boundary.

## 13. Telemetry và SLI

Events:

```text
dashboard_viewed
import_upload_started
import_validation_requested
import_execution_requested
import_job_terminal_viewed
dashboard_filter_applied
dashboard_refresh_completed
dashboard_widget_failed
dashboard_drilldown_opened
feedback_detail_opened
```

Payload chỉ gồm route, filter-field count, widget/dimension, outcome, duration bucket, correlation ID; không gửi filter values, content, user-entered text hoặc token.

Web vitals và client error metric phải tách route, không dùng project/building/user làm label. Target pilot: dashboard useful content p75 dưới 2.5 giây trên staging profile; filter result p95 theo API budget dưới 2 giây cộng network/render budget đã chốt FEAT-05.

## 14. Rollout và rollback

- Import routes phụ thuộc flag `trusted_csv_import`; dashboard routes phụ thuộc `trusted_csv_analytics_api` và `trusted_csv_dashboard`. Mặc định đều off ngoài test.
- Deploy internal pilot trước cho một project/building; kiểm tra count, drill-down, permission, responsive và accessibility.
- Stop rollout khi scope leak/raw exposure, reconciliation mismatch, crash loop hoặc critical accessibility blocker.
- Rollback bằng tắt UI flag; route chuyển tới safe unavailable state. Không xóa data và không fallback sang mock ở staging/production.

## 15. DoR và feature-specific DoD

### DoR

- [ ] FEAT-03 OpenAPI hoặc versioned mock contract được owner API duyệt.
- [ ] FEAT-02 import OpenAPI hoặc versioned mock contract được owner import duyệt.
- [ ] Design/wireframe cho import, dashboard, list/detail và mọi state được duyệt.
- [ ] Representative masked fixture và expected counts có checksum.
- [ ] Auth/scope behavior, timezone, browser support và performance profile đã chốt.
- [ ] Không còn quyết định làm đổi KPI/filter/drill-down contract.

### DoD

- [ ] Không có handwritten API type/metric/taxonomy label; generated client không có manual diff.
- [ ] Tất cả AC có automated evidence; unit/component/contract/E2E pass.
- [ ] Frozen fixture reconcile KPI/chart/list; data-quality invariant hiển thị đúng.
- [ ] Loading/empty/error/permission/offline và stale-response behavior đã test.
- [ ] Axe, keyboard và responsive visual tests pass; không còn defect P0/P1.
- [ ] Privacy scan, telemetry validation, feature flag và rollback smoke test pass.
- [ ] Product Owner chấp nhận staging flow import → dashboard → feedback detail với data FEAT-02.
