
# 02 — Service Taxonomy

- **Project:** CX Intelligence & Operations Platform
- **Document version:** 1.0.0
- **Status:** Draft / Pilot Baseline — chưa phải production baseline
- **Source journey:** `Customer Journey(2).xlsx`
- **Purpose:** Master taxonomy cho Database, API, UI filter, AI classification, Hotspot và RCA
- **Total services:** 34
- **Total issue rows:** 217

> **Important:** `Candidate Cause` chỉ là giả thuyết điều tra. Không được coi là `Confirmed Root Cause` nếu chưa có bằng chứng kỹ thuật/nghiệp vụ và người có thẩm quyền xác nhận.

---

## 1. Taxonomy Model

```text
Customer Lifecycle Stage → Customer Lifecycle Step ─┐
                                                    ├─↔ Service
Service Request Lifecycle → Request Step ──────────┘

Feedback / Observation
    ├── Intake Channel (1)
    ├── Affected Channel (0:N)
    ├── Primary Service (1)
    └── Secondary Service (0:N)

Service
    ↓ 1:N
Issue
    ↕ N:N
Candidate Cause (suggestion only)
    ↓
Investigation / Evidence
    ↓
Confirmed Root Cause
    ↓
Corrective Action / Preventive Action
```

### Quy tắc thiết kế

1. `Customer Lifecycle` mô tả khách hàng đang ở đâu trong hành trình từ nhận thức đến cư trú.
2. `Service Request Lifecycle` mô tả yêu cầu đang ở đâu trong vòng đời tìm thông tin, gửi yêu cầu, xử lý và hoàn tất.
3. Hai lifecycle là hai dimension độc lập. Một feedback có thể đồng thời có một bước `RES-*` và một bước `SRV-*`; không ép chúng vào cùng một trường journey.
4. `Interaction Channel` mô tả nơi feedback được tiếp nhận hoặc nơi lỗi biểu hiện; channel không mặc định là business service.
5. `Service` mô tả năng lực/dịch vụ chịu trách nhiệm.
6. `Issue` mô tả một triệu chứng hoặc vấn đề quan sát được.
7. `Candidate Cause` là giả thuyết có thể xảy ra; `Root Cause` chỉ được xác nhận sau investigation có evidence.
8. Một Journey Step có thể liên quan nhiều Service; một Service có thể xuất hiện tại nhiều Journey Step.
9. Một Feedback Item có `primary_service_value_status`; khi `KNOWN` phải có đúng một `primary_service`, và có thể có nhiều `secondary_service` không trùng primary.
10. Một Issue bắt buộc thuộc một Service. Trong pilot, issue được chọn phải thuộc `primary_service`, trừ khi decision có exception được review và audit.
11. Không cho AI tự xác nhận Root Cause, safety responsibility hoặc legal responsibility.

### Quy tắc chọn `primary_service`

1. Chọn service sở hữu **outcome nghiệp vụ mà khách hàng đang cần** làm primary, không chọn theo kênh tiếp nhận một cách máy móc.
2. Nếu lỗi chỉ nằm ở channel/platform và outcome nghiệp vụ chưa được xác định, service sở hữu channel/platform có thể là primary.
3. Nếu outcome nghiệp vụ và channel cùng lỗi, business service là primary; channel/platform service là secondary. Ví dụ: không đặt được tiện ích do app lỗi → `Amenities` primary, `Resident App / Digital Services` secondary, affected channel = App.
4. Nếu feedback nói về chất lượng vận hành tại một asset, chọn service theo triệu chứng. Ví dụ cabin thang máy bẩn → `Cleaning` primary; `Elevator` chỉ là asset/service context hoặc secondary khi đồng thời có lỗi vận hành thang.
5. `Handling Unit` là routing mặc định sau classification, không phải tiêu chí duy nhất để xác định primary service.

---

## 2. Journey and Channel Dictionary

Hai sheet **Cư Trú** và **Dịch Vụ** trong workbook dùng STT thay vì ID ổn định. Tài liệu này bổ sung mã `RES-*` và `SRV-*` để dùng trong database/API; wording của bước được giữ theo workbook.

| Dimension Code              | Dimension                 | Step prefixes   | Cardinality trên một feedback |
| --------------------------- | ------------------------- | --------------- | ----------------------------- |
| `CUSTOMER_LIFECYCLE`        | Customer Lifecycle        | `A,C,TR,HO,RES` | 0 hoặc 1 step                 |
| `SERVICE_REQUEST_LIFECYCLE` | Service Request Lifecycle | `SRV`           | 0 hoặc 1 step                 |

### 2.1 Customer Lifecycle

#### Nhận thức

| Code   | Bước đã chốt                                                |
| ------ | ---------------------------------------------------------------- |
| `A1` | Tiếp xúc lần đầu với thương hiệu Vinhomes               |
| `A2` | Nhận biết dự án thông qua tên thương hiệu Vinhomes               |
| `A3` | Tiếp cận nội dung, tên thương hiệu dự án trên mạng xã hội, internet               |
| `A4` | Xem video, tin tức, quảng cáo, livestream giới thiệu dự án                              |
| `A5` | Được người quen, cư dân hiện hữu, người môi giới giới thiệu      |
| `A6` | Tiếp cận dự án qua sự kiện giới thiệu hoặc lễ ra quân |


#### Xem xét

| Code    | Bước đã chốt                                                        |
| ------- | ------------------------------------------------------------------------ |
| `C1`  | Tìm hiểu tổng quan dự án qua các website hoặc fanpage chính thức                                         |
| `C2`  | Nghiên cứu và tìm hiểu vị trí, quy hoạch và khả năng kết nối khu vực xung quanh                           |
| `C3`  | Xem mặt bằng, quỹ căn Xem thiết kế, phối cảnh, tiện ích nội khu và lựa chọn loại hình sản phẩm                     |
| `C4`  | Tìm hiểu bảng giá, chính sách bán hàng, phương thức thanh toán              |
| `C5`  | Đối chiếu nhiều dự án hoặc sản phẩm                             |
| `C7`  | Kiểm tra pháp lý dự án |
| `C8`  | Đánh giá khả năng tài chính và vay mua                           |
| `C10` | Trao đổi với nhân viên tư vấn, đăng ký nhận tư vấn chuyên sâu                                   |
| `C11` | Đặt lịch tham quan dự án hoặc căn hộ mẫu                        |
| `C12` | Trao đổi trực tiếp tại dự án hoặc trung tâm bán hàng          |
| `C13` | Tham dự livestream tư vấn hoặc phiên giới thiệu sản phẩm        |
| `C14` | Đặt lịch trao đổi hoặc yêu cầu hỗ trợ theo sản phẩm cụ thể |

#### Giao dịch

| Code      | Bước đã chốt                                              |
| --------- | -------------------------------------------------------------- |
| `TR-01` | Yêu cầu giữ căn hoặc gửi booking                         |
| `TR-02` | Xác nhận căn và phê duyệt booking                        |
| `TR-03` | Xác minh khách hàng và hồ sơ giao dịch                  |
| `TR-04` | Xác nhận thỏa thuận đặt cọc                             |
| `TR-05` | Lựa chọn phương án thanh toán, tài chính và ưu đãi |
| `TR-06` | Xác nhận giá và thông tin lập HĐMB                      |
| `TR-07` | Thanh toán ban đầu                                          |
| `TR-08` | Ký và nhận Hợp đồng mua bán                             |
| `TR-09` | Theo dõi và thực hiện nghĩa vụ sau ký                   |
| `TR-10` | Xử lý thay đổi hoặc phát sinh giao dịch                 |

#### Nhận nhà

| Code      | Bước đã chốt                                     |
| --------- | ----------------------------------------------------- |
| `HO-01` | Nhận thông báo bàn giao                           |
| `HO-02` | Hoàn tất điều kiện trước bàn giao             |
| `HO-03` | Xác nhận lịch và làm thủ tục tiếp nhận       |
| `HO-04` | Kiểm tra hiện trạng căn hộ và trang thiết bị  |
| `HO-05` | Đo và xác nhận diện tích thực tế              |
| `HO-06` | Ghi nhận tồn tại và quyết định nhận bàn giao |
| `HO-07` | Ký biên bản và hoàn tất tiếp nhận căn hộ    |
| `HO-08` | Nhận tài sản và hồ sơ bàn giao                 |

#### Cư trú

| Code       | Bước đã chốt                                                               |
| ---------- | ------------------------------------------------------------------------------- |
| `RES-01` | Thiết lập tư cách cư dân — liên kết số điện thoại/mã căn/hồ sơ |
| `RES-02` | Thiết lập tư cách cư dân — tạo/xác thực tài khoản và OTP           |
| `RES-03` | Thiết lập quyền ra vào — thẻ cư dân                                     |
| `RES-04` | Thiết lập quyền ra vào — đăng ký Face ID                                |
| `RES-05` | Ra vào hằng ngày                                                             |
| `RES-06` | Di chuyển trong tòa                                                           |
| `RES-07` | Sử dụng bãi xe                                                               |
| `RES-08` | Di chuyển nội khu                                                             |
| `RES-09` | Đón khách — intercom/điện thoại cư dân                                 |
| `RES-10` | Đón khách — lễ tân/bảo vệ/sảnh                                         |
| `RES-11` | Nhận thông tin                                                                |
| `RES-12` | Sử dụng tiện ích — đặt tiện ích                                        |
| `RES-13` | Sử dụng tiện ích — xác minh quyền tại điểm sử dụng                  |
| `RES-14` | Thi công/cải tạo                                                             |
| `RES-15` | Xử lý sự cố                                                                 |
| `RES-16` | Xử lý khẩn cấp                                                              |

### 2.2 Service Request Lifecycle

Các bước `SRV-*` mô tả trạng thái của yêu cầu dịch vụ, không phải một stage nối tiếp sau `Cư trú`. Chúng có thể được gán cùng lúc với một bước Customer Lifecycle.

#### Các bước yêu cầu dịch vụ

| Code       | Bước đã chốt      |
| ---------- | ---------------------- |
| `SRV-01` | Tìm thông tin        |
| `SRV-02` | Gửi yêu cầu         |
| `SRV-03` | Xác nhận/phê duyệt |
| `SRV-04` | Thanh toán            |
| `SRV-05` | Được phục vụ      |
| `SRV-06` | Theo dõi/escalate     |
| `SRV-07` | Hoàn tất             |
| `SRV-08` | Đánh giá            |

### 2.3 Interaction Channel

Channel là dimension riêng để tách nơi tiếp nhận/nơi biểu hiện lỗi khỏi service chịu trách nhiệm. Danh sách pilot tối thiểu:

| Channel Code   | Channel                         |
| -------------- | ------------------------------- |
| `CH-APP`       | Resident/Mobile App             |
| `CH-WEB`       | Website/Portal                  |
| `CH-HOTLINE`   | Hotline/Call Center             |
| `CH-EMAIL`     | Email                           |
| `CH-FRONTDESK` | Front Desk/Service Desk         |
| `CH-SOCIAL`    | Social Media/Messaging          |
| `CH-INPERSON`  | In-person/Site Visit            |
| `CH-SYSTEM`    | System Integration/Sensor/Batch |

Mỗi feedback có đúng một `intake_channel` khi nguồn đã biết và có thể có nhiều `affected_channel`. `Resident App / Digital Services` vẫn là một Service khi bản thân app/platform bị lỗi; việc feedback được gửi qua app chỉ tạo `intake_channel = CH-APP`.

---

## 3. Service Catalog

`Default Handling Unit`, `Default Priority` và `Journey Step refs` là thuộc tính/mapping mặc định ở cấp Service. Giá trị routing thực tế có thể được override theo project, location, issue và hard trigger; các chuỗi phân tách bằng `/` phải được normalize thành quan hệ với `org_unit`, không lưu như một owner ID duy nhất.

| Service Code | Service                                  | Default Handling Unit            | Default Priority | Journey Step refs                                                                                                   |
| ------------ | ---------------------------------------- | -------------------------------- | ---------------- | ------------------------------------------------------------------------------------------------------------------- |
| `SVC-01`   | Brand & Marketing Content                | Marketing/Brand                  | P4               | `A1,A2,A3,A4,A5,A6,C1,C4,C13`                                                                                     |
| `SVC-02`   | Project / Product Information            | Product Marketing/Sales          | P4               | `A2,A3,A6,C1,C2,C3,C4,C5,C6,C7,C8,C13,C14`                                                                        |
| `SVC-03`   | Sales Advisory & Site Visit              | Sales                            | P3               | `A4,A5,C10,C11,C12,C13,C14`                                                                                       |
| `SVC-04`   | Inventory & Booking                      | Sales Operations                 | P3               | `C5,C6,C14,TR-01,TR-02`                                                                                           |
| `SVC-05`   | KYC / Transaction Documentation          | Transaction Operations           | P3               | `TR-03,TR-10`                                                                                                     |
| `SVC-06`   | Contract / Legal Process                 | Legal/Transaction Operations     | P2               | `C7,TR-04,TR-06,TR-08,TR-10`                                                                                      |
| `SVC-07`   | Finance / Loan / Payment                 | Finance/Sales Operations         | P2               | `C8,C9,TR-05,TR-07,TR-09,TR-10,HO-02`                                                                             |
| `SVC-08`   | Handover Scheduling & Clearance          | Handover Operations              | P3               | `HO-01,HO-02,HO-03`                                                                                               |
| `SVC-09`   | Apartment Inspection / Defect            | Handover/Quality                 | P2               | `HO-04,HO-05,HO-06,HO-07`                                                                                         |
| `SVC-10`   | Warranty & Defect Resolution             | Warranty/Technical               | P2               | `HO-06,HO-08,RES-15,SRV-02,SRV-03,SRV-05,SRV-06,SRV-07`                                                           |
| `SVC-11`   | Resident Profile & Account               | Resident Operations/BQL          | P3               | `RES-01,RES-02,SRV-01,SRV-02,SRV-03,SRV-05,SRV-06`                                                                |
| `SVC-12`   | Resident App / Digital Services          | Digital Product/IT               | P3               | `RES-01,RES-02,RES-04,RES-07,RES-08,RES-09,RES-11,RES-12,RES-15,SRV-01,SRV-02,SRV-03,SRV-04,SRV-06,SRV-07,SRV-08` |
| `SVC-13`   | Billing / Fees / Payment                 | Finance/BQL                      | P2               | `TR-09,HO-02,RES-11,SRV-01,SRV-04,SRV-06,SRV-07`                                                                  |
| `SVC-14`   | Resident Service Desk                    | CX/CSKH/BQL                      | P2               | `RES-15,RES-16,SRV-01,SRV-02,SRV-03,SRV-05,SRV-06,SRV-07,SRV-08`                                                  |
| `SVC-15`   | Access Control / Resident Card / Face ID | Security/BQL/IT                  | P2               | `RES-03,RES-04,RES-05,RES-06,RES-09,RES-10,RES-13,RES-15,SRV-02,SRV-05,SRV-06`                                    |
| `SVC-16`   | Visitor / Intercom                       | Front Desk/Security/IT           | P3               | `RES-09,RES-10,RES-15,SRV-02,SRV-05,SRV-06`                                                                       |
| `SVC-17`   | Elevator / Vertical Transportation       | Engineering/Elevator Vendor      | P2               | `RES-06,RES-09,RES-15,RES-16,SRV-02,SRV-05,SRV-06,SRV-07`                                                         |
| `SVC-18`   | Parking                                  | Parking Operations/Security      | P3               | `RES-07,RES-15,SRV-02,SRV-03,SRV-04,SRV-05,SRV-06,SRV-07`                                                         |
| `SVC-19`   | Internal Mobility / Shuttle / Bus        | Transport Operations             | P3               | `RES-08,RES-15,SRV-01,SRV-02,SRV-05,SRV-06`                                                                       |
| `SVC-20`   | Water & Plumbing                         | MEP Water/Technical              | P2               | `RES-15,RES-16,SRV-02,SRV-05,SRV-06,SRV-07`                                                                       |
| `SVC-21`   | Electrical & Lighting                    | MEP Electrical/Technical         | P2               | `RES-05,RES-06,RES-11,RES-15,RES-16,SRV-02,SRV-05,SRV-06,SRV-07`                                                  |
| `SVC-22`   | Backup Power                             | MEP Electrical/Generator Vendor  | P1               | `RES-15,RES-16,SRV-02,SRV-05,SRV-06,SRV-07`                                                                       |
| `SVC-23`   | HVAC / Ventilation                       | MEP HVAC/Technical               | P2               | `RES-15,RES-16,SRV-02,SRV-05,SRV-06,SRV-07`                                                                       |
| `SVC-24`   | Fire Safety                              | Fire Safety/Technical/Security   | P1               | `RES-11,RES-16,SRV-02,SRV-05,SRV-06,SRV-07`                                                                       |
| `SVC-25`   | Building / Common Area Assets            | Facilities/Technical             | P3               | `HO-04,HO-06,RES-05,RES-06,RES-10,RES-12,RES-13,RES-15,SRV-02,SRV-05,SRV-06`                                      |
| `SVC-26`   | Security                                 | Security Operations              | P2               | `RES-03,RES-05,RES-09,RES-10,RES-16,SRV-02,SRV-05,SRV-06`                                                         |
| `SVC-27`   | Cleaning                                 | Housekeeping/Vendor              | P3               | `RES-06,RES-10,RES-12,RES-13,RES-15,SRV-02,SRV-05,SRV-06`                                                         |
| `SVC-28`   | Waste Management                         | Housekeeping/Waste Vendor        | P3               | `RES-10,RES-12,RES-15,SRV-02,SRV-05,SRV-06`                                                                       |
| `SVC-29`   | Pest Control                             | Pest Control Vendor/BQL          | P3               | `RES-12,RES-15,SRV-02,SRV-05,SRV-06`                                                                              |
| `SVC-30`   | Landscaping                              | Landscape Vendor/Facilities      | P4               | `RES-08,RES-12,RES-15,SRV-02,SRV-05,SRV-06`                                                                       |
| `SVC-31`   | Amenities                                | Amenities Operations/BQL         | P3               | `RES-12,RES-13,RES-15,SRV-01,SRV-02,SRV-03,SRV-04,SRV-05,SRV-06,SRV-07,SRV-08`                                    |
| `SVC-32`   | Renovation / Construction Permit         | Urban Management/BQL/Technical   | P3               | `RES-14,RES-15,SRV-01,SRV-02,SRV-03,SRV-04,SRV-05,SRV-06,SRV-07`                                                  |
| `SVC-33`   | Move-in / Move-out                       | Resident Operations/Security/BQL | P3               | `HO-08,RES-01,RES-03,RES-05,RES-14,RES-15,SRV-01,SRV-02,SRV-03,SRV-05,SRV-06,SRV-07`                              |
| `SVC-34`   | Community Communication / Notification   | CX/Communications/BQL            | P3               | `RES-11,RES-15,RES-16,SRV-01,SRV-03,SRV-06,SRV-07,SRV-08`                                                         |

