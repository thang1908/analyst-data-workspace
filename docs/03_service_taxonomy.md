# 03 — Taxonomy Dịch vụ (Service Taxonomy)

- **Dự án:** CX Intelligence & Operations Platform
- **Phiên bản taxonomy:** 3.0.1 (active) · 3.0.0 (historical, immutable)
- **Phiên bản tài liệu:** 3.1.0 — cập nhật khớp DB migration 016, 018, 019
- **Quy mô:** 10 Service / 28 Issue / 6 Stage / 36 Step / 8 Service Request Step / Touchpoints
- **Nguồn truth duy nhất:** `alembic/versions/016_seed_taxonomy_v3.py` + `018` + `019`

> Taxonomy phục vụ phân loại và điều phối. Không xác lập trách nhiệm pháp lý, bảo hành hoặc phần sở hữu chung-riêng.

---

## 1. Mô hình Phân loại

```
Feedback Envelope
  ├── source_system (tên hệ thống nguồn)
  └── intake_channel_id (kênh tiếp nhận)
        ↓ 1:N
Feedback Item (atomic observation)
  ├── Customer Lifecycle Stage / Step    0:1
  ├── Touchpoint                         0:1  ← MỚI (migration 019)
  ├── Service Request Step               0:1
  ├── Primary Service                    0:1
  ├── Canonical Issue                    0:1  (thuộc Primary Service)
  ├── Location                           0:1
  ├── Affected Channel                   0:N
  └── symptom_detail + evidence
```

### Quy tắc bắt buộc

1. Một `feedback_item` chứa đúng 1 customer intent hoặc 1 observable failure. Multi-intent → bắt buộc `split`.
2. Khi `Primary Service` và `Issue` đều `KNOWN`: Issue phải thuộc Primary Service đó trong cùng taxonomy release.
3. Không tạo Service/Issue mới chỉ vì khác location, channel, source system hoặc vendor.
4. `SV-10/IS-10-01` chỉ dùng khi nội dung đã rõ nhưng không thuộc SV-01..SV-09; bắt buộc có `other_reason` và `review`.
5. Hard trigger SEV-1/safety không chờ classifier.
6. AI không tự xác nhận Root Cause, warranty eligibility hoặc legal responsibility.

---

## 2. Customer Lifecycle — 6 Stage / 36 Step

> **v3.0.1 dashboard labels** (ngắn hơn v3.0.0, dùng trên UI; code & định nghĩa không đổi)

### Stage A — Nhận thức (Awareness)

| Code | v3.0.0 name | v3.0.1 label (dashboard) |
|---|---|---|
| A1 | Tiếp cận thương hiệu/dự án | Biết đến dự án |
| A2 | Khám phá nội dung & thông tin ban đầu | Tìm hiểu ban đầu |
| A3 | Nhận giới thiệu / tham gia hoạt động quảng bá | Giới thiệu & ưu đãi |

### Stage C — Xem xét (Consideration)

| Code | v3.0.0 name | v3.0.1 label |
|---|---|---|
| C1 | Tìm hiểu dự án & sản phẩm | Tìm hiểu dự án |
| C2 | Đánh giá vị trí, thiết kế & tiện ích | Đánh giá sản phẩm |
| C3 | Xem quỹ căn & so sánh lựa chọn | Chọn căn |
| C4 | Đánh giá pháp lý, giá & chính sách | Giá & chính sách |
| C5 | Đánh giá khả năng tài chính | Khả năng tài chính |
| C6 | Nhận tư vấn & tham quan | Tư vấn & tham quan |

### Stage TR — Giao dịch (Transaction)

| Code | v3.0.0 name | v3.0.1 label |
|---|---|---|
| TR-01 | Yêu cầu giữ căn hoặc gửi booking | Giữ chỗ |
| TR-02 | Xác minh khách hàng & hồ sơ | Xác minh hồ sơ |
| TR-03 | Đặt cọc & xác nhận giao dịch | Đặt cọc |
| TR-04 | Chọn phương án tài chính & thanh toán | Chọn phương án tài chính |
| TR-05 | Ký hợp đồng mua bán | Ký hợp đồng |
| TR-06 | Thực hiện nghĩa vụ & thay đổi sau ký | Thay đổi sau ký |

