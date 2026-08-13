# 02 — Taxonomy Dịch vụ Bất động sản Nhà ở (Residential Real Estate Service Taxonomy)

- **Dự án:** CX Intelligence & Operations Platform
- **Phiên bản tài liệu:** 3.0.0
- **Phạm vi nghiệp vụ:** Chủ đầu tư nhà ở + giao dịch + bàn giao + cư trú + quản lý vận hành chung cư/khu dân cư
- **Quy mô tiêu chuẩn (Canonical size):** 10 Service / 28 Issue đại diện
- **Hành trình (Journey):** 6 Customer Lifecycle Stage / 36 Customer Journey Step / 8 Service Request Step
- **Mục đích:** Một không gian nhãn (label space) ngắn gọn, dễ phân loại, đủ dùng cho dashboard, xác định quyền sở hữu (ownership) và phân tích nguyên nhân gốc rễ

> Taxonomy hỗ trợ phân loại và điều phối. Nó không tự xác lập trách nhiệm pháp lý, nghĩa vụ bảo hành, phần sở hữu chung–riêng hoặc nguồn kinh phí.

## 1. Mô hình Phân loại (Classification Model)

```text
Feedback Envelope
  ├── Source System
  └── Intake Channel
        ↓ 1:N
Feedback Item / Atomic Observation
  ├── Customer Lifecycle Stage/Step   0:1
  ├── Service Request Step            0:1
  ├── Primary Service                 0:1
  ├── Canonical Issue                 0:1; thuộc Primary Service
  ├── Location                        0:1
  ├── Affected Channel                0:N
  └── symptom_detail + evidence
```

### 1.1 Khái niệm

| Entity | Trả lời câu hỏi | Không dùng để biểu diễn |
| --- | --- | --- |
| Customer Lifecycle Stage/Step | Khách hàng hoặc tài sản đang ở giai đoạn nào? | Trạng thái xử lý ticket |
| Service Request Step | Yêu cầu đang ở bước phục vụ nào? | Giai đoạn khách hàng |
| Service | Outcome/năng lực nào chịu trách nhiệm chính? | Phòng ban, vendor, channel, asset |
| Issue | Nhóm failure nào đã quan sát? | Nguyên nhân chưa xác nhận |
| symptom_detail | Biểu hiện cụ thể là gì? | Master code để chia nhỏ dashboard |
| Candidate Cause | Giả thuyết điều tra nào có thể đúng? | Confirmed Root Cause |

### 1.2 Quy tắc bắt buộc

1. Một `feedback_item` chỉ chứa một `customer intent` hoặc một `observable failure`; nhiều ý định (`multi-intent`) phải chia nhỏ (`split`).
2. Khi `Primary Service` và `Issue` đều có `value_status = KNOWN`, item phải có đúng một Primary Service và Issue bắt buộc thuộc Primary Service đó trong cùng taxonomy release. `Primary Service` có thể là `KNOWN` trong khi `Issue` là `UNKNOWN` nếu chưa đủ thông tin để xác định Issue cụ thể.
3. Không tạo Service/Issue mới chỉ vì khác location, channel, source system, vendor hoặc resolver.
4. Không gộp purchase ledger với resident ledger chỉ vì đều là thanh toán.
5. SV-10/IS-10-01 chỉ dùng khi nội dung đã rõ nhưng không thuộc SV-01..SV-09; bắt buộc có `other_reason` và `review`.
6. Hard trigger không chờ classifier hoàn tất.
7. AI không tự xác nhận Root Cause, warranty eligibility hoặc legal responsibility.

## 2. Từ điển Hành trình (Journey Dictionary)

### 2.1 Hai chiều Hành trình (Journey)

| Dimension | Phạm vi | Code | Cardinality |
| --- | --- | --- | --- |
| CUSTOMER_LIFECYCLE | 6 stage: Nhận thức, Xem xét, Giao dịch, Nhận nhà, Cư trú, Vận hành | A, C, TR, HO, RES, OPS | 0:1 step trên feedback item |
| SERVICE_REQUEST_LIFECYCLE | Vòng đời của một yêu cầu dịch vụ | SRV | 0:1 step trên feedback item/case |

