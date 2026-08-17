# 01 — Document Yêu cầu Sản phẩm (Product Requirements Document)

# CX Journey, Service & Root Cause Intelligence Platform

> **Bổ sung vận hành (2026-08-17):** Đặc tả canonical cho touchpoint, action priority
> của hotspot, data/AI quality và so sánh MoM/YoY nằm tại
> [`08_Operating_Dashboard_Spec.md`](./08_Operating_Dashboard_Spec.md). Tài liệu này
> làm rõ phạm vi P0/P1, không thay đổi các bất biến nghiệp vụ trong PRD.

**Phiên bản:** 1.3
**Trạng thái:** Pilot Build Baseline / Căn chỉnh theo Taxonomy 3.0.0 / Đang chờ Quyết định từ Stakeholder chỉ định
**Lĩnh vực:** Bất động sản / Trải nghiệm khách hàng (CX) & Vận hành Nhà ở
**Nguồn hành trình lịch sử:** `Customer Journey(2).xlsx`
**Taxonomy chuẩn (Authoritative taxonomy):** `service_taxonomy.md` phiên bản revision 3.0.0

---

## 1. Tóm tắt Điều hành (Executive Summary)

CX Platform là nền tảng hợp nhất feedback và dữ liệu trải nghiệm khách hàng, sau đó chuẩn hóa chúng theo:

```text
Customer Lifecycle
+ Service Request Lifecycle
+ Primary Service
+ Issue
+ Location
+ Affected Channel
+ symptom_detail
+ Candidate/Confirmed Cause
```

Nền tảng không chỉ trả lời:

> “Có bao nhiêu ticket?”

Mà phải trả lời:

```text
Khách đang ở bước nào?
↓
Đang sử dụng dịch vụ nào?
↓
Gặp vấn đề gì?
↓
Vấn đề xảy ra ở đâu?
↓
Mức độ ảnh hưởng ra sao?
↓
Có đang hình thành hotspot?
↓
Nguyên nhân có thể là gì?
↓
Root Cause thực tế là gì?
↓
Ai phải xử lý?
↓
Làm gì để tránh tái diễn?
```

---

## 2. Vấn đề Sản phẩm (Product Problem)

Customer Journey đã được khảo sát và chốt nhưng chưa đủ để phục vụ vận hành.

Ví dụ:

```text
Feedback:
"Thang máy S2 sáng nào cũng phải chờ rất lâu."

Journey:
Cư trú → RES-03 Ra vào & di chuyển

Operational classification:
Customer Lifecycle Step = RES-03 Ra vào & di chuyển
Service = SV-07 Kỹ thuật, tiện ích & tài sản chung
Issue = IS-07-01 Hệ thống ngừng hoặc suy giảm
Symptom Detail = Chờ thang máy lâu vào buổi sáng
Location = S2
Cause Determination Status = UNKNOWN
Candidate Cause Suggestions = []
```

Nếu nhiều feedback tương tự xuất hiện:

```text
SV-07
+ IS-07-01
+ S2
+ same time window
→ Potential Hotspot
```

Sau technical investigation [P1]:

```text
Candidate Cause
→ Evidence
→ Confirmed Root Cause
→ Corrective Action
→ Preventive Action
```

---

## 3. Khung Lifecycle Cơ sở (Lifecycle Baseline)

Taxonomy 3.0.0 định nghĩa hai chiều lifecycle độc lập: Customer Lifecycle có 6 stage/36 step, bao gồm `Vận hành`, và Service Request Lifecycle có 8 step. `Vận hành` là stage thứ sáu của Customer Lifecycle; Service Request Lifecycle không phải Customer Lifecycle Stage.

### 3.1 Customer Lifecycle

Customer Lifecycle trả lời: **khách hàng đang ở đâu trong quan hệ với chủ đầu tư/đơn vị vận hành?**

| Stage       | Số Step | Code examples          |
| ----------- | -------: | ---------------------- |
| Nhận thức |        3 | A1, A2, A3             |
| Xem xét    |        6 | C1, C2, C3, C4, C5, C6 |
| Giao dịch  |        6 | TR-01…TR-06           |
| Nhận nhà  |        5 | HO-01…HO-05           |
| Cư trú    |        8 | RES-01…RES-08         |
| Vận hành  |        8 | OPS-01…OPS-08         |

Mã và wording canonical của toàn bộ 36 step được quản lý trong `service_taxonomy.md`. Stage `Vận hành` mô tả hoạt động quản lý tài sản và dịch vụ sau bàn giao; stage `Cư trú` mô tả trải nghiệm/touchpoint trực tiếp của cư dân.

### 3.2 Service Request Lifecycle

Service Request Lifecycle trả lời: **một yêu cầu dịch vụ đang ở bước xử lý nào?** Đây là dimension độc lập và có thể xuất hiện tại bất kỳ Customer Lifecycle Stage nào.

| Step       | Ý nghĩa              |
| ---------- | ---------------------- |
| `SRV-01` | Tìm thông tin        |
| `SRV-02` | Gửi yêu cầu         |
| `SRV-03` | Xác nhận/phê duyệt |
| `SRV-04` | Thanh toán            |
| `SRV-05` | Được phục vụ      |
| `SRV-06` | Theo dõi/escalate     |
| `SRV-07` | Hoàn tất             |
| `SRV-08` | Đánh giá            |

Ví dụ, một cư dân phản ánh lỗi thanh toán có thể đồng thời ở `Customer Lifecycle = Cư trú / RES-06` và `Service Request Lifecycle = SRV-02`.

> Wording chi tiết và mapping đầy đủ nằm trong `service_taxonomy.md`. Khi seed dữ liệu, các `SRV-*` phải được nạp vào dictionary riêng, không nạp như Customer Journey Stage.

---

## 4. Tầm nhìn Sản phẩm (Product Vision)

Xây dựng một **CX Intelligence & Operations Platform** với chu trình:

```text
LISTEN
  ↓
UNDERSTAND
  ↓
DETECT
  ↓
PRIORITIZE
  ↓
ACT
  ↓
LEARN
```

---

## 5. Mục tiêu Sản phẩm (Product Goals)

### G1 — Unified CX Data

Đích sản phẩm là hợp nhất feedback từ file, app, hotline, social crawler và API vào một schema chuẩn. Pilot P0 chỉ cam kết CSV/XLSX; API ingestion và connector thuộc P1.

### G2 — Standardized Taxonomy

Chuẩn hóa dữ liệu bằng `Customer Lifecycle + Service Request Lifecycle + Primary Service + Issue + Location + Affected Channel + symptom_detail`; Candidate Cause là giả thuyết riêng, không phải nhãn sự thật.

### G3 — AI-assisted Classification

Gợi ý Customer Lifecycle Step, Service Request Step, Primary Service, Issue, Sentiment và confidence theo từng field; Customer Lifecycle Stage được derive từ Step. Trong P0, AI chỉ gợi ý; con người hoặc nhãn nguồn được duyệt mới tạo current classification dùng cho analytics.

### G4 — Detect Emerging Problems

Phát hiện spike, recurring issue, location cluster và hotspot.

### G5 — Connect Insight to Action

Insight phải drill-down về feedback/ticket và có owner.

### G6 — Cause & Root Cause Intelligence

P0 tách Candidate Cause khỏi sự thật đã xác nhận và liên kết evidence với hotspot. P1 bổ sung Investigation, Confirmed Root Cause, Corrective Action, Preventive Action và RCA đầy đủ.

---

## 6. Phạm vi Không thuộc Mục tiêu — MVP (Non-goals — MVP)

MVP **không** nhằm thay thế:

- CRM bán hàng
- ERP/kế toán
- BMS
- CMMS
- Access Control
- Payment Gateway
- Call Center
- Resident App
- Social platforms

Platform làm lớp CX intelligence/orchestration. Pilot P0 nhập file và lưu reference về hệ thống nguồn; không cam kết connector realtime, ticketing đầy đủ hoặc đồng bộ ngược.

---

## 7. Mô hình Miền Cốt lõi (Core Domain Model)

```text
Customer / Interaction reference
        ↓
Feedback (source envelope, immutable raw content)
        ↓ 1:N
Feedback Item (một intent/vấn đề nguyên tử)
        ├── Location [0:1] + Affected Channel [0:N] + symptom_detail
        ├── AI Prediction Event(s), theo field và model version
        ├── Human/Source Decision Version(s), immutable snapshot theo actor
        └── Current Classification Projection
                ├── Customer Lifecycle Stage/Step
                ├── Service Request Step [optional]
                ├── Primary Service
                ├── Issue + Sentiment + Operational Severity
                └── Candidate Cause Suggestions [0:N, chưa xác nhận]
                         ↓ N:N
              Hotspot + Evidence + Owner/Status          [P0]
                         ↓
              Investigation + Confirmed Root Cause       [P1]
                         ↓
              Corrective / Preventive Action             [P1]
```

`Feedback` giữ provenance của bản ghi nguồn. `Feedback Item` là đơn vị phân loại, review, analytics và hotspot. P0 mặc định tạo một item cho mỗi feedback; reviewer phải có thể tách feedback multi-intent thành nhiều item mà không sửa `content_raw`.

`Current Classification Projection` là trạng thái đọc nhanh được dựng từ decision version mới nhất có hiệu lực. Projection có thể rebuild; prediction, decision snapshot và review event là audit source of truth và không được overwrite.