### Stage HO — Nhận nhà (Handover)

| Code | v3.0.0 name | v3.0.1 label |
|---|---|---|
| HO-01 | Nhận thông báo & chuẩn bị bàn giao | Chuẩn bị nhận nhà |
| HO-02 | Đặt lịch & làm thủ tục bàn giao | Thủ tục nhận nhà |
| HO-03 | Kiểm tra & nghiệm thu căn | Kiểm tra căn |
| HO-04 | Ghi nhận tồn tại / yêu cầu khắc phục | Ghi nhận lỗi |
| HO-05 | Hoàn tất nhận nhà & hồ sơ | Hoàn tất nhận nhà |

### Stage RES — Cư trú (Residence)

| Code | v3.0.0 name | v3.0.1 label |
|---|---|---|
| RES-01 | Thiết lập hồ sơ & quyền cư dân | Hồ sơ cư dân |
| RES-02 | Sử dụng hệ thống & kênh cư dân | Ứng dụng & kênh cư dân |
| RES-03 | Ra vào & di chuyển | Ra vào & di chuyển |
| RES-04 | Tiếp khách | Tiếp khách |
| RES-05 | Sử dụng tiện ích & dịch vụ | Tiện ích cư dân |
| RES-06 | Thanh toán phí & nghĩa vụ cư trú | Phí & thanh toán |
| RES-07 | Gửi yêu cầu / phản ánh / sự cố | Yêu cầu & phản ánh |
| RES-08 | Thực hiện thay đổi liên quan căn hộ | Thay đổi căn hộ |

### Stage OPS — Vận hành (Operations)

| Code | v3.0.0 name | v3.0.1 label | Nội dung |
|---|---|---|---|
| OPS-01 | Tiếp nhận & huy động vận hành | Tiếp nhận vận hành | Hồ sơ O&M, asset register, warranty, hợp đồng, vendor readiness |
| OPS-02 | Lập kế hoạch, ngân sách & nguồn lực | Kế hoạch & nguồn lực | Service standard, ngân sách, bảo trì, SLA |
| OPS-03 | Vận hành thường nhật & giám sát | Vận hành & giám sát | Control room, tuần tra, BMS, utilities, access |
| OPS-04 | Kiểm tra, thử nghiệm & bảo trì định kỳ | Kiểm tra & bảo trì | Preventive/predictive maintenance, kiểm định |
| OPS-05 | Chẩn đoán, sửa chữa & khôi phục | Sửa chữa & khôi phục | Work order, cô lập, sửa/thay, thử chức năng |
| OPS-06 | Ứng phó sự cố, khẩn cấp & duy trì liên tục | Ứng phó khẩn cấp | Triage, dispatch, containment, sơ tán, recovery |
| OPS-07 | Xác minh, tuân thủ & đánh giá hiệu suất | Tuân thủ & hiệu suất | Nghiệm thu, audit, SLA/KPI, vendor performance |
| OPS-08 | Cải tiến, đổi mới & chuyển giao | Cải tiến vận hành | RCA/CAPA, tối ưu, capital works |

---

## 3. Service Request Lifecycle — 8 Step

| Code | Tên VI | Tên EN |
|---|---|---|
| SRV-01 | Tìm thông tin | Find Information |
| SRV-02 | Gửi yêu cầu | Submit Request |
| SRV-03 | Xác nhận/phê duyệt | Confirm / Approve |
| SRV-04 | Thanh toán | Payment |
| SRV-05 | Được phục vụ | Service Delivered |
| SRV-06 | Theo dõi/escalate | Track / Escalate |
| SRV-07 | Hoàn tất | Complete |
| SRV-08 | Đánh giá | Rate & Review |

---

## 4. Interaction Channels — 8 kênh

> Code trong DB dùng chữ thường `ch-xxx`. Tài liệu cũ dùng `CH-XXX` — đã thống nhất theo DB.