Vận hành là stage thứ sáu, dùng cho record mô tả hoạt động quản lý tài sản và dịch vụ sau bàn giao. Cư trú vẫn dùng cho trải nghiệm/touchpoint trực tiếp của cư dân. Service Request Lifecycle là chiều độc lập.

### 2.2 Customer Lifecycle — Nhận thức

| Code | Bước |
| --- | --- |
| A1 | Tiếp cận thương hiệu/dự án |
| A2 | Khám phá nội dung & thông tin ban đầu |
| A3 | Nhận giới thiệu / tham gia hoạt động quảng bá |

### 2.3 Customer Lifecycle — Xem xét

| Code | Bước |
| --- | --- |
| C1 | Tìm hiểu dự án & sản phẩm |
| C2 | Đánh giá vị trí, thiết kế & tiện ích |
| C3 | Xem quỹ căn & so sánh lựa chọn |
| C4 | Đánh giá pháp lý, giá & chính sách |
| C5 | Đánh giá khả năng tài chính |
| C6 | Nhận tư vấn & tham quan |

### 2.4 Customer Lifecycle — Giao dịch

| Code | Bước |
| --- | --- |
| TR-01 | Yêu cầu giữ căn hoặc gửi booking |
| TR-02 | Xác minh khách hàng & hồ sơ |
| TR-03 | Đặt cọc & xác nhận giao dịch |
| TR-04 | Chọn phương án tài chính & thanh toán |
| TR-05 | Ký hợp đồng mua bán |
| TR-06 | Thực hiện nghĩa vụ & thay đổi sau ký |

### 2.5 Customer Lifecycle — Nhận nhà

| Code | Bước |
| --- | --- |
| HO-01 | Nhận thông báo & chuẩn bị bàn giao |
| HO-02 | Đặt lịch & làm thủ tục bàn giao |
| HO-03 | Kiểm tra & nghiệm thu căn |
| HO-04 | Ghi nhận tồn tại / yêu cầu khắc phục |
| HO-05 | Hoàn tất nhận nhà & hồ sơ |

### 2.6 Customer Lifecycle — Cư trú

| Code | Bước |
| --- | --- |
| RES-01 | Thiết lập hồ sơ & quyền cư dân |
| RES-02 | Sử dụng hệ thống & kênh cư dân |
| RES-03 | Ra vào & di chuyển |
| RES-04 | Tiếp khách |
| RES-05 | Sử dụng tiện ích & dịch vụ |
| RES-06 | Thanh toán phí & nghĩa vụ cư trú |
| RES-07 | Gửi yêu cầu / phản ánh / sự cố |
| RES-08 | Thực hiện thay đổi liên quan căn hộ |

### 2.7 Customer Lifecycle — Vận hành

| Code | Bước vận hành | Nội dung chính |
| --- | --- | --- |
| OPS-01 | Tiếp nhận & huy động vận hành | Hồ sơ O&M, asset register, warranty, hợp đồng, nhân sự, vendor và readiness |
| OPS-02 | Lập kế hoạch, ngân sách & nguồn lực | Service standard, ngân sách, bảo trì, staffing, SLA và kế hoạch khẩn cấp |
| OPS-03 | Vận hành thường nhật & giám sát | Control room, tuần tra, chỉ số/cảnh báo, utilities, access, parking và tiện ích |
| OPS-04 | Kiểm tra, thử nghiệm & bảo trì định kỳ | Inspection, preventive/predictive maintenance, kiểm định và planned outage |
| OPS-05 | Chẩn đoán, sửa chữa & khôi phục | Work order, cô lập, sửa/thay, thử chức năng và đưa tài sản trở lại phục vụ |
| OPS-06 | Ứng phó sự cố, khẩn cấp & duy trì liên tục | Triage, dispatch, containment, sơ tán, phương án dự phòng và recovery |
| OPS-07 | Xác minh, tuân thủ & đánh giá hiệu suất | Nghiệm thu, hồ sơ pháp định, audit, SLA/KPI, vendor và hiệu suất tài nguyên |
| OPS-08 | Cải tiến, đổi mới & chuyển giao | RCA/CAPA, tối ưu, thay thế, capital works, recommissioning và transition |