### 7.1 Journey ≠ Service

`Journey Step` và `Service` là quan hệ N:N.

Ví dụ:

```text
Journey Step = RES-03 Ra vào & di chuyển

Possible Services:
- SV-05 Ra vào, khách, bãi xe & di chuyển
- SV-07 Kỹ thuật, tiện ích & tài sản chung
- SV-08 An ninh, PCCC & khẩn cấp
```

### 7.2 Issue ≠ Cause

`Issue` là triệu chứng. `Cause` là giả thuyết nguyên nhân.

### 7.3 Candidate Cause ≠ Root Cause

AI/operator có thể suggest nhiều Candidate Cause có rank/confidence trong P0; chỉ Investigation/RCA P1 có evidence và người có thẩm quyền mới xác nhận Root Cause. `UNKNOWN` chỉ dùng khi đã đánh giá nhưng chưa xác định được giả thuyết cụ thể và không được tồn tại cùng một cause cụ thể trong cùng decision set.

### 7.4 Canonical Cross-document Enums

`decision_source` dùng duy nhất:

```text
MANUAL | SOURCE_TRUSTED | HUMAN_ACCEPTED_AI | HUMAN_CORRECTED_AI | POLICY_AUTO_APPLIED | SYSTEM_MIGRATION
```

`cause_determination_status` dùng duy nhất:

```text
NOT_ASSESSED | UNKNOWN | SUGGESTED | UNDER_INVESTIGATION | CONFIRMED | NOT_APPLICABLE
```

P0 chỉ ghi `NOT_ASSESSED`, `UNKNOWN`, `SUGGESTED`, `NOT_APPLICABLE`. `UNDER_INVESTIGATION` và `CONFIRMED` chỉ được ghi bởi workflow Investigation/RCA P1; classifier/AI không được ghi hai trạng thái này.

Review action canonical:

```text
ACCEPT | CORRECT | MARK_UNKNOWN | MARK_MISSING | MARK_NOT_APPLICABLE | SPLIT_REQUIRED | SKIP
```

Năm action đầu tạo `ReviewEvent` và immutable `ClassificationDecision`; `SPLIT_REQUIRED` và `SKIP` chỉ tạo `ReviewEvent`. Việc split thực tế dùng mutation riêng và không tạo decision cho split-parent.

### 7.5 Delivery Priority ≠ Operational Severity

- `delivery_priority`: `P0`, `P1`, `P2`, dùng cho roadmap/build scope.
- `operational_severity`: `SEV-1`, `SEV-2`, `SEV-3`, `SEV-4`, dùng cho mức độ ảnh hưởng của feedback item, hotspot hoặc ticket.

Các cột `Default Priority P1–P4` trong taxonomy v1.0 là dữ liệu vận hành cũ và phải được map lần lượt sang `SEV-1–SEV-4` khi import. API/domain model mới không dùng cùng tên `priority` cho hai khái niệm.

### 7.6 Lifecycle Independence

Customer Lifecycle và Service Request Lifecycle là hai dimension độc lập. Một feedback item có tối đa một Customer Lifecycle Step hiện hành và tối đa một Service Request Step hiện hành; một trong hai có thể `UNKNOWN`, nhưng hệ thống không được suy diễn `SRV-*` thành Customer Lifecycle Stage.

---

## 8. Chân dung Người dùng (Personas)

Các Persona dưới đây là product roles, không phải analytics dimension. P0 không có Persona segmentation/filter; nếu bổ sung ở P1 phải có definition, provenance, consent và contract riêng.

| Persona                | Mục tiêu chính                                       |
| ---------------------- | ------------------------------------------------------- |
| CX Analyst             | Phân tích feedback, journey, service, hotspot         |
| Operator / CSKH        | Triage, review classification, tạo/điều phối ticket |
| Building Manager / BQL | Theo dõi sự cố, SLA, hotspot, ảnh hưởng theo tòa |
| Service Owner          | Theo dõi issue, recurrence, RCA                        |
| Technical Owner        | Điều tra hệ thống/cause và xác nhận root cause   |
| CX Manager             | Theo dõi experience metrics, journey friction, top hotspot |
| Taxonomy Admin         | Quản lý Journey/Service/Issue/Cause/mapping           |
| Data Steward           | Data quality và metric definition                      |
| AI Reviewer / ML Team  | Review prediction và model quality                     |
| Platform Admin         | Role, permission, audit                                 |

---

## 9. Kiến trúc Thông tin (Information Architecture)

```text
CX Platform
├── Overview
├── Import Jobs
├── Feedback
│   ├── All Feedback
│   ├── Needs Review
│   └── Saved Views        [P1]
├── Hotspots
├── Analytics
│   ├── CX Overview                    [P0 basic]
│   ├── Customer Journey               [P0 basic; P1 advanced]
│   ├── Service & Pain Points          [P0 basic; P1 advanced]
│   └── Hotspot & Root Cause           [P0 hotspot/candidate cause; P1 RCA]
├── Tickets            [P1]
├── RCA                [P1]
├── AI Review
├── Data Quality
├── Access & Audit
└── Taxonomy
    ├── Customer Lifecycle
    ├── Service Request Lifecycle
    ├── Services
    ├── Issues
    ├── Causes
    ├── Location
    └── Lifecycle-Service Mapping
```

---

## 10. Câu chuyện Người dùng & Tiêu chí Chấp nhận (User Stories & Acceptance Criteria)