| DB Code | Tên VI | Tên EN |
|---|---|---|
| ch-app | Ứng dụng di động | Mobile App |
| ch-web | Website/Portal | Website / Portal |
| ch-hotline | Hotline/Call Center | Hotline / Call Center |
| ch-email | Email | Email |
| ch-frontdesk | Quầy lễ tân/Service Desk | Front Desk / Service Desk |
| ch-social | Mạng xã hội/Messaging | Social Media / Messaging |
| ch-inperson | In-person/Site Visit | In-person / Site Visit |
| ch-system | Machine/System event | Machine / System Event |

> `source_system` (CRM, ERP, BMS, CMMS, sensor feed) **không** phải Channel.

---

## 5. Danh mục 10 Dịch vụ (Service Catalog)

### Nhãn theo phiên bản taxonomy

| Code | v3.0.0 (full name) | v3.0.1 (dashboard label) | Default SEV | Định nghĩa kết quả |
|---|---|---|---|---|
| SV-01 | Thông tin, bán hàng & giao dịch | Thông tin & giao dịch | SEV-4 | Khách hàng nhận thông tin chính xác, hoàn tất giao dịch và ký kết hợp đồng |
| SV-02 | Tài chính mua nhà, bàn giao & bảo hành | Tài chính, bàn giao & bảo hành | SEV-3 | Khách hàng hoàn tất nghĩa vụ tài chính, nhận nhà đúng tiêu chuẩn và được bảo hành |
| SV-03 | Hồ sơ, hỗ trợ & trải nghiệm số cư dân | Hồ sơ & hỗ trợ cư dân | SEV-4 | Cư dân có hồ sơ chính xác, truy cập nền tảng số và nhận hỗ trợ kịp thời |
| SV-04 | Hóa đơn, phí & thanh toán cư dân | Hóa đơn & thanh toán | SEV-3 | Cư dân nhận hóa đơn chính xác và thanh toán thành công |
| SV-05 | Ra vào, khách, bãi xe & di chuyển | Ra vào & bãi xe | SEV-2 | Cư dân và khách ra vào, đỗ xe và di chuyển nội khu an toàn |
| SV-06 | Tiện ích, cải tạo & chuyển nhà | Tiện ích & chuyển nhà | SEV-4 | Cư dân sử dụng tiện ích, thực hiện cải tạo và chuyển nhà đúng quy trình |
| SV-07 | Kỹ thuật, tiện ích & tài sản chung | Kỹ thuật & tài sản chung | **SEV-1** | Hệ thống kỹ thuật và tài sản chung hoạt động liên tục, an toàn |
| SV-08 | An ninh, PCCC & khẩn cấp | An ninh & khẩn cấp | **SEV-1** | Tài sản và con người được bảo vệ; sự cố phát hiện và xử lý kịp thời |
| SV-09 | Vệ sinh, môi trường & cảnh quan | Vệ sinh & cảnh quan | SEV-3 | Môi trường sạch, an toàn vệ sinh và cảnh quan được duy trì đúng tiêu chuẩn |
| SV-10 | Khác | Khác | SEV-4 | Nội dung rõ nhưng không thuộc SV-01..SV-09; bắt buộc có other_reason và review |

---

## 6. Danh mục 28 Vấn đề (Issue Catalog)

> Cột "🔴 Safety" = `safety_critical = true` trong DB → kích hoạt hard trigger

### SV-01 — Thông tin & giao dịch (3 issues)

| Code | Tên đầy đủ (v3.0.0) | Dashboard label (v3.0.1) | 🔴 Safety | Phạm vi |
|---|---|---|---|---|
| IS-01-01 | Thông tin thiếu hoặc không chính xác | Thông tin sai hoặc thiếu | | Project, product, legal, policy, price hoặc content unavailable/stale |
| IS-01-02 | Tư vấn, tham quan hoặc giữ chỗ không đạt | Tư vấn, tham quan & giữ chỗ | | Contact, appointment, availability, booking, duplicate hoặc confirmation |
| IS-01-03 | Hồ sơ hoặc giao dịch không hoàn tất | Hồ sơ/giao dịch chưa hoàn tất | | KYC, document, contract data, e-sign, amendment hoặc transfer |

### SV-02 — Tài chính, bàn giao & bảo hành (3 issues)

