# 07 — Đặc tả UI/UX

> **Cập nhật v2.0 (19/08/2026) — thay đổi so với spec gốc:**
> - **OverviewPage**: Layout 2 hàng — hàng 1: ServiceTaxonomyCard (50%) + ChannelBreakdownCard (50%); hàng 2: PainPointsList + TrendChart. ChannelBreakdownCard mới (donut + legend ngang).
> - **FeedbackExplorerPage**: Default page size = **10** (không phải 50). FeedbackDataTable có minWidth 1250px horizontal scroll. Cột hiển thị: nội dung, khu đô thị, dịch vụ, vấn đề, touchpoint, bước hành trình, cảm xúc, thời gian.
> - **HotspotPage**: Thêm `HotspotDashboard` phía trên HotspotActionQueue — 4 KPI boxes + Donut "Mức độ ưu tiên" + Donut "Trạng thái xử lý" + Bar chart "Top dịch vụ".
> - **Sidebar nav**: "Điểm nóng & Căn nguyên" → **"Điểm nóng"**
> - **Tech stack**: React 18 + Vite 5.1.4 + Recharts 3.10.1 + lucide-react + framer-motion 13 + date-fns 4



# Nền tảng Phân tích Trải nghiệm Khách hàng, Dịch vụ & Nguyên nhân Gốc rễ (CX Journey, Service & Root Cause Intelligence Platform)

> **Bổ sung vận hành (2026-08-17):** Dashboard phải tuân theo cấu trúc stage → step
> → touchpoint → service → issue, các empty state taxonomy và hotspot action priority
> được định nghĩa tại [`08_Operating_Dashboard_Spec.md`](./08_Operating_Dashboard_Spec.md).

**Version:** 2.1  
**Status:** P0 CX-First UI/UX Baseline  
**Scope:** Desktop-first CX Intelligence Platform  
**Primary Users:** CX Manager, CX Analyst, Reviewer, Operations Manager, Pilot Admin  
**Derived from:** `PRD.md` v1.3, `service_taxonomy.md` v3.0.0, `Business_Rules.md` v1.1, `System_Design.md` v1.1, `05_Data_Model.md` v1.1, `06_API_Specification.md` v1.1

---

# 1. Mục đích

Tài liệu này xác định kiến trúc UI/UX cho Nền tảng CX P0 (P0 CX Platform).

Sản phẩm phải thể hiện là một **Nền tảng Phân tích Trải nghiệm Khách hàng (Customer Experience Intelligence Platform)**, chứ không phải là một hệ thống quản lý yêu cầu/vé (ticket-management system).

Giao diện người dùng (UI) phải dẫn dắt người dùng qua chuỗi câu hỏi nghiệp vụ sau:

```text
CX đang tốt hay xấu?
        ↓
Khách hàng gặp khó khăn ở giai đoạn nào?
        ↓
Journey Step nào đang tạo trải nghiệm xấu?
        ↓
Service nào liên quan?
        ↓
Issue / Pain Point nào đang xảy ra?
        ↓
Feedback nào là bằng chứng?
        ↓
Có hình thành Hotspot không?
        ↓
Candidate Cause là gì?
        ↓ [P1]
Confirmed Root Cause và improvement action là gì?
```

Do đó, UI P0 được tổ chức xoay quanh:

```text
CUSTOMER EXPERIENCE
        ↓
CUSTOMER JOURNEY
        ↓
SERVICE & PAIN POINT
        ↓
HOTSPOT & ROOT CAUSE
        ↓
ACTION / IMPROVEMENT
```

Các không gian làm việc vận hành (Operational workspaces) như Feedback Explorer, Review Queue và Imports hỗ trợ luồng phân tích thông minh này nhưng không được coi là các dashboard chính.

---

# 2. Định vị UX Cốt lõi

## 2.1 Định danh Sản phẩm (Product Identity)

Sản phẩm là:

> Một Nền tảng Phân tích & Vận hành CX (CX Intelligence & Operations Platform) kết nối hành trình khách hàng (customer journey), phản hồi khách hàng (customer feedback), sự cố dịch vụ (service failures), điểm nóng (hotspots), nguyên nhân gốc rễ (root causes) và các hành động cải tiến (improvement actions).

Sản phẩm CÓ BẢN CHẤT KHÔNG PHẢI LÀ:

- một hệ thống trợ giúp (helpdesk);
- một hệ thống CRM;
- một ứng dụng quản lý ticket;
- một hệ thống CMMS;
- một dashboard ERP;
- một dashboard theo dõi mạng xã hội (social listening dashboard).

Do đó, UI phải ưu tiên:

1. Customer Experience (Trải nghiệm khách hàng)
2. Customer Journey (Hành trình khách hàng)
3. Pain Point (Điểm đau / Vấn đề)
4. Evidence (Bằng chứng)
5. Root Cause (Nguyên nhân gốc rễ)
6. Improvement (Cải tiến)

thay vì:

```text
Ticket → Status → Assignee
```

---

# 3. Nguyên tắc UX

## UX-001 — Customer Journey là Ống kính Phân tích Chính

Hành trình trải nghiệm khách hàng (Customer Lifecycle) phải hiển thị như một cấu trúc điều hướng và phân tích cấp cao nhất (first-class structure).

Các giai đoạn chuẩn hóa (Canonical stages):

```text
Nhận thức
→ Xem xét
→ Giao dịch
→ Nhận nhà
→ Cư trú
→ Vận hành
```

UI phải cho phép người dùng di chuyển từ Stage → Step → Service → Issue → Feedback.

---

## UX-002 — Bằng chứng Trước khi Nhận định

Người dùng luôn phải có khả năng khoan sâu (drill down) từ thông tin CX tổng hợp xuống các Feedback Items gốc.

Ví dụ:

```text
Negative Rate: 42%
        ↓
Cư trú
        ↓
RES-03 Ra vào & di chuyển
        ↓
SV-07
        ↓
IS-07-01
        ↓
42 Feedback Items
```

Không chỉ số KPI hay Hotspot nào được tồn tại như một chỉ số ngõ cấm (dead-end metric).

---

## UX-003 — Phân biệt Vấn đề Quan sát được với Nguyên nhân

UI phải phân biệt rõ:

```text
Issue
= vấn đề quan sát được / mẫu sự cố (observed problem / failure pattern)

Candidate Cause
= giả thuyết điều tra (investigation hypothesis)

Confirmed Root Cause
= kết luận có bằng chứng xác thực (evidence-backed conclusion)
```

Gợi ý từ AI (AI suggestions) tuyệt đối không được hiển thị như nguyên nhân gốc rễ đã xác nhận (confirmed root cause).

---

## UX-004 — Gợi ý của AI ≠ Sự thật được Chấp nhận

UI phải phân biệt trực quan:

```text
AI Prediction (Dự đoán từ AI)
Human/Source Decision (Quyết định từ Con người/Nguồn)
Current Classification (Phân loại Hiện tại)
```

Các gợi ý từ AI có thể hỗ trợ người duyệt (reviewers) nhưng không được trông như đã tự động chấp nhận.

---

## UX-005 — Vòng đời Khách hàng ≠ Vòng đời Yêu cầu Dịch vụ

UI phải thể hiện hai chiều độc lập:

```text
Customer Lifecycle (Vòng đời Khách hàng)
Service Request Lifecycle (Vòng đời Yêu cầu Dịch vụ)
```

Ví dụ:

```text
Customer Lifecycle:
RES-07 · Gửi yêu cầu / phản ánh / sự cố

Service Request Lifecycle:
SRV-02 · Gửi yêu cầu
```

Giá trị `SRV-*` không bao giờ được xuất hiện bên trong thanh điều hướng Customer Journey.

---

## UX-006 — Phân tích Phải Kể một Câu chuyện

Mỗi dashboard phải trả lời một câu hỏi rõ ràng.

Bốn dashboard P0 gồm:

```text
01 CX Overview
02 Customer Journey
03 Service & Pain Points
04 Hotspot & Root Cause
```

Cùng nhau, chúng tạo thành một câu chuyện phân tích thay vì bốn dashboard rời rạc.

---

## UX-007 — Không gian Làm việc Doanh nghiệp Khung rộng

UI desktop nên sử dụng bố cục doanh nghiệp khung rộng (wide-frame enterprise layout).