| Epic                               | User Story      | Persona            | Tôi muốn                                                                | Để                                                               | Độ ưu tiên   | Tiêu chí Chấp nhận (Acceptance Criteria)                                                                                                                                                                        |
| ---------------------------------- | --------------- | ------------------ | ----------------------------------------------------------------------- | ---------------------------------------------------------------- | ------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `EPIC-01` Lifecycle Taxonomy     | `US-JRN-01`   | Taxonomy Admin     | publish 6 Customer Lifecycle Stage/36 Step và 8 Service Request Step   | CX data được phân loại đúng hai lifecycle độc lập      | **P0** | Đủ A/C/TR/HO/RES/OPS theo taxonomy 3.0.0; code duy nhất; dictionary riêng; import seed đã validate; draft/approved/published/retired; effective date; không hard-delete.                                 |
| `EPIC-01` Lifecycle Taxonomy     | `US-JRN-02`   | Taxonomy Admin     | xem dictionary theo taxonomy canonical                                  | team dùng cùng một định nghĩa lifecycle                    | **P0** | Giữ wording approved trong `service_taxonomy.md`; hiển thị code/type/stage/step/version; mọi publish/retire tạo audit.                                                                                    |
| `EPIC-02` Service Catalog        | `US-SVC-01`   | Taxonomy Admin     | publish Canonical Service/Issue Catalog                                 | feedback được gắn đúng outcome/năng lực vận hành       | **P0** | Release có đúng 10 Service/28 Issue; Service có code, tên VI/EN, outcome definition, in/out scope và default severity; SV-10 có review queue và other-rate monitoring.                                  |
| `EPIC-02` Service Catalog        | `US-SVC-02`   | Taxonomy Admin     | map Lifecycle Step với nhiều Service                                  | system biết service nào có thể tác động tới từng bước | **P0** | N:N mapping; bật/tắt; lịch sử hiệu lực; API đọc mapping; Customer và Service Request mapping không trộn type.                                                                                        |
| `EPIC-03` Issue & Cause Taxonomy | `US-ISS-01`   | Service Owner      | quản lý Issue thuộc Service                                          | complaint được chuẩn hóa theo triệu chứng                 | **P0** | Issue thuộc đúng một Service; code unique; có tên VI/EN, definition, inclusion examples, safety flag và severity override; SV-01..SV-09 có 3 Issue, SV-10 có 1 Issue.                                  |
| `EPIC-03` Issue & Cause Taxonomy | `US-CAUSE-01` | Technical Owner    | quản lý Candidate Cause theo Issue                                    | investigation có checklist nguyên nhân nhất quán            | **P1** | Issue↔Cause N:N; suggestion set hỗ trợ nhiều cause có rank/confidence; `UNKNOWN` không đi cùng cause cụ thể.                                                                                         |
| `EPIC-03` Issue & Cause Taxonomy | `US-CAUSE-02` | Technical Owner    | xác nhận Root Cause sau điều tra                                    | giả thuyết không bị coi là sự thật                        | **P1** | Root cause CONFIRMED bắt buộc evidence + confirmed_by + confirmed_at; AI không được confirm.                                                                                                              |
| `EPIC-04` Feedback Intake        | `US-INT-01`   | CX Analyst         | import feedback từ CSV/XLSX                                            | dữ liệu lịch sử có thể vào platform                       | **P0** | Async job; preview; reusable column mapping; validate; idempotency; error file; partial/failed status; retry; row lineage; batch audit.                                                                         |
| `EPIC-04` Feedback Intake        | `US-INT-02`   | Integration System | gửi feedback qua API                                                   | feedback mới đi vào platform tự động                       | **P1** | Idempotency key; source/channel; timestamp; content; response trả feedback_id.                                                                                                                                 |
| `EPIC-04` Feedback Intake        | `US-INT-03`   | CX Analyst         | nhìn thấy nguồn và raw content nguyên bản                         | có thể audit classification                                    | **P0** | Raw content immutable; source URL/ref; ingested_at; original payload reference.                                                                                                                                 |
| `EPIC-05` Feedback Workspace     | `US-FB-01`    | CX Analyst         | xem feedback và các feedback item                                     | điều tra từng vấn đề nguyên tử trên một workspace      | **P0** | Table có event date, channel, project, location, lifecycle, primary service, issue, symptom detail, sentiment, operational severity và review status.                                                         |
| `EPIC-05` Feedback Workspace     | `US-FB-02`    | CX Analyst         | filter feedback item theo các dimension CX                             | thu hẹp chính xác phạm vi điều tra                         | **P0** | Filter date/project/location/customer lifecycle/service-request step/service/issue/sentiment/severity/channel/status.                                                                                           |
| `EPIC-05` Feedback Workspace     | `US-FB-03`    | CX Analyst         | save view                                                               | không phải cấu hình filter lặp lại                         | **P1** | Save private/shared view; owner; default view; delete/rename.                                                                                                                                                   |
| `EPIC-05` Feedback Workspace     | `US-FB-04`    | Operator           | split item và quyết định classification thủ công                  | multi-intent và label sai được xử lý có kiểm soát       | **P0** | Raw content không đổi; mỗi correction tạo immutable decision version mới có actor, reason, timestamp và reference tới version trước; projection rebuild được; correction vào gold-set candidate. |
| `EPIC-06` AI Classification      | `US-AI-01`    | Operator           | nhận AI suggestion cho lifecycle/service/issue/sentiment               | giảm tagging thủ công                                         | **P0** | Suggest-only; prediction tách theo item+field, có candidate value, confidence, model/prompt/taxonomy version; không tự sửa current projection.                                                             |
| `EPIC-06` AI Classification      | `US-AI-02`    | AI Reviewer        | review AI suggestion bằng action canonical                              | chỉ decision được duyệt mới vào analytics                 | **P0** | Hỗ trợ `ACCEPT/CORRECT/MARK_UNKNOWN/MARK_MISSING/MARK_NOT_APPLICABLE/SPLIT_REQUIRED/SKIP`; năm action đầu tạo Decision+ReviewEvent, hai action cuối chỉ tạo ReviewEvent.                                  |
| `EPIC-06` AI Classification      | `US-AI-03`    | AI/ML Team         | tạo gold set và theo dõi chất lượng theo label                    | biết model đủ điều kiện để mở rộng hay chưa           | **P0** | Gold set versioned; sampling rule; label guideline; correction/unknown/confidence distribution; offline metrics theo field.                                                                                     |
| `EPIC-07` Ticket / Case          | `US-TKT-01`   | Operator           | chuyển feedback thành ticket hoặc attach ticket có sẵn             | chỉ vấn đề cần action mới thành case                      | **P1** | Feedback có thể remain feedback/create/attach; audit relationship.                                                                                                                                            |
| `EPIC-07` Ticket / Case          | `US-TKT-02`   | Operator           | assign ticket tới handling unit                                        | đảm bảo có owner xử lý                                     | **P1** | Assignment history; accepted_at; reassignment reason; current accountable owner.                                                                                                                                |
| `EPIC-07` Ticket / Case          | `US-TKT-03`   | Building Manager   | theo dõi SLA và escalation                                            | case rủi ro được ưu tiên                                   | **P1** | SLA countdown; near-breach; breach; pause reason; escalation event.                                                                                                                                             |
| `EPIC-08` Hotspot                | `US-HOT-01`   | CX Manager         | phát hiện cluster theo deterministic rule Service+Issue+Location+Time | vấn đề lặp lại được phát hiện nhất quán              | **P0** | Rule dùng accepted item, cấu hình threshold/window/location level, có rule version và evidence items; cùng key/window không tạo candidate trùng.                                                       |
| `EPIC-08` Hotspot                | `US-HOT-02`   | CX Manager         | drill-down hotspot về feedback item                                    | hiểu dữ liệu nào tạo ra cảnh báo                          | **P0** | Hotspot detail có trend, evidence items, locations, sentiment và operational severity.                                                                                                                        |
| `EPIC-08` Hotspot                | `US-HOT-03`   | Building Manager   | acknowledge/assign hotspot                                              | candidate P0 có accountable owner                               | **P0** | Owner mặc định từ Service; acknowledge/assign/dismiss/resolve có actor, timestamp, reason và timeline.                                                                                                    |
| `EPIC-08` Hotspot                | `US-HOT-04`   | System             | kích hoạt hard trigger với vấn đề an toàn                        | không chờ volume đủ lớn mới cảnh báo                     | **P1** | SEV-1 safety issue tạo alert tức thời; rule độc lập AI score và chỉ bật sau sign-off.                                                                                                                  |
| `EPIC-09` RCA                    | `US-RCA-01`   | Service Owner      | mở RCA từ hotspot hoặc repeat issue                                  | tìm nguyên nhân gốc thay vì đóng triệu chứng            | **P1** | RCA liên kết hotspot/ticket; problem statement; candidate causes; evidence; asset/work-order chỉ là investigation reference ngoài taxonomy khi có.                                                        |
| `EPIC-09` RCA                    | `US-RCA-02`   | Technical Owner    | xác nhận root cause và corrective action                             | ngăn lỗi tái diễn                                            | **P1** | Confirmed cause; corrective/preventive action; owner; due date; verification.                                                                                                                                   |
| `EPIC-10` Pilot Analytics        | `US-ANA-01`   | CX Manager         | xem bốn dashboard P0 cơ bản                                             | theo dõi CX từ overview tới journey, service và hotspot | **P0** | Có CX Overview, Customer Journey, Service & Pain Points, Hotspot & Root Cause; mỗi breakdown trả item volume, negative rate, active hotspots, trend và drill-down cùng filter context.                     |
| `EPIC-10` Journey Analytics      | `US-ANA-02`   | CX Manager         | xem Journey Stage/Step ở mức cơ bản                                  | biết step nào có volume/negative/hotspot nổi bật       | **P0** | Breakdown theo stage/step có `item_volume`, `negative_rate`, `active_hotspots`, `trend`; không có Persona filter; WoW/MoM/YoY thuộc P1.                                                                    |
| `EPIC-11` Service Analytics      | `US-ANA-03`   | Service Owner      | xem Service/Issue ở mức cơ bản                                       | biết dịch vụ/pain point nào cần chú ý                  | **P0** | Breakdown theo service/issue có `item_volume`, `negative_rate`, `active_hotspots`, `trend`; advanced comparison/recurrence thuộc P1.                                                                      |
| `EPIC-11` Service Analytics      | `US-ANA-04`   | Service Owner      | xem recurring issue và candidate cause                                 | ưu tiên hoạt động phòng ngừa                              | **P1** | Repeat rate; RCA linkage; Journey/Location/Channel/symptom-detail concentration.                                                                                                                                |
| `EPIC-12` Governance             | `US-GOV-01`   | Platform Admin     | quản lý basic role và quyền xem PII                                 | dữ liệu chỉ hiển thị đúng đối tượng                   | **P0** | SSO; Pilot Admin/Analyst/Reviewer/Viewer; server-side authorization; raw PII/export privilege; audit privileged actions.                                                                                        |
| `EPIC-12` Governance             | `US-GOV-02`   | Data Steward       | theo dõi data quality thiết yếu                                      | analytics không dựa trên dữ liệu bẩn                       | **P0** | Import errors, duplicate, missing/invalid taxonomy/location, unknown rate, stale prediction và ineligible item counts.                                                                                         |
| `EPIC-13` Location               | `US-LOC-01`   | Taxonomy Admin     | quản lý location hierarchy trong pilot                                | filter và hotspot dùng cùng stable location ID                | **P0** | Project→site/building→floor/zone→space/point; code unique trong parent; timezone; active/effective date; không hard-delete.                                                                                 |

---

## 11. Yêu cầu Chức năng (Functional Requirements)

### FR-01 — Lifecycle Taxonomy

- Giữ đúng 6 Customer Lifecycle Stage/36 Customer Journey Step và 8 Service Request Step trong hai dictionary riêng theo taxonomy 3.0.0.
- Stage/Step có stable ID, `lifecycle_type`, version và effective date.
- Version state gồm `DRAFT`, `APPROVED`, `PUBLISHED`, `RETIRED`; chỉ `PUBLISHED` được dùng cho decision mới.
- Structured seed có checksum/validator và phải kiểm tra đủ A/C/TR/HO/RES/OPS trước khi publish.
- Không hard-delete historical taxonomy; feedback item cũ giữ reference tới taxonomy version đã dùng.

### FR-02 — Service Catalog

Mỗi Service có:

```text
service_id
service_code
name_vi
name_en
outcome_definition
in_scope
out_of_scope
default_severity
```

Thông tin accountable owner dùng cho assignment/hotspot là operational configuration versioned theo Service, không phải một nhãn hay boundary của taxonomy. `SV-10` không có default owner và luôn vào manual triage queue.

### FR-03 — Issue Taxonomy

Mỗi Issue có:

```text
issue_id
issue_code
service_id
name_vi
name_en
definition
inclusion_examples
safety_critical
severity_override
```

Release phải có đúng 10 Service/28 Issue: `SV-01..SV-09` có đúng 3 Issue/Service và `SV-10` có `IS-10-01`. Khi dùng `SV-10/IS-10-01`, decision bắt buộc có `other_reason` và human review; record thiếu hoặc mơ hồ phải dùng value status phù hợp, không được gán `SV-10`.