Vận hành là chu kỳ, không phải funnel bắt buộc:

```text
OPS-01 → OPS-02 → OPS-03
                   ↕
              OPS-04 / OPS-05
                   ↓
                 OPS-07 → OPS-08 → OPS-02

Sự cố từ OPS-03/04/05 → OPS-06 → OPS-07
```

### 2.8 Service Request Lifecycle

| Code | Bước |
| --- | --- |
| SRV-01 | Tìm thông tin |
| SRV-02 | Gửi yêu cầu |
| SRV-03 | Xác nhận/phê duyệt |
| SRV-04 | Thanh toán |
| SRV-05 | Được phục vụ |
| SRV-06 | Theo dõi/escalate |
| SRV-07 | Hoàn tất |
| SRV-08 | Đánh giá |

### 2.9 Kênh Tương tác (Interaction Channel)

| Code | Channel |
| --- | --- |
| CH-APP | Ứng dụng di động |
| CH-WEB | Website/Portal |
| CH-HOTLINE | Hotline/Call Center |
| CH-EMAIL | Email |
| CH-FRONTDESK | Quầy lễ tân/Service Desk |
| CH-SOCIAL | Mạng xã hội/Messaging |
| CH-INPERSON | In-person/Site Visit |
| CH-SYSTEM | Machine/System event |

CRM, ERP, BMS, CMMS, contact-center platform và sensor feed là source_system, không phải Channel.

---

## 3. Danh mục Dịch vụ Tiêu chuẩn (Canonical Service Catalog) — 10 Service

### 3.1 Ranh giới Dịch vụ (Service Boundaries)

| Code | Service (VI / EN) | Bao gồm |
| --- | --- | --- |
| SV-01 | Thông tin, bán hàng & giao dịch / Information, Sales & Transaction | Thông tin dự án, tư vấn, tham quan, quỹ căn, booking, KYC, đặt cọc và hợp đồng |
| SV-02 | Tài chính mua nhà, bàn giao & bảo hành / Purchase Finance, Handover & Warranty | Khoản vay, purchase ledger, thanh toán, kiểm tra/tiếp nhận nhà, claim và khắc phục |
| SV-03 | Hồ sơ, hỗ trợ & trải nghiệm số cư dân / Resident Administration, Support & Digital | Hồ sơ cư dân, tài khoản, app/portal, case handling và truyền thông |
| SV-04 | Hóa đơn, phí & thanh toán cư dân / Resident Billing & Payments | Resident ledger, invoice, fee, payment, posting, adjustment và refund |
| SV-05 | Ra vào, khách, bãi xe & di chuyển / Access, Visitor, Parking & Mobility | Credential, Face ID, intercom, visitor, LPR/barrier, parking và shuttle |
| SV-06 | Tiện ích, cải tạo & chuyển nhà / Amenities, Renovation & Move Services | Booking/admission tiện ích, permit/compliance cải tạo, move-in/out logistics |
| SV-07 | Kỹ thuật, tiện ích & tài sản chung / Engineering, Utilities & Common Assets | Elevator, water, electrical, generator, HVAC, building fabric, maintenance và major works |
| SV-08 | An ninh, PCCC & khẩn cấp / Security, Fire & Emergency | Intrusion, theft, disturbance, security response, fire system, egress, evacuation và continuity |
| SV-09 | Vệ sinh, môi trường & cảnh quan / Cleaning, Environment & Grounds | Cleaning, hygiene, waste, pest, landscaping và environmental nuisance |
| SV-10 | Khác / Other | Nội dung rõ nhưng không thuộc SV-01..SV-09 |

---

## 4. Danh mục Vấn đề Tiêu chuẩn (Canonical Issue Catalog) — 28 Issue

### SV-01 — Information, Sales & Transaction (3)