Bố cục desktop đề xuất:

```text
Sidebar: 200–240px
Content: phần chiều rộng còn lại
Max content width: không giới hạn hoặc rất rộng
Primary dashboard grid: 12 cột
```

Tránh:

- quá nhiều thẻ (cards) nhỏ;
- widget quá trang trí;
- bố cục kiểu ứng dụng tiêu dùng (consumer-app);
- khoảng trắng quá lớn;
- các thẻ không có mục đích khoan sâu (drill-down).

Ưu tiên:

- bảng phân tích rộng;
- danh sách xếp hạng;
- biểu đồ xu hướng lớn;
- trực quan hóa hành trình (journey visualization);
- bảng bằng chứng đặt song song (side-by-side evidence panels);
- dữ liệu vận hành cô đọng nhưng dễ đọc.

---

# 4. Kiến trúc Thông tin (Information Architecture)

```text
CX PLATFORM

DASHBOARDS
├── 01. CX Overview
├── 02. Customer Journey
├── 03. Service & Pain Points
└── 04. Hotspot & Root Cause

WORKSPACES
├── Feedback Explorer
├── Review Queue
├── Hotspot Investigation
└── Imports

GOVERNANCE
├── Data Quality
├── Taxonomy
└── Audit
```

---

# 5. Khung Ứng dụng Toàn cục (Global Application Shell)

## 5.1 Left Sidebar

Điều hướng đề xuất:

```text
CX Platform

OVERVIEW
  Overview

CUSTOMER EXPERIENCE
  Customer Journey
  Service & Pain Points
  Hotspot & Root Cause

OPERATIONS
  Feedback Explorer
  Review Queue
  Imports

GOVERNANCE
  Data Quality
  Taxonomy
  Audit
```

Ví dụ badge tùy chọn:

```text
Review Queue   128
Hotspots         7
Imports           1
```

---

## 5.2 Top Bar

Bao gồm:

```text
Project Selector
Global Search
Date Context
User / Role
```

Project selector phải thực thi đúng phạm vi được phân quyền (authorized scope).

Ví dụ:

```text
Vinhomes Symphony ▼
```

---

# 6. Mô hình Bộ lọc Toàn cục (Global Filter Model)

Tất cả các dashboard nên chia sẻ một tập bộ lọc thống nhất.

Các bộ lọc chính:

```text
Project
Date Range

Customer Lifecycle Stage
Customer Lifecycle Step

Service Request Step

Primary Service
Issue

Location
Source System
Intake Channel
Affected Channel

Sentiment
Operational Severity
```

Quy tắc phụ thuộc ngữ cảnh:

```text
Stage → thu hẹp Journey Step
Service → thu hẹp Issue
Issue → thuộc về Service đã chọn
Location → bộ chọn phân cấp (hierarchical selector)
```

Các chip bộ lọc phải hiển thị mã cố định (stable code) + nhãn bản địa hóa (localized label).

Ví dụ:

```text
Service:
SV-07 · Kỹ thuật, tiện ích & tài sản chung
```

---

# 7. Dashboard 01 — CX Overview

## 7.1 Mục đích

Trả lời:

> Trải nghiệm khách hàng (Customer Experience) tổng thể đang như thế nào, và đâu là vùng trải nghiệm cần chú ý nhất?

Route:

```text
/overview
```

---

## 7.2 Bố cục Chính

```text
┌───────────────────────────────────────────────────────────────────────────┐
│ CX OVERVIEW                                                               │
│ Global filters                                                            │
├───────────────────────────────────────────────────────────────────────────┤
│ KPI SUMMARY                                                               │
├───────────────────────────────────────────────────────────────────────────┤
│ CUSTOMER JOURNEY                                                          │
├───────────────────────────────────────┬───────────────────────────────────┤
│ EXPERIENCE TREND                      │ TOP PAIN POINTS                   │
├───────────────────────────────────────┴───────────────────────────────────┤
│ EMERGING HOTSPOTS                                                         │
└───────────────────────────────────────────────────────────────────────────┘
```

---

## 7.3 Tóm tắt KPI (KPI Summary)

Thẻ P0:

```text
Negative Rate
Feedback Volume
Active Hotspots
Unknown / Ineligible Rate
```

Các chỉ số phụ tùy chọn:

```text
Unknown Rate
Pending Reviews
Top Service
Top Journey Stage
```

`CX Score` và `CX Health Index` không phải P0 KPI vì chưa có công thức được phê duyệt. Không dùng hai nhãn này trên card, chart, status hoặc navigation P0.

---

## 7.4 Reference Wide-Frame Wireframe

> Wireframe này là **bố cục tham chiếu cho việc triển khai (implementation)**, không phải thiết kế đồ họa cuối cùng (final visual design). Đội ngũ phát triển/thiết kế có thể thay đổi typography, spacing, component styling nhưng phải giữ nguyên thứ bậc thông tin (hierarchy) và logic khoan sâu (drill-down).

```text
┌───────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ CX PLATFORM                                           Project ▼     Last 30 days ▼      Search      User       │
├─────────────────────┬─────────────────────────────────────────────────────────────────────────────────────────┤
│                     │ CX OVERVIEW                                                                                     │
│ Overview            │ Tổng quan trải nghiệm khách hàng toàn hệ thống                                                  │
│                     │                                                                                                  │
│ Customer Journey    │ [ Project ▼ ] [ Date ▼ ] [ Journey ▼ ] [ Service ▼ ] [ Location ▼ ] [ Channel ▼ ]           │
│                     │                                                                                                  │
│ Service &           │ ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐             │
│ Pain Points         │ │ UNKNOWN RATE    │ │ NEGATIVE RATE   │ │ FEEDBACK        │ │ ACTIVE HOTSPOT  │             │
│                     │ │                 │ │                 │ │                 │ │                 │             │
│ Hotspot & RCA       │ │    7.4%         │ │    34.2%        │ │    18,546       │ │       7         │             │
│                     │ │   ↓ 0.8 pts     │ │    ↓ 2.1 pts    │ │    ↑ 8.4%       │ │    2 critical   │             │
│ ─────────────────   │ └─────────────────┘ └─────────────────┘ └─────────────────┘ └─────────────────┘             │
│ Feedback Explorer   │                                                                                                  │
│ Review Queue    128 │ CUSTOMER JOURNEY                                                                                │
│ Imports          1  │                                                                                                  │
│                     │ ┌───────────┐ → ┌───────────┐ → ┌────────────┐ → ┌───────────┐ → ┌───────────┐ → ┌──────────┐ │
│ ─────────────────   │ │ NHẬN THỨC │   │ XEM XÉT   │   │ GIAO DỊCH │   │ NHẬN NHÀ  │   │ CƯ TRÚ    │   │ VẬN HÀNH│ │
│ Data Quality        │ │ Neg 12%   │   │ Neg 18%   │   │ Neg 27%    │   │ Neg 31%   │   │ Neg 42%   │   │ Neg 35%  │ │
│ Taxonomy            │ │ 1.2k FB   │   │ 2.1k FB   │   │ 3.4k FB    │   │ 2.6k FB   │   │ 7.4k FB   │   │ 1.8k FB  │ │
│ Audit               │ └───────────┘   └───────────┘   └────────────┘   └───────────┘   └───────────┘   └──────────┘ │
│                     │                                                                                                  │
│                     │ EXPERIENCE TREND                                   TOP PAIN POINTS                               │
│                     │ ┌───────────────────────────────────────────┐       ┌─────────────────────────────────────────┐ │
│                     │ │                                           │       │ 1  Elevator waiting           1,490      │ │
│                     │ │       /\        /\                        │       │ 2  App login / OTP            1,120      │ │
│                     │ │ ___ /  \______/  \_______                 │       │ 3  Payment not recorded         860      │ │
│                     │ │                                           │       │ 4  Parking access failure       620      │ │
│                     │ └───────────────────────────────────────────┘       └─────────────────────────────────────────┘ │
│                     │                                                                                                  │
│                     │ EMERGING HOTSPOTS                                                                                │
│                     │ ┌───────┬─────────────────────────────┬────────────┬──────────┬──────────┬──────────────────┐ │
│                     │ │ Sev   │ Customer Pain               │ Location   │ Feedback │ Trend    │ Status           │ │
│                     │ ├───────┼─────────────────────────────┼────────────┼──────────┼──────────┼──────────────────┤ │
│                     │ │ SEV-2 │ Elevator waiting            │ S2         │ 42       │ ↑180%    │ Investigating    │ │
│                     │ │ SEV-3 │ Resident app login          │ Project    │ 27       │ ↑75%     │ Candidate        │ │
│                     │ └───────┴─────────────────────────────┴────────────┴──────────┴──────────┴──────────────────┘ │
└─────────────────────┴─────────────────────────────────────────────────────────────────────────────────────────┘
```