### FR-04 — Cause Taxonomy

Mỗi Cause có:

```text
cause_id
cause_code
cause_group
cause_name
description
active
version
```

`Issue ↔ Cause` là N:N qua `issue_cause_map`. Một candidate-cause suggestion set có 0:N cause, mỗi cause có `rank`, `confidence`, `source` và version; `UNKNOWN` là trạng thái không có cause cụ thể, không phải bằng chứng root cause.

### FR-05 — Lifecycle-Service Mapping

- N:N.
- Mapping bắt buộc có `lifecycle_type`, effective date, version và audit.
- Customer Lifecycle mapping và Service Request Lifecycle mapping được query riêng; API không trả một danh sách mơ hồ chỉ có `journey_step_id`.

### FR-05A — Location Hierarchy

```text
Project
  ↓
Site / Building
  ↓
Floor / Zone
  ↓
Space / Point
```

Mỗi location có `location_id`, `location_type`, `parent_location_id`, `location_code`, `location_name`, `timezone`, `active_from`, `active_to`. Location là chiều 0:1 trên Feedback Item. Asset/System không phải classification dimension; asset/work-order reference chỉ có thể được bổ sung trong investigation ở P1. Hotspot rule phải khai báo location level dùng để group.

### FR-05B — Interaction Channel

- Dictionary canonical gồm `CH-APP`, `CH-WEB`, `CH-HOTLINE`, `CH-EMAIL`, `CH-FRONTDESK`, `CH-SOCIAL`, `CH-INPERSON`, `CH-SYSTEM`.
- Intake Channel mô tả kênh tiếp nhận; Affected Channel là quan hệ 0:N trên Feedback Item.
- CRM, ERP, BMS, CMMS, contact-center platform và sensor feed là `source_system`, không phải Channel.

### FR-05C — Async Feedback Import

Import CSV/XLSX là job bất đồng bộ với lifecycle:

```text
UPLOADED → MAPPED → VALIDATING → VALIDATED → QUEUED → PROCESSING
                                                    ├── COMPLETED
                                                    ├── PARTIAL
                                                    ├── FAILED
                                                    └── CANCELLED
```

- Preview và validate không ghi feedback production.
- User chỉ được `execute` từ `VALIDATED`; execute chuyển job sang `QUEUED`. Validation có row lỗi vẫn có thể ở `VALIDATED` nếu policy cho phép commit valid rows; lỗi cấp file/schema chuyển job sang `FAILED`.
- Mapping profile có version và có thể tái sử dụng theo source.
- Mỗi row giữ `import_job_id`, `source_row_number`, checksum/idempotency key và kết quả xử lý.
- Không silent-drop: row lỗi phải có error code/message và file lỗi tải được.
- Retry chỉ chạy row chưa thành công và không tạo feedback trùng.
- `reported_at` giữ timezone nguồn; nếu thiếu thì dùng `ingested_at` và đánh dấu `event_time_inferred=true`.
- `content_raw` immutable; masking tạo `content_masked` riêng trước khi gửi sang AI.

### FR-06 — Feedback Workspace

User có thể:

- search;
- filter;
- sort;
- paginate;
- show/hide columns;
- open detail;
- xem/tách feedback item;
- tạo decision version mới để sửa classification;
- bulk select;
- export;
- save view [P1].

Export raw content/PII là privileged action và luôn có audit. UI đọc current projection nhưng phải hiển thị được prediction/decision history trong detail.

### FR-07 — AI Classification

P0 outputs theo từng `feedback_item_id`:

```text
customer_lifecycle_step
service_request_step [optional]
primary_service
issue
sentiment
```

Mỗi prediction event:

```text
prediction_id
feedback_item_id
field_name
predicted_value
confidence
model_version
prompt_or_pipeline_version
taxonomy_release_id
created_at
```

P0 là **suggest-only**: prediction không được tự ghi vào current projection bất kể confidence. Mỗi item chỉ có một Primary Service. 0:N Candidate Cause Suggestions có schema từ P0 và AI chỉ sinh loại suggestion này từ P1.

### FR-08 — AI Review

- Queue theo field, confidence, source và age.
- Review endpoint chỉ nhận action canonical. `ACCEPT`, `CORRECT`, `MARK_UNKNOWN`, `MARK_MISSING`, `MARK_NOT_APPLICABLE` tạo ReviewEvent và immutable decision version; `SPLIT_REQUIRED`, `SKIP` chỉ tạo ReviewEvent.
- Decision version chứa snapshot nguyên tử, actor, reason, timestamp và prediction reference nếu có; concurrent stale write bị reject.
- Current projection được cập nhật idempotent từ decision version mới nhất có hiệu lực.
- Correction chỉ trở thành training/gold-set candidate sau khi Data Steward duyệt; không tự động train model production.
- Reviewer có thể split multi-intent thành nhiều feedback item trước khi quyết định nhãn.

### FR-09 — Hotspot

MVP dimension:

```text
Service
+ Issue
+ Location
+ Time window
```

Hotspot lưu:

```text
hotspot_id
dimension_key
score
level
first_seen
last_seen
affected_feedback_count
affected_feedback_item_count
affected_household_count [nullable]
status
owner_unit_id
owner_user_id
rule_version
acknowledged_at
resolved_at
```

`affected_household_count` chỉ hiển thị khi có household key đã pseudonymize và đạt data-quality gate; nếu không, metric là `N/A`, không suy diễn từ số feedback.

### FR-10 — Analytics

Dashboard bắt buộc drill-down:

```text
KPI
↓
Chart segment
↓
Filtered feedback list
↓
Feedback detail
```

Không có chart dead-end.

P0 có bốn dashboard basic trong pilot scope với multi-metric breakdown và drill-down. Advanced analytics như WoW/MoM/YoY, recurring issue, cross-project comparison và RCA metrics thuộc P1.

### FR-11 — Basic Access, PII & Audit

- P0 dùng SSO và bốn role tối thiểu: `PILOT_ADMIN`, `ANALYST`, `REVIEWER`, `VIEWER`.
- Quyền phải được enforce ở API, không chỉ ẩn control trên UI.
- Chỉ role được cấp privilege mới xem/export `content_raw` hoặc customer identifiers; user còn lại dùng `content_masked`.
- Audit tối thiểu cho login/admin action, import execution, raw-PII view/export, taxonomy publish, split item, classification decision, hotspot ownership/status và rule change.
- Fine-grained scope theo project/building/service và delegated administration thuộc P1; pilot vẫn phải giới hạn user vào đúng pilot project.

---

## 12. Mô hình Dữ liệu Feedback (Feedback Data Model)

### 12.1 Feedback envelope

```text
feedback_id
interaction_id
source_system
intake_channel
source_reference
source_record_key
import_job_id
source_row_number
reported_at
reported_timezone
event_time_inferred
ingested_at
content_raw
content_masked
project_id
source_location_text
customer_reference_hash [nullable]
household_reference_hash [nullable]
status
created_at
updated_at
```

### 12.2 Feedback item

```text
feedback_item_id
feedback_id
item_index
item_text_start [nullable]
item_text_end [nullable]
raw_text
normalized_text
item_text_masked
symptom_detail [nullable]
location_id [nullable]
intake_channel
split_source
status
analytic_eligibility
created_at
updated_at
```

Affected Channel là quan hệ 0:N qua `feedback_item_affected_channel`; `source_system` mô tả hệ thống nguồn, còn Intake/Affected Channel dùng code `CH-*` trong taxonomy. Location là 0:1 và `symptom_detail` là mô tả tự do, không phải master label mới.

### 12.3 Prediction event

```text
prediction_id
feedback_item_id
prediction_run_id
field_name
candidate_value_id
confidence
rank
model_version
prompt_or_pipeline_version
taxonomy_release_id
created_at
```

Một run có thể sinh nhiều candidate cho cùng field. `candidate_cause` được biểu diễn bằng nhiều prediction row, không bằng cột JSON không version.

### 12.4 Classification decision

```text
decision_id
feedback_item_id
decision_version
customer_lifecycle_value_status
customer_lifecycle_step_id [nullable]
service_request_value_status
service_request_step_id [nullable]
primary_service_value_status
primary_service_id [nullable]
issue_value_status
issue_id [nullable]
sentiment
operational_severity
cause_determination_status
other_reason [nullable; required for IS-10-01]
decision_source        # MANUAL | SOURCE_TRUSTED | HUMAN_ACCEPTED_AI | HUMAN_CORRECTED_AI | POLICY_AUTO_APPLIED | SYSTEM_MIGRATION
taxonomy_release_id
reason
decided_by
decided_at
supersedes_decision_id [nullable]
```

Mỗi decision là một snapshot nguyên tử, append-only. Candidate Cause dùng child relation `classification_decision_candidate_cause`; prediction được accept/correct được nối qua `classification_decision_prediction_ref`. Sửa sai bằng decision version mới có `supersedes_decision_id`, không cập nhật snapshot cũ. Review action chi tiết được lưu trong `review_event`.

### 12.5 Current classification projection

```text
feedback_item_id
current_decision_id
customer_lifecycle_value_status
customer_lifecycle_stage_id [nullable, derived from step]
customer_lifecycle_step_id [nullable]
service_request_value_status
service_request_step_id [nullable]
primary_service_value_status
primary_service_id [nullable]
issue_value_status
issue_id [nullable]
sentiment
operational_severity
cause_determination_status
other_reason [nullable]
classification_state
taxonomy_release_id
last_decision_at
projection_version
```