| Code | Issue | Bao gồm |
| --- | --- | --- |
| IS-01-01 | Thông tin thiếu hoặc không chính xác / Information Missing or Inaccurate | Project, product, legal, policy, price hoặc content unavailable/stale |
| IS-01-02 | Tư vấn, tham quan hoặc giữ chỗ không đạt / Advisory, Viewing or Reservation Failure | Contact, appointment, availability, booking, duplicate hoặc confirmation |
| IS-01-03 | Hồ sơ hoặc giao dịch không hoàn tất / Dossier or Transaction Failure | KYC, document, contract data, e-sign, amendment hoặc transfer |

### SV-02 — Purchase Finance, Handover & Warranty (3)

| Code | Issue | Bao gồm |
| --- | --- | --- |
| IS-02-01 | Tài chính hoặc quyết toán mua nhà có vấn đề / Purchase Finance or Settlement Failure | Loan, payment, allocation, due amount, adjustment hoặc refund |
| IS-02-02 | Bàn giao hoặc nghiệm thu không đạt / Handover or Acceptance Failure | Readiness, schedule, inspection, area, defect capture hoặc acceptance |
| IS-02-03 | Bảo hành hoặc khắc phục không đạt / Warranty or Remediation Failure | Scope unclear, delay, ineffective repair, recurrence hoặc invalid closure |

### SV-03 — Resident Administration, Support & Digital (3)

| Code | Issue | Bao gồm |
| --- | --- | --- |
| IS-03-01 | Hồ sơ hoặc quyền cư dân sai / Resident Record or Entitlement Incorrect | Household/unit/profile/role/account status |
| IS-03-02 | Nền tảng số hoặc case handling lỗi / Digital Platform or Case Handling Failure | Login, OTP, crash, API, missing/duplicate case, wrong owner, premature closure |
| IS-03-03 | Hỗ trợ hoặc truyền thông không đạt / Support or Communication Failure | Response, audience, timing, clarity, follow-up hoặc notification |

### SV-04 — Resident Billing & Payments (3)

| Code | Issue | Bao gồm |
| --- | --- | --- |
| IS-04-01 | Hóa đơn hoặc phí sai / Charge or Invoice Incorrect | Tariff, amount, penalty hoặc duplicate |
| IS-04-02 | Thanh toán hoặc ghi nhận thất bại / Payment or Posting Failure | Gateway, bank, callback, reference, allocation hoặc reconciliation |
| IS-04-03 | Điều chỉnh hoặc hoàn tiền chậm / Adjustment or Refund Delay | Adjustment, deposit settlement, refund hoặc document issuance delay |

### SV-05 — Access, Visitor, Parking & Mobility (3)

| Code | Issue | Bao gồm |
| --- | --- | --- |
| IS-05-01 | Ra vào hoặc hành trình khách thất bại / Access or Visitor Failure | Card, Face ID, floor permission, intercom, registration hoặc check-in |
| IS-05-02 | Dịch vụ bãi xe không đạt / Parking Service Failure | LPR, barrier, entitlement, capacity, congestion hoặc availability |
| IS-05-03 | Di chuyển nội khu không đạt / Estate Mobility Failure | Route, stop, schedule, realtime information, missed trip hoặc capacity |

### SV-06 — Amenities, Renovation & Move Services (3)

| Code | Issue | Bao gồm |
| --- | --- | --- |
| IS-06-01 | Tiện ích không đặt hoặc sử dụng được / Amenity Reservation or Use Failure | Booking, slot, eligibility, admission, opening status hoặc equipment |
| IS-06-02 | Phê duyệt hoặc kiểm soát cải tạo không đạt / Renovation Approval or Compliance Failure | Dossier, approval, contractor, schedule, access, noise hoặc damage assessment |
| IS-06-03 | Chuyển vào/chuyển ra không đạt / Move Service Failure | Registration, loading bay, freight lift, vehicle, contractor hoặc logistics |

### SV-07 — Engineering, Utilities & Common Assets (3)