---

## 4. Cause Group Dictionary

| Cause Group Code | Cause Group            | Ý nghĩa                                                  |
| ---------------- | ---------------------- | ---------------------------------------------------------- |
| `CG01`   | Asset / Hardware       | Thiết bị vật lý, linh kiện, cơ cấu cơ khí         |
| `CG02`   | Electrical / Power     | Nguồn điện, breaker, wiring, tiếp địa                |
| `CG03`   | Software               | Ứng dụng, backend service, bug phần mềm                |
| `CG04`   | Network                | Mạng, connectivity, timeout                               |
| `CG05`   | Integration            | API, message, callback, đồng bộ hệ thống              |
| `CG06`   | Master Data            | Sai/thiếu dữ liệu cư dân, căn, xe, quyền            |
| `CG07`   | Configuration          | Cấu hình rule, quyền, tariff, calendar                  |
| `CG08`   | Process / SOP          | Quy trình, workflow, handoff, closure                     |
| `CG09`   | Human / Staffing       | Sai thao tác, thiếu người, năng lực xử lý          |
| `CG10`   | Capacity / Demand      | Quá tải người dùng, thiết bị, slot, lưu lượng    |
| `CG11`   | Maintenance            | Bảo trì thiếu, chậm, preventive maintenance            |
| `CG12`   | Vendor / Partner       | Nhà thầu, ngân hàng, nhà mạng, đối tác            |
| `CG13`   | External Supply        | Điện, nước, mạng hoặc dịch vụ bên ngoài          |
| `CG14`   | Environment            | Mưa, ngập, bụi, nhiệt, độ ẩm, vật cản             |
| `CG15`   | Construction / Design  | Thiết kế, thi công, lắp đặt, defect                  |
| `CG16`   | Customer Input         | Thiếu hồ sơ, sai thao tác, thông tin khách cung cấp |
| `CG17`   | Policy / Business Rule | Chính sách, điều kiện, hạn mức, rule nghiệp vụ    |
| `CG18`   | Unknown                | Chưa đủ bằng chứng để xác định                   |

`CG01–CG17` là **cause group**, không phải candidate cause atomic. Mỗi giả thuyết cụ thể phải có `cause_id`/`cause_code` riêng và tham chiếu một cause group. Ví dụ `booster pump failure` và `closed valve` là hai cause records khác nhau dù có thể cùng thuộc `CG01`.

`CG18 Unknown` là trạng thái runtime biểu thị **chưa đủ evidence**, không phải một nguyên nhân. Chuỗi `CG18 unknown` được giữ trong 217 dòng pilot để phục vụ review nguồn, nhưng importer production phải loại nó khỏi `issue_cause_map`; runtime dùng `cause_determination_status = UNKNOWN`. Không được tính `UNKNOWN` như candidate/confirmed cause trong báo cáo RCA.

---

## 5. Master Service → Issue → Candidate Cause Mapping

**Cách đọc một dòng:**

```text
Service = Water & Plumbing
Issue = Low Water Pressure
Candidate Causes = external supply / booster pump / valve / high demand / pipe blockage
Journey refs = RES-15, SRV-02, SRV-05...
```

Điều này **không có nghĩa** hệ thống được phép kết luận booster pump hỏng chỉ từ nội dung feedback. Candidate cause chỉ dùng để:

- gợi ý checklist điều tra;
- gợi ý resolver group;
- hỗ trợ RCA;
- aggregate recurring patterns;
- kết nối với BMS/CMMS/work order ở phase sau.

Trong bảng dưới đây, `Handling Unit` và `Journey Step refs` là cột **derived/display-only** từ Service Catalog để người review đọc thuận tiện; source of truth là `service_unit_assignment` và `journey_service_map`. Importer phải kiểm tra chúng khớp catalog nhưng không tạo bản ghi độc lập ở cấp Issue. `Issue Priority Override` là cột legacy được map sang `Issue.operational_severity_override` và ưu tiên hơn `Service.default_operational_severity`; severity thực tế vẫn phải được tính lại theo impact, urgency và hard trigger.