| Code | Tên đầy đủ | Dashboard label | 🔴 Safety | Phạm vi |
|---|---|---|---|---|
| IS-02-01 | Tài chính hoặc quyết toán mua nhà có vấn đề | Tài chính & quyết toán | | Loan, payment, allocation, due amount, adjustment hoặc refund |
| IS-02-02 | Bàn giao hoặc nghiệm thu không đạt | Bàn giao & nghiệm thu | | Readiness, schedule, inspection, area, defect capture hoặc acceptance |
| IS-02-03 | Bảo hành hoặc khắc phục không đạt | Bảo hành & khắc phục | | Scope unclear, delay, ineffective repair, recurrence hoặc invalid closure |

### SV-03 — Hồ sơ & hỗ trợ cư dân (3 issues)

| Code | Tên đầy đủ | Dashboard label | 🔴 Safety | Phạm vi |
|---|---|---|---|---|
| IS-03-01 | Hồ sơ hoặc quyền cư dân sai | Hồ sơ hoặc quyền cư dân | | Household/unit/profile/role/account status |
| IS-03-02 | Nền tảng số hoặc case handling lỗi | Nền tảng số & case | | Login, OTP, crash, API, missing/duplicate case, wrong owner, premature closure |
| IS-03-03 | Hỗ trợ hoặc truyền thông không đạt | Hỗ trợ & truyền thông | | Response, audience, timing, clarity, follow-up hoặc notification |

### SV-04 — Hóa đơn & thanh toán (3 issues)

| Code | Tên đầy đủ | Dashboard label | 🔴 Safety | Phạm vi |
|---|---|---|---|---|
| IS-04-01 | Hóa đơn hoặc phí sai | Hóa đơn hoặc phí sai | | Tariff, amount, penalty hoặc duplicate |
| IS-04-02 | Thanh toán hoặc ghi nhận thất bại | Thanh toán/ghi nhận thất bại | | Gateway, bank, callback, reference, allocation hoặc reconciliation |
| IS-04-03 | Điều chỉnh hoặc hoàn tiền chậm | Điều chỉnh/hoàn tiền chậm | | Adjustment, deposit settlement, refund hoặc document issuance delay |

### SV-05 — Ra vào & bãi xe (3 issues)

| Code | Tên đầy đủ | Dashboard label | 🔴 Safety | Phạm vi |
|---|---|---|---|---|
| IS-05-01 | Ra vào hoặc hành trình khách thất bại | Ra vào hoặc tiếp khách | | Card, Face ID, floor permission, intercom, registration hoặc check-in |
| IS-05-02 | Dịch vụ bãi xe không đạt | Bãi xe | | LPR, barrier, entitlement, capacity, congestion hoặc availability |
| IS-05-03 | Di chuyển nội khu không đạt | Di chuyển nội khu | | Route, stop, schedule, realtime information, missed trip hoặc capacity |

### SV-06 — Tiện ích & chuyển nhà (3 issues)

| Code | Tên đầy đủ | Dashboard label | 🔴 Safety | Phạm vi |
|---|---|---|---|---|
| IS-06-01 | Tiện ích không đặt hoặc sử dụng được | Đặt hoặc dùng tiện ích | | Booking, slot, eligibility, admission, opening status hoặc equipment |
| IS-06-02 | Phê duyệt hoặc kiểm soát cải tạo không đạt | Phê duyệt cải tạo | | Dossier, approval, contractor, schedule, access, noise hoặc damage assessment |
| IS-06-03 | Chuyển vào/chuyển ra không đạt | Chuyển vào/chuyển ra | | Registration, loading bay, freight lift, vehicle, contractor hoặc logistics |

### SV-07 — Kỹ thuật & tài sản chung (3 issues)

| Code | Tên đầy đủ | Dashboard label | 🔴 Safety | Phạm vi |
|---|---|---|---|---|
| IS-07-01 | Hệ thống ngừng hoặc suy giảm | Hệ thống suy giảm | | Elevator, water, electrical, generator, HVAC outage/performance/quality |
| IS-07-02 | Rò rỉ hoặc điều kiện kỹ thuật nguy hiểm | Rò rỉ/rủi ro kỹ thuật | 🔴 | Leak, blockage, flooding, entrapment, abnormal stop, overheat, burning smell |
| IS-07-03 | Tài sản chung hoặc bảo trì không đạt | Tài sản chung & bảo trì | | Fabric defect, preventive/capital work, inspection, vendor/compliance record |

