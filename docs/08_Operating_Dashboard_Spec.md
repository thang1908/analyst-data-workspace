# 08 — Đặc tả Dashboard Vận hành CX, Touchpoint & Hotspot

> **Cập nhật v2.0 (19/08/2026) — trạng thái triển khai thực tế:**
> - **OverviewPage (`/`)**: Đã implement — 2-row grid: KPI cards + Journey3DMatrix + ChannelBreakdownCard + PainPointsList + TrendChart
> - **FeedbackExplorerPage (`/feedback`)**: Đã implement — 15+ filters, FeedbackDataTable 1250px, default 10/page
> - **HotspotPage (`/hotspot`)**: Đã implement — HotspotDashboard (4 KPI + 2 Donut + Bar) + HotspotActionQueue
> - **Touchpoint dimension**: Đã implement trong analytics breakdown, feedback filters, taxonomy API
> - **Action Priority**: Đã implement trên Hotspot (IMMEDIATE/URGENT/PLANNED/MONITOR)
> - **ChannelBreakdownCard**: Đã implement — donut + legend ngang
> - **data-quality panel**: Chưa implement (API trả 501 Not Implemented)
> - **MoM/YoY comparison**: Chưa implement (P1 reserved)



**Trạng thái:** Canonical backlog specification
**Cập nhật:** 2026-08-17
**Phạm vi:** Làm rõ phần vận hành bổ sung cho `01_PRD.md`, `02_Business_Rules.md`, `03_service_taxonomy.md` và `07_UI_UX_Spec.md`.

---

## 1. Mục tiêu quyết định

Dashboard phải giúp CX Manager, BQL và Service Owner trả lời được, từ tổng quan đến từng phản hồi:

1. Khách đang gặp khó khăn ở **giai đoạn, bước và điểm chạm** nào?
2. Bước đó đang dùng **dịch vụ** nào, phát sinh **vấn đề** gì và có giả thuyết **nguyên nhân** nào?
3. Vấn đề nào là một **điểm nóng** cần tiếp nhận ngay, vấn đề nào cần cải thiện có kế hoạch?
4. Chỉ số có tốt hơn tháng trước hoặc cùng kỳ năm trước không, và có đủ dữ liệu để so sánh không?

Một KPI hoặc hotspot phải drill-down được về các `feedback_item` đã tạo ra nó. Không tạo insight trực tiếp từ bảng import thô.

---

## 2. Chuỗi phân loại chuẩn

```text
Giai đoạn → Bước hành trình → Điểm chạm → Dịch vụ → Vấn đề → Nguyên nhân ứng viên
                                        └→ Feedback item (bằng chứng)
```

| Cấp | Ý nghĩa | Quan hệ | Trạng thái hiện tại |
|---|---|---|---|
| Giai đoạn | Nhận thức, Xem xét, Giao dịch, Nhận nhà, Cư trú, Vận hành | 1:N bước | Có 6 stage |
| Bước | Hành động/trải nghiệm cụ thể của khách | 1:N điểm chạm | Có 36 step |
| Điểm chạm | Kênh/moment cụ thể khách tiếp xúc hoặc trải nghiệm dịch vụ | N:N dịch vụ | **Cần bổ sung taxonomy** |
| Dịch vụ | Nhóm năng lực BQL/doanh nghiệp cung cấp | 1:N vấn đề | Có 10 service |
| Vấn đề | Triệu chứng/khó khăn khách quan sát | N:N nguyên nhân ứng viên | Có 28 issue |
| Nguyên nhân | Giả thuyết kỹ thuật/vận hành cần điều tra | Không tự động là root cause | **Chưa có dữ liệu cause/mapping** |

### 2.1 Điểm chạm là taxonomy riêng

`touchpoint` không phải là channel nhập liệu và cũng không phải service. Ví dụ:

| Bước | Điểm chạm | Dịch vụ thường liên quan | Khó khăn thường quan sát |
|---|---|---|---|
| Ứng dụng & kênh cư dân | Gửi yêu cầu trên app | Hồ sơ & hỗ trợ cư dân | App/case handling lỗi |
| Ra vào & di chuyển | Quét thẻ/cổng ra vào | Ra vào & bãi xe | Ra vào hoặc tiếp khách |
| Ra vào & di chuyển | Gửi/nhận xe | Ra vào & bãi xe | Bãi xe |
| Sử dụng tiện ích & dịch vụ | Đặt/sử dụng hồ bơi hoặc gym | Tiện ích & chuyển nhà | Đặt hoặc dùng tiện ích |
| Yêu cầu & phản ánh | Báo lỗi kỹ thuật | Kỹ thuật & tài sản chung | Hệ thống suy giảm, rủi ro kỹ thuật |
| Yêu cầu & phản ánh | Báo an ninh/PCCC | An ninh & khẩn cấp | Giám sát/phản ứng, PCCC & khẩn cấp |