|   # | Service                                             | Issue Code     | Issue                                                       | Candidate Cause / Hypothesis                                                                        | Handling Unit (derived)          | Issue Priority Override | Journey Step refs (derived)                                                                                         |
| --: | --------------------------------------------------- | -------------- | ----------------------------------------------------------- | --------------------------------------------------------------------------------------------------- | -------------------------------- | ----------------------- | ------------------------------------------------------------------------------------------------------------------- |
|   1 | `SVC-01` Brand & Marketing Content                | `MKT-01`     | Thông tin thương hiệu không nhất quán                | CG08 content governance; CG09 editorial error; CG17 messaging policy; CG18 unknown                  | Marketing/Brand                  | P4               | `A1,A2,A3,A4,A5,A6,C1,C4,C13`                                                                                     |
|   2 | `SVC-01` Brand & Marketing Content                | `MKT-02`     | Nội dung dự án sai hoặc lỗi thời                      | CG06 source data stale; CG08 update process; CG09 human error; CG18 unknown                         | Marketing/Brand                  | P4               | `A1,A2,A3,A4,A5,A6,C1,C4,C13`                                                                                     |
|   3 | `SVC-01` Brand & Marketing Content                | `MKT-03`     | Link/landing page không truy cập được                  | CG03 web application; CG04 network/CDN; CG07 routing/configuration; CG18 unknown                    | Marketing/Brand                  | P4               | `A1,A2,A3,A4,A5,A6,C1,C4,C13`                                                                                     |
|   4 | `SVC-01` Brand & Marketing Content                | `MKT-04`     | Livestream/nội dung số chất lượng kém                 | CG03 streaming software; CG04 network; CG09 operation; CG12 platform partner; CG18 unknown          | Marketing/Brand                  | P4               | `A1,A2,A3,A4,A5,A6,C1,C4,C13`                                                                                     |
|   5 | `SVC-02` Project / Product Information            | `INFO-01`    | Thiếu thông tin tổng quan dự án                        | CG08 content process; CG09 human omission; CG17 disclosure policy; CG18 unknown                     | Product Marketing/Sales          | P4               | `A2,A3,A6,C1,C2,C3,C4,C5,C6,C7,C8,C13,C14`                                                                        |
|   6 | `SVC-02` Project / Product Information            | `INFO-02`    | Thông tin vị trí/kết nối không rõ                    | CG06 mapping data; CG08 content process; CG09 human error; CG18 unknown                             | Product Marketing/Sales          | P4               | `A2,A3,A6,C1,C2,C3,C4,C5,C6,C7,C8,C13,C14`                                                                        |
|   7 | `SVC-02` Project / Product Information            | `INFO-03`    | Mặt bằng/thông số sản phẩm không nhất quán         | CG06 product master data; CG05 sync; CG08 version control; CG18 unknown                             | Product Marketing/Sales          | P4               | `A2,A3,A6,C1,C2,C3,C4,C5,C6,C7,C8,C13,C14`                                                                        |
|   8 | `SVC-02` Project / Product Information            | `INFO-04`    | Hình ảnh/virtual tour không tải được                 | CG03 application; CG04 network/CDN; CG12 hosting partner; CG18 unknown                              | Product Marketing/Sales          | P4               | `A2,A3,A6,C1,C2,C3,C4,C5,C6,C7,C8,C13,C14`                                                                        |
|   9 | `SVC-02` Project / Product Information            | `INFO-05`    | Quỹ căn/availability hiển thị không chính xác        | CG06 inventory data; CG05 integration; CG10 concurrent demand; CG18 unknown                         | Product Marketing/Sales          | P4               | `A2,A3,A6,C1,C2,C3,C4,C5,C6,C7,C8,C13,C14`                                                                        |
|  10 | `SVC-02` Project / Product Information            | `INFO-06`    | Tài liệu pháp lý/chính sách khó tìm                 | CG08 document process; CG17 access policy; CG09 human; CG18 unknown                                 | Product Marketing/Sales          | P4               | `A2,A3,A6,C1,C2,C3,C4,C5,C6,C7,C8,C13,C14`                                                                        |
|  11 | `SVC-03` Sales Advisory & Site Visit              | `SAL-01`     | Không liên hệ được tư vấn                           | CG09 staffing; CG08 routing; CG04 telephony/network; CG18 unknown                                   | Sales                            | P3               | `A4,A5,C10,C11,C12,C13,C14`                                                                                       |
|  12 | `SVC-03` Sales Advisory & Site Visit              | `SAL-02`     | Tư vấn trả lời không nhất quán                       | CG08 knowledge process; CG09 training; CG17 policy interpretation; CG18 unknown                     | Sales                            | P3               | `A4,A5,C10,C11,C12,C13,C14`                                                                                       |
|  13 | `SVC-03` Sales Advisory & Site Visit              | `SAL-03`     | Đặt lịch tham quan thất bại                            | CG03 booking app; CG05 calendar integration; CG10 slot capacity; CG18 unknown                       | Sales                            | P3               | `A4,A5,C10,C11,C12,C13,C14`                                                                                       |
|  14 | `SVC-03` Sales Advisory & Site Visit              | `SAL-04`     | Sales phản hồi chậm                                      | CG09 staffing; CG08 queue process; CG10 demand spike; CG18 unknown                                  | Sales                            | P3               | `A4,A5,C10,C11,C12,C13,C14`                                                                                       |
|  15 | `SVC-03` Sales Advisory & Site Visit              | `SAL-05`     | Thông tin sau tư vấn không được ghi nhận            | CG08 CRM process; CG05 CRM integration; CG09 human omission; CG18 unknown                           | Sales                            | P3               | `A4,A5,C10,C11,C12,C13,C14`                                                                                       |
|  16 | `SVC-04` Inventory & Booking                      | `BOOK-01`    | Không giữ/booking được căn                            | CG03 booking system; CG05 inventory sync; CG10 concurrency; CG17 booking rule; CG18 unknown         | Sales Operations                 | P2               | `C5,C6,C14,TR-01,TR-02`                                                                                           |
|  17 | `SVC-04` Inventory & Booking                      | `BOOK-02`    | Căn vừa chọn đã hết/không còn khả dụng            | CG10 demand concurrency; CG05 inventory sync; CG06 stale inventory; CG18 unknown                    | Sales Operations                 | P3               | `C5,C6,C14,TR-01,TR-02`                                                                                           |
|  18 | `SVC-04` Inventory & Booking                      | `BOOK-03`    | Booking chờ phê duyệt quá lâu                          | CG08 approval workflow; CG09 approver capacity; CG10 queue; CG18 unknown                            | Sales Operations                 | P3               | `C5,C6,C14,TR-01,TR-02`                                                                                           |
|  19 | `SVC-04` Inventory & Booking                      | `BOOK-04`    | Sai căn/sai giá/sai chính sách trong booking            | CG06 product master; CG07 pricing config; CG05 sync; CG09 human; CG18 unknown                       | Sales Operations                 | P2               | `C5,C6,C14,TR-01,TR-02`                                                                                           |
|  20 | `SVC-04` Inventory & Booking                      | `BOOK-05`    | Không nhận được xác nhận booking                     | CG03 notification service; CG05 event integration; CG04 email/SMS; CG18 unknown                     | Sales Operations                 | P3               | `C5,C6,C14,TR-01,TR-02`                                                                                           |
|  21 | `SVC-04` Inventory & Booking                      | `BOOK-06`    | Booking trùng/duplicate                                    | CG03 idempotency defect; CG05 event duplication; CG09 manual duplicate; CG18 unknown                | Sales Operations                 | P3               | `C5,C6,C14,TR-01,TR-02`                                                                                           |
|  22 | `SVC-05` KYC / Transaction Documentation          | `KYC-01`     | Không kích hoạt được tài khoản giao dịch           | CG03 IAM; CG04 network; CG05 identity integration; CG06 user data; CG18 unknown                     | Transaction Operations           | P3               | `TR-03,TR-10`                                                                                                     |
|  23 | `SVC-05` KYC / Transaction Documentation          | `KYC-02`     | Không tải được hồ sơ KYC                             | CG03 upload service; CG04 network; CG07 file rule; CG18 unknown                                     | Transaction Operations           | P3               | `TR-03,TR-10`                                                                                                     |
|  24 | `SVC-05` KYC / Transaction Documentation          | `KYC-03`     | Hồ sơ bị từ chối không rõ lý do                     | CG08 review process; CG17 KYC rule; CG09 reviewer; CG18 unknown                                     | Transaction Operations           | P3               | `TR-03,TR-10`                                                                                                     |
|  25 | `SVC-05` KYC / Transaction Documentation          | `KYC-04`     | Thông tin khách hàng sai/không khớp                    | CG06 master data; CG05 sync; CG16 customer input; CG18 unknown                                      | Transaction Operations           | P3               | `TR-03,TR-10`                                                                                                     |
|  26 | `SVC-05` KYC / Transaction Documentation          | `KYC-05`     | Kiểm duyệt hồ sơ chậm                                  | CG09 staffing; CG08 workflow; CG10 queue; CG12 verification partner; CG18 unknown                   | Transaction Operations           | P3               | `TR-03,TR-10`                                                                                                     |
|  27 | `SVC-06` Contract / Legal Process                 | `LEG-01`     | Không xem/tải được thỏa thuận hoặc HĐMB            | CG03 document service; CG04 network; CG05 DMS integration; CG18 unknown                             | Legal/Transaction Operations     | P2               | `C7,TR-04,TR-06,TR-08,TR-10`                                                                                      |
|  28 | `SVC-06` Contract / Legal Process                 | `LEG-02`     | Thông tin HĐMB sai                                        | CG06 master data; CG05 contract generation integration; CG09 human; CG18 unknown                    | Legal/Transaction Operations     | P2               | `C7,TR-04,TR-06,TR-08,TR-10`                                                                                      |
|  29 | `SVC-06` Contract / Legal Process                 | `LEG-03`     | OTP/ký điện tử thất bại                               | CG03 e-sign service; CG04 SMS/network; CG12 e-sign partner; CG06 phone data; CG18 unknown           | Legal/Transaction Operations     | P2               | `C7,TR-04,TR-06,TR-08,TR-10`                                                                                      |
|  30 | `SVC-06` Contract / Legal Process                 | `LEG-04`     | Yêu cầu chỉnh sửa hợp đồng xử lý chậm             | CG08 legal workflow; CG09 staffing; CG10 queue; CG18 unknown                                        | Legal/Transaction Operations     | P2               | `C7,TR-04,TR-06,TR-08,TR-10`                                                                                      |
|  31 | `SVC-06` Contract / Legal Process                 | `LEG-05`     | Không rõ trạng thái ký/nhận hợp đồng               | CG08 status process; CG05 event sync; CG03 portal; CG18 unknown                                     | Legal/Transaction Operations     | P2               | `C7,TR-04,TR-06,TR-08,TR-10`                                                                                      |
|  32 | `SVC-06` Contract / Legal Process                 | `LEG-06`     | Chuyển nhượng/thay đổi chủ thể giao dịch lỗi       | CG17 legal/business rule; CG08 workflow; CG06 customer data; CG05 integration; CG18 unknown         | Legal/Transaction Operations     | P2               | `C7,TR-04,TR-06,TR-08,TR-10`                                                                                      |
|  33 | `SVC-07` Finance / Loan / Payment                 | `FIN-01`     | Sai phương án thanh toán/ưu đãi                      | CG07 pricing config; CG06 product data; CG09 human; CG17 policy; CG18 unknown                       | Finance/Sales Operations         | P2               | `C8,C9,TR-05,TR-07,TR-09,TR-10,HO-02`                                                                             |
|  34 | `SVC-07` Finance / Loan / Payment                 | `FIN-02`     | Không tính được dòng tiền/khoản phải trả          | CG03 calculator/service; CG07 formula config; CG06 price data; CG18 unknown                         | Finance/Sales Operations         | P2               | `C8,C9,TR-05,TR-07,TR-09,TR-10,HO-02`                                                                             |
|  35 | `SVC-07` Finance / Loan / Payment                 | `FIN-03`     | Hồ sơ vay bị treo/chậm                                  | CG12 bank partner; CG08 workflow; CG16 customer documents; CG18 unknown                             | Finance/Sales Operations         | P2               | `C8,C9,TR-05,TR-07,TR-09,TR-10,HO-02`                                                                             |
|  36 | `SVC-07` Finance / Loan / Payment                 | `FIN-04`     | Thanh toán thất bại                                      | CG12 bank/payment gateway; CG04 network; CG03 payment service; CG18 unknown                         | Finance/Sales Operations         | P2               | `C8,C9,TR-05,TR-07,TR-09,TR-10,HO-02`                                                                             |
|  37 | `SVC-07` Finance / Loan / Payment                 | `FIN-05`     | Đã thanh toán nhưng chưa ghi nhận                     | CG05 bank callback; CG08 reconciliation; CG06 payment reference; CG18 unknown                       | Finance/Sales Operations         | P2               | `C8,C9,TR-05,TR-07,TR-09,TR-10,HO-02`                                                                             |
|  38 | `SVC-07` Finance / Loan / Payment                 | `FIN-06`     | Sai số tiền đến hạn                                    | CG07 billing config; CG06 contract data; CG05 ERP integration; CG18 unknown                         | Finance/Sales Operations         | P2               | `C8,C9,TR-05,TR-07,TR-09,TR-10,HO-02`                                                                             |
|  39 | `SVC-07` Finance / Loan / Payment                 | `FIN-07`     | Không nhận được thông báo đến hạn                 | CG03 notification; CG05 event integration; CG06 contact data; CG18 unknown                          | Finance/Sales Operations         | P2               | `C8,C9,TR-05,TR-07,TR-09,TR-10,HO-02`                                                                             |
|  40 | `SVC-07` Finance / Loan / Payment                 | `FIN-08`     | Điều chỉnh công nợ/hoàn tiền chậm                   | CG08 finance process; CG12 bank; CG09 staffing; CG18 unknown                                        | Finance/Sales Operations         | P2               | `C8,C9,TR-05,TR-07,TR-09,TR-10,HO-02`                                                                             |
|  41 | `SVC-08` Handover Scheduling & Clearance          | `HOS-01`     | Không nhận được thông báo bàn giao                  | CG03 notification; CG05 CRM/DMS sync; CG06 contact data; CG18 unknown                               | Handover Operations              | P3               | `HO-01,HO-02,HO-03`                                                                                               |
|  42 | `SVC-08` Handover Scheduling & Clearance          | `HOS-02`     | Không xác nhận/đặt được lịch nhận nhà            | CG03 scheduling; CG05 calendar integration; CG10 slot capacity; CG18 unknown                        | Handover Operations              | P3               | `HO-01,HO-02,HO-03`                                                                                               |
|  43 | `SVC-08` Handover Scheduling & Clearance          | `HOS-03`     | Sai ngày/giờ/địa điểm bàn giao                       | CG06 schedule data; CG09 human; CG05 sync; CG18 unknown                                             | Handover Operations              | P3               | `HO-01,HO-02,HO-03`                                                                                               |
|  44 | `SVC-08` Handover Scheduling & Clearance          | `HOS-04`     | Chưa đủ điều kiện bàn giao nhưng không rõ lý do  | CG08 clearance process; CG06 debt data; CG17 business rule; CG18 unknown                            | Handover Operations              | P3               | `HO-01,HO-02,HO-03`                                                                                               |
|  45 | `SVC-08` Handover Scheduling & Clearance          | `HOS-05`     | Chờ làm thủ tục tiếp nhận lâu                        | CG09 staffing; CG10 arrival peak; CG08 check-in process; CG18 unknown                               | Handover Operations              | P3               | `HO-01,HO-02,HO-03`                                                                                               |
|  46 | `SVC-09` Apartment Inspection / Defect            | `DEF-01`     | Sai/thiếu vật liệu hoặc thiết bị bàn giao            | CG15 construction/installation; CG08 QA process; CG12 contractor; CG18 unknown                      | Handover/Quality                 | P2               | `HO-04,HO-05,HO-06,HO-07`                                                                                         |
|  47 | `SVC-09` Apartment Inspection / Defect            | `DEF-02`     | Lỗi hoàn thiện bề mặt                                  | CG15 workmanship; CG12 contractor; CG11 quality maintenance; CG18 unknown                           | Handover/Quality                 | P2               | `HO-04,HO-05,HO-06,HO-07`                                                                                         |
|  48 | `SVC-09` Apartment Inspection / Defect            | `DEF-03`     | Thiết bị trong căn không hoạt động                   | CG01 hardware; CG02 power; CG15 installation; CG12 supplier; CG18 unknown                           | Handover/Quality                 | P2               | `HO-04,HO-05,HO-06,HO-07`                                                                                         |
|  49 | `SVC-09` Apartment Inspection / Defect            | `DEF-04`     | Rò rỉ/thấm trong căn hộ                                | CG15 waterproofing/plumbing; CG01 pipe/fixture; CG12 contractor; CG18 unknown                       | Handover/Quality                 | P2               | `HO-04,HO-05,HO-06,HO-07`                                                                                         |
|  50 | `SVC-09` Apartment Inspection / Defect            | `DEF-05`     | Sai diện tích/khác hồ sơ                               | CG06 measurement/design data; CG15 construction; CG09 measurement; CG18 unknown                     | Handover/Quality                 | P2               | `HO-04,HO-05,HO-06,HO-07`                                                                                         |
|  51 | `SVC-09` Apartment Inspection / Defect            | `DEF-06`     | Không ghi nhận được defect                             | CG03 defect app; CG08 inspection process; CG09 human; CG18 unknown                                  | Handover/Quality                 | P2               | `HO-04,HO-05,HO-06,HO-07`                                                                                         |
|  52 | `SVC-09` Apartment Inspection / Defect            | `DEF-07`     | Danh sách defect không đồng bộ                         | CG05 defect system integration; CG06 record data; CG03 app; CG18 unknown                            | Handover/Quality                 | P2               | `HO-04,HO-05,HO-06,HO-07`                                                                                         |
|  53 | `SVC-09` Apartment Inspection / Defect            | `DEF-08`     | Tranh chấp trạng thái đạt/không đạt                 | CG08 acceptance criteria; CG17 contract rule; CG09 judgment; CG18 unknown                           | Handover/Quality                 | P2               | `HO-04,HO-05,HO-06,HO-07`                                                                                         |
|  54 | `SVC-10` Warranty & Defect Resolution             | `WAR-01`     | Defect đã báo nhưng chưa được sửa                  | CG08 work-order workflow; CG09 staffing; CG12 contractor; CG11 maintenance; CG18 unknown            | Warranty/Technical               | P2               | `HO-06,HO-08,RES-15,SRV-02,SRV-03,SRV-05,SRV-06,SRV-07`                                                           |
|  55 | `SVC-10` Warranty & Defect Resolution             | `WAR-02`     | Sửa xong nhưng lỗi tái diễn                            | CG01 component; CG11 poor repair; CG15 underlying defect; CG18 unknown                              | Warranty/Technical               | P2               | `HO-06,HO-08,RES-15,SRV-02,SRV-03,SRV-05,SRV-06,SRV-07`                                                           |
|  56 | `SVC-10` Warranty & Defect Resolution             | `WAR-03`     | Không rõ defect còn bảo hành hay không                | CG17 warranty rule; CG06 handover data; CG08 process; CG18 unknown                                  | Warranty/Technical               | P2               | `HO-06,HO-08,RES-15,SRV-02,SRV-03,SRV-05,SRV-06,SRV-07`                                                           |
|  57 | `SVC-10` Warranty & Defect Resolution             | `WAR-04`     | Nhà thầu không đến đúng lịch                        | CG12 contractor; CG09 staffing; CG08 scheduling; CG18 unknown                                       | Warranty/Technical               | P2               | `HO-06,HO-08,RES-15,SRV-02,SRV-03,SRV-05,SRV-06,SRV-07`                                                           |
|  58 | `SVC-10` Warranty & Defect Resolution             | `WAR-05`     | Đóng yêu cầu khi khách chưa xác nhận                | CG08 closure process; CG09 operator; CG07 workflow config; CG18 unknown                             | Warranty/Technical               | P2               | `HO-06,HO-08,RES-15,SRV-02,SRV-03,SRV-05,SRV-06,SRV-07`                                                           |
|  59 | `SVC-10` Warranty & Defect Resolution             | `WAR-06`     | Thiếu bằng chứng hoàn thành sửa chữa                 | CG08 evidence gate; CG09 contractor/operator; CG03 mobile work-order; CG18 unknown                  | Warranty/Technical               | P2               | `HO-06,HO-08,RES-15,SRV-02,SRV-03,SRV-05,SRV-06,SRV-07`                                                           |
|  60 | `SVC-11` Resident Profile & Account               | `RES-ACC-01` | Mã căn không liên kết đúng tài khoản               | CG06 resident-unit mapping; CG05 sync; CG16 registration input; CG18 unknown                        | Resident Operations/BQL          | P3               | `RES-01,RES-02,SRV-01,SRV-02,SRV-03,SRV-05,SRV-06`                                                                |
|  61 | `SVC-11` Resident Profile & Account               | `RES-ACC-02` | Không xác thực được OTP                               | CG12 OTP provider; CG04 network; CG06 phone data; CG03 IAM; CG18 unknown                            | Resident Operations/BQL          | P3               | `RES-01,RES-02,SRV-01,SRV-02,SRV-03,SRV-05,SRV-06`                                                                |
|  62 | `SVC-11` Resident Profile & Account               | `RES-ACC-03` | Thông tin cư dân sai                                     | CG06 master data; CG05 sync; CG16 user input; CG18 unknown                                          | Resident Operations/BQL          | P3               | `RES-01,RES-02,SRV-01,SRV-02,SRV-03,SRV-05,SRV-06`                                                                |
|  63 | `SVC-11` Resident Profile & Account               | `RES-ACC-04` | Thay đổi chủ hộ/thành viên chưa cập nhật           | CG08 approval process; CG06 master data; CG05 integration; CG18 unknown                             | Resident Operations/BQL          | P3               | `RES-01,RES-02,SRV-01,SRV-02,SRV-03,SRV-05,SRV-06`                                                                |
|  64 | `SVC-11` Resident Profile & Account               | `RES-ACC-05` | Tài khoản bị khóa/không truy cập                      | CG03 IAM; CG07 security policy; CG16 failed attempts; CG18 unknown                                  | Resident Operations/BQL          | P3               | `RES-01,RES-02,SRV-01,SRV-02,SRV-03,SRV-05,SRV-06`                                                                |
|  65 | `SVC-11` Resident Profile & Account               | `RES-ACC-06` | Phân quyền cư dân không đúng                         | CG06 role data; CG07 permission config; CG08 approval; CG18 unknown                                 | Resident Operations/BQL          | P2               | `RES-01,RES-02,SRV-01,SRV-02,SRV-03,SRV-05,SRV-06`                                                                |
|  66 | `SVC-12` Resident App / Digital Services          | `APP-01`     | Không đăng nhập được                                 | CG03 application/IAM; CG04 network; CG06 account data; CG18 unknown                                 | Digital Product/IT               | P3               | `RES-01,RES-02,RES-04,RES-07,RES-08,RES-09,RES-11,RES-12,RES-15,SRV-01,SRV-02,SRV-03,SRV-04,SRV-06,SRV-07,SRV-08` |
|  67 | `SVC-12` Resident App / Digital Services          | `APP-02`     | OTP không gửi/không hợp lệ                             | CG12 OTP provider; CG04 carrier; CG03 auth service; CG06 phone data; CG18 unknown                   | Digital Product/IT               | P3               | `RES-01,RES-02,RES-04,RES-07,RES-08,RES-09,RES-11,RES-12,RES-15,SRV-01,SRV-02,SRV-03,SRV-04,SRV-06,SRV-07,SRV-08` |
|  68 | `SVC-12` Resident App / Digital Services          | `APP-03`     | Không hiển thị căn hộ/dịch vụ                        | CG06 master data; CG05 integration; CG07 entitlement config; CG18 unknown                           | Digital Product/IT               | P3               | `RES-01,RES-02,RES-04,RES-07,RES-08,RES-09,RES-11,RES-12,RES-15,SRV-01,SRV-02,SRV-03,SRV-04,SRV-06,SRV-07,SRV-08` |
|  69 | `SVC-12` Resident App / Digital Services          | `APP-04`     | Ứng dụng crash/treo                                       | CG03 mobile defect; CG10 device resource; CG07 compatibility; CG18 unknown                          | Digital Product/IT               | P3               | `RES-01,RES-02,RES-04,RES-07,RES-08,RES-09,RES-11,RES-12,RES-15,SRV-01,SRV-02,SRV-03,SRV-04,SRV-06,SRV-07,SRV-08` |
|  70 | `SVC-12` Resident App / Digital Services          | `APP-05`     | Không nhận push notification                              | CG03 push service; CG05 event integration; CG07 device permission; CG18 unknown                     | Digital Product/IT               | P3               | `RES-01,RES-02,RES-04,RES-07,RES-08,RES-09,RES-11,RES-12,RES-15,SRV-01,SRV-02,SRV-03,SRV-04,SRV-06,SRV-07,SRV-08` |
|  71 | `SVC-12` Resident App / Digital Services          | `APP-06`     | Không gửi được yêu cầu dịch vụ                     | CG03 ticket API; CG04 network; CG05 case integration; CG18 unknown                                  | Digital Product/IT               | P3               | `RES-01,RES-02,RES-04,RES-07,RES-08,RES-09,RES-11,RES-12,RES-15,SRV-01,SRV-02,SRV-03,SRV-04,SRV-06,SRV-07,SRV-08` |
|  72 | `SVC-12` Resident App / Digital Services          | `APP-07`     | Không đặt được tiện ích                             | CG03 booking module; CG05 amenities integration; CG10 slot load; CG18 unknown                       | Digital Product/IT               | P3               | `RES-01,RES-02,RES-04,RES-07,RES-08,RES-09,RES-11,RES-12,RES-15,SRV-01,SRV-02,SRV-03,SRV-04,SRV-06,SRV-07,SRV-08` |
|  73 | `SVC-12` Resident App / Digital Services          | `APP-08`     | Phiên bản app không tương thích                       | CG07 release/config; CG03 client defect; CG16 outdated app; CG18 unknown                            | Digital Product/IT               | P3               | `RES-01,RES-02,RES-04,RES-07,RES-08,RES-09,RES-11,RES-12,RES-15,SRV-01,SRV-02,SRV-03,SRV-04,SRV-06,SRV-07,SRV-08` |
|  74 | `SVC-13` Billing / Fees / Payment                 | `BILL-01`    | Sai hóa đơn/phí quản lý                               | CG06 meter/unit data; CG07 tariff; CG05 billing integration; CG18 unknown                           | Finance/BQL                      | P2               | `TR-09,HO-02,RES-11,SRV-01,SRV-04,SRV-06,SRV-07`                                                                  |
|  75 | `SVC-13` Billing / Fees / Payment                 | `BILL-02`    | Hóa đơn bị trùng                                       | CG03 billing job; CG05 duplicate event; CG08 reconciliation; CG18 unknown                           | Finance/BQL                      | P2               | `TR-09,HO-02,RES-11,SRV-01,SRV-04,SRV-06,SRV-07`                                                                  |
|  76 | `SVC-13` Billing / Fees / Payment                 | `BILL-03`    | Thanh toán thất bại                                      | CG12 payment gateway/bank; CG04 network; CG03 payment service; CG18 unknown                         | Finance/BQL                      | P2               | `TR-09,HO-02,RES-11,SRV-01,SRV-04,SRV-06,SRV-07`                                                                  |
|  77 | `SVC-13` Billing / Fees / Payment                 | `BILL-04`    | Đã thanh toán nhưng chưa ghi nhận                     | CG05 bank callback; CG08 reconciliation; CG06 reference; CG18 unknown                               | Finance/BQL                      | P2               | `TR-09,HO-02,RES-11,SRV-01,SRV-04,SRV-06,SRV-07`                                                                  |
|  78 | `SVC-13` Billing / Fees / Payment                 | `BILL-05`    | Sai phí phạt/chậm thanh toán                            | CG07 rule/tariff; CG06 due-date data; CG08 process; CG18 unknown                                    | Finance/BQL                      | P2               | `TR-09,HO-02,RES-11,SRV-01,SRV-04,SRV-06,SRV-07`                                                                  |
|  79 | `SVC-13` Billing / Fees / Payment                 | `BILL-06`    | Hoàn tiền/điều chỉnh chậm                             | CG08 finance workflow; CG09 staffing; CG12 bank; CG18 unknown                                       | Finance/BQL                      | P2               | `TR-09,HO-02,RES-11,SRV-01,SRV-04,SRV-06,SRV-07`                                                                  |
|  80 | `SVC-13` Billing / Fees / Payment                 | `BILL-07`    | Không nhận được hóa đơn/thông báo                 | CG03 notification; CG05 billing event; CG06 contact data; CG18 unknown                              | Finance/BQL                      | P2               | `TR-09,HO-02,RES-11,SRV-01,SRV-04,SRV-06,SRV-07`                                                                  |
|  81 | `SVC-14` Resident Service Desk                    | `SD-01`      | Yêu cầu không được ghi nhận                          | CG03 intake system; CG05 channel integration; CG09 manual intake; CG18 unknown                      | CX/CSKH/BQL                      | P2               | `RES-15,RES-16,SRV-01,SRV-02,SRV-03,SRV-05,SRV-06,SRV-07,SRV-08`                                                  |
|  82 | `SVC-14` Resident Service Desk                    | `SD-02`      | Tạo ticket trùng                                          | CG03 dedup/idempotency; CG05 duplicate events; CG09 manual; CG18 unknown                            | CX/CSKH/BQL                      | P2               | `RES-15,RES-16,SRV-01,SRV-02,SRV-03,SRV-05,SRV-06,SRV-07,SRV-08`                                                  |
|  83 | `SVC-14` Resident Service Desk                    | `SD-03`      | Chuyển sai đơn vị xử lý                               | CG07 routing rules; CG06 taxonomy; CG09 triage; CG18 unknown                                        | CX/CSKH/BQL                      | P2               | `RES-15,RES-16,SRV-01,SRV-02,SRV-03,SRV-05,SRV-06,SRV-07,SRV-08`                                                  |
|  84 | `SVC-14` Resident Service Desk                    | `SD-04`      | Không có owner rõ ràng                                  | CG08 ownership process; CG07 workflow config; CG09 staffing; CG18 unknown                           | CX/CSKH/BQL                      | P2               | `RES-15,RES-16,SRV-01,SRV-02,SRV-03,SRV-05,SRV-06,SRV-07,SRV-08`                                                  |
|  85 | `SVC-14` Resident Service Desk                    | `SD-05`      | Khách phải kể lại nhiều lần                           | CG05 channel history integration; CG08 handoff; CG09 agent behavior; CG18 unknown                   | CX/CSKH/BQL                      | P2               | `RES-15,RES-16,SRV-01,SRV-02,SRV-03,SRV-05,SRV-06,SRV-07,SRV-08`                                                  |
|  86 | `SVC-14` Resident Service Desk                    | `SD-06`      | Không có cập nhật tiến độ                            | CG08 communication process; CG03 notification; CG09 owner discipline; CG18 unknown                  | CX/CSKH/BQL                      | P2               | `RES-15,RES-16,SRV-01,SRV-02,SRV-03,SRV-05,SRV-06,SRV-07,SRV-08`                                                  |
|  87 | `SVC-14` Resident Service Desk                    | `SD-07`      | SLA bị vi phạm                                            | CG09 capacity; CG08 workflow; CG10 backlog; CG12 vendor; CG18 unknown                               | CX/CSKH/BQL                      | P2               | `RES-15,RES-16,SRV-01,SRV-02,SRV-03,SRV-05,SRV-06,SRV-07,SRV-08`                                                  |
|  88 | `SVC-14` Resident Service Desk                    | `SD-08`      | Đóng ticket quá sớm                                     | CG08 closure criteria; CG09 operator; CG07 workflow; CG18 unknown                                   | CX/CSKH/BQL                      | P2               | `RES-15,RES-16,SRV-01,SRV-02,SRV-03,SRV-05,SRV-06,SRV-07,SRV-08`                                                  |
|  89 | `SVC-14` Resident Service Desk                    | `SD-09`      | Ticket tái mở/tái diễn                                  | CG11 incomplete fix; CG08 verification; CG01 underlying asset; CG18 unknown                         | CX/CSKH/BQL                      | P2               | `RES-15,RES-16,SRV-01,SRV-02,SRV-03,SRV-05,SRV-06,SRV-07,SRV-08`                                                  |
|  90 | `SVC-15` Access Control / Resident Card / Face ID | `ACS-01`     | Thẻ cư dân không hoạt động                           | CG01 card/reader; CG06 entitlement data; CG07 permission config; CG18 unknown                       | Security/BQL/IT                  | P2               | `RES-03,RES-04,RES-05,RES-06,RES-09,RES-10,RES-13,RES-15,SRV-02,SRV-05,SRV-06`                                    |
|  91 | `SVC-15` Access Control / Resident Card / Face ID | `ACS-02`     | Face ID không nhận diện                                  | CG01 camera; CG03 recognition service; CG06 face profile; CG14 lighting/environment; CG18 unknown   | Security/BQL/IT                  | P2               | `RES-03,RES-04,RES-05,RES-06,RES-09,RES-10,RES-13,RES-15,SRV-02,SRV-05,SRV-06`                                    |
|  92 | `SVC-15` Access Control / Resident Card / Face ID | `ACS-03`     | Không được cấp đúng tầng                            | CG07 floor permission; CG06 resident-unit mapping; CG05 elevator integration; CG18 unknown          | Security/BQL/IT                  | P2               | `RES-03,RES-04,RES-05,RES-06,RES-09,RES-10,RES-13,RES-15,SRV-02,SRV-05,SRV-06`                                    |
|  93 | `SVC-15` Access Control / Resident Card / Face ID | `ACS-04`     | Access denied dù cư dân hợp lệ                         | CG06 identity data; CG07 rule; CG05 sync; CG01 controller; CG18 unknown                             | Security/BQL/IT                  | P2               | `RES-03,RES-04,RES-05,RES-06,RES-09,RES-10,RES-13,RES-15,SRV-02,SRV-05,SRV-06`                                    |
|  94 | `SVC-15` Access Control / Resident Card / Face ID | `ACS-05`     | Quyền mới chưa cập nhật                                | CG05 synchronization; CG08 approval workflow; CG06 master data; CG18 unknown                        | Security/BQL/IT                  | P2               | `RES-03,RES-04,RES-05,RES-06,RES-09,RES-10,RES-13,RES-15,SRV-02,SRV-05,SRV-06`                                    |
|  95 | `SVC-15` Access Control / Resident Card / Face ID | `ACS-06`     | Reader/cổng kiểm soát không hoạt động                | CG01 reader/controller; CG02 power; CG04 network; CG18 unknown                                      | Security/BQL/IT                  | P2               | `RES-03,RES-04,RES-05,RES-06,RES-09,RES-10,RES-13,RES-15,SRV-02,SRV-05,SRV-06`                                    |
|  96 | `SVC-15` Access Control / Resident Card / Face ID | `ACS-07`     | Thẻ mất nhưng chưa khóa kịp                           | CG08 lost-card process; CG09 response delay; CG05 access integration; CG18 unknown                  | Security/BQL/IT                  | P1               | `RES-03,RES-04,RES-05,RES-06,RES-09,RES-10,RES-13,RES-15,SRV-02,SRV-05,SRV-06`                                    |
|  97 | `SVC-16` Visitor / Intercom                       | `VIS-01`     | Intercom không gọi được cư dân                       | CG01 intercom hardware; CG04 network; CG03 call service; CG18 unknown                               | Front Desk/Security/IT           | P3               | `RES-09,RES-10,RES-15,SRV-02,SRV-05,SRV-06`                                                                       |
|  98 | `SVC-16` Visitor / Intercom                       | `VIS-02`     | Cư dân không nhận được cuộc gọi khách             | CG03 app/intercom integration; CG04 network; CG07 device permission; CG18 unknown                   | Front Desk/Security/IT           | P3               | `RES-09,RES-10,RES-15,SRV-02,SRV-05,SRV-06`                                                                       |
|  99 | `SVC-16` Visitor / Intercom                       | `VIS-03`     | Khách đã đăng ký nhưng lễ tân không thấy         | CG05 visitor sync; CG06 visitor data; CG03 frontdesk app; CG18 unknown                              | Front Desk/Security/IT           | P3               | `RES-09,RES-10,RES-15,SRV-02,SRV-05,SRV-06`                                                                       |
| 100 | `SVC-16` Visitor / Intercom                       | `VIS-04`     | Khách không được cấp quyền lên tầng                | CG07 visitor permission; CG05 access/elevator sync; CG06 host unit data; CG18 unknown               | Front Desk/Security/IT           | P3               | `RES-09,RES-10,RES-15,SRV-02,SRV-05,SRV-06`                                                                       |
| 101 | `SVC-16` Visitor / Intercom                       | `VIS-05`     | Thời gian check-in khách quá lâu                        | CG09 staffing; CG08 verification process; CG10 peak demand; CG18 unknown                            | Front Desk/Security/IT           | P3               | `RES-09,RES-10,RES-15,SRV-02,SRV-05,SRV-06`                                                                       |
| 102 | `SVC-16` Visitor / Intercom                       | `VIS-06`     | Không xác định được người bảo lãnh/host          | CG06 resident data; CG16 visitor input; CG08 verification; CG18 unknown                             | Front Desk/Security/IT           | P3               | `RES-09,RES-10,RES-15,SRV-02,SRV-05,SRV-06`                                                                       |
| 103 | `SVC-17` Elevator / Vertical Transportation       | `ELV-01`     | Thời gian chờ thang máy lâu                             | CG10 traffic/capacity; CG01 cabin unavailable; CG11 maintenance; CG07 dispatch config; CG18 unknown | Engineering/Elevator Vendor      | P2               | `RES-06,RES-09,RES-15,RES-16,SRV-02,SRV-05,SRV-06,SRV-07`                                                         |
| 104 | `SVC-17` Elevator / Vertical Transportation       | `ELV-02`     | Thang máy ngừng hoạt động                              | CG01 controller/drive/door; CG02 power; CG11 maintenance; CG18 unknown                              | Engineering/Elevator Vendor      | P2               | `RES-06,RES-09,RES-15,RES-16,SRV-02,SRV-05,SRV-06,SRV-07`                                                         |
| 105 | `SVC-17` Elevator / Vertical Transportation       | `ELV-03`     | Cửa không mở                                             | CG01 door lock/sensor/drive; CG14 obstruction; CG11 maintenance; CG18 unknown                       | Engineering/Elevator Vendor      | P2               | `RES-06,RES-09,RES-15,RES-16,SRV-02,SRV-05,SRV-06,SRV-07`                                                         |
| 106 | `SVC-17` Elevator / Vertical Transportation       | `ELV-04`     | Cửa không đóng                                          | CG01 door sensor/lock; CG14 obstruction; CG11 maintenance; CG18 unknown                             | Engineering/Elevator Vendor      | P2               | `RES-06,RES-09,RES-15,RES-16,SRV-02,SRV-05,SRV-06,SRV-07`                                                         |
| 107 | `SVC-17` Elevator / Vertical Transportation       | `ELV-05`     | Sai/không có quyền tầng                                 | CG07 permission; CG06 resident-unit mapping; CG05 access integration; CG18 unknown                  | Engineering/Elevator Vendor      | P2               | `RES-06,RES-09,RES-15,RES-16,SRV-02,SRV-05,SRV-06,SRV-07`                                                         |
| 108 | `SVC-17` Elevator / Vertical Transportation       | `ELV-06`     | Tiếng ồn/rung bất thường                               | CG01 mechanical component; CG11 maintenance; CG15 alignment/installation; CG18 unknown              | Engineering/Elevator Vendor      | P2               | `RES-06,RES-09,RES-15,RES-16,SRV-02,SRV-05,SRV-06,SRV-07`                                                         |
| 109 | `SVC-17` Elevator / Vertical Transportation       | `ELV-07`     | Người bị mắc kẹt                                       | CG01 door/controller/drive; CG02 power; CG11 maintenance; CG18 unknown                              | Engineering/Elevator Vendor      | P1               | `RES-06,RES-09,RES-15,RES-16,SRV-02,SRV-05,SRV-06,SRV-07`                                                         |
| 110 | `SVC-17` Elevator / Vertical Transportation       | `ELV-08`     | Thang dừng/giật bất thường                             | CG01 drive/controller/sensor; CG02 power quality; CG11 maintenance; CG18 unknown                    | Engineering/Elevator Vendor      | P1               | `RES-06,RES-09,RES-15,RES-16,SRV-02,SRV-05,SRV-06,SRV-07`                                                         |
| 111 | `SVC-17` Elevator / Vertical Transportation       | `ELV-09`     | Cabin bẩn/mùi khó chịu                                  | CG08 housekeeping process; CG09 staffing; CG14 spill/environment; CG18 unknown                      | Engineering/Elevator Vendor      | P2               | `RES-06,RES-09,RES-15,RES-16,SRV-02,SRV-05,SRV-06,SRV-07`                                                         |
| 112 | `SVC-18` Parking                                  | `PKG-01`     | Biển số không được nhận diện                        | CG01 LPR camera; CG03 recognition software; CG14 lighting/weather; CG06 vehicle data; CG18 unknown  | Parking Operations/Security      | P3               | `RES-07,RES-15,SRV-02,SRV-03,SRV-04,SRV-05,SRV-06,SRV-07`                                                         |
| 113 | `SVC-18` Parking                                  | `PKG-02`     | Barrier không mở                                          | CG01 barrier/controller; CG02 power; CG05 authorization sync; CG18 unknown                          | Parking Operations/Security      | P2               | `RES-07,RES-15,SRV-02,SRV-03,SRV-04,SRV-05,SRV-06,SRV-07`                                                         |
| 114 | `SVC-18` Parking                                  | `PKG-03`     | Đăng ký xe chưa có hiệu lực                          | CG08 approval workflow; CG06 vehicle master; CG05 sync; CG18 unknown                                | Parking Operations/Security      | P3               | `RES-07,RES-15,SRV-02,SRV-03,SRV-04,SRV-05,SRV-06,SRV-07`                                                         |
| 115 | `SVC-18` Parking                                  | `PKG-04`     | Gia hạn đã duyệt nhưng không vào được bãi        | CG05 approval-to-gate sync; CG06 entitlement; CG07 rule; CG18 unknown                               | Parking Operations/Security      | P3               | `RES-07,RES-15,SRV-02,SRV-03,SRV-04,SRV-05,SRV-06,SRV-07`                                                         |
| 116 | `SVC-18` Parking                                  | `PKG-05`     | Sai phí gửi xe                                            | CG07 tariff; CG06 vehicle type; CG05 billing integration; CG18 unknown                              | Parking Operations/Security      | P3               | `RES-07,RES-15,SRV-02,SRV-03,SRV-04,SRV-05,SRV-06,SRV-07`                                                         |
| 117 | `SVC-18` Parking                                  | `PKG-06`     | Bãi xe đầy/không còn chỗ                              | CG10 capacity; CG08 allocation policy; CG17 parking policy; CG18 unknown                            | Parking Operations/Security      | P3               | `RES-07,RES-15,SRV-02,SRV-03,SRV-04,SRV-05,SRV-06,SRV-07`                                                         |
| 118 | `SVC-18` Parking                                  | `PKG-07`     | Ùn tắc cổng bãi xe                                      | CG10 peak demand; CG01 barrier/LPR performance; CG09 manual handling; CG18 unknown                  | Parking Operations/Security      | P3               | `RES-07,RES-15,SRV-02,SRV-03,SRV-04,SRV-05,SRV-06,SRV-07`                                                         |
| 119 | `SVC-18` Parking                                  | `PKG-08`     | Mất an ninh/tài sản trong bãi                           | CG08 security process; CG01 CCTV; CG09 patrol/staffing; CG18 unknown                                | Parking Operations/Security      | P1               | `RES-07,RES-15,SRV-02,SRV-03,SRV-04,SRV-05,SRV-06,SRV-07`                                                         |
| 120 | `SVC-19` Internal Mobility / Shuttle / Bus        | `MOB-01`     | Không tìm thấy tuyến/lịch xe                           | CG06 route data; CG03 app; CG08 content update; CG18 unknown                                        | Transport Operations             | P3               | `RES-08,RES-15,SRV-01,SRV-02,SRV-05,SRV-06`                                                                       |
| 121 | `SVC-19` Internal Mobility / Shuttle / Bus        | `MOB-02`     | Xe đến chậm/bỏ chuyến                                  | CG12 operator/vendor; CG14 traffic/weather; CG09 staffing; CG18 unknown                             | Transport Operations             | P3               | `RES-08,RES-15,SRV-01,SRV-02,SRV-05,SRV-06`                                                                       |
| 122 | `SVC-19` Internal Mobility / Shuttle / Bus        | `MOB-03`     | Thông tin thời gian thực không chính xác              | CG05 GPS integration; CG04 network; CG06 route data; CG18 unknown                                   | Transport Operations             | P3               | `RES-08,RES-15,SRV-01,SRV-02,SRV-05,SRV-06`                                                                       |
| 123 | `SVC-19` Internal Mobility / Shuttle / Bus        | `MOB-04`     | Quá tải/không lên được xe                            | CG10 passenger demand; CG08 dispatch planning; CG18 unknown                                         | Transport Operations             | P3               | `RES-08,RES-15,SRV-01,SRV-02,SRV-05,SRV-06`                                                                       |
| 124 | `SVC-19` Internal Mobility / Shuttle / Bus        | `MOB-05`     | Điểm dừng/biển chỉ dẫn khó hiểu                     | CG15 design; CG08 wayfinding process; CG09 maintenance; CG18 unknown                                | Transport Operations             | P3               | `RES-08,RES-15,SRV-01,SRV-02,SRV-05,SRV-06`                                                                       |
| 125 | `SVC-20` Water & Plumbing                         | `WAT-01`     | Mất nước                                                 | CG13 external supply; CG01 pump/valve; CG02 power; CG15 pipe failure; CG18 unknown                  | MEP Water/Technical              | P1               | `RES-15,RES-16,SRV-02,SRV-05,SRV-06,SRV-07`                                                                       |
| 126 | `SVC-20` Water & Plumbing                         | `WAT-02`     | Áp lực nước yếu                                        | CG13 source pressure; CG01 booster pump/valve; CG10 high demand; CG15 pipe blockage; CG18 unknown   | MEP Water/Technical              | P2               | `RES-15,RES-16,SRV-02,SRV-05,SRV-06,SRV-07`                                                                       |
| 127 | `SVC-20` Water & Plumbing                         | `WAT-03`     | Áp lực nước không ổn định                           | CG01 pump/controller/sensor; CG10 demand fluctuation; CG02 power; CG18 unknown                      | MEP Water/Technical              | P2               | `RES-15,RES-16,SRV-02,SRV-05,SRV-06,SRV-07`                                                                       |
| 128 | `SVC-20` Water & Plumbing                         | `WAT-04`     | Rò rỉ nước                                              | CG01 pipe/fixture; CG15 joint/installation; CG11 maintenance; CG18 unknown                          | MEP Water/Technical              | P2               | `RES-15,RES-16,SRV-02,SRV-05,SRV-06,SRV-07`                                                                       |
| 129 | `SVC-20` Water & Plumbing                         | `WAT-05`     | Nước đục/đổi màu                                     | CG13 source quality; CG15 sediment/pipe; CG11 tank maintenance; CG18 unknown                        | MEP Water/Technical              | P2               | `RES-15,RES-16,SRV-02,SRV-05,SRV-06,SRV-07`                                                                       |
| 130 | `SVC-20` Water & Plumbing                         | `WAT-06`     | Nước có mùi                                             | CG13 source quality; CG11 tank/pipe cleaning; CG14 contamination; CG18 unknown                      | MEP Water/Technical              | P2               | `RES-15,RES-16,SRV-02,SRV-05,SRV-06,SRV-07`                                                                       |
| 131 | `SVC-20` Water & Plumbing                         | `WAT-07`     | Thoát nước chậm/tắc                                    | CG15 pipe blockage/slope; CG14 foreign material; CG11 cleaning; CG18 unknown                        | MEP Water/Technical              | P2               | `RES-15,RES-16,SRV-02,SRV-05,SRV-06,SRV-07`                                                                       |
| 132 | `SVC-20` Water & Plumbing                         | `WAT-08`     | Ngập/tràn nước khu vực chung                           | CG15 drainage capacity; CG14 heavy rain; CG01 pump failure; CG11 maintenance; CG18 unknown          | MEP Water/Technical              | P1               | `RES-15,RES-16,SRV-02,SRV-05,SRV-06,SRV-07`                                                                       |
| 133 | `SVC-21` Electrical & Lighting                    | `ELE-01`     | Mất điện khu vực/căn hộ                               | CG13 grid outage; CG02 breaker/cable/panel; CG01 equipment; CG18 unknown                            | MEP Electrical/Technical         | P1               | `RES-05,RES-06,RES-11,RES-15,RES-16,SRV-02,SRV-05,SRV-06,SRV-07`                                                  |
| 134 | `SVC-21` Electrical & Lighting                    | `ELE-02`     | Mất điện cục bộ                                        | CG02 branch breaker/wiring; CG01 panel; CG15 installation; CG18 unknown                             | MEP Electrical/Technical         | P2               | `RES-05,RES-06,RES-11,RES-15,RES-16,SRV-02,SRV-05,SRV-06,SRV-07`                                                  |
| 135 | `SVC-21` Electrical & Lighting                    | `ELE-03`     | Đèn không sáng                                          | CG01 lamp/LED driver; CG02 circuit; CG07 timer/control; CG18 unknown                                | MEP Electrical/Technical         | P2               | `RES-05,RES-06,RES-11,RES-15,RES-16,SRV-02,SRV-05,SRV-06,SRV-07`                                                  |
| 136 | `SVC-21` Electrical & Lighting                    | `ELE-04`     | Đèn chập chờn                                           | CG01 driver/lamp; CG02 loose connection/voltage; CG18 unknown                                       | MEP Electrical/Technical         | P2               | `RES-05,RES-06,RES-11,RES-15,RES-16,SRV-02,SRV-05,SRV-06,SRV-07`                                                  |
| 137 | `SVC-21` Electrical & Lighting                    | `ELE-05`     | Đèn sự cố không hoạt động                           | CG01 battery/luminaire; CG02 power; CG11 test/maintenance; CG18 unknown                             | MEP Electrical/Technical         | P1               | `RES-05,RES-06,RES-11,RES-15,RES-16,SRV-02,SRV-05,SRV-06,SRV-07`                                                  |
| 138 | `SVC-21` Electrical & Lighting                    | `ELE-06`     | Breaker nhảy lặp lại                                     | CG02 overload/short/ground fault; CG01 appliance/equipment; CG15 wiring; CG18 unknown               | MEP Electrical/Technical         | P2               | `RES-05,RES-06,RES-11,RES-15,RES-16,SRV-02,SRV-05,SRV-06,SRV-07`                                                  |
| 139 | `SVC-21` Electrical & Lighting                    | `ELE-07`     | Ổ cắm/tủ điện quá nhiệt hoặc có mùi khét         | CG02 loose connection/overload; CG01 component; CG15 installation; CG18 unknown                     | MEP Electrical/Technical         | P1               | `RES-05,RES-06,RES-11,RES-15,RES-16,SRV-02,SRV-05,SRV-06,SRV-07`                                                  |
| 140 | `SVC-22` Backup Power                             | `GEN-01`     | Máy phát không khởi động                              | CG01 generator/starter; CG02 battery; CG13 fuel; CG11 maintenance; CG18 unknown                     | MEP Electrical/Generator Vendor  | P1               | `RES-15,RES-16,SRV-02,SRV-05,SRV-06,SRV-07`                                                                       |
| 141 | `SVC-22` Backup Power                             | `GEN-02`     | Máy phát chạy nhưng không nhận tải                   | CG01 alternator/controller; CG02 breaker; CG07 control config; CG18 unknown                         | MEP Electrical/Generator Vendor  | P1               | `RES-15,RES-16,SRV-02,SRV-05,SRV-06,SRV-07`                                                                       |
| 142 | `SVC-22` Backup Power                             | `GEN-03`     | Chuyển nguồn ATS chậm/không chuyển                     | CG01 ATS/controller; CG02 control power; CG11 maintenance; CG18 unknown                             | MEP Electrical/Generator Vendor  | P1               | `RES-15,RES-16,SRV-02,SRV-05,SRV-06,SRV-07`                                                                       |
| 143 | `SVC-22` Backup Power                             | `GEN-04`     | Nguồn dự phòng không ổn định                         | CG01 governor/AVR; CG02 load/connection; CG10 overload; CG18 unknown                                | MEP Electrical/Generator Vendor  | P1               | `RES-15,RES-16,SRV-02,SRV-05,SRV-06,SRV-07`                                                                       |
| 144 | `SVC-22` Backup Power                             | `GEN-05`     | Kiểm tra định kỳ không đạt                           | CG11 maintenance/testing; CG01 component aging; CG12 vendor; CG18 unknown                           | MEP Electrical/Generator Vendor  | P1               | `RES-15,RES-16,SRV-02,SRV-05,SRV-06,SRV-07`                                                                       |
| 145 | `SVC-23` HVAC / Ventilation                       | `HVAC-01`    | Khu vực chung quá nóng                                   | CG01 fan/coil; CG10 load; CG07 setpoint; CG11 filter/maintenance; CG18 unknown                      | MEP HVAC/Technical               | P2               | `RES-15,RES-16,SRV-02,SRV-05,SRV-06,SRV-07`                                                                       |
| 146 | `SVC-23` HVAC / Ventilation                       | `HVAC-02`    | Làm mát yếu                                              | CG11 dirty filter/coil; CG01 fan/compressor; CG15 duct leakage; CG18 unknown                        | MEP HVAC/Technical               | P2               | `RES-15,RES-16,SRV-02,SRV-05,SRV-06,SRV-07`                                                                       |
| 147 | `SVC-23` HVAC / Ventilation                       | `HVAC-03`    | Không có thông gió                                      | CG01 fan; CG02 power; CG15 duct blockage; CG07 control; CG18 unknown                                | MEP HVAC/Technical               | P2               | `RES-15,RES-16,SRV-02,SRV-05,SRV-06,SRV-07`                                                                       |
| 148 | `SVC-23` HVAC / Ventilation                       | `HVAC-04`    | Tiếng ồn/rung bất thường                               | CG01 fan/bearing; CG15 alignment; CG11 maintenance; CG18 unknown                                    | MEP HVAC/Technical               | P2               | `RES-15,RES-16,SRV-02,SRV-05,SRV-06,SRV-07`                                                                       |
| 149 | `SVC-23` HVAC / Ventilation                       | `HVAC-05`    | Mùi khó chịu từ HVAC                                    | CG11 filter/coil cleanliness; CG14 moisture/mold; CG15 drainage/duct; CG18 unknown                  | MEP HVAC/Technical               | P2               | `RES-15,RES-16,SRV-02,SRV-05,SRV-06,SRV-07`                                                                       |
| 150 | `SVC-23` HVAC / Ventilation                       | `HVAC-06`    | Đọng nước/rò nước điều hòa                        | CG15 drain blockage/slope; CG01 pump/coil; CG11 maintenance; CG18 unknown                           | MEP HVAC/Technical               | P2               | `RES-15,RES-16,SRV-02,SRV-05,SRV-06,SRV-07`                                                                       |
| 151 | `SVC-23` HVAC / Ventilation                       | `HVAC-07`    | Nhiệt độ/setpoint không đúng                          | CG01 thermostat/sensor; CG07 control config; CG03 BMS software; CG18 unknown                        | MEP HVAC/Technical               | P2               | `RES-15,RES-16,SRV-02,SRV-05,SRV-06,SRV-07`                                                                       |
| 152 | `SVC-24` Fire Safety                              | `FIRE-01`    | Báo cháy giả                                             | CG01 detector; CG14 dust/steam/environment; CG07 sensitivity config; CG11 cleaning; CG18 unknown    | Fire Safety/Technical/Security   | P1               | `RES-11,RES-16,SRV-02,SRV-05,SRV-06,SRV-07`                                                                       |
| 153 | `SVC-24` Fire Safety                              | `FIRE-02`    | Đầu báo/chuông không hoạt động                      | CG01 detector/sounder; CG02 power; CG04 loop communication; CG18 unknown                            | Fire Safety/Technical/Security   | P1               | `RES-11,RES-16,SRV-02,SRV-05,SRV-06,SRV-07`                                                                       |
| 154 | `SVC-24` Fire Safety                              | `FIRE-03`    | Báo động lặp lại không rõ nguyên nhân              | CG01 detector/panel; CG14 contamination; CG04 communication; CG18 unknown                           | Fire Safety/Technical/Security   | P1               | `RES-11,RES-16,SRV-02,SRV-05,SRV-06,SRV-07`                                                                       |
| 155 | `SVC-24` Fire Safety                              | `FIRE-04`    | Cửa chống cháy không hoạt động đúng                | CG01 closer/lock; CG14 obstruction; CG11 maintenance; CG18 unknown                                  | Fire Safety/Technical/Security   | P1               | `RES-11,RES-16,SRV-02,SRV-05,SRV-06,SRV-07`                                                                       |
| 156 | `SVC-24` Fire Safety                              | `FIRE-05`    | Sprinkler/van có bất thường                             | CG01 valve/head; CG15 installation; CG11 inspection; CG18 unknown                                   | Fire Safety/Technical/Security   | P1               | `RES-11,RES-16,SRV-02,SRV-05,SRV-06,SRV-07`                                                                       |
| 157 | `SVC-24` Fire Safety                              | `FIRE-06`    | Bơm chữa cháy không sẵn sàng                          | CG01 pump/controller; CG02 power; CG11 maintenance/test; CG18 unknown                               | Fire Safety/Technical/Security   | P1               | `RES-11,RES-16,SRV-02,SRV-05,SRV-06,SRV-07`                                                                       |
| 158 | `SVC-24` Fire Safety                              | `FIRE-07`    | Lối thoát hiểm bị cản trở/biển chỉ dẫn lỗi        | CG14 obstruction; CG09 housekeeping/security; CG01 emergency sign; CG18 unknown                     | Fire Safety/Technical/Security   | P1               | `RES-11,RES-16,SRV-02,SRV-05,SRV-06,SRV-07`                                                                       |
| 159 | `SVC-25` Building / Common Area Assets            | `BLD-01`     | Cửa/khoá khu vực chung hỏng                             | CG01 lock/hinge/door; CG11 maintenance; CG15 installation; CG18 unknown                             | Facilities/Technical             | P3               | `HO-04,HO-06,RES-05,RES-06,RES-10,RES-12,RES-13,RES-15,SRV-02,SRV-05,SRV-06`                                      |
| 160 | `SVC-25` Building / Common Area Assets            | `BLD-02`     | Kính/lan can/trần/tường có hư hỏng                   | CG15 construction; CG14 impact/weather; CG11 maintenance; CG18 unknown                              | Facilities/Technical             | P2               | `HO-04,HO-06,RES-05,RES-06,RES-10,RES-12,RES-13,RES-15,SRV-02,SRV-05,SRV-06`                                      |
| 161 | `SVC-25` Building / Common Area Assets            | `BLD-03`     | Sàn trơn/nứt/gồ ghề                                    | CG15 finish/design; CG14 water/spill; CG11 maintenance; CG18 unknown                                | Facilities/Technical             | P2               | `HO-04,HO-06,RES-05,RES-06,RES-10,RES-12,RES-13,RES-15,SRV-02,SRV-05,SRV-06`                                      |
| 162 | `SVC-25` Building / Common Area Assets            | `BLD-04`     | Biển chỉ dẫn/wayfinding thiếu hoặc sai                 | CG08 signage process; CG15 design; CG09 maintenance; CG18 unknown                                   | Facilities/Technical             | P3               | `HO-04,HO-06,RES-05,RES-06,RES-10,RES-12,RES-13,RES-15,SRV-02,SRV-05,SRV-06`                                      |
| 163 | `SVC-25` Building / Common Area Assets            | `BLD-05`     | Thiết bị công cộng không sử dụng được             | CG01 hardware; CG02 power; CG11 maintenance; CG18 unknown                                           | Facilities/Technical             | P3               | `HO-04,HO-06,RES-05,RES-06,RES-10,RES-12,RES-13,RES-15,SRV-02,SRV-05,SRV-06`                                      |
| 164 | `SVC-25` Building / Common Area Assets            | `BLD-06`     | Khu vực chung xuống cấp/tái diễn lỗi                  | CG11 preventive maintenance; CG15 material/design; CG12 contractor; CG18 unknown                    | Facilities/Technical             | P3               | `HO-04,HO-06,RES-05,RES-06,RES-10,RES-12,RES-13,RES-15,SRV-02,SRV-05,SRV-06`                                      |
| 165 | `SVC-26` Security                                 | `SEC-01`     | Người lạ vào khu vực hạn chế                         | CG08 access/security process; CG09 guard action; CG01 access/CCTV; CG18 unknown                     | Security Operations              | P1               | `RES-03,RES-05,RES-09,RES-10,RES-16,SRV-02,SRV-05,SRV-06`                                                         |
| 166 | `SVC-26` Security                                 | `SEC-02`     | Xô xát/hành vi gây rối                                 | CG09 response/staffing; CG08 escalation; CG18 unknown                                               | Security Operations              | P1               | `RES-03,RES-05,RES-09,RES-10,RES-16,SRV-02,SRV-05,SRV-06`                                                         |
| 167 | `SVC-26` Security                                 | `SEC-03`     | Mất cắp/nghi ngờ mất cắp                               | CG01 CCTV/access evidence; CG09 patrol; CG08 incident process; CG18 unknown                         | Security Operations              | P1               | `RES-03,RES-05,RES-09,RES-10,RES-16,SRV-02,SRV-05,SRV-06`                                                         |
| 168 | `SVC-26` Security                                 | `SEC-04`     | Camera không hoạt động/mất hình                       | CG01 camera/NVR; CG02 power; CG04 network; CG18 unknown                                             | Security Operations              | P2               | `RES-03,RES-05,RES-09,RES-10,RES-16,SRV-02,SRV-05,SRV-06`                                                         |
| 169 | `SVC-26` Security                                 | `SEC-05`     | Bảo vệ phản ứng chậm                                   | CG09 staffing; CG08 dispatch; CG10 incident load; CG18 unknown                                      | Security Operations              | P1               | `RES-03,RES-05,RES-09,RES-10,RES-16,SRV-02,SRV-05,SRV-06`                                                         |
| 170 | `SVC-26` Security                                 | `SEC-06`     | Kiểm soát khách/nhà thầu không đúng quy trình      | CG08 SOP; CG09 guard operation; CG06 visitor data; CG18 unknown                                     | Security Operations              | P2               | `RES-03,RES-05,RES-09,RES-10,RES-16,SRV-02,SRV-05,SRV-06`                                                         |
| 171 | `SVC-26` Security                                 | `SEC-07`     | Hotline an ninh không liên lạc được                   | CG04 telephony; CG09 staffing; CG08 on-call process; CG18 unknown                                   | Security Operations              | P1               | `RES-03,RES-05,RES-09,RES-10,RES-16,SRV-02,SRV-05,SRV-06`                                                         |
| 172 | `SVC-27` Cleaning                                 | `CLN-01`     | Sảnh/hành lang bẩn                                       | CG08 cleaning schedule; CG09 staffing; CG12 vendor; CG10 high traffic; CG18 unknown                 | Housekeeping/Vendor              | P3               | `RES-06,RES-10,RES-12,RES-13,RES-15,SRV-02,SRV-05,SRV-06`                                                         |
| 173 | `SVC-27` Cleaning                                 | `CLN-02`     | Thang máy bẩn                                             | CG08 cleaning schedule; CG09 staffing; CG10 usage; CG18 unknown                                     | Housekeeping/Vendor              | P3               | `RES-06,RES-10,RES-12,RES-13,RES-15,SRV-02,SRV-05,SRV-06`                                                         |
| 174 | `SVC-27` Cleaning                                 | `CLN-03`     | Nhà vệ sinh chung bẩn/thiếu vật tư                    | CG09 staffing; CG08 replenishment; CG12 vendor; CG18 unknown                                        | Housekeeping/Vendor              | P3               | `RES-06,RES-10,RES-12,RES-13,RES-15,SRV-02,SRV-05,SRV-06`                                                         |
| 175 | `SVC-27` Cleaning                                 | `CLN-04`     | Mùi khó chịu khu vực chung                              | CG14 waste/odor source; CG14 moisture; CG08 cleaning; CG18 unknown                                  | Housekeeping/Vendor              | P3               | `RES-06,RES-10,RES-12,RES-13,RES-15,SRV-02,SRV-05,SRV-06`                                                         |
| 176 | `SVC-27` Cleaning                                 | `CLN-05`     | Tràn đổ không được xử lý kịp                      | CG09 response; CG08 dispatch; CG10 workload; CG18 unknown                                           | Housekeeping/Vendor              | P2               | `RES-06,RES-10,RES-12,RES-13,RES-15,SRV-02,SRV-05,SRV-06`                                                         |
| 177 | `SVC-27` Cleaning                                 | `CLN-06`     | Chất lượng vệ sinh không đạt sau xử lý             | CG12 vendor quality; CG09 supervision; CG08 acceptance criteria; CG18 unknown                       | Housekeeping/Vendor              | P3               | `RES-06,RES-10,RES-12,RES-13,RES-15,SRV-02,SRV-05,SRV-06`                                                         |
| 178 | `SVC-28` Waste Management                         | `WST-01`     | Rác đầy/tràn điểm tập kết                           | CG10 volume; CG08 collection schedule; CG12 vendor; CG18 unknown                                    | Housekeeping/Waste Vendor        | P3               | `RES-10,RES-12,RES-15,SRV-02,SRV-05,SRV-06`                                                                       |
| 179 | `SVC-28` Waste Management                         | `WST-02`     | Thu gom rác bị bỏ lượt/chậm                           | CG12 vendor; CG09 staffing; CG08 routing/schedule; CG18 unknown                                     | Housekeeping/Waste Vendor        | P3               | `RES-10,RES-12,RES-15,SRV-02,SRV-05,SRV-06`                                                                       |
| 180 | `SVC-28` Waste Management                         | `WST-03`     | Mùi khu rác                                               | CG10 volume; CG14 temperature/moisture; CG08 cleaning; CG18 unknown                                 | Housekeeping/Waste Vendor        | P3               | `RES-10,RES-12,RES-15,SRV-02,SRV-05,SRV-06`                                                                       |
| 181 | `SVC-28` Waste Management                         | `WST-04`     | Phân loại/xử lý rác không đúng                      | CG08 SOP; CG09 resident/vendor behavior; CG17 policy; CG18 unknown                                  | Housekeeping/Waste Vendor        | P3               | `RES-10,RES-12,RES-15,SRV-02,SRV-05,SRV-06`                                                                       |
| 182 | `SVC-28` Waste Management                         | `WST-05`     | Rác cồng kềnh/xây dựng không được xử lý          | CG08 special waste process; CG16 resident input; CG12 vendor; CG18 unknown                          | Housekeeping/Waste Vendor        | P3               | `RES-10,RES-12,RES-15,SRV-02,SRV-05,SRV-06`                                                                       |
| 183 | `SVC-29` Pest Control                             | `PST-01`     | Gián/côn trùng xuất hiện nhiều                        | CG14 environment/food/water; CG08 treatment frequency; CG12 vendor; CG18 unknown                    | Pest Control Vendor/BQL          | P3               | `RES-12,RES-15,SRV-02,SRV-05,SRV-06`                                                                              |
| 184 | `SVC-29` Pest Control                             | `PST-02`     | Muỗi tăng bất thường                                   | CG14 standing water/weather; CG08 source control; CG12 vendor; CG18 unknown                         | Pest Control Vendor/BQL          | P3               | `RES-12,RES-15,SRV-02,SRV-05,SRV-06`                                                                              |
| 185 | `SVC-29` Pest Control                             | `PST-03`     | Chuột/động vật gây hại                                | CG14 waste/access points; CG15 building gaps; CG08 control program; CG18 unknown                    | Pest Control Vendor/BQL          | P3               | `RES-12,RES-15,SRV-02,SRV-05,SRV-06`                                                                              |
| 186 | `SVC-29` Pest Control                             | `PST-04`     | Xử lý pest nhưng tái diễn                              | CG08 incomplete source treatment; CG12 vendor quality; CG14 external source; CG18 unknown           | Pest Control Vendor/BQL          | P3               | `RES-12,RES-15,SRV-02,SRV-05,SRV-06`                                                                              |
| 187 | `SVC-30` Landscaping                              | `LAN-01`     | Cây xanh chết/héo                                        | CG14 weather/water; CG08 irrigation process; CG12 vendor; CG15 planting quality; CG18 unknown       | Landscape Vendor/Facilities      | P4               | `RES-08,RES-12,RES-15,SRV-02,SRV-05,SRV-06`                                                                       |
| 188 | `SVC-30` Landscaping                              | `LAN-02`     | Tưới nước quá mức/gây đọng nước                  | CG07 irrigation config; CG01 valve/controller; CG09 operation; CG18 unknown                         | Landscape Vendor/Facilities      | P4               | `RES-08,RES-12,RES-15,SRV-02,SRV-05,SRV-06`                                                                       |
| 189 | `SVC-30` Landscaping                              | `LAN-03`     | Cây/cành có nguy cơ mất an toàn                       | CG14 storm/wind; CG11 inspection; CG08 pruning plan; CG18 unknown                                   | Landscape Vendor/Facilities      | P1               | `RES-08,RES-12,RES-15,SRV-02,SRV-05,SRV-06`                                                                       |
| 190 | `SVC-30` Landscaping                              | `LAN-04`     | Thảm cỏ/cảnh quan xuống cấp                            | CG10 usage; CG14 weather; CG12 vendor; CG08 maintenance plan; CG18 unknown                          | Landscape Vendor/Facilities      | P4               | `RES-08,RES-12,RES-15,SRV-02,SRV-05,SRV-06`                                                                       |
| 191 | `SVC-30` Landscaping                              | `LAN-05`     | Côn trùng/mùi từ cảnh quan                             | CG14 organic matter/water; CG08 landscape care; CG14 pest source; CG18 unknown                      | Landscape Vendor/Facilities      | P4               | `RES-08,RES-12,RES-15,SRV-02,SRV-05,SRV-06`                                                                       |
| 192 | `SVC-31` Amenities                                | `AMN-01`     | Không đặt được tiện ích                             | CG03 booking system; CG05 amenities integration; CG07 eligibility rule; CG18 unknown                | Amenities Operations/BQL         | P3               | `RES-12,RES-13,RES-15,SRV-01,SRV-02,SRV-03,SRV-04,SRV-05,SRV-06,SRV-07,SRV-08`                                    |
| 193 | `SVC-31` Amenities                                | `AMN-02`     | Không còn slot/slot hiển thị sai                        | CG10 capacity; CG05 calendar sync; CG07 booking rule; CG18 unknown                                  | Amenities Operations/BQL         | P3               | `RES-12,RES-13,RES-15,SRV-01,SRV-02,SRV-03,SRV-04,SRV-05,SRV-06,SRV-07,SRV-08`                                    |
| 194 | `SVC-31` Amenities                                | `AMN-03`     | Overbooking/trùng lịch                                    | CG03 concurrency; CG05 duplicate event; CG07 capacity config; CG18 unknown                          | Amenities Operations/BQL         | P3               | `RES-12,RES-13,RES-15,SRV-01,SRV-02,SRV-03,SRV-04,SRV-05,SRV-06,SRV-07,SRV-08`                                    |
| 195 | `SVC-31` Amenities                                | `AMN-04`     | Đã đặt nhưng không được vào                       | CG05 booking-access sync; CG06 resident entitlement; CG07 access rule; CG18 unknown                 | Amenities Operations/BQL         | P3               | `RES-12,RES-13,RES-15,SRV-01,SRV-02,SRV-03,SRV-04,SRV-05,SRV-06,SRV-07,SRV-08`                                    |
| 196 | `SVC-31` Amenities                                | `AMN-05`     | Tiện ích đóng nhưng app chưa cập nhật               | CG05 status sync; CG08 communication; CG06 schedule data; CG18 unknown                              | Amenities Operations/BQL         | P3               | `RES-12,RES-13,RES-15,SRV-01,SRV-02,SRV-03,SRV-04,SRV-05,SRV-06,SRV-07,SRV-08`                                    |
| 197 | `SVC-31` Amenities                                | `AMN-06`     | Thiết bị tiện ích hỏng                                 | CG01 equipment; CG02 power; CG11 maintenance; CG18 unknown                                          | Amenities Operations/BQL         | P3               | `RES-12,RES-13,RES-15,SRV-01,SRV-02,SRV-03,SRV-04,SRV-05,SRV-06,SRV-07,SRV-08`                                    |
| 198 | `SVC-31` Amenities                                | `AMN-07`     | Vệ sinh/chất lượng tiện ích không đạt              | CG08 cleaning process; CG09 staffing; CG12 vendor; CG18 unknown                                     | Amenities Operations/BQL         | P3               | `RES-12,RES-13,RES-15,SRV-01,SRV-02,SRV-03,SRV-04,SRV-05,SRV-06,SRV-07,SRV-08`                                    |
| 199 | `SVC-31` Amenities                                | `AMN-08`     | Thanh toán/hoàn tiền tiện ích lỗi                     | CG12 payment gateway; CG05 billing sync; CG08 refund process; CG18 unknown                          | Amenities Operations/BQL         | P3               | `RES-12,RES-13,RES-15,SRV-01,SRV-02,SRV-03,SRV-04,SRV-05,SRV-06,SRV-07,SRV-08`                                    |
| 200 | `SVC-32` Renovation / Construction Permit         | `REN-01`     | Không rõ hồ sơ cần nộp                                | CG08 process communication; CG17 policy; CG18 unknown                                               | Urban Management/BQL/Technical   | P3               | `RES-14,RES-15,SRV-01,SRV-02,SRV-03,SRV-04,SRV-05,SRV-06,SRV-07`                                                  |
| 201 | `SVC-32` Renovation / Construction Permit         | `REN-02`     | Hồ sơ thi công bị yêu cầu bổ sung nhiều lần        | CG16 incomplete documents; CG08 checklist; CG09 reviewer inconsistency; CG18 unknown                | Urban Management/BQL/Technical   | P3               | `RES-14,RES-15,SRV-01,SRV-02,SRV-03,SRV-04,SRV-05,SRV-06,SRV-07`                                                  |
| 202 | `SVC-32` Renovation / Construction Permit         | `REN-03`     | Phê duyệt thi công chậm                                 | CG09 reviewer capacity; CG08 workflow; CG10 queue; CG18 unknown                                     | Urban Management/BQL/Technical   | P3               | `RES-14,RES-15,SRV-01,SRV-02,SRV-03,SRV-04,SRV-05,SRV-06,SRV-07`                                                  |
| 203 | `SVC-32` Renovation / Construction Permit         | `REN-04`     | Không đặt được lịch thi công/vận chuyển           | CG10 capacity; CG03 scheduling; CG07 rule; CG18 unknown                                             | Urban Management/BQL/Technical   | P3               | `RES-14,RES-15,SRV-01,SRV-02,SRV-03,SRV-04,SRV-05,SRV-06,SRV-07`                                                  |
| 204 | `SVC-32` Renovation / Construction Permit         | `REN-05`     | Nhà thầu không được cấp quyền ra vào               | CG06 contractor data; CG05 access sync; CG08 approval; CG18 unknown                                 | Urban Management/BQL/Technical   | P3               | `RES-14,RES-15,SRV-01,SRV-02,SRV-03,SRV-04,SRV-05,SRV-06,SRV-07`                                                  |
| 205 | `SVC-32` Renovation / Construction Permit         | `REN-06`     | Vi phạm giờ/tiếng ồn/quy định thi công               | CG17 policy; CG09 contractor behavior; CG08 supervision; CG18 unknown                               | Urban Management/BQL/Technical   | P3               | `RES-14,RES-15,SRV-01,SRV-02,SRV-03,SRV-04,SRV-05,SRV-06,SRV-07`                                                  |
| 206 | `SVC-33` Move-in / Move-out                       | `MOV-01`     | Không rõ thủ tục chuyển vào/chuyển ra                | CG08 communication; CG17 building rule; CG18 unknown                                                | Resident Operations/Security/BQL | P3               | `HO-08,RES-01,RES-03,RES-05,RES-14,RES-15,SRV-01,SRV-02,SRV-03,SRV-05,SRV-06,SRV-07`                              |
| 207 | `SVC-33` Move-in / Move-out                       | `MOV-02`     | Không đăng ký được lịch chuyển đồ                | CG03 scheduling; CG10 freight-elevator capacity; CG07 rule; CG18 unknown                            | Resident Operations/Security/BQL | P3               | `HO-08,RES-01,RES-03,RES-05,RES-14,RES-15,SRV-01,SRV-02,SRV-03,SRV-05,SRV-06,SRV-07`                              |
| 208 | `SVC-33` Move-in / Move-out                       | `MOV-03`     | Không được cấp quyền xe/nhà thầu chuyển đồ       | CG06 vehicle/contractor data; CG05 access sync; CG08 approval; CG18 unknown                         | Resident Operations/Security/BQL | P3               | `HO-08,RES-01,RES-03,RES-05,RES-14,RES-15,SRV-01,SRV-02,SRV-03,SRV-05,SRV-06,SRV-07`                              |
| 209 | `SVC-33` Move-in / Move-out                       | `MOV-04`     | Xung đột lịch thang hàng/khu vực bốc dỡ              | CG10 capacity; CG07 scheduling rule; CG08 coordination; CG18 unknown                                | Resident Operations/Security/BQL | P3               | `HO-08,RES-01,RES-03,RES-05,RES-14,RES-15,SRV-01,SRV-02,SRV-03,SRV-05,SRV-06,SRV-07`                              |
| 210 | `SVC-33` Move-in / Move-out                       | `MOV-05`     | Hư hỏng tài sản chung trong quá trình chuyển         | CG16 mover behavior; CG09 supervision; CG15 protection setup; CG18 unknown                          | Resident Operations/Security/BQL | P2               | `HO-08,RES-01,RES-03,RES-05,RES-14,RES-15,SRV-01,SRV-02,SRV-03,SRV-05,SRV-06,SRV-07`                              |
| 211 | `SVC-33` Move-in / Move-out                       | `MOV-06`     | Hoàn/đối soát đặt cọc thi công/chuyển đồ chậm   | CG08 finance process; CG06 inspection record; CG09 staffing; CG18 unknown                           | Resident Operations/Security/BQL | P3               | `HO-08,RES-01,RES-03,RES-05,RES-14,RES-15,SRV-01,SRV-02,SRV-03,SRV-05,SRV-06,SRV-07`                              |
| 212 | `SVC-34` Community Communication / Notification   | `COM-01`     | Không nhận được thông báo vận hành                 | CG03 notification; CG05 event integration; CG06 recipient data; CG18 unknown                        | CX/Communications/BQL            | P3               | `RES-11,RES-15,RES-16,SRV-01,SRV-03,SRV-06,SRV-07,SRV-08`                                                         |
| 213 | `SVC-34` Community Communication / Notification   | `COM-02`     | Thông báo sai đối tượng/tòa/căn                     | CG06 audience data; CG07 segmentation config; CG09 human; CG18 unknown                              | CX/Communications/BQL            | P3               | `RES-11,RES-15,RES-16,SRV-01,SRV-03,SRV-06,SRV-07,SRV-08`                                                         |
| 214 | `SVC-34` Community Communication / Notification   | `COM-03`     | Thông báo gửi quá muộn                                 | CG08 approval process; CG09 owner delay; CG03 notification; CG18 unknown                            | CX/Communications/BQL            | P2               | `RES-11,RES-15,RES-16,SRV-01,SRV-03,SRV-06,SRV-07,SRV-08`                                                         |
| 215 | `SVC-34` Community Communication / Notification   | `COM-04`     | Nội dung thông báo khó hiểu/không nhất quán         | CG08 editorial process; CG09 human; CG17 policy; CG18 unknown                                       | CX/Communications/BQL            | P3               | `RES-11,RES-15,RES-16,SRV-01,SRV-03,SRV-06,SRV-07,SRV-08`                                                         |
| 216 | `SVC-34` Community Communication / Notification   | `COM-05`     | Không có cập nhật tiếp theo khi sự cố kéo dài      | CG08 incident communication; CG09 owner discipline; CG18 unknown                                    | CX/Communications/BQL            | P2               | `RES-11,RES-15,RES-16,SRV-01,SRV-03,SRV-06,SRV-07,SRV-08`                                                         |
| 217 | `SVC-34` Community Communication / Notification   | `COM-06`     | Khảo sát/đánh giá không liên kết về ticket/service | CG05 survey integration; CG06 linkage key; CG08 closed-loop process; CG18 unknown                   | CX/Communications/BQL            | P3               | `RES-11,RES-15,RES-16,SRV-01,SRV-03,SRV-06,SRV-07,SRV-08`                                                         |