### SV-08 — An ninh & khẩn cấp (3 issues)

| Code | Tên đầy đủ | Dashboard label | 🔴 Safety | Phạm vi |
|---|---|---|---|---|
| IS-08-01 | Sự kiện an ninh | Sự cố an ninh | 🔴 | Unauthorized access, theft, suspicious behavior, disturbance hoặc threat |
| IS-08-02 | Giám sát hoặc phản ứng an ninh thất bại | Giám sát/phản ứng an ninh | | CCTV, hotline, guard, patrol, dispatch hoặc response |
| IS-08-03 | PCCC hoặc sẵn sàng khẩn cấp không đạt | PCCC & khẩn cấp | 🔴 | Fire/smoke, alarm, detection, suppression, egress, evacuation, command |

### SV-09 — Vệ sinh & cảnh quan (3 issues)

| Code | Tên đầy đủ | Dashboard label | 🔴 Safety | Phạm vi |
|---|---|---|---|---|
| IS-09-01 | Vệ sinh hoặc hygiene không đạt | Vệ sinh | | Dirty surface, restroom, supply hoặc spill response |
| IS-09-02 | Rác thải hoặc sinh vật gây hại không được kiểm soát | Rác thải & côn trùng | | Overflow, missed collection, sorting, bulky waste, insect hoặc rodent |
| IS-09-03 | Cảnh quan hoặc phiền nhiễu môi trường | Cảnh quan & môi trường | | Plant, irrigation, unsafe branch, odor hoặc nuisance |

### SV-10 — Khác (1 issue)

| Code | Tên | Dashboard label | Phạm vi |
|---|---|---|---|
| IS-10-01 | Vấn đề khác cần review | Vấn đề khác cần review | Nội dung đủ rõ nhưng ngoài phạm vi 9 Service |

> **Kiểm soát IS-10-01:** Bắt buộc lưu `other_reason` + `raw evidence` + `reviewer`. Không auto-apply bằng AI. Đánh giá hàng tuần; cluster lặp → đề xuất thêm vào taxonomy revision.

---

## 7. Touchpoints (MỚI — Migration 019, Taxonomy 3.0.1)

Touchpoint là điểm tiếp xúc cụ thể giữa cư dân và hệ thống/nhân viên. Mỗi touchpoint gắn với 1 lifecycle step và 1+ service.

> **Lưu ý:** Dữ liệu touchpoint được seed cho cả 2 taxonomy releases (3.0.0 và 3.0.1).

### Stage A — Nhận thức

| Code | Tên VI | Step | Service chính |
|---|---|---|---|
| TP-A1-01 | Xem quảng cáo & mạng xã hội | A1 | SV-01 |
| TP-A1-02 | Biển bảng & sự kiện ngoài trời | A1 | SV-01 |
| TP-A2-01 | Truy cập website & cổng thông tin | A2 | SV-01 |
| TP-A2-02 | Tra cứu online & diễn đàn | A2 | SV-01 |
| TP-A3-01 | Nhận tin nhắn & cuộc gọi tư vấn | A3 | SV-01 |
| TP-A3-02 | Nhận tài liệu sự kiện & ưu đãi | A3 | SV-01 |

### Stage C — Xem xét

| Code | Tên VI | Step | Service chính | Service phụ |
|---|---|---|---|---|
| TP-C1-01 | Xem brochure & sa bàn điện tử | C1 | SV-01 | |
| TP-C2-01 | Khảo sát mặt bằng & tiện ích | C2 | SV-01 | SV-06 |
| TP-C3-01 | Xem bảng hàng & chọn mã căn | C3 | SV-01 | |
| TP-C4-01 | Xem bảng giá & chính sách bán hàng | C4 | SV-01 | SV-02 |
| TP-C5-01 | Tư vấn gói vay & lịch thanh toán | C5 | SV-02 | |
| TP-C6-01 | Tham quan nhà mẫu & dự án thực tế | C6 | SV-01 | |

### Stage TR — Giao dịch