Mỗi touchpoint bắt buộc có `code`, `name_vi`, `definition`, `lifecycle_step_id`, `active/effective dates`. Mapping `touchpoint_service_map` phải versioned theo taxonomy release và cho phép `PRIMARY | SECONDARY`.

### 2.2 Quy tắc phân loại feedback

- Một `feedback_item` có tối đa một `customer_lifecycle_step`, một touchpoint chính, một primary service và một issue hiện hành.
- Touchpoint có thể `UNKNOWN`/`MISSING`; không suy đoán khi source không đủ tín hiệu.
- Issue luôn thuộc đúng một service. `Nhóm nguyên nhân kỹ thuật` trong file nguồn chỉ là tín hiệu phân loại, **không** là root cause đã xác nhận.
- Cause là tập `0:N` candidate cause, được lưu với nguồn, confidence và bằng chứng. Chỉ Investigation/RCA có quyền xác nhận root cause.

---

## 3. Bố cục dashboard vận hành

Một dashboard chung, có shared filter context và các vùng drill-down. Không tách người dùng giữa CX Overview, Journey và Service Pain Points.

1. **Thanh filter toàn cục:** thời gian, source, location, stage, step, touchpoint, service, issue, sentiment, severity, channel.
2. **KPI tổng quan:** feedback volume, positive/negative/unknown rate, active hotspot và data-completeness.
3. **Hành trình khách hàng:** stage → step; mỗi step mở rộng danh sách touchpoint cuộn dọc. Step/touchpoint không có feedback vẫn hiện `0` để phân biệt “không có sự cố” với “taxonomy bị thiếu”.
4. **Danh mục dịch vụ:** luôn hiển thị đủ 10 dịch vụ; mỗi service mở rộng issue và touchpoint liên quan. Dịch vụ không có dữ liệu có empty state `0 feedback trong bộ lọc`.
5. **Điểm nóng cần hành động:** hàng đợi theo action priority, owner, status, SLA và evidence count.
6. **Feedback Explorer:** bảng/side panel phản hồi gốc đã masking; chọn một issue/hotspot sẽ áp bộ lọc vào đây, không tạo chart dead-end.

### 3.1 Các chỉ số bắt buộc

Mọi tile/breakdown dùng cùng eligibility predicate: item `ACTIVE`, `INCLUDED`, current decision `ACCEPTED`.

| Chỉ số | Định nghĩa |
|---|---|
| Volume | Số feedback item đủ điều kiện, khử trùng lặp theo item ID |
| Negative rate | Negative / (Positive + Neutral + Negative) |
| Unknown rate | Unknown / tổng eligible item |
| Hotspot active | Hotspot chưa `RESOLVED`/`DISMISSED` trong filter context |
| Data completeness | Tỷ lệ item có đủ step, touchpoint, service, issue và location cho use case đang xem |

---

## 4. Điểm nóng và mức ưu tiên xử lý

### 4.1 Định nghĩa hotspot P0

Hotspot là cluster lặp lại, không phải chỉ là một feedback tiêu cực. Detection key chuẩn:

```text
primary_service + issue + normalized_location + rolling_window + rule_version
```

Touchpoint là dimension hiển thị/routing khi coverage đủ; không thêm vào detection key mặc định vì dễ chia nhỏ một cluster thành quá nhiều nhóm. Chỉ item accepted, eligible, đã deduplicate và có location đúng level mới được tính.

Rule P0 bắt đầu bằng threshold xác định: trong cửa sổ `W`, ít nhất `N` item cùng detection key thì upsert một hotspot `CANDIDATE`, liên kết toàn bộ evidence item và không tạo trùng khi retry.

### 4.2 Action priority tách biệt với severity

`operational_severity` đo mức ảnh hưởng của từng feedback; `action_priority` dùng để điều phối hotspot. Không thay thế một trường cho trường kia.