---

## 6. Canonical Data Model and Required Fields

### Quy ước chung

- Dùng immutable surrogate key (`UUID`, `ULID` hoặc bigint) làm PK nội bộ; public code là business identifier ổn định, không tái sử dụng.
- Mọi master entity và mapping phải thuộc một `taxonomy_release` hoặc có validity range theo release. Không dùng một cờ `active` đơn lẻ để thay thế version history.
- Prediction của AI/rule là dữ liệu bất biến và tách khỏi decision đã được áp dụng. Review tạo decision/review event mới, không overwrite prediction.
- Runtime record phải pin `taxonomy_release_id` để có thể tái dựng đúng label tại thời điểm phân loại.

### 6.1 Release và governance

#### `taxonomy_release`

```text
taxonomy_release_id
version                 # semantic version
status                  # DRAFT | APPROVED | PUBLISHED | RETIRED
effective_from
effective_to
source_reference
source_checksum
change_summary
created_by
created_at
approved_by
approved_at
```

#### Common revision fields

Các bảng master bên dưới có tối thiểu:

```text
entity_id               # immutable identity
entity_code             # stable public code
name
description
valid_from_release_id
valid_to_release_id     # nullable
record_status           # DRAFT | ACTIVE | RETIRED
superseded_by_id        # nullable; chỉ cho 1:1 rename/replace
```