| Code | Tên VI | Step | Service chính | Service phụ |
|---|---|---|---|---|
| TP-TR-01-01 | Nộp phiếu đăng ký giữ chỗ / booking | TR-01 | SV-01 | |
| TP-TR-02-01 | Xác minh định danh & hồ sơ khách | TR-02 | SV-01 | |
| TP-TR-03-01 | Ký thỏa thuận đặt cọc & nộp tiền cọc | TR-03 | SV-01 | SV-02 |
| TP-TR-04-01 | Xác nhận phương án tài chính & giải ngân | TR-04 | SV-02 | |
| TP-TR-05-01 | Ký hợp đồng mua bán tại văn phòng | TR-05 | SV-01 | SV-02 |
| TP-TR-06-01 | Đề nghị chuyển nhượng & sửa đổi sau ký | TR-06 | SV-01 | |

### Stage HO — Nhận nhà

| Code | Tên VI | Step | Service chính | Service phụ |
|---|---|---|---|---|
| TP-HO-01-01 | Nhận thông báo bàn giao & hướng dẫn | HO-01 | SV-02 | |
| TP-HO-02-01 | Làm thủ tục check-in bàn giao | HO-02 | SV-02 | |
| TP-HO-03-01 | Kiểm tra & nghiệm thu căn hộ | HO-03 | SV-02 | SV-07 |
| TP-HO-04-01 | Ghi nhận tồn đọng & hẹn khắc phục | HO-04 | SV-02 | SV-07 |
| TP-HO-05-01 | Nhận bàn giao chìa khóa & hồ sơ căn | HO-05 | SV-02 | SV-03 |

### Stage RES — Cư trú (nhiều touchpoint nhất)

| Code | Tên VI | Step | Service chính | Service phụ |
|---|---|---|---|---|
| TP-RES-01-01 | Đăng ký cư dân & nhân khẩu | RES-01 | SV-03 | |
| TP-RES-02-01 | Gửi yêu cầu & tra cứu trên app | RES-02 | SV-03 | |
| TP-RES-02-02 | Tra cứu tin tức & thông báo BQL | RES-02 | SV-03 | |
| TP-RES-03-01 | Quét thẻ & cổng ra vào tòa nhà | RES-03 | SV-05 | |
| TP-RES-03-02 | Gửi & nhận xe tại bãi | RES-03 | SV-05 | |
| TP-RES-03-03 | Sử dụng thang máy & sảnh chung | RES-03 | SV-05 | SV-07 |
| TP-RES-04-01 | Đăng ký khách & người giao hàng | RES-04 | SV-05 | SV-08 |
| TP-RES-05-01 | Đặt & sử dụng hồ bơi / phòng gym | RES-05 | SV-06 | |
| TP-RES-05-02 | Đăng ký khu BBQ & phòng sinh hoạt | RES-05 | SV-06 | |
| TP-RES-06-01 | Nhận thông báo hóa đơn phí quản lý | RES-06 | SV-04 | |
| TP-RES-06-02 | Thanh toán phí qua app / chuyển khoản | RES-06 | SV-04 | |
| TP-RES-07-01 | Báo lỗi kỹ thuật & thiết bị chung | RES-07 | SV-07 | |
| TP-RES-07-02 | Báo an ninh, tiếng ồn & PCCC | RES-07 | SV-08 | |
| TP-RES-07-03 | Phản ánh vệ sinh & cảnh quan | RES-07 | SV-09 | |
| TP-RES-08-01 | Đăng ký thi công sửa chữa nội thất | RES-08 | SV-06 | SV-07 |
| TP-RES-08-02 | Đăng ký chuyển đồ & chuyển nhà | RES-08 | SV-06 | |

### Stage OPS — Vận hành

| Code | Tên VI | Step | Service chính | Service phụ |
|---|---|---|---|---|
| TP-OPS-01-01 | Tiếp nhận bàn giao tài sản CĐT | OPS-01 | SV-07 | |
| TP-OPS-02-01 | Lập lịch trực & phân bổ ca làm việc | OPS-02 | SV-07 | SV-08 |
| TP-OPS-03-01 | Trực phòng điều khiển & camera an ninh | OPS-03 | SV-08 | |
| TP-OPS-04-01 | Tuần tra định kỳ & bảo dưỡng thiết bị | OPS-04 | SV-07 | |
| TP-OPS-05-01 | Xử lý sự cố kỹ thuật hạ tầng | OPS-05 | SV-07 | |
| TP-OPS-06-01 | Kích hoạt quy trình PCCC & khẩn cấp | OPS-06 | SV-08 | |
| TP-OPS-07-01 | Đánh giá chất lượng dịch vụ nhà thầu | OPS-07 | SV-07 | SV-08, SV-09 |
| TP-OPS-08-01 | Đề xuất cải tiến vận hành & tiện ích | OPS-08 | SV-07 | SV-10 |