### Hợp đồng Tương tác Wireframe (Wireframe Interaction Contract)

```text
Click Journey Stage
→ Customer Journey Dashboard
→ duy trì các bộ lọc Project / Date / Location

Click Pain Point
→ Service & Pain Points Dashboard
→ duy trì ngữ cảnh Service / Issue

Click Hotspot
→ Hotspot & Root Cause Dashboard
→ mở hotspot được chọn

Click KPI / Trend point
→ Feedback Explorer
→ cùng ngữ cảnh bộ lọc đã được quản trị
```

---

# 8. CX Overview — Customer Journey Hero

Hình ảnh trung tâm của trang Overview nên là 6 giai đoạn vòng đời (lifecycle stages).

Ví dụ:

```text
NHẬN THỨC
Score / Negative
     ↓

XEM XÉT
Score / Negative
     ↓

GIAO DỊCH
Score / Negative
     ↓

NHẬN NHÀ
Score / Negative
     ↓

CƯ TRÚ
Score / Negative
     ↓

VẬN HÀNH
Score / Negative
```

Bố cục Desktop:

```text
┌────────────┐ → ┌────────────┐ → ┌────────────┐ → ┌────────────┐ → ┌────────────┐ → ┌────────────┐
│ NHẬN THỨC │   │ XEM XÉT    │   │ GIAO DỊCH │   │ NHẬN NHÀ  │   │ CƯ TRÚ     │   │ VẬN HÀNH  │
│ Neg 12%    │   │ Neg 18%    │   │ Neg 27%    │   │ Neg 31%    │   │ Neg 42%    │   │ Neg 35%    │
└────────────┘   └────────────┘   └────────────┘   └────────────┘   └────────────┘   └────────────┘
```

Nhiệm vụ khi nhấp vào bất kỳ giai đoạn nào:

```text
→ Customer Journey Dashboard
→ Stage đã chọn được duy trì
→ cùng ngữ cảnh bộ lọc toàn cục
```

---

# 9. CX Overview — Xu hướng Trải nghiệm (Experience Trend)

Biểu đồ đề xuất:

```text
Biểu đồ đường theo chuỗi thời gian (Time-series line chart)
```

Chỉ số bật/tắt (Toggle metric):

```text
Feedback Volume
Negative Rate
Unknown Rate
Hotspot Count
```

So sánh tùy chọn:

```text
Kỳ trước (Previous period)
MoM (So với tháng trước)
YoY (So với cùng kỳ năm trước)
```

Tooltip:

```text
Ngày (Date)
Giá trị chỉ số (Metric value)
Mức thay đổi (Delta)
Số lượng Feedback (Feedback count)
```

Nhấp vào một điểm trên biểu đồ:

```text
→ Feedback Explorer
→ cùng khung thời gian / ngữ cảnh bộ lọc
```

---

# 10. CX Overview — Top Pain Points

Xếp hạng pain points theo:

```text
Issue
+ volume (số lượng)
+ negative rate (tỷ lệ tiêu cực)
+ trend (xu hướng)
+ hotspot signal (tín hiệu điểm nóng)
```

Ví dụ:

```text
1. Elevator waiting                 1,490
2. Resident app login / OTP         1,120
3. Payment not recorded               860
4. Parking access failure             620
```

Nhấp vào:

```text
→ Service & Pain Points Dashboard
→ chọn trước Issue / Service
```

---

# 11. CX Overview — Emerging Hotspots

Các cột:

```text
Severity
Customer Pain
Service / Issue
Location
Evidence Count
Trend
Status
Owner
```

Ví dụ:

```text
SEV-2
Elevator waiting
SV-07 / IS-07-01
S2
42
↑180%
INVESTIGATING
Engineering
```

Nhấp vào:

```text
→ Hotspot & Root Cause Dashboard
→ hotspot đã chọn
```

---

# 12. Dashboard 02 — Customer Journey

## 12.1 Mục đích

Trả lời:

> Khách hàng gặp khó khăn ở Stage và Step nào trong lifecycle?

Route:

```text
/customer-journey
```

---

## 12.2 Bố cục

```text
CUSTOMER JOURNEY

Global Filters

[ 6 Lifecycle Stages ]

Selected Stage

[ Step Card ] [ Step Card ] [ Step Card ] [ Step Card ]
[ Step Card ] [ Step Card ] [ Step Card ] [ Step Card ]

Worst Experience Steps
Journey Trend
Top Related Services
```

---

## 12.3 Reference Wide-Frame Wireframe

```text
┌───────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ CUSTOMER JOURNEY                                                                                              │
│ Khách hàng đang gặp khó khăn ở đâu trong lifecycle?                                                           │
├───────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ [Project ▼] [Date ▼] [Intake Channel ▼] [Affected Channel ▼] [Location ▼]                                  │
├───────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                               │
│ CUSTOMER LIFECYCLE                                                                                            │
│                                                                                                               │
│ ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐              │
│ │ NHẬN THỨC   │ →  │ XEM XÉT      │ →  │ GIAO DỊCH   │ →  │ NHẬN NHÀ    │ →  │ CƯ TRÚ       │ → VẬN HÀNH   │
│ │ 1.2k FB      │    │ 2.1k FB      │    │ 3.4k FB      │    │ 2.6k FB      │    │ 7.4k FB      │              │
│ │ 12% negative │    │ 18% negative │    │ 27% negative │    │ 31% negative │    │ 42% negative │              │
│ └──────────────┘    └──────────────┘    └──────────────┘    └──────────────┘    └──────────────┘              │
│                                                                                                               │
│ Selected: CƯ TRÚ                                                                                              │
│ ─────────────────────────────────────────────────────────────────────────────────────────────────────────── │
│                                                                                                               │
│ ┌───────────────┐ ┌───────────────┐ ┌───────────────┐ ┌───────────────┐                                     │
│ │ RES-01        │ │ RES-02        │ │ RES-03        │ │ RES-04        │                                     │
│ │ Hồ sơ cư dân  │ │ App / hệ thống│ │ Ra vào        │ │ Tiếp khách    │                                     │
│ │ 640 FB        │ │ 1,210 FB      │ │ 2,140 FB      │ │ 520 FB        │                                     │
│ │ Neg 18%       │ │ Neg 44%       │ │ Neg 51%       │ │ Neg 20%       │                                     │
│ └───────────────┘ └───────────────┘ └───────────────┘ └───────────────┘                                     │
│                                                                                                               │
│ ┌───────────────┐ ┌───────────────┐ ┌───────────────┐ ┌───────────────┐                                     │
│ │ RES-05        │ │ RES-06        │ │ RES-07        │ │ RES-08        │                                     │
│ │ Tiện ích      │ │ Thanh toán    │ │ Phản ánh      │ │ Thay đổi căn  │                                     │
│ │ 980 FB        │ │ 910 FB        │ │ 780 FB        │ │ 240 FB        │                                     │
│ │ Neg 34%       │ │ Neg 47%       │ │ Neg 39%       │ │ Neg 15%       │                                     │
│ └───────────────┘ └───────────────┘ └───────────────┘ └───────────────┘                                     │
│                                                                                                               │
│ SELECTED STEP: RES-03 · RA VÀO & DI CHUYỂN                                                                    │
│                                                                                                               │
│ ┌─────────────────────────────────────────────┐        ┌─────────────────────────────────────────────────┐   │
│ │ RELATED SERVICES                            │        │ EXPERIENCE TREND                                │   │
│ │                                             │        │                                                 │   │
│ │ SV-05 Access & Mobility       51%           │        │ Negative Rate                                   │   │
│ │ SV-07 Engineering             31%           │        │      ╲                                          │   │
│ │ SV-08 Security                12%           │        │       ╲__                                       │   │
│ │ Other                          6%           │        │          ╲___                                   │   │
│ └─────────────────────────────────────────────┘        └─────────────────────────────────────────────────┘   │
└───────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### Hợp đồng Khoan sâu (Drill-Down Contract)

```text
Stage
→ Step
→ Related Services
→ Issues
→ Feedback Evidence
```

Dashboard KHÔNG ĐƯỢC hàm ý rằng một Journey Step ánh xạ tương ứng 1-1 tới đúng một Service.

---

# 13. Customer Journey — Stage Selector

Sử dụng 6 giai đoạn chuẩn hóa (canonical stages).

Khi một stage được chọn, UI sẽ mở rộng các step chuẩn hóa của nó.

Ví dụ:

```text
CƯ TRÚ