Mọi `*_value_status` dùng enum `KNOWN | UNKNOWN | MISSING | NOT_APPLICABLE`: `KNOWN` yêu cầu ID hợp lệ, các trạng thái còn lại yêu cầu ID null. Candidate Cause dùng read projection `classification_current_candidate_cause`, được rebuild từ decision snapshot hiện hành. Location/Channel/symptom detail được đọc từ Feedback Item; projection không chứa prediction chưa được quyết định.

### 12.6 Action relationships

`feedback_item_hotspot`, `feedback_item_ticket` và `feedback_item_rca` là join table N:N có `linked_by`, `linked_at`, `link_reason`. Không đặt `hotspot_id`, `ticket_id` hoặc `rca_id` đơn lẻ trên feedback.

---

## 13. Quy tắc Nghiệp vụ (Business Rules)

### BR-01

Một Lifecycle Step có thể liên quan nhiều Service.

### BR-02

Một Service có thể xuất hiện tại nhiều Lifecycle Step ở một hoặc cả hai lifecycle type.

### BR-03

Một Feedback có 1:N Feedback Item. Mỗi Feedback Item có tối đa một `primary_service` và không có Secondary Service; feedback multi-intent phải được tách item trước khi có nhiều primary issue.

### BR-04

Mỗi Feedback Item có tối đa một Location và 0:N Affected Channel. `symptom_detail` là mô tả tự do; không tạo Service/Issue mới chỉ vì khác Location, Channel, source system, vendor hoặc resolver.

### BR-05

Khi `issue_value_status=KNOWN`, Issue bắt buộc thuộc đúng primary Service đã biết của cùng current projection. Nếu đổi primary Service làm Issue không còn hợp lệ, transaction phải yêu cầu chọn Issue mới hoặc đặt `issue_value_status=UNKNOWN` với `issue_id=null`.

### BR-06

Candidate Cause là suggestion set 0:N. `UNKNOWN` không được tồn tại cùng cause cụ thể. Classification/review P0 chỉ ghi `NOT_ASSESSED | UNKNOWN | SUGGESTED | NOT_APPLICABLE`; `UNDER_INVESTIGATION | CONFIRMED` chỉ do Investigation/RCA P1 ghi. `CONFIRMED` bắt buộc có evidence và người có thẩm quyền.

### BR-07

AI không được auto-confirm Root Cause.

### BR-08

Root Cause `CONFIRMED` bắt buộc có:

```text
confirmed_by
confirmed_at
evidence
```

### BR-09

Safety hard trigger không phụ thuộc sentiment.

### BR-10

Technical feedback nên có Location và symptom detail. Asset/System không phải taxonomy dimension; investigation có thể liên kết asset/work-order reference riêng khi cần.

### BR-11

Mọi manual override phải có audit.

### BR-12

Không hard-delete ticket/taxonomy đã có dữ liệu lịch sử.

### BR-13

Prediction không phải classification đã chấp nhận. Chỉ `SOURCE_TRUSTED` theo source-trust policy được version/audit hoặc Human Decision mới cập nhật current projection trong P0.

### BR-14

Analytics và hotspot dùng `Feedback Item`, không dùng Feedback envelope. Chỉ item có `analytic_eligibility=INCLUDED` và current projection hợp lệ mới vào denominator.

### BR-15

Mọi timestamp dùng UTC khi lưu và timezone của location/source khi hiển thị, bucket analytics hoặc tính rolling window. Nếu event time bị suy diễn phải hiển thị cờ data quality.

### BR-16

`delivery_priority` và `operational_severity` là hai enum khác nhau, không dùng chung field, filter hoặc màu hiển thị.

### BR-17

Taxonomy, mapping, metric definition và hotspot rule phải versioned. Event/history cũ luôn truy ngược được version đã áp dụng.

### BR-18

Raw content immutable. Split item, masking, prediction, decision và projection không được sửa `content_raw`; quyền xem raw PII được kiểm tra server-side và audit.

---

## 14. Quản trị AI (AI Governance)

P0 vận hành ở chế độ **suggest-only** cho mọi confidence. Confidence chỉ dùng để sắp hàng review và phân tích calibration; không có threshold auto-apply trước khi có gold set và phê duyệt rủi ro theo từng field.

| Trạng thái     | Hành vi P0                                                       |
| ---------------- | ----------------------------------------------------------------- |
| Prediction mới  | Lưu riêng, không vào current projection/analytics             |
| Reviewer Accept  | Tạo decision version và cập nhật projection                   |
| Reviewer Correct | Tạo decision version; đưa vào gold-set candidate              |
| Reviewer Unknown | Projection dùng UNKNOWN có chủ đích                          |
| Safety/legal/RCA | Luôn cần người có thẩm quyền; AI không được xác nhận |

### P0

- Customer Lifecycle Step
- Service Request Step [khi có tín hiệu]
- Primary Service
- Issue
- Sentiment

Customer Lifecycle Stage không phải prediction field riêng; hệ thống derive Stage từ Customer Lifecycle Step trong cùng taxonomy release.

### Gold set và calibration — P0

- `gold_set_v1` chỉ gồm feedback item trong pilot scope, đã mask PII và có taxonomy version.
- Có labeling guideline, sampling rule, dataset version và holdout cố định.
- Tối thiểu 10% mẫu được hai reviewer độc lập gán nhãn để đo mức thống nhất; bất đồng phải adjudicate.
- Mục tiêu khởi tạo: tối thiểu 300 item đại diện và, khi dữ liệu cho phép, tối thiểu 20 item cho mỗi Issue nằm trong pilot scope. Nếu không đạt, báo thiếu coverage thay vì suy diễn metric.
- Báo cáo theo từng field: coverage, Macro-F1, per-label precision/recall, unknown rate, override rate và calibration error.
- Threshold auto-apply là quyết định P1 riêng theo từng field/model version; rollback được bằng feature flag.

### P1

- Priority suggestion
- Candidate Cause suggestion
- Handling Unit suggestion
- Duplicate detection

---

## 15. Logic Hotspot — MVP (Hotspot Logic — MVP)

### Detection key

```text
service_id
+ issue_id
+ location_id
+ rolling_time_window
```

`location_id` phải ở level được cấu hình trong rule, ví dụ Building hoặc Floor; không trộn level trong cùng detection key.

### Quy tắc Pilot Định tính / Rõ ràng (Deterministic pilot rule)

P0 không dùng anomaly score mơ hồ. Rule baseline:

```text
Trong rolling window W,
nếu có ít nhất N feedback_item INCLUDED
với cùng primary_service + issue + normalized_location,
sau source-record deduplication,
thì upsert một Hotspot CANDIDATE cho detection key đó.
```

- `W`, `N`, location level, in-scope Service/Issue và owner mặc định là cấu hình versioned.
- Baseline đề xuất để test vertical slice: `W=2 giờ`, `N=3`, Service=`SV-07`, Issue=`IS-07-01`, location level=`Building/Zone`. Đây là pilot default, không phải ngưỡng production toàn hệ thống.
- Chỉ accepted/source-trusted current projection được tính. Prediction chưa review, item excluded, duplicate và record thiếu detection dimension không được tính.
- Cùng `dimension_key + rule_version + active window` phải idempotent upsert, không tạo hotspot trùng.
- Mỗi candidate lưu danh sách evidence item để drill-down và tái tính.

### Lifecycle và ownership

```text
CANDIDATE → ACKNOWLEDGED → INVESTIGATING → RESOLVED
     └──────────────→ DISMISSED
RESOLVED/DISMISSED → REOPENED → INVESTIGATING
```

- Khi tạo candidate, owner mặc định lấy từ Service; nếu thiếu owner thì đưa vào unassigned queue và báo data-quality error.
- Mọi acknowledge, assign, reassign, dismiss, resolve, reopen phải có actor, timestamp và reason.
- `RESOLVED` hoặc `DISMISSED` không xóa evidence. Nếu rule tiếp tục vượt ngưỡng sau cooldown, hệ thống reopen hoặc tạo occurrence mới theo rule version.

### Signals P1

- Volume anomaly
- Rate of increase
- Negative ratio
- Priority mix
- Affected scope
- Recurrence

### Hard triggers — P1 sau phê duyệt

Ví dụ:

```text
PERSON_TRAPPED_ELEVATOR
FIRE
MAJOR_WATER_OUTAGE
BUILDING_WIDE_POWER_OUTAGE
LIFE_SAFETY
```

Hard trigger tạo alert ngay, không chờ hotspot volume. Danh sách trên chỉ là ví dụ; P0 không kích hoạt tự động cho tới khi Service Owner, Safety/Legal và BQL ký duyệt rule, operational severity, owner và playbook.

---

## 16. Phạm vi UI/UX — MVP (UI/UX Scope — MVP)

P0 ưu tiên workflow end-to-end, không yêu cầu mười navigation module độc lập. Các màn hình có thể dùng tab/drawer nếu vẫn giữ URL/filter context và quyền truy cập.

### Màn hình 01 — Import Jobs [P0]

- Upload/mapping profile
- Preview/validation summary
- Job progress và trạng thái
- Row error download/retry
- Batch audit/lineage