| Code | Issue | Bao gồm |
| --- | --- | --- |
| IS-07-01 | Hệ thống ngừng hoặc suy giảm / System Outage or Degradation | Elevator, water, electrical, generator, HVAC outage/performance/quality |
| IS-07-02 | Rò rỉ hoặc điều kiện kỹ thuật nguy hiểm / Leakage or Unsafe Technical Condition | Leak, blockage, flooding, entrapment, abnormal stop, overheat, burning smell |
| IS-07-03 | Tài sản chung hoặc bảo trì không đạt / Common Asset or Maintenance Failure | Fabric defect, preventive/capital work, inspection, vendor/compliance record |

### SV-08 — Security, Fire & Emergency (3)

| Code | Issue | Bao gồm |
| --- | --- | --- |
| IS-08-01 | Sự kiện an ninh / Security Incident | Unauthorized access, theft, suspicious behavior, disturbance hoặc threat |
| IS-08-02 | Giám sát hoặc phản ứng an ninh thất bại / Security Monitoring or Response Failure | CCTV, hotline, guard, patrol, dispatch hoặc response |
| IS-08-03 | PCCC hoặc sẵn sàng khẩn cấp không đạt / Fire or Emergency Readiness Failure | Fire/smoke, alarm, detection, suppression, egress, evacuation, command hoặc continuity |

### SV-09 — Cleaning, Environment & Grounds (3)

| Code | Issue | Bao gồm |
| --- | --- | --- |
| IS-09-01 | Vệ sinh hoặc hygiene không đạt / Cleaning or Hygiene Failure | Dirty surface, restroom, supply hoặc spill response |
| IS-09-02 | Rác thải hoặc sinh vật gây hại không được kiểm soát / Waste or Pest Failure | Overflow, missed collection, sorting, bulky waste, insect hoặc rodent |
| IS-09-03 | Cảnh quan hoặc phiền nhiễu môi trường / Landscape or Environmental Nuisance | Plant, irrigation, unsafe branch, odor hoặc nuisance chưa rõ nguồn |

### SV-10 — Other (1)

| Code | Issue | Bao gồm |
| --- | --- | --- |
| IS-10-01 | Vấn đề khác cần review / Other Issue Requiring Review | Nội dung đủ rõ nhưng ngoài phạm vi chín Service |

### 4.1 Kiểm soát nhãn “Khác”

- Bắt buộc lưu `other_reason`, `raw evidence` và `reviewer`.
- Không tự động áp dụng (auto-apply) bằng AI.
- Đánh giá (review) theo tuần; các nhóm (cluster) lặp lại được đề xuất bổ sung vào Service/Issue hiện hữu hoặc tạo phiên bản taxonomy mới (taxonomy revision).
- `other_rate` được theo dõi theo project/source; tăng bất thường là tín hiệu về chất lượng dữ liệu (data-quality signal).
- Nhãn Khác không có người chịu trách nhiệm mặc định (default owner); ticket/case phải được phân loại thủ công (triage thủ công).

---

## 5. Cause, Severity and Safety

### 5.1 Cause

Candidate Cause là giả thuyết (hypothesis). Confirmed Root Cause bắt buộc có điều tra (investigation), bằng chứng (evidence), người xác nhận có thẩm quyền (authorized confirmer) và dấu thời gian (timestamp).

```text
mechanism
contributing_factor
external_condition
responsible_party
required_evidence
```

UNKNOWN là cause_determination_status, không phải Cause.

### 5.2 Operational severity

| Severity | Baseline |
| --- | --- |
| SEV-1 | Mối đe dọa tức thì, an toàn tính mạng, sự cố nghiêm trọng toàn tòa nhà hoặc kích hoạt hard trigger |
| SEV-2 | Tác động cao, ảnh hưởng nhiều cư dân hoặc cần phản ứng nhanh |
| SEV-3 | Tác động vận hành cục bộ, không nguy hiểm tức thời |
| SEV-4 | Thông tin, thẩm mỹ hoặc cải tiến |

```text
Hard trigger / safety rule
  > authorized human override
  > Issue severity override
  > Service default
```

Danh mục Hard-trigger độc lập với Service. Mắc kẹt thang, điện giật, cháy/khói, nước nghi nhiễm bẩn, ngập nghiêm trọng, cây sắp đổ và đe dọa an ninh đều phải được điều phối (dispatch) ngay lập tức.