Merge/split dùng bảng `taxonomy_supersession_map`, không nhét nhiều ID vào `superseded_by_id`.

### 6.2 Journey dimensions

```text
journey_dimension
  journey_dimension_id
  dimension_code        # CUSTOMER_LIFECYCLE | SERVICE_REQUEST_LIFECYCLE
  dimension_name

journey_stage
  journey_stage_id
  journey_dimension_id
  stage_code
  stage_name
  sort_order

journey_step
  journey_step_id
  journey_dimension_id
  journey_stage_id        # nullable; required only for CUSTOMER_LIFECYCLE
  step_code
  step_name
  sort_order

journey_service_map
  journey_step_id
  service_id
  relationship_type
  is_primary_candidate
  valid_from_release_id
  valid_to_release_id
```

Customer Lifecycle Step bắt buộc có `journey_stage_id`; Service Request Step thuộc trực tiếp `SERVICE_REQUEST_LIFECYCLE` và có `journey_stage_id = null`. `journey_stage_id` ở runtime được derive từ `journey_step_id`; nếu API nhận cả hai thì phải validate cùng một hierarchy.

### 6.3 Service và Issue

```text
service
  service_id
  service_code
  service_name
  description
  default_operational_severity # SEV-1..SEV-4; fallback khi Issue không có override
  criticality

issue_family             # optional roll-up cho symptom giống nhau ở nhiều service
  issue_family_id
  issue_family_code
  issue_family_name

issue
  issue_id
  issue_code
  service_id
  issue_family_id        # nullable
  issue_name
  description
  issue_type             # CUSTOMER_SYMPTOM | PROCESS_FAILURE | TECHNICAL_ALERT | DERIVED_KPI
  operational_severity_override # ưu tiên hơn service.default_operational_severity khi có giá trị
  safety_critical
```