### Dashboard 01 — CX Overview [P0 basic]

- Total feedback
- Negative rate
- Top service
- Top issue
- Top location
- Active hotspot
- Trend
- Unknown/ineligible rate
- Mọi KPI/segment drill-down cùng filter context

### Màn hình 03 — Feedback Workspace [P0]

- Data grid
- Global filters
- Search
- Classification fields
- Confidence
- Review status
- Feedback item count/split indicator

### Màn hình 04 — Feedback Detail & Decision History [P0]

- Original content
- Source
- Customer/location context
- Customer Lifecycle/Service Request Lifecycle
- Primary Service, Issue và symptom detail
- AI predictions theo field
- Decision/current projection history
- Related feedback
- Hotspot/Ticket refs

### Màn hình 05 — AI Review [P0]

- Low confidence queue
- `ACCEPT`, `CORRECT`, `MARK_UNKNOWN`, `MARK_MISSING`, `MARK_NOT_APPLICABLE`
- `SPLIT_REQUIRED`, `SKIP`
- Split multi-intent qua mutation riêng

### Dashboard 02 — Customer Journey [P0 basic; P1 advanced]

- P0: Stage/Step breakdown với Feedback Volume, Negative Rate, Active Hotspots và Trend
- P0: filter Project/Date/Channel/Affected Channel/Location; không có Persona filter
- P1: WoW/MoM/YoY, comparison nâng cao và recurring issue

### Dashboard 03 — Service & Pain Points [P0 basic; P1 advanced]

- P0: Service/Issue breakdown với Feedback Volume, Negative Rate, Active Hotspots và Trend
- P0: Location/Channel/Affected Channel drill-down
- P1: cross-project comparison, recurrence, advanced trend period

### Dashboard 04 — Hotspot & Root Cause [P0 basic; P1 RCA]

- P0: hotspot list/detail, evidence, owner, status, Candidate Cause cơ bản
- P0: không hiển thị Investigation, Confirmed Root Cause hoặc Corrective/Preventive Action như chức năng khả dụng
- P1: Investigation, Confirmed Root Cause, Corrective Action, Preventive Action và RCA đầy đủ

### Màn hình 09 — Hotspot Detail [P0]

- Trend
- Related feedback
- Locations
- Candidate cause
- Owner
- Acknowledge/assign/dismiss/resolve/reopen timeline

### Màn hình 10 — Pilot Configuration & Taxonomy [P0 read/validate/publish]

- Customer/Service Request lifecycle dictionary
- Service tree
- Issue tree
- Location hierarchy
- Version/publish state
- Hotspot rule/owner
- Cause mapping [P1]

P0 configuration được load từ structured seed/migration đã review; màn hình không hỗ trợ row-level CRUD. Full taxonomy/location/rule editor thuộc P1.

### Màn hình 11 — Lifecycle-Service Matrix [P1 full editor]

- N:N mapping management

### Màn hình 12 — Access & Audit [P0 minimal]

- Pilot role assignment
- Raw PII/export privilege
- Privileged action audit search

---

## 17. Khung API Cơ sở (API Baseline)

### Feedback

```http
POST /api/v1/import-jobs
POST /api/v1/import-jobs/{id}/validate
POST /api/v1/import-jobs/{id}/execute
POST /api/v1/import-jobs/{id}/retry
GET  /api/v1/import-jobs/{id}
GET  /api/v1/import-jobs/{id}/errors
GET  /api/v1/feedback-items
GET  /api/v1/feedback/{id}
POST /api/v1/feedback/{id}/items/split
GET  /api/v1/feedback-items/{id}
GET  /api/v1/feedback-items/{id}/predictions
GET  /api/v1/feedback-items/{id}/decisions
POST /api/v1/feedback-items/{id}/decisions
GET  /api/v1/feedback-items/{id}/current-classification
```

P1 realtime ingestion thêm `POST /api/v1/feedback` với idempotency key; không dùng endpoint import file đồng bộ.

### Taxonomy

```http
GET /api/v1/customer-lifecycle/stages
GET /api/v1/customer-lifecycle/steps
GET /api/v1/service-request-lifecycle/steps
GET /api/v1/services
GET /api/v1/services/{id}/issues
GET /api/v1/issues/{id}/candidate-causes
GET /api/v1/lifecycle-service-mappings
GET /api/v1/locations
POST /api/v1/taxonomy-versions/{id}/validate
POST /api/v1/taxonomy-versions/{id}/publish
```

P0 không có row-level taxonomy/location/rule CRUD. Approved configuration được nạp bằng migration/structured seed package có checksum; API/UI chỉ đọc, hiển thị validation và publish một version đã `APPROVED`. Full editor và rollback UI thuộc P1.

### AI

```http
POST /api/v1/ai/prediction-jobs
GET  /api/v1/ai/prediction-jobs/{id}
POST /api/v1/ai/predictions/{id}/review
```

Review body dùng `action` thuộc bộ canonical ở §7.4; API không nhận alias như `AI_ACCEPTED`, `HUMAN`, `Unknown` hoặc `Mark Unknown`.

### Analytics [P0]

```http
GET /api/v1/analytics/summary
GET /api/v1/analytics/breakdown?dimension={journey_stage|journey_step|service|issue|location|intake_channel|affected_channel}
GET /api/v1/analytics/trend
```

Breakdown contract hỗ trợ multi-metric:

```text
dimension = journey_step | service | ...
metrics = item_volume, negative_rate, active_hotspots, trend
```

Mọi endpoint dùng chung filter context gồm Project, Date, Customer Lifecycle, Service Request Step, Service, Issue, Location, Intake Channel, Affected Channel, Sentiment và Severity. Persona không thuộc P0 filter contract.

### Hotspot

```http
GET  /api/v1/hotspots
GET  /api/v1/hotspots/{id}
POST /api/v1/hotspots/{id}/acknowledge
POST /api/v1/hotspots/{id}/assign
POST /api/v1/hotspots/{id}/dismiss
POST /api/v1/hotspots/{id}/resolve
POST /api/v1/hotspots/{id}/reopen
```

Mọi mutation endpoint nhận idempotency key khi có khả năng retry và trả correlation ID. Authorization, audit actor và taxonomy/rule version được xử lý server-side.

P1:

```http
POST /api/v1/tickets
POST /api/v1/rca
```

---

## 18. Yêu cầu Phi chức năng (Non-functional Requirements)

### Hiệu năng (Performance)

- Feedback list/filter p95 < 3s cho standard query trong pilot sizing đã ký duyệt.
- Feedback detail p95 < 2s.
- Standard dashboard p95 < 5s.
- Import và AI batch xử lý async; UI không chờ inference theo từng item để hoàn tất upload.
- Trước implementation phải chốt pilot sizing: số row lịch sử, daily ingest, concurrent user, retention và file-size limit. Nếu chưa chốt, latency target không được dùng để phê duyệt kiến trúc production.

### Độ tin cậy (Reliability)

- Core feedback read/decision availability target ≥ 99.9% sau khi pilot được đưa vào production limited.
- Import phải resumable/retryable.
- Idempotent ingestion.
- Current projection phải rebuild được từ immutable decision snapshots/review events.
- Backup/restore và recovery test phải phù hợp retention/PII policy được phê duyệt.

### Bảo mật (Security)

- SSO/basic RBAC là P0; fine-grained scope theo project/building/service là P1.
- Pilot user luôn bị giới hạn vào pilot project.
- Audit classification/operational-severity/root-cause changes.
- Mask PII ở analytics/AI khi không cần thiết.
- Attachment ngoài scope P0; khi đưa vào P1 phải dùng malware scan, access check và signed URL ngắn hạn.

### Khả năng Quan sát (Observability)

- Request correlation ID.
- API logs.
- Import job logs.
- AI model version.
- Data-quality metrics.
- Hotspot rule version.

---

## 19. Chỉ số Thành công (Success Metrics)

### 19.1 Ngữ nghĩa của Metric (Metric semantics)

- Đơn vị analytics mặc định là `feedback_item`; UI phải ghi rõ khi KPI đếm feedback envelope.
- `event_date` dùng `reported_at` theo timezone location/source; fallback `ingested_at` chỉ khi thiếu và phải gắn cờ inferred.
- `eligible_item`: item active, không duplicate/excluded, có current projection từ source trusted hoặc human decision và hợp lệ với taxonomy version.
- `item_volume`: số `feedback_item_id` distinct thỏa `eligible_item` trong filter context.
- `negative_rate`: số eligible item có `sentiment=NEGATIVE` chia số eligible item có sentiment xác định; UNKNOWN không nằm trong denominator và phải hiển thị `sentiment_unknown_rate` riêng.
- `taxonomy_coverage(field)`: số eligible item có giá trị active/UNKNOWN hợp lệ chia tổng item cần field đó.
- `unknown_rate(field)`: số eligible item có `UNKNOWN` chia tổng eligible item; coverage cao không được dùng để che unknown rate cao.
- `manual_override_rate(field)`: số accepted source/AI value bị reviewer sửa chia số decision đã review.
- `active_hotspots`: số hotspot chưa ở trạng thái `RESOLVED` hoặc `DISMISSED` trong cùng filter/dimension context.
- `trend`: chuỗi bucket thời gian của metric được yêu cầu; P0 hỗ trợ trend cơ bản, P1 mới thêm WoW/MoM/YoY comparison.
- Hotspot MTTD: thời gian từ feedback item đủ điều kiện thứ `N` trong rule đến `hotspot.created_at`; không tính từ feedback đầu tiên.
- Household count chỉ tính distinct pseudonymous household key; thiếu key thì metric là `N/A`.
- Mọi metric lưu `metric_definition_version`; chart và drill-down phải dùng cùng filter, eligibility và version.