RES-01
Thiết lập hồ sơ & quyền cư dân

RES-02
Sử dụng hệ thống & kênh cư dân

RES-03
Ra vào & di chuyển

RES-04
Tiếp khách

RES-05
Sử dụng tiện ích & dịch vụ

RES-06
Thanh toán phí & nghĩa vụ cư trú

RES-07
Gửi yêu cầu / phản ánh / sự cố

RES-08
Thực hiện thay đổi liên quan căn hộ
```

---

# 14. Thẻ Journey Step (Journey Step Card)

Mỗi thẻ Journey Step hiển thị:

```text
Step code
Step name
Feedback Volume
Negative Rate
Active Hotspots
Trend
```

Ví dụ:

```text
RES-03
Ra vào & di chuyển

2,140 feedback
51% negative
3 hotspots
↑ 22%
```

Nhấp vào:

```text
→ Phần chi tiết Journey Step (Journey Step Detail section)
```

---

# 15. Journey Step Drill-Down

Journey Step được chọn sẽ hiển thị:

```text
RES-03 — Ra vào & di chuyển

Feedback Volume
Negative Rate
Hotspots

Service Distribution

SV-05 Access, Visitor, Parking & Mobility
SV-07 Engineering, Utilities & Common Assets
SV-08 Security, Fire & Emergency
```

Quan trọng:

Journey Step và Service có mối quan hệ N:N (nhiều - nhiều).

Do đó UI không được hàm ý:

```text
RES-03 = một Service cố định
```

Thay vào đó:

```text
RES-03
   ↓
Các Service liên quan khả thi / quan sát được
```

---

# 16. Dashboard 03 — Service & Pain Points

## 16.1 Mục đích

Trả lời:

> Service nào đang tạo trải nghiệm xấu, và khách hàng đang gặp Issue gì?

Route:

```text
/service-pain-points
```

---

## 16.2 Bố cục

```text
SERVICE & PAIN POINTS

Global Filters

Service Performance Table

Selected Service

[ Issue 1 ] [ Issue 2 ] [ Issue 3 ]

Top Symptoms
Location Distribution
Voice of Customer
Trend
```

---

## 16.3 Reference Wide-Frame Wireframe

```text
┌───────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ SERVICE & PAIN POINTS                                                                                         │
│ Service nào đang tạo trải nghiệm xấu và khách hàng đang gặp vấn đề cụ thể gì?                                 │
├───────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ [Date ▼] [Journey ▼] [Service ▼] [Location ▼] [Sentiment ▼]                                                 │
├───────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                               │
│ SERVICE PERFORMANCE                                                                                           │
│                                                                                                               │
│ ┌───────────────────────────────────────────────────────────────────────────────────────────────────────────┐ │
│ │ Service                               Feedback      Negative       Hotspots        Trend                    │ │
│ ├───────────────────────────────────────────────────────────────────────────────────────────────────────────┤ │
│ │ SV-07 Engineering                     3,620         48%            3               ↑ 21%                    │ │
│ │ SV-03 Resident Digital                3,180         43%            2               ↑ 16%                    │ │
│ │ SV-04 Billing & Payment               2,410         39%            1               ↓  4%                    │ │
│ │ SV-05 Access & Parking                2,040         31%            1               ↑  8%                    │ │
│ └───────────────────────────────────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                                               │
│ Selected Service: SV-07 · ENGINEERING                                                                         │
│                                                                                                               │
│ ┌───────────────────────────────────────┐ ┌───────────────────────────────────────┐ ┌───────────────────────┐ │
│ │ IS-07-01                             │ │ IS-07-02                             │ │ IS-07-03             │ │
│ │ System degradation                  │ │ Unsafe technical condition           │ │ Maintenance failure  │ │
│ │                                     │ │                                       │ │                       │ │
│ │ 1,490 feedback                      │ │ 530 feedback                          │ │ 1,600 feedback        │ │
│ │ 71% negative                        │ │ 62% negative                          │ │ 40% negative          │ │
│ │ 3 hotspots                          │ │ 1 hotspot                             │ │ 2 hotspots            │ │
│ └───────────────────────────────────────┘ └───────────────────────────────────────┘ └───────────────────────┘ │
│                                                                                                               │
│ TOP CUSTOMER SYMPTOMS                                  LOCATION DISTRIBUTION                                  │
│                                                                                                               │
│ 1. Chờ thang máy lâu                 620              S2               █████████████                           │
│ 2. Thang dừng bất thường             410              S10              █████████                               │
│ 3. Mất nước / áp lực nước yếu        260              S1               █████                                   │
│ 4. Điều hòa khu chung không ổn       200              S5               ████                                    │
│                                                                                                               │
│ VOICE OF CUSTOMER                                                                                             │
│ ┌───────────────────────────────────────────────────────────────────────────────────────────────────────────┐ │
│ │ “Sáng nào đi làm cũng mất gần 10 phút chờ thang.”                                      Negative          │ │
│ │ “Thang dừng bất thường ở tầng 12.”                                                     Negative          │ │
│ │ “Đã báo kỹ thuật nhưng vài ngày lại bị lại.”                                            Negative          │ │
│ └───────────────────────────────────────────────────────────────────────────────────────────────────────────┘ │
└───────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### Pain Point UI Contract

```text
Canonical Service
→ Canonical Issue
→ symptom_detail / recurring symptom
→ representative Feedback
```

`Pain Point` là một khái niệm phân tích/hiển thị. Nó KHÔNG ĐƯỢC tự động tạo ra một Issue taxonomy mới.

---

# 17. Bảng Hiệu năng Dịch vụ (Service Performance Table)

Các cột:

```text
Service
Feedback Volume
Negative Rate
Active Hotspots
Trend
Top Issue
```

Ví dụ:

```text
SV-07 Engineering
3,620
48%
3 hotspots
↑21%
IS-07-01
```

---

# 18. Chi tiết Service được Chọn (Selected Service Detail)

Ví dụ:

```text
SV-07
Kỹ thuật, tiện ích & tài sản chung
```

Hiển thị các issue chuẩn hóa (canonical issues):

```text
IS-07-01
System Outage or Degradation

IS-07-02
Leakage or Unsafe Technical Condition

IS-07-03
Common Asset or Maintenance Failure
```

Mỗi thẻ Issue:

```text
Feedback count
Negative rate
Locations affected
Active hotspots
Trend
```

---

# 19. Biểu diễn Pain Point (Pain Point Representation)

Trong nội dung văn bản UI:

```text
Pain Point
```

có thể đại diện cho sự kết hợp đọc được của con người giữa:

```text
Issue
+ symptom_detail
+ context
```

Ví dụ:

```text
Issue:
IS-07-01 System Outage or Degradation

Pain Point:
“Chờ thang máy lâu vào giờ cao điểm”
```

Quan trọng:

Không tạo ra Issue chuẩn hóa (canonical Issue) mới cho mỗi triệu chứng.

`Pain Point` là một khái niệm UI/phân tích; danh mục phân loại chuẩn hóa (canonical taxonomy) vẫn duy trì ở cấp Service + Issue.

---

# 20. Top Symptoms (Triệu chứng Hàng đầu)

Sử dụng tổng hợp/phân cụm `symptom_detail`.

Ví dụ:

```text
Chờ thang máy lâu
Thang dừng bất thường
Không gọi được thang
Áp lực nước yếu
Điều hòa khu chung không ổn
```

Các triệu chứng này không nên tự động trở thành các nhãn danh mục phân loại mới.