Trong pilot, một Issue thuộc đúng một Service. Các symptom có wording giống nhau nhưng khác routing có thể là các Issue khác nhau và cùng trỏ về một `issue_family` để reporting không bị phân mảnh.

### 6.4 Cause atomic và mapping

```text
cause_group
  cause_group_id
  cause_group_code       # CG01–CG17; CG18 không materialize như cause
  cause_group_name

cause
  cause_id
  cause_code             # ví dụ CAUSE-000123
  cause_group_id
  cause_name             # một hypothesis atomic
  description
  required_evidence

issue_cause_map
  issue_id
  cause_id
  relationship_type      # CANDIDATE | COMMON | EXCLUDED
  display_rank
  prior_weight           # nullable; chỉ dùng khi có nguồn/calibration
  evidence_source
  valid_from_release_id
  valid_to_release_id
```

Không tạo `cause` cho `UNKNOWN`. Classification runtime chỉ cho ghi `cause_determination_status = NOT_ASSESSED | UNKNOWN | SUGGESTED | UNDER_INVESTIGATION`. `CONFIRMED` không phải classification write value; nó chỉ được derive/read từ `root_cause_finding` có investigation, evidence và authorized confirmer.

### 6.5 Organization, Location và Channel

```text
org_unit
  org_unit_id
  org_unit_code
  org_unit_name
  parent_org_unit_id

service_unit_assignment
  service_id
  org_unit_id
  assignment_role        # OWNER | DEFAULT_RESOLVER | ESCALATION
  location_id            # nullable scope override
  valid_from_release_id
  valid_to_release_id

location
  location_id
  location_code
  location_type          # PROJECT | BUILDING | TOWER | FLOOR | UNIT | ZONE
  parent_location_id
  timezone

interaction_channel
  interaction_channel_id
  channel_code
  channel_name
```