### 19.2 Chỉ số Đợt phát hành Pilot (Pilot release metrics)

- 100% manual decision, taxonomy publish, raw-PII view/export và hotspot state/owner change có audit.
- 100% import row có outcome và lineage; không silent-drop.
- ≥ 95% in-scope item có primary Service hợp lệ sau review.
- ≥ 90% in-scope item có Customer Lifecycle Stage hợp lệ sau review.
- Issue unknown rate và location unknown rate phải có baseline tuần đầu; target giảm được chốt sau khi biết chất lượng nguồn, không đặt “Issue hoặc UNKNOWN” làm thành công.
- Hotspot deterministic test tạo đúng một candidate, evidence set đúng, owner/status đúng và không duplicate khi retry.

### 19.3 Đánh giá AI — không phải auto-apply gate P0 (AI evaluation)

Sau khi có `gold_set_v1`, báo cáo target định hướng:

```text
Primary Service Macro-F1 ≥ 0.88
Issue Macro-F1 ≥ 0.85
Customer Lifecycle Stage Macro-F1 ≥ 0.85
Sentiment Macro-F1 ≥ 0.90
```

Kết quả phải kèm sample size, label coverage, per-label precision/recall, calibration error và confidence interval. Không đạt target không chặn workflow manual của pilot; chỉ chặn quyết định bật auto-apply P1.

### 19.4 Kết quả Vận hành (Operational outcome)

- Đo median handling time/item và review queue age trong hai tuần baseline trước khi đặt target giảm.
- Đo Hotspot MTTD theo định nghĩa trên; target giảm chỉ so với cùng nguồn dữ liệu và rule version.
- Repeat issue rate và hiệu quả RCA bắt đầu đo ở P1 sau khi Ticket/RCA có system-of-record rõ ràng.

---

## 20. Phạm vi MVP (MVP Scope)

### P0 — Pilot Build Baseline

P0 là production-limited pilot, không phải rollout vận hành trên toàn doanh nghiệp. Taxonomy release vẫn phải publish đủ canonical 10 Service/28 Issue và 6 Customer Lifecycle Stage/36 Step; `pilot_scope_manifest` giới hạn dữ liệu và tính năng vận hành vào 1–3 Service, Issue tương ứng, project/building, date range, source, user cohort và volume target. Vertical slice `SV-07 / IS-07-01` với symptom detail “chờ thang máy lâu” là scope tối thiểu.

1. Domain schema/migration cho Feedback → Feedback Item → Prediction/Decision → Current Projection.
2. Basic SSO/RBAC, raw PII privilege và immutable audit.
3. Hai lifecycle dictionary riêng; canonical 10 Service/28 Issue; pilot Lifecycle-Service mapping; location hierarchy; version/publish workflow tối thiểu.
4. Async CSV/XLSX import có validation, idempotency, row lineage, retry và error report.
5. Feedback Workspace/Detail; manual split; manual/source classification decision.
6. AI suggest-only theo field; review queue; gold set/calibration workflow.
7. Bốn dashboard P0 cơ bản: CX Overview, Customer Journey, Service & Pain Points, Hotspot & Root Cause; breakdown multi-metric và drill-down thống nhất.
8. Deterministic Hotspot rule cho vertical slice; lifecycle, owner, evidence và idempotent upsert.
9. Essential data-quality summary và operational observability.

Các Service/Issue ngoài pilot usage scope vẫn phải có trong structured seed và vượt taxonomy release gate; chúng không bắt buộc có dữ liệu vận hành trong P0.

### P1 — Mở rộng Vận hành (Operational Expansion)

1. Full taxonomy Admin UI, approval/rollback và Lifecycle-Service Matrix.
2. Realtime Feedback API/connectors, saved/shared views và governed export.
3. Advanced analytics cho Journey/Service; WoW/MoM/YoY, recurring issue và cross-project comparison.
4. Generalized hotspot/anomaly engine, hard-trigger alerts sau phê duyệt và duplicate clustering.
5. Lightweight ticket/case hoặc integration tới system of record; assignment và SLA.
6. Asset/work-order integration phục vụ investigation (không mở rộng taxonomy), Candidate Cause AI 0:N, RCA và action tracking.
7. Fine-grained RBAC theo project/building/service.
8. Auto-apply label low-risk chỉ sau gold-set calibration, risk sign-off và feature flag.

### P2 — Trí tuệ Nâng cao (Advanced Intelligence)

1. BMS/IoT và work-order integration sâu.
2. Predictive maintenance.
3. AI Root Cause Assistant.
4. Customer 360 theo consent/retention policy.
5. AI CX Analyst, semantic clustering và cross-project benchmarking.

---

## 21. Phân chia Tính năng, Thứ tự Xây dựng & Quy tắc Nhóm (Feature Slicing, Build Order & Team Rules)

### 21.1 Feature slices

| Slice                        | Outcome có thể demo/test                                                                    | Delivery |
| ---------------------------- | --------------------------------------------------------------------------------------------- | -------- |
| `F0 Governance Foundation` | Pilot scope, enums, SSO/basic roles, PII policy enforcement, audit/correlation ID             | P0       |
| `F1 Reference Data`        | Hai lifecycle, Service/Issue, mapping, location được seed/validate/publish bằng stable ID | P0       |
| `F2 Trusted Intake`        | Một file thật đi qua async job; mọi row có feedback hoặc error/lineage                  | P0       |
| `F3 Human Classification`  | Feedback được tách item, quyết định nhãn, rebuild projection và filter/drill-down    | P0       |
| `F4 AI Assist`             | Suggestion theo field được review; correction vào gold-set candidate; không auto-apply   | P0       |
| `F5 Pilot Insight`         | KPI versioned drill-down đúng về eligible item                                             | P0       |
| `F6 Detect & Own`          | Rule thang máy tạo đúng một hotspot, có evidence, owner và lifecycle                   | P0       |
| `F7 Operational Action`    | Ticket/SLA/RCA hoặc integration system of record                                             | P1       |

### 21.2 Thứ tự xây dựng đề xuất (Recommended build order)

```text
F0 Scope + terminology + security/audit contract
 → F1 Taxonomy/location seed + version/publish
 → F2 Async import + immutable feedback envelope
 → F3 Feedback item + decision ledger + current projection + workspace
 → F4 AI prediction ledger + review + gold set
 → F5 Metric layer + 4 basic dashboards/drill-down
 → F6 Deterministic hotspot + owner/lifecycle
 → P1 connectors, full analytics, ticket/SLA/RCA
```

Không build AI, chart hoặc hotspot trực tiếp trên raw import table. Tất cả phải đi qua feedback item và current projection contract.

### 21.3 Quy tắc mọi team phải tuân thủ khi build

1. **Stable contract first:** schema, enum, API và event contract được review trước UI; change breaking cần migration/version.
2. **No hard-code taxonomy/rules:** code chỉ dùng stable ID; wording, mapping, threshold, owner và effective date nằm trong versioned config.
3. **Append-only evidence:** raw feedback, prediction, decision và audit event không overwrite; projection/cache phải rebuild được.
4. **Server-side security:** API enforce scope/PII privilege; UI hiding không được coi là authorization.
5. **Idempotent async jobs:** import, AI và hotspot retry không tạo duplicate; mọi job có state, correlation ID và observable error.
6. **Metric consistency:** chart, KPI, export và drill-down dùng cùng semantic layer, eligibility rule, event time và definition version.
7. **Traceability:** mỗi story map tới acceptance test, API/schema change, audit event và metric/alert liên quan.
8. **Vertical slice before breadth:** hoàn tất `SV-07/IS-07-01/S2` end-to-end trước khi mở service, source hoặc dashboard mới.
9. **Feature flags:** AI auto-apply, hard trigger và connector mutation mặc định off cho tới khi có sign-off.
10. **No silent fallback:** missing taxonomy/location/time/owner phải thành UNKNOWN hoặc data-quality error có thể quan sát, không tự đoán âm thầm.

---

## 22. Lát cắt Dọc Thủ công Đầu tiên — FEAT-001 (First Manual Vertical Slice — FEAT-001)

### 22.1 Manual intake-to-insight

Input:

```text
"Thang máy S2 sáng nào cũng phải chờ rất lâu."
```

Pipeline:

```text
Async Import Job + row lineage
↓
Feedback envelope (immutable raw/masked)
↓
Feedback Item #1
  Location = S2 normalized location ID
  Intake Channel = channel code canonical
  Symptom Detail = Chờ thang máy lâu vào buổi sáng
↓
Manual Classification Decision v1
↓
Current Projection:
  Customer Lifecycle Stage = Cư trú
  Customer Lifecycle Step = RES-03 Ra vào & di chuyển
  Service Request Value Status = NOT_APPLICABLE
  Service Request Step = null
  Primary Service = SV-07 Kỹ thuật, tiện ích & tài sản chung
  Issue = IS-07-01 Hệ thống ngừng hoặc suy giảm
  Cause Determination Status = UNKNOWN
  Candidate Cause Suggestions = []
  Operational Severity = reviewer/source decision
↓
Pilot Analytics + eligible-item drill-down
```