---

# 21. Phân bố theo Vị trí (Location Distribution)

Hiển thị nơi xảy ra pain point.

Các góc nhìn có thể có:

```text
Project
Building
Zone
Floor
```

P0 có thể sử dụng:

- biểu đồ thanh xếp hạng (ranked bar chart);
- bảng (table);
- xếp hạng nhiệt đơn giản (simple heat ranking).

GIS/bản đồ thuộc phạm vi P1 trừ khi cần phân tích không gian địa lý chính xác.

---

# 22. Ý kiến Khách hàng (Voice of Customer)

Hiển thị phản hồi đại diện đã được ẩn danh (masked feedback).

Ví dụ:

```text
“Buổi sáng đi làm phải chờ thang gần 10 phút.”

“App cư dân thường xuyên không nhận OTP.”

“Đã thanh toán nhưng phí vẫn hiển thị chưa trả.”
```

Mỗi đoạn trích phản hồi bao gồm:

```text
Sentiment
Source
Date
Location
```

Nhấp vào:

```text
→ Feedback Explorer / Item Detail
```

---

# 23. Dashboard 04 — Hotspot & Root Cause

## 23.1 Mục đích

Trả lời:

> Pain Point nào đang trở thành vấn đề vận hành, vì sao nó xảy ra, và doanh nghiệp đang xử lý thế nào?

Route:

```text
/hotspot-root-cause
```

---

## 23.2 Bố cục

```text
HOTSPOT & ROOT CAUSE

Filters

Active Hotspots Table

Selected Hotspot

Customer Pain / Context
Evidence
Candidate Causes

P1-only extension (hidden/absent in P0):
Investigation Timeline → Confirmed Root Cause → Corrective/Preventive Actions
```

---

## 23.3 Reference Wide-Frame Wireframe

```text
┌───────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ HOTSPOT & ROOT CAUSE                                                                                          │
│ Những trải nghiệm xấu nào đang hình thành thành vấn đề vận hành, vì sao và đang xử lý thế nào?                │
├───────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ [Active ▼] [Severity ▼] [Service ▼] [Location ▼] [Owner ▼]                                                  │
├───────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                               │
│ ACTIVE HOTSPOTS                                                                                               │
│                                                                                                               │
│ ┌──────┬───────────────────────────────┬──────────┬──────────┬───────────┬──────────────┬───────────────────┐ │
│ │ Sev  │ Pain Point                    │ Location │ Feedback │ Trend     │ Owner        │ Status            │ │
│ ├──────┼───────────────────────────────┼──────────┼──────────┼───────────┼──────────────┼───────────────────┤ │
│ │ SEV-2│ Elevator waiting              │ S2       │ 42       │ ↑ 180%    │ Engineering  │ Investigating     │ │
│ │ SEV-3│ App login / OTP               │ All      │ 27       │ ↑ 75%     │ Digital      │ Candidate         │ │
│ │ SEV-3│ Parking access                │ S10      │ 19       │ ↑ 42%     │ Security     │ Acknowledged      │ │
│ └──────┴───────────────────────────────┴──────────┴──────────┴───────────┴──────────────┴───────────────────┘ │
│                                                                                                               │
│ Selected Hotspot                                                                                              │
│                                                                                                               │
│ CUSTOMER PAIN                                     EVIDENCE                                                      │
│ ┌───────────────────────────────────────┐         ┌────────────────────────────────────────────────────────┐  │
│ │ Elevator waiting                     │         │ 42 Feedback Items                                      │  │
│ │                                      │         │                                                        │  │
│ │ Journey: RES-03                      │         │ 31 Hotline / Frontdesk                                 │  │
│ │ Service: SV-07                       │         │ 11 App / Social                                       │  │
│ │ Issue: IS-07-01                      │         │                                                        │  │
│ │ Location: S2                         │         │ Peak time: 07:00–09:00                                │  │
│ │ Negative: 84%                        │         │ Recurrence: 6 days                                   │  │
│ └───────────────────────────────────────┘         └────────────────────────────────────────────────────────┘  │
│                                                                                                               │
│ CANDIDATE CAUSES                                                                                              │
│                                                                                                               │
│ ┌─────────────────────────────────────────┬────────────┐                                                      │
│ │ Peak-hour capacity overload             │ 72%        │                                                      │
│ │ Dispatch configuration                  │ 61%        │                                                      │
│ │ One elevator unavailable               │ 47%        │                                                      │
│ └─────────────────────────────────────────┴────────────┘                                                      │
│                                                                                                               │
│ P0 boundary: evidence + owner/status + Candidate Cause only.                                                  │
│ Investigation / Confirmed Root Cause / Corrective / Preventive workflows are introduced in P1.               │
└───────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### Hợp đồng Phân tích-đến-Hành động (Intelligence-to-Action Contract)

```text
P0:
Pain Point
→ Hotspot
→ Candidate Cause
→ Evidence

P1:
→ Investigation
→ Confirmed Root Cause
→ Corrective Action
→ Preventive Action
→ Resolve / Monitor
```

P0 KHÔNG ĐƯỢC hiển thị các điều khiển P1 dưới dạng bật (enabled) hoặc hàm ý Candidate Cause là đã được xác nhận. Khi P1 được bật, UI PHẢI hiển thị từng giai đoạn của quy trình làm việc và không được bỏ qua trực quan từ giả thuyết AI sang nguyên nhân gốc rễ đã xác nhận.

---

# 24. Bảng Hotspot Đang Hoạt động (Active Hotspots Table)

Các cột:

```text
Severity
Status
Pain Point
Service / Issue
Location
Evidence Count
Trend
Owner
First Seen
Last Seen
```

Sắp xếp mặc định:

```text
SEV-1
→ SEV-2
→ mới nhất / xu hướng cao nhất
```

---

# 25. Selected Hotspot — Ngữ cảnh Pain Point Khách hàng

Ví dụ:

```text
Pain Point:
Elevator waiting

Journey:
RES-03 · Ra vào & di chuyển

Service:
SV-07

Issue:
IS-07-01

Location:
S2

Feedback:
42

Negative:
84%

Time concentration:
07:00–09:00
```

---

# 26. Selected Hotspot — Bằng chứng (Evidence)

Bảng bằng chứng có thể bao gồm:

```text
Feedback Items
Source distribution
Time pattern
Location pattern
```

P0 sử dụng các Feedback Items liên kết như bằng chứng hotspot có thể tái lập. Hồ sơ vận hành, tham chiếu BMS/CMMS và bằng chứng kiểm tra được đưa vào cùng Investigation ở P1.

---

# 27. Nguyên nhân Ứng viên (Candidate Causes)

Chỉ hiển thị các giả thuyết.

Ví dụ:

```text
Peak-hour capacity overload          72%
Dispatch configuration               61%
One elevator unavailable             47%
```

Nhãn hiển thị:

```text
Candidate Cause
```

Tuyệt đối không dùng:

```text
Root Cause
```

trước khi xác nhận.

---

# 28. Dành riêng cho P1 — Dòng thời gian Điều tra (Investigation Timeline)

Phần này không được render, định tuyến hoặc gọi bởi P0.

Luồng trực quan:

```text
Feedback
    ┐
BMS Data
    ├──→ Investigation
Maintenance Log
    ┤
Inspection
    ┘

Investigation
    ↓
Confirmed Root Cause
    ↓
Corrective Action
    ↓
Preventive Action
```

Các sự kiện trên timeline:

```text
Hotspot detected
Acknowledged
Owner assigned
Investigation started
Evidence added
Root cause confirmed
Corrective action started
Action completed
Hotspot resolved
```

---

# 29. Dành riêng cho P1 — Nguyên nhân Gốc rễ đã Xác nhận (Confirmed Root Cause)

Chỉ hiển thị khi quá trình điều tra xác nhận.

Ví dụ:

```text
Confirmed Root Cause

1/4 elevator unavailable
+
dispatch configuration not optimized for morning peak.
```

Bao gồm:

```text
Confirmed by
Confirmed at
Evidence summary
```

---

# 30. Dành riêng cho P1 — Phần Hành động / Cải tiến (Action / Improvement Section)

Các phần:

```text
Corrective Actions
Preventive Actions
```

Mỗi hành động hiển thị:

```text
Description
Owner
Due Date
Status
Verification
```

Ví dụ:

```text
✓ Restore elevator
Completed