---

## 6. Canonical Vocabulary Constraints

Tài liệu này chỉ định nghĩa mô hình khái niệm (conceptual model), không gian nhãn (label space), mã (code), ranh giới (boundary) và bội số/quan hệ (cardinality) của taxonomy. Nó không định nghĩa bảng/cột DB, payload API hoặc trường triển khai (implementation field).

Nguồn duy nhất cho schema triển khai là `05_Data_Model.md`; enum nghiệp vụ và chuyển đổi trạng thái (state transition) được định nghĩa trong `Business_Rules.md`. Chi tiết lưu trữ (persistence) không được lặp lại tại đây.

### 6.1 Code patterns

| Entity | Pattern |
| --- | --- |
| Service | ^SV-[0-9]{2}$ |
| Issue | ^IS-[0-9]{2}-[0-9]{2}$ |
| Transaction step | ^TR-[0-9]{2}$ |
| Handover step | ^HO-[0-9]{2}$ |
| Residence step | ^RES-[0-9]{2}$ |
| Operations step | ^OPS-[0-9]{2}$ |
| Service Request step | ^SRV-[0-9]{2}$ |
| Channel | ^CH-[A-Z0-9]+(?:-[A-Z0-9]+)*$ |

### 6.2 Cardinality

- Issue thuộc đúng một Service.
- Khi Service/Issue là KNOWN, Issue phải thuộc Primary Service trong cùng phiên bản (release).
- Một feedback item có tối đa một Customer Lifecycle Step và một Service Request Step.
- Báo cáo (reporting) mặc định theo Service + Issue; Location/Channel dùng để đi sâu chi tiết (drill-down).
- Không cộng UNKNOWN hoặc SV-10 vào tỷ lệ bao phủ (coverage) đạt chuẩn.

---

## 7. AI and Analytics Policy

AI chỉ đưa ra gợi ý:

```text
customer_lifecycle_step
service_request_step
primary_service
issue
sentiment
```

Dự đoán (prediction) không ghi đè quyết định con người. SV-10/IS-10-01, an toàn (safety), pháp lý (legal), trách nhiệm bảo hành (warranty responsibility) và Root Cause đã xác nhận (confirmed Root Cause) luôn cần con người đánh giá (human review).

Cơ sở xác định điểm nóng (Hotspot baseline):

```text
Service + Issue + Location + Time window
```

Journey, Location, Channel, symptom_detail, recurrence và rủi ro SLA (SLA risk) là các chiều đi sâu chi tiết (drill-down); không tạo thêm Issue chỉ để phục vụ biểu đồ (chart).

---

## 8. Governance and Publication

```text
Draft
  → schema validation
  → Service owner review
  → Operations/Safety review
  → Data/AI impact review
  → APPROVED
  → PUBLISHED
```

Các cổng phát hành (Release gates):

- đúng 10 Service và 28 Issue;
- SV-01..SV-09 có đúng 3 Issue; SV-10 có đúng 1 Issue;
- đủ 6 Customer Lifecycle Stage, 36 Customer Journey Step và 8 Service Request Step;
- SV-10 có hàng chờ đánh giá (review queue) và theo dõi tỷ lệ nhãn Khác (other-rate monitoring);
- dữ liệu khởi tạo cấu trúc (structured seed) có mã kiểm tra (checksum) và bộ xác thực (validator);
- API/UI không mã hóa cứng nhãn (hard-code label);
- kiểm thử kích hoạt an toàn (safety trigger test) độc lập với bộ phân loại (classifier).
- mỗi Service có định nghĩa (definition) và phạm vi bao hàm (inclusion scope) rõ ràng;

---

## 9. Research and Regulatory References

### 9.1 Khung Tiêu chuẩn Chuyên ngành (Professional Framework)