### 6.6 Alias, synonym và localization

```text
taxonomy_alias
  taxonomy_alias_id
  entity_type            # SERVICE | ISSUE | CAUSE | JOURNEY_STEP | CHANNEL
  entity_id
  alias_text
  normalized_alias
  locale
  alias_type             # SYNONYM | LEGACY_CODE | ABBREVIATION | SEARCH_TERM
  valid_from_release_id
  valid_to_release_id
```

`synonyms` không lưu dưới dạng chuỗi phân tách bằng dấu phẩy trong bảng Issue. Search phải hỗ trợ tiếng Việt có dấu/không dấu nhưng vẫn giữ nguyên original text để audit.

### 6.7 Runtime: Feedback Item, Prediction và Decision

Runtime pilot dùng `feedback_item` làm đơn vị phân loại/analytics. `feedback` là envelope nguồn bất biến; mô hình `observation` tổng quát cho ticket/alert/work order chỉ được bổ sung ở phase sau, không thay đổi contract dưới đây.

```text
feedback
  feedback_id
  source_type
  source_reference
  raw_text
  reported_at
  ingested_at
  source_location_text
  intake_channel_id

feedback_affected_channel
  feedback_id
  interaction_channel_id

feedback_item
  feedback_item_id
  feedback_id
  item_index
  item_text_masked
  status
  analytic_eligibility

prediction_run
  prediction_run_id
  feedback_item_id
  taxonomy_release_id
  classification_source  # AI | RULE
  model_version
  prompt_or_rule_version
  created_at

classification_prediction
  prediction_id
  prediction_run_id
  field_name
  candidate_value_id
  rank
  confidence
```