✓ Reconfigure dispatch
Completed

○ Monitor for 7 days
In Progress

○ Update preventive maintenance checklist
Planned
```

---

# 31. Workspace 01 — Feedback Explorer

## 31.1 Mục đích

Khoan sâu vận hành xuống từng bằng chứng riêng lẻ (individual evidence).

Route:

```text
/feedback
```

Bố cục:

```text
┌────────────────────────────────────────────────┬───────────────────────────────┐
│ Feedback Table                                 │ Feedback Item Detail          │
│                                                │                               │
│ Filters                                        │ Evidence                      │
│ Table                                          │ Current Classification        │
│                                                │ AI Suggestions                │
│                                                │ Human Decision                │
└────────────────────────────────────────────────┴───────────────────────────────┘
```

Chiều rộng đề xuất:

```text
65% list
35% detail
```

---

# 32. Bảng Feedback Explorer

Các cột:

```text
Reported Time
Masked Feedback
Journey Step
Service
Issue
Sentiment
Severity
Location
Review State
```

Các cột tùy chọn:

```text
Source
Service Request Step
Hotspot Link
```

---

# 33. Feedback Item Detail

Hiển thị:

```text
Masked content
Source
Reported time
Location
Intake channel
Affected channel
Related hotspot
Split lineage
```

Nội dung gốc (raw content) bị ẩn theo mặc định.

---

# 34. Bảng Duyệt Phân loại (Classification Review Panel)

Các phần:

```text
Customer Lifecycle
Service Request Lifecycle
Primary Service
Issue
Sentiment
Operational Severity
Candidate Causes
```

Hành vi UI quan trọng:

### Customer Lifecycle

```text
Value Status
Step
Derived Stage
```

Stage là chỉ đọc (read-only) và được suy ra từ Step.

### Service Request Lifecycle

Nhóm riêng biệt:

```text
Value Status
Step
```

### Primary Service / Issue

Bộ chọn Issue bị giới hạn bởi Service đã chọn.

---

# 35. Mẫu Gợi ý từ AI (AI Suggestion Pattern)

Ví dụ:

```text
AI Suggestion

Primary Service
SV-07 · Engineering
Confidence: 93%

[Accept]

Issue
IS-07-01
Confidence: 81%

[Accept]
```

Giá trị được chấp nhận hiện tại phải có cách xử lý trực quan khác biệt.

---

# 36. Trải nghiệm Xung đột Phiên bản (Version Conflict UX)

Khi một người duyệt khác đã cập nhật mục này:

```text
This item was updated by another reviewer.

Your version: 3
Current version: 4

[Reload Latest]
[Copy My Notes]
```

Không bao giờ tự động ghi đè âm thầm.

---

# 37. Tách Phản hồi Đa Ý định (Split Multi-Intent Feedback)

Hành động:

```text
Split Feedback
```

Sử dụng khi một phản hồi nguồn chứa nhiều vấn đề độc lập.

Ví dụ:

```text
“Thang máy chậm và app không đăng nhập được.”
```

Tách thành:

```text
Item 1
Thang máy chậm

Item 2
App không đăng nhập được
```

Quy tắc hiển thị trên UI:

```text
Phản hồi gốc (Original Feedback) giữ nguyên không đổi.
Các quyết định lịch sử (Historical decisions) vẫn được lưu lại.
Các mục con (Child items) được phân loại độc lập.
```

---

# 38. Workspace 02 — Review Queue

Route:

```text
/review
```

Mục đích:

> Duyệt các gợi ý từ AI một cách hiệu quả trong khi vẫn duy trì sự kiểm soát của con người.

Bố cục:

```text
Queue List | Review Panel
```

Độ ưu tiên hàng chờ (Queue priority):

```text
Hard trigger / safety
→ SEV-1
→ SEV-2
→ oldest pending
→ low confidence
```

---

# 39. Hành động trong Review Queue (Review Queue Actions)

Cho phép:

```text
ACCEPT
CORRECT
MARK_UNKNOWN
MARK_MISSING
MARK_NOT_APPLICABLE
SPLIT_REQUIRED
SKIP
```

Nhãn UI có thể được bản địa hóa/định dạng viết hoa chữ cái đầu, nhưng các giá trị wire gửi đi chính xác là các giá trị tiếng Anh ở trên. 5 hành động đầu tiên tạo ra ClassificationDecision + ReviewEvent; `SPLIT_REQUIRED` và `SKIP` chỉ tạo ReviewEvent. “Save & Next” là thao tác điều hướng sau một hành động thành công, không phải là một hành động duyệt.

Không cho phép chấp nhận hàng loạt mù quáng (blind bulk acceptance) phân loại AI trong P0.

---

# 40. Workspace 03 — Imports

Route:

```text
/imports
```

Wizard:

```text
1 Upload
2 Map Columns
3 Preview
4 Validate
5 Execute
6 Result
```

---

# 41. Import Upload

Các trường:

```text
Project
Source System
File
Mapping Profile
```

Hiển thị:

```text
Filename
File size
Checksum
```

---

# 42. Import Mapping

Ánh xạ 2 cột:

```text
Source Column
→
Platform Field
```

Ví dụ:

```text
ticket_id
→ source_record_key

reported_date
→ reported_at

content_masked
→ content

channel
→ intake_channel
```

---

# 43. Import Validation

Tóm tắt:

```text
18,546 total
18,110 valid
436 invalid
```

Bảng lỗi:

```text
Row
Field
Error Code
Message
```

Không có Feedback nào được commit trước bước Execute.

---

# 44. Quản trị — Chất lượng Dữ liệu (Governance — Data Quality)

Route:

```text
/data-quality
```

Mục đích:

> Giám sát xem dữ liệu phân tích và AI có đủ độ tin cậy để sử dụng hay không.

Chỉ số:

```text
Unknown rate
Missing rate
Unclassified items
SV-10 / Other rate
Low-confidence prediction rate
Pending review age
Import error rate
Ineligible items
```

---

# 45. Quản trị — Danh mục Phân loại (Governance — Taxonomy)

Route:

```text
/admin/taxonomy
```

P0 hỗ trợ quản trị (governance), không phải CRUD sản xuất tùy ý.

Hiển thị:

```text
Release Version
Status
Checksum
6 Customer Lifecycle Stages
36 Customer Lifecycle Steps
8 Service Request Steps
10 Services
28 Issues
```

Hành động:

```text
Validate
View
Publish
```

---

# 46. Quản trị — Kiểm toán (Governance — Audit)

Route:

```text
/admin/audit
```

Các cột:

```text
Time
Actor
Role
Action
Resource
Reason
Correlation ID
```

Không hiển thị phản hồi thô (raw feedback) trong bảng kiểm toán.

---

# 47. Chính sách Chỉ số CX Score / CX Health

P0 KHÔNG ĐƯỢC hiển thị `CX Score` hoặc `CX Health` dưới dạng một KPI chính thức vì chưa có công thức nào được phê duyệt.

Các dữ liệu đầu vào điểm số có thể gồm:

```text
Negative Rate
Severity
Hotspot Penalty
Resolution Improvement
Unknown/Data Quality Penalty
```

Đặc tả UI này KHÔNG xác định hay phê duyệt công thức nghiệp vụ. Một phiên bản trong tương lai có thể thêm chỉ số này chỉ sau khi được phê duyệt quản trị và có hỗ trợ phiên bản API/chỉ số.

Cho đến khi được phê duyệt, hãy sử dụng các chỉ số rõ ràng:

```text
Negative Rate
Feedback Volume
Hotspots
Trend
```

thay vì tự tạo ra chỉ số tổng hợp CX Score.

---

# 48. Quy tắc Trực quan hóa Customer Journey

Customer Journey phải duy trì tính dễ hiểu ở hai cấp độ:

## Cấp độ 1 — Stage

```text
6 stages
```

## Cấp độ 2 — Step

```text
36 canonical steps
```

UI không bao giờ nên hiển thị tất cả 36 steps cùng một lúc trên Overview.

Thay vào đó:

```text
Overview
→ 6 Stages