| Action priority | Khi nào áp dụng | Mục tiêu phản hồi | Khuyến nghị rule-based ban đầu |
|---|---|---|---|
| `IMMEDIATE` | Safety/life-safety hoặc SEV-1 hard trigger đã được BQL/Safety sign-off | Tiếp nhận ngay, kích hoạt playbook khẩn cấp | Gọi owner trực ca, cô lập rủi ro, thông báo BQL, lưu evidence. Đây là P1 cho đến khi playbook được phê duyệt. |
| `URGENT` | Hotspot đạt ngưỡng và có SEV-2, hoặc tốc độ tăng cao | Acknowledge trong 24 giờ | Gán Service Owner, kiểm tra location/asset liên quan, xác nhận phạm vi và theo dõi hằng ngày. |
| `PLANNED` | Lặp lại SEV-3/SEV-4, không có safety signal | Đưa vào backlog cải tiến | Nhóm theo issue/touchpoint, xác định owner, đưa mốc xử lý và đo lại negative rate sau thay đổi. |
| `MONITOR` | Có tín hiệu nhưng chưa đạt threshold hoặc dữ liệu chưa đủ | Theo dõi | Bổ sung location/touchpoint, kiểm tra chất lượng dữ liệu, không đóng kết luận nguyên nhân. |

Mỗi priority phải có playbook phiên bản, owner mặc định, SLA, điều kiện nâng/hạ mức và audit log. AI chỉ được gợi ý playbook; không được tự resolve hotspot hoặc xác nhận nguyên nhân gốc.

### 4.3 Vòng đời P0

```text
CANDIDATE → ACKNOWLEDGED → INVESTIGATING → RESOLVED
     └──────────────────────────────→ DISMISSED
RESOLVED/DISMISSED → REOPENED → INVESTIGATING
```

Mọi chuyển trạng thái, assignment, dismissal và resolution phải giữ actor, timestamp, reason và evidence. `INVESTIGATING` ở đây là trạng thái xử lý vận hành, không tự tạo RCA hoặc confirmed root cause.

---

## 5. So sánh theo thời gian

| So sánh | Điều kiện | Cách hiển thị |
|---|---|---|
| MoM | Hai tháng dương lịch hoàn tất; cùng filter context và taxonomy version comparable | Delta volume, delta negative rate, delta hotspot; ghi rõ tháng so sánh |
| YoY | Có tối thiểu 13 tháng dữ liệu lịch sử tương đương | So cùng tháng năm trước; ẩn KPI thay vì hiển thị 0 khi không đủ dữ liệu |
| Trend | Có timestamp nguồn hoặc timestamp suy diễn được đánh dấu | Day/week/month; đánh dấu nguồn có ngày suy diễn |

Không so sánh hai khoảng thời gian nếu có thay đổi taxonomy release, filter, source scope hoặc completeness material. Khi không comparable, UI phải hiện lý do thay vì suy luận xu hướng.

Dataset OCP1 hiện được phân bố trong 180 ngày do file không có `reported_at`; vì vậy chỉ phù hợp demo trend/MoM giới hạn, **không đủ YoY** và không dùng làm baseline vận hành thực tế.

---

## 6. Đánh giá chất lượng dữ liệu và AI

### 6.1 Dataset hiện tại

OCP1 là synthetic dataset có nhãn nguồn trusted cho sentiment, severity, journey và technical group. Nó không phải gold set AI và không chứng minh được độ chính xác mô hình. Dashboard phải hiển thị provenance `SOURCE_TRUSTED` khi xem dữ liệu này.

### 6.2 Điều kiện để chấm điểm mô hình

Trước khi công bố AI score, cần có:

- bộ gold set versioned, holdout cố định và sampling plan;
- hai reviewer độc lập cho tối thiểu 10% mẫu, có adjudication;
- coverage tối thiểu theo issue/touchpoint, báo thiếu coverage thay vì suy diễn;
- per-field precision, recall, Macro-F1, unknown rate, override rate và calibration error;
- báo cáo riêng cho step, touchpoint, service, issue, sentiment, severity và candidate cause.

Không dùng accuracy tổng để thay thế Macro-F1 khi label mất cân bằng. Prediction chỉ suggest; human/source-trusted decision mới được vào dashboard chính thức.

---

## 7. Khoảng trống hiện tại và thứ tự triển khai