### 22.2 Mở rộng về sau — F6 Detect & Own (Later extension — F6 Detect & Own)

Sau khi `FEAT-001` hoàn tất, slice `F6` mở rộng cùng contract khi nhiều feedback tương tự xuất hiện:

```text
SV-07
+ IS-07-01
+ normalized S2 location ID
+ rolling 2h
+ at least 3 accepted, deduplicated feedback items
→ idempotent Hotspot CANDIDATE
→ default Service owner
→ acknowledge / investigate / resolve or dismiss
```

Acceptance demo của `FEAT-001` phải chứng minh retry import không tạo duplicate, manual correction không overwrite history và mọi decision có audit. AI và hotspot được thêm ở các slice sau; khi tới `F6`, retry hotspot không được tạo duplicate và prediction chưa review không được xuất hiện trong analytics/hotspot. Hoàn tất manual intake-to-insight end-to-end trước khi mở rộng platform.

---

## 23. Định nghĩa Sẵn sàng — Feature/Slice (Definition of Ready — Feature/Slice)

Một feature/slice chỉ vào sprint khi:

- Có outcome, persona, delivery priority và acceptance criteria kiểm thử được.
- `pilot_scope_manifest` và dữ liệu mẫu đại diện đã được Product/Data Owner duyệt.
- Lifecycle/Service/Issue/Location stable ID và version cần dùng đã ở `PUBLISHED` hoặc có fixture được duyệt.
- Cardinality, enum, source of truth, API/schema/event contract và migration impact đã thống nhất.
- Metric definition/eligibility/filter context đã chốt nếu feature tạo KPI/chart/export/hotspot.
- PII classification, role/permission, audit event và retention impact đã được Security/Data Owner review.
- Error/empty/loading/retry/idempotency behavior đã có trong acceptance criteria.
- Dependency, owner và rollout/feature-flag plan đã rõ; không còn open decision làm thay đổi kiến trúc của slice.

UI/UX có thể wireframe song song khi contract baseline đã có; không cần chờ toàn bộ taxonomy hoàn hảo, nhưng không được tự tạo terminology hoặc cardinality khác PRD.

---

## 24. Định nghĩa Hoàn tất — MVP (Definition of Done — MVP)

MVP được xem là hoàn thành khi:

1. `pilot_scope_manifest` được named Product Owner, Data Owner, Service Owner và Security/Privacy Owner ký duyệt.
2. SSO/basic RBAC hoạt động; raw PII view/export và mọi privileged action được enforce server-side và audit.
3. Import dataset thật chạy async, retry idempotent; 100% row có outcome/lineage và error report; không silent-drop.
4. Hai lifecycle dictionary có đủ 6 Customer Lifecycle Stage/36 Step và 8 Service Request Step; taxonomy release có đủ canonical 10 Service/28 Issue; pilot mapping và location hierarchy dùng stable ID/version, publish được và không hard-code trong application.
5. Feedback envelope giữ raw immutable; feedback multi-intent tách được thành item; decision ledger rebuild được current projection.
6. User filter Customer Lifecycle/Service Request/Service/Issue/Location/Intake Channel/Affected Channel/Severity được trên eligible feedback item; không có Persona filter; drill-down giữ nguyên filter/metric version.
7. AI trả prediction theo field với confidence/model/pipeline/taxonomy version nhưng không auto-apply; reviewer dùng đủ 7 action canonical và Decision/ReviewEvent được tạo đúng quy tắc.
8. `gold_set_v1` có guideline, dataset version, holdout, coverage report và baseline metrics; thiếu label coverage được báo rõ.
9. Bốn dashboard P0 trả đúng `item_volume`, `negative_rate`, `active_hotspots`, `trend` theo cùng analytics contract và khớp truy vấn/drill-down kiểm chứng.
10. Deterministic rule tạo đúng một hotspot candidate từ accepted items, gắn đúng evidence/owner/rule version; acknowledge/assign/dismiss/resolve/reopen có audit và retry không duplicate.
11. Data quality hiển thị import error, duplicate, invalid taxonomy/location, unknown/ineligible và missing owner.
12. Contract/unit/integration test cho authorization, import idempotency, decision projection, metric query và hotspot lifecycle pass; migration/rollback, logs, correlation ID và runbook pilot đã được kiểm tra.
13. Không còn decision mở nào trong `§26` được đánh dấu `Blocks P0`; issue còn lại có owner, deadline và feature flag/default an toàn.

---

## 25. Tài liệu Tham khảo Nghiên cứu (Research References)

- Vinhomes — Thẻ cư dân, thang máy và tiện ích: https://vinhomes.vn/vi/the-cu-dan-vinhomes
- Vinhomes Smart City — Face ID, phân tầng thang máy: https://smartcity.vinhomes.vn/thanh-pho-thong-minh/
- Vinhomes — Thanh toán hóa đơn V-App: https://vinhomes.vn/vi/thanh-toan-hoa-don-tren-v-app-hoan-vpoint-sieu-hap-dan
- IBM — Facility maintenance scope: https://www.ibm.com/think/topics/facility-maintenance
- KONE — Elevator condition monitoring: https://origin-www.kone.com/en/products-and-services/maintenance-and-modernization/24-7-connected-services.aspx

---

## 26. Các Quyết định Mở cho Hội thảo Stakeholder (Open Decisions for Stakeholder Workshop)

Mỗi decision phải có một người chịu trách nhiệm theo vai trò, deadline và link Decision Record. “Cần workshop” không được dùng như trạng thái vô thời hạn.

| Decision                                                                                                                           | Delivery impact                                                 | Accountable role            | Default an toàn nếu chưa chốt                                         |
| ---------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------- | --------------------------- | ------------------------------------------------------------------------- |
| Pilot project/building, 1–3 Service, source, date range, volume và user cohort                                                   | **Blocks P0**                                             | Product Owner               | Không bắt đầu Sprint 1                                                |
| Data sample quyền sử dụng, language/encoding, required columns và source trust rule                                            | **Blocks P0**                                             | Data Owner                  | Chỉ synthetic fixture; không production data                            |
| Authoritative `service_taxonomy.md` revision 3.0.0, structured-seed checksum, approval owner và nơi lưu được team truy cập | **Blocks P0 taxonomy publish**                            | Product + Data Owner        | Không publish taxonomy release                                           |
| Multi-intent split guideline và field nào bắt buộc/cho phép UNKNOWN                                                           | **Blocks P0**                                             | CX/Data Steward             | Manual split; prediction không auto-apply                                |
| Location hierarchy, normalized S2 ID, grouping level và timezone                                                                  | **Blocks P0**                                             | BQL + Data Owner            | Record thiếu location bị ineligible cho hotspot                         |
| Pilot Service/Issue owner và mapping; mapping legacy Priority P1–P4 sang SEV-1–SEV-4                                            | **Blocks P0**                                             | Service Owner               | Không publish taxonomy version                                           |
| PII classification, masking, retention, raw-view/export role và AI data boundary                                                  | **Blocks P0**                                             | Security/Privacy Owner      | Mask trước AI; deny raw/export by default                               |
| Hotspot pilot `N`, `W`, location level, cooldown, owner và resolve/dismiss playbook                                            | **Blocks P0**                                             | CX Manager + Service Owner  | Dùng test default chỉ trong non-production; feature flag off production |
| Pilot sizing, file limit, daily ingest, concurrent users và retention                                                             | **Blocks P0 architecture/performance sign-off**           | Product + Engineering       | Không tuyên bố production SLO                                          |
| Gold-set sampling, label guideline, adjudication owner và target coverage                                                         | **Blocks P0 AI evaluation**, không block manual workflow | Data Steward + ML Lead      | AI suggest-only; không auto-apply                                        |
| Metric baseline window, eligible source và operational target                                                                     | P0 measurement                                                  | Product Analytics           | Hiển thị baseline, chưa tuyên bố % cải thiện                       |
| Fine-grained RBAC theo project/building/service                                                                                    | P1                                                              | Security + Platform Owner   | Pilot project allowlist                                                   |
| Realtime API/connectors và idempotency contract theo source                                                                       | P1                                                              | Integration Owner           | File import P0                                                            |
| Ticket/Case system of record; native module hay integration                                                                        | P1                                                              | Operations Owner            | Chỉ lưu external reference trong P0                                     |
| SLA từng Service/Issue, assignment/escalation và contractor/vendor ownership                                                     | P1                                                              | Operations + Service Owner  | Không hiển thị SLA giả định                                         |
| Hard trigger chính thức, SEV-1 rule và safety/legal playbook                                                                    | P1; không bật tự động ở P0                                | Safety/Legal + BQL          | Feature flag off; manual escalation                                       |
| Required evidence và thẩm quyền confirm Root Cause                                                                              | P1                                                              | Technical Owner + Legal     | Không có trạng thái CONFIRMED                                         |
| Asset hierarchy/BMS/CMMS naming và work-order integration cho investigation (không phải taxonomy dimension)                     | P1/P2                                                           | Technical/Integration Owner | Không gắn asset vào classification; investigation reference nullable   |
| Survey policy CSAT/CES/NPS                                                                                                         | P2                                                              | CX Owner                    | Ngoài pilot                                                              |