Customer Journey Dashboard
→ Stage đã chọn
→ các Step của Stage đó
```

Điều này tránh gây quá tải thông tin.

---

# 49. Trực quan hóa Vòng đời Yêu cầu Dịch vụ (Service Request Lifecycle)

Service Request Lifecycle là một chiều phân tích thứ cấp.

Nó nên xuất hiện chủ yếu ở:

```text
Feedback Explorer
Review
Journey Step detail
Service detail
```

Không làm cho nó cạnh tranh trực quan với phần chính Customer Lifecycle.

---

# 50. Chiến lược Đáp ứng (Responsive Strategy)

Mục tiêu chính:

```text
Desktop / laptop màn hình lớn
```

### Large Desktop

```text
Persistent sidebar
Wide dashboard
Multi-column visualization
Feedback 65/35 split view
```

### Tablet / Small Laptop

```text
Collapsible sidebar
2-column to 1-column dashboard
Feedback detail as drawer
```

### Mobile

P0 hỗ trợ:

```text
Read
Basic drill-down
Hotspot summary
```

nhưng không cam kết đầy đủ năng suất duyệt mật độ cao cho người duyệt.

---

# 51. Khả năng Truy cập (Accessibility)

P0 tối thiểu:

1. Điều hướng bằng bàn phím (Keyboard navigation).
2. Trạng thái focus rõ ràng (Visible focus state).
3. Nhãn (labels) trên tất cả các trường form.
4. Trạng thái/độ nghiêm trọng không chỉ được biểu diễn bằng màu sắc.
5. Tiêu đề bảng truy cập được (Accessible table headers).
6. Tóm tắt văn bản cho biểu đồ (Chart textual summary).
7. Giữ focus trong modal (Modal focus trap).
8. Mục tiêu WCAG 2.1 AA cho các quy trình làm việc chính.

---

# 52. Trạng thái Đang tải (Loading States)

Sử dụng skeletons cho:

```text
KPI
Journey cards
Charts
Tables
Detail panels
```

Khi các bộ lọc thay đổi:

```text
Giữ kết quả trước đó hiển thị
Hiển thị trạng thái đang tải (loading state)
Thay thế sau khi có phản hồi
```

Tránh tải trang trắng hoàn toàn (full-page blank loading).

---

# 53. Trạng thái Trống (Empty States)

Ví dụ:

```text
No feedback matches these filters.
[Clear Filters]
```

```text
No active hotspots for this time window.
```

```text
No AI prediction has been generated.
[Run Prediction]
```

```text
No confirmed root cause yet.
Investigation is still in progress.
```

---

# 54. Trạng thái Lỗi (Error States)

Ví dụ:

```text
Couldn't load Customer Journey data.

Request ID: ...
[Retry]
```

Các lỗi tên miền ở cấp trường (field-level domain errors) phải xuất hiện ngay bên cạnh trường tương ứng.

---

# 55. UX cho Thông tin Định danh Cá nhân (PII UX)

Mặc định:

```text
Masked content
```

Chế độ xem thô có đặc quyền (Privileged raw view):

```text
View Raw Content
    ↓
Yêu cầu nhập lý do
    ↓
Yêu cầu API được ghi log kiểm toán
    ↓
Hiển thị thô tạm thời
```

Nội dung thô không được đưa vào:

- URL;
- sự kiện analytics;
- dữ liệu đo đạc trình duyệt thông thường (standard browser telemetry);
- các bảng dashboard thông thường.

---

# 56. Hệ thống Thành phần UI (UI Component System)

Các thành phần dùng lại cốt lõi:

```text
AppShell
Sidebar
TopBar
ProjectSelector

GlobalFilterBar
FilterChip

KpiCard
JourneyStageCard
JourneyStepCard

TrendChart
RankedBarList
ServicePerformanceTable
PainPointCard
VoiceOfCustomerCard

SeverityBadge
StatusBadge
TaxonomyCodeLabel

FeedbackTable
FeedbackDetailPanel
EvidencePanel

AiSuggestionCard
ValueStatusControl
TaxonomySelect
DecisionHistory

HotspotTable
HotspotDetailPanel
CandidateCauseList
InvestigationTimeline
ActionTracker

ImportWizard
DataQualityCard
ValidationCheckList
AuditTable
```

---

# 57. Ngôn ngữ Thiết kế (Design Language)

Phong cách trực quan nên là:

```text
Professional
Analytical
Enterprise
Calm
Evidence-driven
Modern but not decorative
```

Tránh:

```text
bright consumer gradients everywhere
excessive glassmorphism
large rounded cards for every metric
gaming-style heatmap colors
UI that resembles a helpdesk SaaS
```

Ưu tiên:

```text
neutral surfaces
clear typography hierarchy
subtle borders
one primary brand color
semantic severity/status colors
high-density data tables
wide analytical sections
```

---

# 58. Cấu trúc Phân cấp Dashboard (Dashboard Hierarchy)

Mỗi dashboard nên tuân theo:

```text
Context
↓
Summary
↓
Breakdown
↓
Trend
↓
Evidence
↓
Drill-down
```

Ví dụ:

```text
Customer Journey
↓
Cư trú
↓
RES-03
↓
Negative Rate 51%
↓
SV-07 = 31%
↓
IS-07-01
↓
42 feedback items
```

---

# 59. Điều hướng Giữa các Dashboard (Navigation Between Dashboards)

Luồng liên kết sâu bắt buộc (Required deep-link flow):

```text
CX Overview
→ Customer Journey
→ Service & Pain Points
→ Hotspot & Root Cause
→ Feedback Evidence
```

Các bộ lọc phải duy trì khi có ý nghĩa ngữ cảnh.

Ví dụ:

```text
Project = Symphony
Date = last 30 days
Location = S2
```

phải duy trì kích hoạt khi di chuyển giữa các dashboard.

---

# 60. Đường dẫn URL (URL Routes)

```text
/overview

/customer-journey
/customer-journey/:stageCode
/customer-journey/:stageCode/:stepCode

/service-pain-points
/service-pain-points/:serviceCode
/service-pain-points/:serviceCode/:issueCode

/hotspot-root-cause
/hotspot-root-cause/:hotspotId

/feedback
/feedback/:feedbackItemId

/review

/imports
/imports/:importJobId

/data-quality

/admin/taxonomy
/admin/taxonomy/:releaseId