| Ưu tiên | Kết quả cần có | Điều kiện đầu vào |
|---|---|---|
| P0.1 | Touchpoint taxonomy và mapping Step → Touchpoint → Service → Issue | Taxonomy release mới, migration và API filter/options |
| P0.2 | Chuẩn hoá nguồn nhập có `reported_at`, location và touchpoint khi có thể | Data contract/import mapper; backfill có provenance |
| P0.3 | Deterministic hotspot + evidence + owner + lifecycle | Location coverage, rule `N/W`, service owner và playbook ký duyệt |
| P0.4 | Hotspot queue/dashboard + Feedback Explorer drill-down | P0.3 |
| P1.1 | MoM comparable | Ít nhất hai tháng hoàn chỉnh, metadata nguồn/taxonomy |
| P1.2 | YoY comparable | Tối thiểu 13 tháng dữ liệu nguồn thực |
| P1.3 | Candidate cause/AI evaluation/RCA | Cause taxonomy, gold set, review workflow và governance |

---

## 8. Acceptance criteria

1. Dashboard giữ đủ stage, step, touchpoint và 10 service khi slice có zero data.
2. Chọn một touchpoint/service/issue/hotspot mở Feedback Explorer với cùng filter context.
3. Hotspot có evidence reproducible, owner, action priority, lifecycle và audit history.
4. `IMMEDIATE` không được kích hoạt nếu chưa có approved safety playbook.
5. MoM/YoY chỉ hiện khi dữ liệu comparable; nếu không, UI nêu rõ thiếu ngày, location, lịch sử hoặc taxonomy comparability.
6. UI không gọi technical group hoặc AI prediction là root cause đã xác nhận.

---

## Phụ lục — Trạng thái triển khai Dashboard (v2.0)

### Tính năng đã implement (P0 ✅)

| Tính năng | Component/File | Ghi chú |
|---|---|---|
| KPI Summary cards | `KPICard.tsx` | volume, negative_rate, unknown_rate, active_hotspots |
| Journey matrix | `Journey3DMatrix.tsx` | 6 stages × 10 services |
| Channel breakdown | `ChannelBreakdownCard.tsx` | Donut + legend ngang, 8 kênh |
| Trend chart | `TrendChart.tsx` | Line chart, grain day/week/month |
| Pain points list | `PainPointsList.tsx` | Top 5 vấn đề |
| Feedback explorer | `FeedbackExplorerPage.tsx` | 15+ filters, pagination 10/page |
| Hotspot dashboard | `HotspotDashboard.tsx` | 4 KPI + 2 Donut + Bar chart |
| Hotspot queue | `HotspotActionQueue.tsx` | Cards ngang, filter priority/status |
| Hotspot detail | `HotspotDetailModal.tsx` | Evidence list + timeline |
| Detect hotspots | `POST /hotspots/detect` | Rolling window clustering |
| Action Priority | `engine.py::calculate_action_priority` | IMMEDIATE/URGENT/PLANNED/MONITOR |
| Touchpoint filter | Analytics + Feedback | Dimension touchpoint_code |
| Direct CSV import | `POST /feedback-items/direct-import-csv` | Đồng bộ, không cần worker |
| Hotspot REOPEN | `POST /hotspots/{id}/reopen` | RESOLVED/DISMISSED → INVESTIGATING |
| Hotspot ASSIGN | `POST /hotspots/{id}/assign` | → INVESTIGATING + owner |

### Tính năng chưa implement (P1/P2)

| Tính năng | Trạng thái | Ghi chú |
|---|---|---|
| Data quality panel | 501 Not Implemented | API reserved, UI chưa build |
| MoM/YoY comparison | P1 | Chưa implement |
| AI classification review | Partial | AI router có, UI chưa đầy đủ |
| Import wizard advanced mapping | Partial | Basic upload có, advanced map P1 |
| Root Cause confirmation flow | P1 | Domain model có, UI chưa |
| PDF/Excel export | P2 | Chưa implement |

### Analytics API — breakdown dimensions đã implement

```
service, issue, location, journey_stage, journey_step,
touchpoint, service_request_step, intake_channel,
affected_channel, sentiment, severity
```

### Hotspot detect request (thực tế)

```json
{
  "project_id": "uuid",
  "window_days": 180,
  "threshold_count": 3,
  "rule_version": "v1.0.0",
  "safety_playbook_approved": false,
  "window_start": null,
  "window_end": null
}
```