---

## 8. Severity & Action Priority

### Operational Severity

| Mức | Baseline |
|---|---|
| SEV-1 | Mối đe dọa tức thì, an toàn tính mạng, sự cố nghiêm trọng toàn tòa nhà hoặc kích hoạt hard trigger |
| SEV-2 | Tác động cao, ảnh hưởng nhiều cư dân hoặc cần phản ứng nhanh |
| SEV-3 | Tác động vận hành cục bộ, không nguy hiểm tức thời |
| SEV-4 | Thông tin, thẩm mỹ hoặc cải tiến |

> Thứ tự ưu tiên: Hard trigger > authorized override > Issue override > Service default

### Action Priority (Hotspot — migration 019)

| Priority | Điều kiện kích hoạt |
|---|---|
| IMMEDIATE | SEV-1 + `safety_critical=true` + `safety_playbook_approved=true` |
| URGENT | SEV-1 (playbook chưa duyệt) hoặc SEV-2 hoặc evidence_count ≥ 10 |
| PLANNED | SEV-3/SEV-4 + evidence_count ≥ 2 |
| MONITOR | Còn lại |

**Hard trigger issues** (safety_critical=true trong DB): IS-07-02, IS-08-01, IS-08-03

---

## 9. Hotspot Clustering

```
Dimension Key = {service_id} : {issue_id} : {location_id | GLOBAL} : {rule_version}
```

Điều kiện tạo Hotspot:
- `evidence_count ≥ N` (default N=3) trong cửa sổ W ngày (default W=7)
- HOẶC: 1 phản ánh SEV-1 safety_critical (Hard Trigger → IMMEDIATE ngay lập tức)

Hotspot Status lifecycle:
```
CANDIDATE → ACKNOWLEDGED → INVESTIGATING → RESOLVED
                                         → DISMISSED
RESOLVED / DISMISSED → REOPENED (→ INVESTIGATING)
```

---

## 10. Governance & CI Invariants

### Release gates (kiểm tra sau mỗi migration seed)

- Đúng **10 Service active** và **28 Issue active**
- SV-01..SV-09: đúng **3 Issue/Service**; SV-10: đúng **1 Issue**
- Đúng **6 Customer Lifecycle Stage** (A, C, TR, HO, RES, OPS)
- Đúng **36 Customer Lifecycle Step** (3+6+6+5+8+8)
- Đúng **8 Service Request Step** (SRV-01..SRV-08)
- Đúng **8 Interaction Channel**
- Code là duy nhất, đúng pattern, không tái sử dụng
- SV-10 có hàng chờ review và theo dõi other_rate

### Code patterns

| Entity | Pattern | Ví dụ |
|---|---|---|
| Service | `^SV-[0-9]{2}$` | SV-07 |
| Issue | `^IS-[0-9]{2}-[0-9]{2}$` | IS-07-02 |
| Touchpoint | `^TP-[A-Z0-9]+-[0-9]{2}-[0-9]{2}$` | TP-RES-07-01 |
| Transaction step | `^TR-[0-9]{2}$` | TR-05 |
| Handover step | `^HO-[0-9]{2}$` | HO-03 |
| Residence step | `^RES-[0-9]{2}$` | RES-07 |
| Operations step | `^OPS-[0-9]{2}$` | OPS-06 |
| Service Request step | `^SRV-[0-9]{2}$` | SRV-03 |
| Channel (DB) | `^ch-[a-z]+$` | ch-app |

---

*Nguồn truth: `alembic/versions/016_seed_taxonomy_v3.py`, `018_publish_dashboard_labels_v301.py`, `019_touchpoints_and_hotspot_action_priority.py`*