/admin/audit
```

Không đưa PII thô vào URL.

---

# 61. Ánh xạ API (API Mapping)

| Bề mặt UI (UI Surface) | API |
|---|---|
| CX Overview | `/analytics/summary`, `/analytics/trend`, `/analytics/breakdown`, `/hotspots` |
| Customer Journey | `/analytics/breakdown?dimension=journey_stage&metrics=item_volume,negative_rate,active_hotspots,trend`, cùng cấu trúc cho `journey_step` |
| Service & Pain Points | `/analytics/breakdown?dimension=service&metrics=item_volume,negative_rate,active_hotspots,trend`, cùng cấu trúc cho `issue`, cộng thêm `/feedback-items` |
| Hotspot & RCA [P0] | `/hotspots`, `/hotspots/{id}` |
| Investigation/RCA [Dành riêng cho P1] | `/investigations/{id}` và các endpoint mutation của P1 |
| Feedback Explorer | `/feedback-items`, `/feedback-items/{id}` |
| Review Queue | `/review-queue`, `/ai/predictions/{id}/review`, `/feedback-items/{id}/decisions` |
| Imports | `/import-jobs/*` |
| Data Quality | `/analytics/data-quality` |
| Taxonomy | các endpoint taxonomy |
| Audit | `/audit-events` |

---

# 62. Luồng Người dùng Chính — Manager

```text
Mở CX Overview
↓
Thấy Cư trú có tỷ lệ tiêu cực cao nhất
↓
Mở Customer Journey
↓
Chọn RES-03 Ra vào & di chuyển
↓
Thấy sự tập trung vào SV-07 / IS-07-01
↓
Mở Service & Pain Points
↓
Thấy Elevator Waiting là triệu chứng hàng đầu
↓
Mở Hotspot & Root Cause
↓
Thấy điểm nóng ở S2
↓
Duyệt bằng chứng, người phụ trách/trạng thái và Candidate Causes
```

---

# 63. Luồng Người dùng Chính — CX Analyst

```text
Mở CX Overview
↓
Phát hiện bất thường về xu hướng
↓
Khoan sâu vào Journey
↓
So sánh Service / Issue
↓
Mở phản hồi đại diện
↓
Xác thực nhận định
↓
Chuẩn bị đề xuất vận hành
```

---

# 64. Luồng Người dùng Chính — Reviewer

```text
Mở Review Queue
↓
Đọc bằng chứng Feedback
↓
Duyệt gợi ý từ AI
↓
Gửi một hành động duyệt chuẩn hóa
↓
Lưu quyết định (Save Decision)
↓
Cập nhật Phân loại Hiện tại (Current Classification)
↓
Dữ liệu phân tích phản ánh mục đã được chấp nhận
```

---

# 65. Luồng Người dùng Chính — Operations Manager

```text
Mở Hotspot & Root Cause
↓
Duyệt bằng chứng
↓
Ghi nhận hotspot (Acknowledge hotspot)
↓
Gán người phụ trách (Assign owner)
↓
Cập nhật trạng thái hotspot / giải quyết hoặc loại bỏ

Mở rộng P1:
Khởi động Investigation → thêm bằng chứng → xác nhận Root Cause → theo dõi Corrective/Preventive Actions
```

---

# 66. Luồng Người dùng Chính — Data Admin

```text
Tải file lên (Upload file)
↓
Ánh xạ các cột (Map columns)
↓
Xem trước (Preview)
↓
Xác thực (Validate)
↓
Thực thi (Execute)
↓
Duyệt chất lượng dữ liệu
↓
Chạy dự đoán (Run prediction)
↓
Giám sát tỷ lệ unknown / other
```

---

# 67. Danh mục Màn hình P0 (P0 Screen Inventory)

## Dashboards

```text
01 CX Overview
02 Customer Journey
03 Service & Pain Points
04 Hotspot & Root Cause
```

## Workspaces

```text
05 Feedback Explorer
06 Review Queue
07 Imports
08 Hotspot Investigation Detail
```

## Governance

```text
09 Data Quality
10 Taxonomy Admin
11 Audit
```

Tổng cộng:

```text
4 dashboards
+
4 operational workspaces
+
3 governance screens
=
11 màn hình P0 chính
```

---

# 68. Thứ tự Ưu tiên Xây dựng P0 (P0 Build Priority)

Thứ tự đề xuất cho frontend:

```text
1. App Shell + Global Filters
2. Feedback Explorer
3. Feedback Detail / Classification
4. Review Queue
5. CX Overview
6. Customer Journey
7. Service & Pain Points
8. Hotspot & Root Cause
9. Imports
10. Data Quality
11. Taxonomy Admin
12. Audit
```

---

# 68A. Quy tắc Triển khai Wireframe (Wireframe Implementation Rule)

Bốn wireframe dashboard trong tài liệu đặc tả này là **các tham chiếu bố cục chuẩn hóa cho P0 (normative layout references for P0)**.

Kỹ thuật/thiết kế CÓ THỂ điều chỉnh:

- phong cách trực quan (visual styling);
- kiểu chữ (typography);
- khoảng cách (spacing);
- hệ thống biểu tượng (iconography);
- thư viện biểu đồ cụ thể (exact chart library);
- sắp xếp đáp ứng (responsive arrangement).

Kỹ thuật/thiết kế KHÔNG NÊN thay đổi nếu không có sự đánh giá từ phía sản phẩm/thiết kế:

- mục đích của dashboard;
- cấu trúc phân cấp thông tin;
- mức độ nổi bật của Customer Journey;
- trình tự khoan sâu (drill-down sequence);
- mối quan hệ Service → Issue;
- khả năng truy cập Bằng chứng (Evidence access);
- sự tách biệt giữa Candidate Cause và Confirmed Root Cause;
- điều hướng từ dashboard sang workspace;
- tính duy trì của bộ lọc đã quản trị.

Khi các chi tiết triển khai bị mơ hồ, hãy sử dụng wireframe tương ứng cùng với các yêu cầu của phần đó để làm hành vi dự kiến cho P0.

---

# 69. Lát cắt Dọc Đầu tiên (First Vertical Slice)

Xây dựng điều này trước tiên:

```text
Taxonomy Seed
↓
Import 50–100 Feedback records
↓
Feedback Explorer
↓
AI Prediction
↓
Human Review
↓
Classification Current
↓
CX Overview
↓
Customer Journey drill-down
```

Điều này xác thực:

```text
Data
→ Taxonomy
→ API
→ Review
→ Analytics
→ CX UI
```

trước khi triển khai quy trình nguyên nhân gốc rễ nâng cao.

---

# 70. Tiêu chí Nghiệm thu UI/UX P0 (P0 UI/UX Acceptance Criteria)

UI/UX được coi là sẵn sàng xây dựng (build-ready) khi:

1. Sản phẩm trông và hoạt động rõ ràng như một Nền tảng CX (CX Platform), không phải một công cụ quản lý ticket.
2. 6 giai đoạn Customer Lifecycle là trung tâm của trải nghiệm.
3. Người dùng có thể khoan sâu từ Stage → Step → Service → Issue → Feedback.
4. Bốn dashboard trả lời bốn câu hỏi CX riêng biệt.
5. Feedback luôn có sẵn làm bằng chứng đằng sau các thông tin phân tích tổng hợp.
6. Customer Lifecycle và Service Request Lifecycle được tách biệt rõ ràng về mặt trực quan.
7. AI Prediction khác biệt rõ ràng về mặt trực quan so với Classification đã được chấp nhận.
8. Issue khác biệt rõ ràng so với Candidate Cause; Confirmed Root Cause vắng mặt ở P0 và phân biệt rõ ràng khi P1 được bật.
9. P0 Hotspot hiển thị bằng chứng, người phụ trách/trạng thái và Candidate Cause mà không có đột biến RCA; Investigation → Root Cause → Action là dành riêng cho P1.
10. Bộ lọc Analytics duy trì qua các thao tác khoan sâu dashboard.
11. Các nhãn Taxonomy được tải từ API, không hard-code.
12. PII được ẩn danh theo mặc định.
13. Xung đột phiên bản không thể ghi đè âm thầm lên công việc của người duyệt khác.
14. Service giới hạn phạm vi của Issue.
15. Customer Lifecycle Stage được suy ra từ Step.
16. Số liệu dashboard và khoan sâu sử dụng cùng logic tính điều kiện dữ liệu phân tích.
17. Phân rã Journey Step và Service/Issue hiển thị Feedback Volume, Negative Rate, Active Hotspots và Trend từ hợp đồng API đa chỉ số.
18. Persona không được hiển thị như một bộ lọc P0; Intake Channel và Affected Channel là các bộ lọc riêng biệt được hỗ trợ.
19. Review Queue gửi chính xác 7 giá trị hành động chuẩn hóa và phản ánh hành vi Decision-so-với-ReviewEvent.
20. UI hỗ trợ hiệu quả việc phân tích trên màn hình desktop rộng.
21. Các quy trình làm việc cốt lõi có trạng thái đang tải (loading), trống (empty), lỗi (error) và phân quyền (permission).
22. Tất cả các đột biến vận hành đều ánh xạ tới các endpoint API đã được xác định.
23. UI có thể được triển khai mà không cần thay đổi mô hình tên miền (domain model).

---

# 71. Các Điểm Mở rộng P1 (P1 Extension Points)

Các phiên bản sau có thể thêm:

- mô hình CX Score / CX Health chính thức;
- phân khúc nhân vật (persona segmentation);
- tích hợp NPS/CSAT/CES;
- so sánh hành trình giữa các dự án;
- phát hiện bất thường (anomaly detection);
- dashboard đã lưu;
- trung tâm thông báo (notification center);
- hộp thư đến SLA/leo thang;
- trực quan hóa địa lý/bản đồ;
- theo dõi hiệu quả hành động;
- tác động CX trước/sau;
- đồ thị kiến thức RCA nâng cao;
- bình luận cộng tác;
- quy trình vận hành trên di động;
- giám sát sức khỏe đầu nối (connector health monitoring);
- quy trình chỉnh sửa taxonomy.

Những điểm này phải duy trì luồng phân tích P0:

```text
Experience
→ Journey
→ Pain Point
→ Evidence
→ Root Cause
→ Improvement
```