Decision đã áp dụng là immutable snapshot riêng; prediction không tự trở thành decision:

```text
classification_decision
  classification_decision_id
  feedback_item_id
  decision_version
  taxonomy_release_id
  decision_source         # MANUAL | SOURCE_TRUSTED | HUMAN_ACCEPTED_AI | HUMAN_CORRECTED_AI | POLICY_AUTO_APPLIED | SYSTEM_MIGRATION
  customer_lifecycle_value_status
  customer_lifecycle_step_id
  service_request_value_status
  service_request_step_id
  primary_service_value_status
  primary_service_id
  issue_value_status
  issue_id
  sentiment
  operational_severity
  location_value_status
  location_id
  cause_determination_status
  reason
  decided_by
  decided_at
  supersedes_decision_id

classification_decision_secondary_service
  classification_decision_id
  service_id

classification_decision_candidate_cause
  classification_decision_id
  cause_id
  confidence
  suggestion_status       # SUGGESTED | ACCEPTED_FOR_INVESTIGATION | REJECTED

classification_decision_prediction_ref
  classification_decision_id
  prediction_id

review_event
  review_event_id
  prediction_id              # nullable
  classification_decision_id # nullable; Skip có thể không tạo decision
  action
  reason_code
  actor_id
  created_at

classification_current   # rebuildable read projection
  feedback_item_id
  current_decision_id
  projection_version
  updated_at
```

`review_event` phải tham chiếu ít nhất một `prediction_id` hoặc `classification_decision_id`. `SKIP` không tạo decision; `ACCEPT/CORRECT/UNKNOWN` tạo decision version mới khi làm thay đổi accepted classification.

Mỗi decision có tối đa một primary Service và tối đa một step trong mỗi lifecycle dimension; field có thể chưa biết dùng companion `*_value_status = KNOWN | UNKNOWN | MISSING | NOT_APPLICABLE`. `KNOWN` yêu cầu ID hợp lệ, các status còn lại yêu cầu ID null. Secondary Service/Candidate Cause nằm ở child relation. `feedback_classification` cũ, nếu cần tương thích API, chỉ là read view trên `classification_current`; không dùng làm source-of-truth có thể overwrite.

### 6.8 Investigation và RCA

```text
investigation_case
evidence
root_cause_finding
corrective_action
preventive_action
```

`root_cause_finding` phải tham chiếu investigation, evidence và người có thẩm quyền xác nhận. Candidate-cause prediction/suggestion không được tự động chuyển thành confirmed root cause.

---

## 7. Operational Severity Baseline

| Legacy Priority | Canonical Severity | Ý nghĩa baseline | Ví dụ |
| --------------- | ------------------ | ---------------- | ----- |
| P1 | `SEV-1` | Critical / safety / building-wide / immediate dispatch | cháy, mắc kẹt thang máy, mất điện/nước diện rộng, nguy cơ an toàn |
| P2 | `SEV-2` | High impact hoặc ảnh hưởng nhiều cư dân / cần xử lý nhanh | water pressure, access failure, defect nghiêm trọng, SLA major |
| P3 | `SEV-3` | Medium / ảnh hưởng cục bộ / không nguy hiểm tức thời | booking, parking admin, cleaning, app function |
| P4 | `SEV-4` | Low / information / cosmetic / improvement | content, landscaping cosmetic, general information |

`P1–P4` chỉ tồn tại trong các bảng legacy/pilot source để bảo toàn dữ liệu nguồn và phải được importer map sang `SEV-1–SEV-4`. Delivery dùng `MVP`, `Delivery Phase 1`, `Delivery Phase 2`; API/domain model không dùng field mơ hồ tên `priority`.

Priority precedence:

```text
Hard trigger / safety rule
    > approved human override
    > Issue.operational_severity_override
    > Service.default_operational_severity
```

Priority thực tế phải được tính lại bằng matrix `Impact × Urgency` cộng hard trigger. Trước production phải chốt enum Impact/Urgency, threshold, hard-trigger catalog, `priority_source` và `override_reason`; không suy diễn actual priority chỉ từ default trong taxonomy.

---

## 8. AI Classification Policy

### Pilot policy: suggest-only

Trong Draft / Pilot Baseline, **mọi output của AI đều là suggestion**, bất kể confidence. Confidence chỉ dùng để sắp xếp review queue; không tự cấp quyền auto-apply.

| Output                                  | Hành vi trong pilot                                      |
| --------------------------------------- | --------------------------------------------------------- |
| Journey, service, issue, sentiment      | Suggest-only; human/rule decision mới là source-of-truth  |
| Priority                                | Suggest-only; hard trigger và approved matrix quyết định  |
| Candidate cause                         | Suggest-only cho investigation checklist                 |
| Safety/legal responsibility             | Bắt buộc manual review/escalation                         |
| Confirmed Root Cause                    | AI không được phép xác nhận                               |

### Điều kiện trước khi cho phép auto-apply

Auto-apply chỉ được xem xét trong một release sau khi có đủ tất cả điều kiện:

1. Gold/holdout dataset đã được domain owner phê duyệt và tách khỏi training data.
2. Confidence được calibration riêng theo từng output/label; không dùng một threshold chung cho journey, service và issue.
3. Có precision/recall floor, minimum sample size và allowlist label low-risk được phê duyệt.
4. Safety/legal/hard-trigger labels luôn nằm ngoài allowlist.
5. Có shadow run, drift monitoring, review sampling, audit log và rollback switch.
6. Threshold, model version, prompt/rule version và taxonomy release được version cùng nhau.

### MVP delivery scope

AI có thể **gợi ý**:

```text
customer_lifecycle_step
service_request_step
primary_service
issue
sentiment
```

### Delivery Phase 1 (sau MVP)

AI có thể mở rộng suggestion cho:

```text
priority
secondary_service
candidate_cause
handling_unit
duplicate_cluster
```

---

## 9. Hotspot Dimensions

Hotspot MVP:

```text
Service
+ Issue
+ Location
+ Time window
```

Delivery Phase 1 mở rộng:

```text
+ Asset
+ Journey Step
+ Semantic similarity
+ Recurrence
+ SLA risk
```

---

## 10. Research References

Các nguồn này dùng để kiểm chứng phạm vi service/touchpoint và nguyên tắc technical facilities; taxonomy chi tiết vẫn cần được xác nhận bằng SOP nội bộ, hợp đồng vận hành, asset list và dữ liệu ticket thực tế.

- Vinhomes — Thẻ cư dân, quyền ra vào/thang máy/tiện ích: https://vinhomes.vn/vi/the-cu-dan-vinhomes
- Vinhomes Smart City — Face ID, phân tầng thang máy, vận hành thông minh: https://smartcity.vinhomes.vn/thanh-pho-thong-minh/
- Vinhomes — Thanh toán hóa đơn trên V-App: https://vinhomes.vn/vi/thanh-toan-hoa-don-tren-v-app-hoan-vpoint-sieu-hap-dan
- IBM — Facility maintenance, electrical/HVAC/plumbing/security/groundskeeping: https://www.ibm.com/think/topics/facility-maintenance
- KONE — Condition monitoring/predictive elevator maintenance: https://origin-www.kone.com/en/products-and-services/maintenance-and-modernization/24-7-connected-services.aspx

---

## 11. Validation Required Before Production

Trước khi khóa taxonomy v1.0 production cần workshop với:

- BQL / Building Manager
- MEP / Technical
- Security
- Housekeeping
- Parking
- Amenities
- Resident Service / CSKH
- Digital / IT
- Finance
- Warranty / Handover
- Sales / Transaction
- Legal
- Data / AI

Mỗi service owner cần xác nhận:

```text
Service owner
Issue definitions
Issue synonyms
Candidate causes
Handling unit
Default priority
SLA
Hard trigger
Required evidence
Asset mapping
```

Ngoài nội dung nghiệp vụ, workshop phải chốt các decision boundary dễ nhầm giữa business service và channel/platform, ví dụ `APP-07` với `AMN-01`, `FIN-04` với `BILL-03`, `ELV-09` với `CLN-02`. Mỗi Issue cần có tối thiểu definition, inclusion examples, exclusion examples và escalation/hard-trigger rule.

Production release chỉ được publish khi:

- owner của mọi active Service đã approve;
- mọi active Issue có owner/routing hợp lệ;
- cause dùng trong mapping đã được atomize và có evidence requirement phù hợp;
- location/org/channel master đã được map cho phạm vi pilot;
- validation và CI invariants ở section 14 đều pass;
- migration dry-run và rollback plan đã được kiểm chứng.

---

## 12. Taxonomy Versioning and Change Control

### Quy tắc version

- `PATCH`: sửa typo/format hoặc bổ sung alias không đổi meaning/routing. Ví dụ sửa một invalid cause-group reference về code đã được định nghĩa.
- `MINOR`: thêm Service/Issue/Cause/Journey/Channel tương thích ngược hoặc bổ sung mapping không làm mất code cũ.
- `MAJOR`: merge/split entity, đổi meaning, đổi primary-service decision rule, xóa contract hoặc thay đổi khiến historical classification phải remap.
- Public code và immutable ID không được tái sử dụng, kể cả sau khi entity retired.
- Rename giữ nguyên ID/code và tạo revision/alias. Merge/split phải có `taxonomy_supersession_map` với transformation rule; không rewrite historical decision.
- Mỗi release có changelog, approver, effective time và source checksum. Chỉ một release `PUBLISHED` có hiệu lực cho cùng scope/time; draft không được phục vụ production API mặc định.
- Runtime decision luôn giữ `taxonomy_release_id`. Reporting phải hỗ trợ cả `as_classified` và `mapped_to_current_release`.

### Governance workflow

```text
Draft change
    → automated validation
    → domain-owner review
    → data/AI impact review
    → APPROVED
    → migration dry-run
    → PUBLISHED
    → monitor / rollback or RETIRED
```

Mọi thay đổi ảnh hưởng training label, routing, SLA, safety hoặc legal phải có explicit approval; không publish chỉ dựa trên pull-request merge.

---

## 13. Migration and Publication Rules

1. Chuyển nguồn Markdown/workbook thành structured seed (`CSV`, `JSON` hoặc migration fixture) có schema và checksum; Markdown không phải runtime database.
2. Nạp seed vào staging tables, không upsert trực tiếp vào release đang published.
3. Validator resolve toàn bộ service, journey, org, location, channel và atomic cause references. `CG18 unknown` được chuyển thành runtime state/ghi chú, không thành `issue_cause_map`.
4. Tạo diff theo entity: add, rename, retire, merge, split, mapping change, priority change và routing change.
5. Domain owner review diff và Data/AI review impact tới label distribution, training set, search index và dashboard.
6. Publish toàn bộ release trong một transaction; nếu bất kỳ invariant nào fail thì rollback toàn bộ.
7. Với dữ liệu lịch sử, giữ `raw_source_label`, `original_taxonomy_release_id` và decision gốc. Dùng alias/crosswalk để tạo mapping view; không overwrite audit history.
8. Label cũ không map chắc chắn phải vào `UNMAPPED_FOR_REVIEW`, không ép vào Issue gần nhất. Split 1:N luôn cần rule hoặc human review.
9. Chạy dual-read/shadow classification trong pilot, so sánh coverage, unknown rate, confusion pairs, reviewer agreement và hotspot continuity trước cutover.
10. Cache/search index phải mang release ID và được invalidate nguyên tử cùng publication.

---

## 14. CI Invariants

Các invariant dưới đây là release-blocking và phải chạy tự động trên structured seed lẫn migration output:

### Identity và referential integrity

- Mọi code unique theo entity type, đúng regex đã công bố và không trùng code đã retired.
- Mọi FK/mapping resolve tới entity tồn tại trong cùng release/effective window; không có orphan Service, Issue, Journey, Cause, Org, Location hoặc Channel.
- Mỗi Issue thuộc đúng một Service trong pilot; Issue trong decision phải thuộc primary Service.
- Mọi step thuộc đúng một dimension; Customer Lifecycle Step thuộc đúng một stage, còn Service Request Step không có stage. Stage runtime phải được derive/validate từ step.
- Không có validity range chồng lấn cho cùng entity/scope.

### Source-table integrity

- Release pilot này phải có đúng 34 services và 217 issue rows; số metadata phải khớp dữ liệu parse được.
- Issue row number liên tục, Issue Code unique, Service Code hợp lệ và priority chỉ thuộc `P1–P4`.
- Mọi `Journey Step refs` tồn tại trong dictionary. Cột derived Handling Unit/Journey refs ở bảng Issue phải khớp Service Catalog.
- Mọi cause group token phải thuộc `CG01–CG18`; production mapping chỉ nhận atomic `cause_code` thuộc `CG01–CG17`.
- `CG18/UNKNOWN` không được materialize thành cause, không được đồng thời tính cùng suggested/confirmed cause và không được đưa vào RCA aggregation.
- Alias normalized không được trỏ tới nhiều active entity cùng type/scope nếu chưa có disambiguation rule.

### Runtime decision integrity

- Một decision có `primary_service_value_status`; `KNOWN` yêu cầu đúng một primary Service, còn status khác yêu cầu ID null. Secondary Service là 0:N và không có duplicate/primary-secondary overlap.
- Tối đa một journey step cho mỗi journey dimension; Customer Lifecycle và Service Request Lifecycle có thể cùng tồn tại.
- Confidence nằm trong `[0,1]` và được lưu riêng theo từng prediction, không dùng một confidence chung cho toàn classification.
- Prediction không được overwrite decision; mọi accept/reject/override tạo audit event.
- Classification command không được ghi `cause_determination_status=CONFIRMED`; confirmed state chỉ được project từ valid `root_cause_finding`.
- Safety/legal/hard-trigger record bắt buộc manual review/escalation theo policy.
- AI/candidate-cause suggestion không được tạo `root_cause_finding` nếu thiếu investigation, evidence và authorized confirmer.
- Mọi runtime decision pin một `taxonomy_release_id` đã published/effective tại thời điểm decision, hoặc ghi rõ lý do import lịch sử.

### Migration safety

- Migration phải idempotent trên staging, có dry-run diff, transaction boundary và tested rollback.
- Merge/split/retire bắt buộc có supersession/crosswalk; không được silently delete code đang được historical record tham chiếu.
- Search index, API cache và reporting bridge phải được build/test cho release mới trước cutover.