- [ISO 41011:2024 — Facility management vocabulary](https://www.iso.org/standard/82405.html)
- [ISO 41001:2018 — Facility management management systems](https://www.iso.org/standard/68021.html)
- [ISO 41012:2017 — Strategic sourcing and agreements](https://www.iso.org/standard/68168.html)
- [ISO 55001:2024 — Asset management system requirements](https://www.iso.org/standard/83054.html)
- [ISO/TC 267 Functional Areas](https://committee.iso.org/files/live/sites/tc267/files/Documents/AG1-Functional-Areas.html/)
- [IFMA — Optimizing Building Management with a Lifecycle Approach](https://knowledgelibrary.ifma.org/optimizing-building-management-with-a-lifecycle-approach/)

Các tiêu chuẩn trên hỗ trợ về từ vựng (vocabulary), vòng đời (lifecycle), cung cấp dịch vụ (service delivery), hiệu suất (performance), rủi ro (risk) và quản lý tài sản (asset management); danh sách 10 Service/28 Issue được thiết kế riêng cho phạm vi BĐS nhà ở.

### 9.2 Khung Pháp lý Việt Nam

- [Văn bản hợp nhất Luật Nhà ở 132/VBHN-VPQH](https://vanban.chinhphu.vn/?classid=0&docid=215257&pageid=27160)
- [Luật Kinh doanh BĐS 29/2023/QH15](https://vanban.chinhphu.vn/?docid=209624&pageid=27160)
- [Luật Bảo vệ quyền lợi người tiêu dùng 19/2023/QH15](https://vanban.chinhphu.vn/?classid=1&docid=208363&orggroupid=1&pageid=27160&previousPage=other+articles)
- [Nghị định 06/2021/NĐ-CP](https://vanban.chinhphu.vn/default.aspx?docid=202585&pageid=27160)
- [Luật Bảo vệ dữ liệu cá nhân 91/2025/QH15](https://vanban.chinhphu.vn/?classid=1&docid=214590&pageid=27160)
- [Luật PCCC và CNCH 55/2024/QH15](https://vanban.chinhphu.vn/?classid=1&docid=212483&orggroupid=1&pageid=27160)

Đơn vị phụ trách Pháp lý/Vận hành (Legal/Operations owner) đối chiếu theo dự án, hợp đồng, nội quy, hồ sơ kỹ thuật và quy định địa phương.

---

## 10. Các Ràng buộc Bất biến trong CI (CI Invariants)

### Cấu trúc (Structure)

- đúng 10 Service hoạt động và 28 Issue hoạt động;
- SV-01..SV-09 có 3 Issue/Service; SV-10 có 1 Issue;
- mỗi Issue thuộc đúng một Service;
- mã (code) là duy nhất, đúng pattern và không tái sử dụng;
- đúng 6 Customer Lifecycle Stage và đủ A/C/TR/HO/RES/OPS;
- OPS-01..OPS-08 tồn tại, duy nhất và thuộc stage Vận hành.

### Ngữ nghĩa (Semantics)

- Issue không chỉ khác nhau bởi location, channel, source system hoặc vendor.
- UNKNOWN không phải Service, Issue hoặc Cause;
- SV-10 không nhận bản ghi thiếu thông tin hoặc mơ hồ (missing/ambiguous record);
- tách các ý định bị trùng/kép (split multi-intent) trước khi phân loại (classification);
- Issue trong quyết định phân loại (decision) phải thuộc Primary Service của cùng phiên bản release.
- Service có định nghĩa/kết quả đầu ra (outcome/definition) và phạm vi bao hàm (inclusion scope) rõ ràng;

### An toàn và Bằng chứng (Safety and Evidence)

- kiểm thử kích hoạt an toàn (hard-trigger test) độc lập với bộ phân loại Service (Service classifier);
- IS-07-02, IS-08-01, IS-08-03 và các mối nguy hiểm được định nghĩa trong chính sách (policy-defined hazards) bắt buộc phải được điều phối (dispatch) hoặc đánh giá thủ công (manual review);
- AI không tự động áp dụng (auto-apply) SV-10, xác nhận Root Cause hoặc đưa ra kết luận pháp lý/bảo hành (legal/warranty determination);
- kết quả xác minh (confirmed finding) bắt buộc có điều tra (investigation), bằng chứng (evidence) và người xác nhận có thẩm quyền (authorized confirmer).
