# 07 — UI/UX Specification

# CX Journey, Service & Root Cause Intelligence Platform

**Version:** 2.1  
**Status:** P0 CX-First UI/UX Baseline  
**Scope:** Desktop-first CX Intelligence Platform  
**Primary Users:** CX Manager, CX Analyst, Reviewer, Operations Manager, Pilot Admin  
**Derived from:** `PRD.md` v1.3, `service_taxonomy.md` v3.0.0, `Business_Rules.md` v1.1, `System_Design.md` v1.1, `05_Data_Model.md` v1.1, `06_API_Specification.md` v1.1

---

# 1. Purpose

This document defines the UI/UX architecture for the P0 CX Platform.

The product must present itself as a **Customer Experience Intelligence Platform**, not as a ticket-management system.

The UI must guide users through the following business question chain:

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

The P0 UI is therefore organized around:

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

Operational workspaces such as Feedback Explorer, Review Queue and Imports support this intelligence flow but are not treated as primary dashboards.

---

# 2. Core UX Positioning

## 2.1 Product Identity

The product is:

> A CX Intelligence & Operations Platform that connects customer journey, customer feedback, service failures, hotspots, root causes and improvement actions.

The product is NOT primarily:

- a helpdesk;
- a CRM;
- a ticketing application;
- a CMMS;
- an ERP dashboard;
- a social listening dashboard.

The UI must therefore prioritize:

1. Customer Experience
2. Customer Journey
3. Pain Point
4. Evidence
5. Root Cause
6. Improvement

instead of:

```text
Ticket → Status → Assignee
```

---

# 3. UX Principles

## UX-001 — Customer Journey Is the Primary Lens

The Customer Lifecycle must be visible as a first-class navigation and analysis structure.

Canonical stages:

```text
Nhận thức
→ Xem xét
→ Giao dịch
→ Nhận nhà
→ Cư trú
→ Vận hành
```

The UI must allow the user to move from Stage → Step → Service → Issue → Feedback.

---

## UX-002 — Evidence Before Interpretation

Users should always be able to drill from aggregated CX insight to underlying Feedback Items.

Example:

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

No KPI or hotspot should exist as a dead-end metric.

---

## UX-003 — Separate Observed Problem from Cause

The UI must distinguish:

```text
Issue
= observed problem / failure pattern

Candidate Cause
= investigation hypothesis

Confirmed Root Cause
= evidence-backed conclusion
```

AI suggestions must never be presented as confirmed root cause.

---

## UX-004 — AI Suggestion ≠ Accepted Truth

The UI must visually distinguish:

```text
AI Prediction
Human/Source Decision
Current Classification
```

AI suggestions can help reviewers but must not look automatically accepted.

---

## UX-005 — Customer Lifecycle ≠ Service Request Lifecycle

The UI must present two separate dimensions:

```text
Customer Lifecycle
Service Request Lifecycle
```

Example:

```text
Customer Lifecycle:
RES-07 · Gửi yêu cầu / phản ánh / sự cố

Service Request Lifecycle:
SRV-02 · Gửi yêu cầu
```

An `SRV-*` value must never appear inside Customer Journey navigation.

---

## UX-006 — Analytics Must Tell a Story

Each dashboard must answer one clear question.

The four P0 dashboards are:

```text
01 CX Overview
02 Customer Journey
03 Service & Pain Points
04 Hotspot & Root Cause
```

Together they form one analytical story rather than four disconnected dashboards.

---

## UX-007 — Wide Enterprise Workspace

The desktop UI should use a wide-frame enterprise layout.

Recommended desktop composition:

```text
Sidebar: 200–240px
Content: remaining width
Max content width: none or very high
Primary dashboard grid: 12 columns
```

Avoid:

- excessive small cards;
- overly decorative widgets;
- consumer-app layouts;
- oversized whitespace;
- cards with no drill-down purpose.

Prefer:

- wide analysis tables;
- ranked lists;
- large trend charts;
- journey visualization;
- side-by-side evidence panels;
- dense but readable operational data.

---

# 4. Information Architecture

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

# 5. Global Application Shell

## 5.1 Left Sidebar

Recommended navigation:

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

Optional badge examples:

```text
Review Queue   128
Hotspots         7
Imports           1
```

---

## 5.2 Top Bar

Contains:

```text
Project Selector
Global Search
Date Context
User / Role
```

Project selector must enforce authorized scope.

Example:

```text
Vinhomes Symphony ▼
```

---

# 6. Global Filter Model

All dashboards should share a consistent filter vocabulary.

Primary filters:

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

Context-sensitive rules:

```text
Stage → narrows Journey Step
Service → narrows Issue
Issue → belongs to selected Service
Location → hierarchical selector
```

Filter chips should show stable code + localized label.

Example:

```text
Service:
SV-07 · Kỹ thuật, tiện ích & tài sản chung
```

---

# 7. Dashboard 01 — CX Overview

## 7.1 Purpose

Answer:

> Customer Experience overall đang như thế nào, và đâu là vùng trải nghiệm cần chú ý nhất?

Route:

```text
/overview
```

---

## 7.2 Primary Layout

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

## 7.3 KPI Summary

P0 cards:

```text
Negative Rate
Feedback Volume
Active Hotspots
Unknown / Ineligible Rate
```

Optional secondary metrics:

```text
Unknown Rate
Pending Reviews
Top Service
Top Journey Stage
```

`CX Score` và `CX Health Index` không phải P0 KPI vì chưa có formula được phê duyệt. Không dùng hai nhãn này trên card, chart, status hoặc navigation P0.

---


## 7.4 Reference Wide-Frame Wireframe

> Wireframe này là **bố cục tham chiếu cho implementation**, không phải final visual design. Dev/design có thể thay đổi typography, spacing, component styling nhưng phải giữ hierarchy thông tin và drill-down logic.

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

### Wireframe Interaction Contract

```text
Click Journey Stage
→ Customer Journey Dashboard
→ preserve Project / Date / Location filters

Click Pain Point
→ Service & Pain Points Dashboard
→ preserve Service / Issue context

Click Hotspot
→ Hotspot & Root Cause Dashboard
→ open selected hotspot

Click KPI / Trend point
→ Feedback Explorer
→ same governed filter context
```

---

# 8. CX Overview — Customer Journey Hero

The central visual of the overview should be the six lifecycle stages.

Example:

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

Desktop layout:

```text
┌────────────┐ → ┌────────────┐ → ┌────────────┐ → ┌────────────┐ → ┌────────────┐ → ┌────────────┐
│ NHẬN THỨC │   │ XEM XÉT    │   │ GIAO DỊCH │   │ NHẬN NHÀ  │   │ CƯ TRÚ     │   │ VẬN HÀNH  │
│ Neg 12%    │   │ Neg 18%    │   │ Neg 27%    │   │ Neg 31%    │   │ Neg 42%    │   │ Neg 35%    │
└────────────┘   └────────────┘   └────────────┘   └────────────┘   └────────────┘   └────────────┘
```

Clicking any stage:

```text
→ Customer Journey Dashboard
→ selected Stage preserved
→ same global filter context
```

---

# 9. CX Overview — Experience Trend

Recommended chart:

```text
Time-series line chart
```

Toggle metric:

```text
Feedback Volume
Negative Rate
Unknown Rate
Hotspot Count
```

Optional comparison:

```text
Previous period
MoM
YoY
```

Tooltip:

```text
Date
Metric value
Delta
Feedback count
```

Click point:

```text
→ Feedback Explorer
→ same date window/filter context
```

---

# 10. CX Overview — Top Pain Points

Rank pain points by:

```text
Issue
+ volume
+ negative rate
+ trend
+ hotspot signal
```

Example:

```text
1. Elevator waiting                 1,490
2. Resident app login / OTP         1,120
3. Payment not recorded               860
4. Parking access failure             620
```

Click:

```text
→ Service & Pain Points Dashboard
→ pre-select Issue / Service
```

---

# 11. CX Overview — Emerging Hotspots

Columns:

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

Example:

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

Click:

```text
→ Hotspot & Root Cause Dashboard
→ selected hotspot
```

---

# 12. Dashboard 02 — Customer Journey

## 12.1 Purpose

Answer:

> Khách hàng gặp khó khăn ở Stage và Step nào trong lifecycle?

Route:

```text
/customer-journey
```

---

## 12.2 Layout

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

### Drill-Down Contract

```text
Stage
→ Step
→ Related Services
→ Issues
→ Feedback Evidence
```

The dashboard MUST NOT imply that one Journey Step maps to exactly one Service.

---

# 13. Customer Journey — Stage Selector

Use the six canonical stages.

When a stage is selected, the UI expands its canonical steps.

Example:

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

# 14. Journey Step Card

Each Journey Step card shows:

```text
Step code
Step name
Feedback Volume
Negative Rate
Active Hotspots
Trend
```

Example:

```text
RES-03
Ra vào & di chuyển

2,140 feedback
51% negative
3 hotspots
↑ 22%
```

Click:

```text
→ Journey Step Detail section
```

---

# 15. Journey Step Drill-Down

Selected Journey Step shows:

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

Important:

Journey Step and Service are N:N.

Therefore UI must not imply:

```text
RES-03 = one fixed Service
```

Instead:

```text
RES-03
   ↓
Possible / observed related Services
```

---

# 16. Dashboard 03 — Service & Pain Points

## 16.1 Purpose

Answer:

> Service nào đang tạo trải nghiệm xấu, và khách hàng đang gặp Issue gì?

Route:

```text
/service-pain-points
```

---

## 16.2 Layout

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

`Pain Point` is an analytical/display concept. It MUST NOT automatically create a new taxonomy Issue.

---

# 17. Service Performance Table

Columns:

```text
Service
Feedback Volume
Negative Rate
Active Hotspots
Trend
Top Issue
```

Example:

```text
SV-07 Engineering
3,620
48%
3 hotspots
↑21%
IS-07-01
```

---

# 18. Selected Service Detail

Example:

```text
SV-07
Kỹ thuật, tiện ích & tài sản chung
```

Show canonical issues:

```text
IS-07-01
System Outage or Degradation

IS-07-02
Leakage or Unsafe Technical Condition

IS-07-03
Common Asset or Maintenance Failure
```

Each Issue card:

```text
Feedback count
Negative rate
Locations affected
Active hotspots
Trend
```

---

# 19. Pain Point Representation

In UI copy:

```text
Pain Point
```

may represent a human-readable combination of:

```text
Issue
+ symptom_detail
+ context
```

Example:

```text
Issue:
IS-07-01 System Outage or Degradation

Pain Point:
“Chờ thang máy lâu vào giờ cao điểm”
```

Important:

Do not create a new canonical Issue for every symptom.

`Pain Point` is a UI/analysis concept; canonical taxonomy remains at Service + Issue level.

---

# 20. Top Symptoms

Use `symptom_detail` aggregation/clustering.

Example:

```text
Chờ thang máy lâu
Thang dừng bất thường
Không gọi được thang
Áp lực nước yếu
Điều hòa khu chung không ổn
```

These should not automatically become new taxonomy labels.

---

# 21. Location Distribution

Show where the pain point occurs.

Possible views:

```text
Project
Building
Zone
Floor
```

P0 may use:

- ranked bar chart;
- table;
- simple heat ranking.

GIS/map is P1 unless exact geospatial analysis is needed.

---

# 22. Voice of Customer

Show representative masked feedback.

Example:

```text
“Buổi sáng đi làm phải chờ thang gần 10 phút.”

“App cư dân thường xuyên không nhận OTP.”

“Đã thanh toán nhưng phí vẫn hiển thị chưa trả.”
```

Each feedback snippet includes:

```text
Sentiment
Source
Date
Location
```

Click:

```text
→ Feedback Explorer / Item Detail
```

---

# 23. Dashboard 04 — Hotspot & Root Cause

## 23.1 Purpose

Answer:

> Pain Point nào đang trở thành vấn đề vận hành, vì sao nó xảy ra, và doanh nghiệp đang xử lý thế nào?

Route:

```text
/hotspot-root-cause
```

---

## 23.2 Layout

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

### Intelligence-to-Action Contract

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

P0 MUST NOT render P1 controls as enabled or imply Candidate Cause is confirmed. When P1 is enabled, the UI MUST show each workflow stage and must not visually skip directly from AI hypothesis to confirmed root cause.

---

# 24. Active Hotspots Table

Columns:

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

Default sort:

```text
SEV-1
→ SEV-2
→ newest/highest trend
```

---

# 25. Selected Hotspot — Customer Pain Context

Example:

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

# 26. Selected Hotspot — Evidence

Evidence panel may include:

```text
Feedback Items
Source distribution
Time pattern
Location pattern
```

P0 uses linked Feedback Items as reproducible hotspot evidence. Operational records, BMS/CMMS references and inspection evidence are introduced with Investigation in P1.

---

# 27. Candidate Causes

Show hypotheses only.

Example:

```text
Peak-hour capacity overload          72%
Dispatch configuration               61%
One elevator unavailable             47%
```

Display label:

```text
Candidate Cause
```

Never:

```text
Root Cause
```

before confirmation.

---

# 28. P1 Only — Investigation Timeline

This section is not rendered, routed or called by P0.

Visual flow:

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

Timeline events:

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

# 29. P1 Only — Confirmed Root Cause

Only display when investigation confirms it.

Example:

```text
Confirmed Root Cause

1/4 elevator unavailable
+
dispatch configuration not optimized for morning peak.
```

Include:

```text
Confirmed by
Confirmed at
Evidence summary
```

---

# 30. P1 Only — Action / Improvement Section

Sections:

```text
Corrective Actions
Preventive Actions
```

Each action shows:

```text
Description
Owner
Due Date
Status
Verification
```

Example:

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

## 31.1 Purpose

Operational drill-down to individual evidence.

Route:

```text
/feedback
```

Layout:

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

Recommended width:

```text
65% list
35% detail
```

---

# 32. Feedback Explorer Table

Columns:

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

Optional columns:

```text
Source
Service Request Step
Hotspot Link
```

---

# 33. Feedback Item Detail

Display:

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

Raw content is hidden by default.

---

# 34. Classification Review Panel

Sections:

```text
Customer Lifecycle
Service Request Lifecycle
Primary Service
Issue
Sentiment
Operational Severity
Candidate Causes
```

Important UI behavior:

### Customer Lifecycle

```text
Value Status
Step
Derived Stage
```

Stage is read-only and derived from Step.

### Service Request Lifecycle

Separate group:

```text
Value Status
Step
```

### Primary Service / Issue

Issue selector is constrained by selected Service.

---

# 35. AI Suggestion Pattern

Example:

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

Current accepted value must have a different visual treatment.

---

# 36. Version Conflict UX

When another reviewer has updated the item:

```text
This item was updated by another reviewer.

Your version: 3
Current version: 4

[Reload Latest]
[Copy My Notes]
```

Never silently overwrite.

---

# 37. Split Multi-Intent Feedback

Action:

```text
Split Feedback
```

Use when one source feedback contains multiple independent issues.

Example:

```text
“Thang máy chậm và app không đăng nhập được.”
```

Split into:

```text
Item 1
Thang máy chậm

Item 2
App không đăng nhập được
```

Rules shown in UI:

```text
Original Feedback remains unchanged.
Historical decisions remain available.
Child items are classified independently.
```

---

# 38. Workspace 02 — Review Queue

Route:

```text
/review
```

Purpose:

> Review AI suggestions efficiently while preserving human control.

Layout:

```text
Queue List | Review Panel
```

Queue priority:

```text
Hard trigger / safety
→ SEV-1
→ SEV-2
→ oldest pending
→ low confidence
```

---

# 39. Review Queue Actions

Allowed:

```text
ACCEPT
CORRECT
MARK_UNKNOWN
MARK_MISSING
MARK_NOT_APPLICABLE
SPLIT_REQUIRED
SKIP
```

UI labels may be localized/title-cased, but submitted wire values are exactly those above. The first five actions create ClassificationDecision + ReviewEvent; `SPLIT_REQUIRED` and `SKIP` create only ReviewEvent. “Save & Next” is navigation after a successful action, not a review action.

Do not allow blind bulk acceptance of AI classification in P0.

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

Fields:

```text
Project
Source System
File
Mapping Profile
```

Display:

```text
Filename
File size
Checksum
```

---

# 42. Import Mapping

Two-column mapping:

```text
Source Column
→
Platform Field
```

Example:

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

Summary:

```text
18,546 total
18,110 valid
436 invalid
```

Error table:

```text
Row
Field
Error Code
Message
```

No Feedback is committed before Execute.

---

# 44. Governance — Data Quality

Route:

```text
/data-quality
```

Purpose:

> Monitor whether analytics and AI are trustworthy enough to use.

Metrics:

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

# 45. Governance — Taxonomy

Route:

```text
/admin/taxonomy
```

P0 supports governance, not arbitrary production CRUD.

Display:

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

Actions:

```text
Validate
View
Publish
```

---

# 46. Governance — Audit

Route:

```text
/admin/audit
```

Columns:

```text
Time
Actor
Role
Action
Resource
Reason
Correlation ID
```

Do not expose raw feedback in audit table.

---

# 47. CX Score / CX Health Metric Policy

P0 MUST NOT display `CX Score` or `CX Health` as an official KPI because no formula is approved.

Possible score inputs may include:

```text
Negative Rate
Severity
Hotspot Penalty
Resolution Improvement
Unknown/Data Quality Penalty
```

This UI spec does NOT define or approve the business formula. A future version may add the metric only after governance approval and versioned API/metric-definition support.

Until approved, use explicit metrics:

```text
Negative Rate
Feedback Volume
Hotspots
Trend
```

instead of inventing a composite CX Score.

---

# 48. Customer Journey Visualization Rules

Customer Journey must remain understandable at two levels:

## Level 1 — Stage

```text
6 stages
```

## Level 2 — Step

```text
36 canonical steps
```

The UI should never display all 36 steps at once on the Overview.

Instead:

```text
Overview
→ 6 Stages

Customer Journey Dashboard
→ selected Stage
→ its Steps
```

This avoids information overload.

---

# 49. Service Request Lifecycle Visualization

Service Request Lifecycle is a secondary dimension.

It should appear primarily in:

```text
Feedback Explorer
Review
Journey Step detail
Service detail
```

Do not make it compete visually with the main Customer Lifecycle hero.

---

# 50. Responsive Strategy

Primary target:

```text
Desktop / large laptop
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

P0 supports:

```text
Read
Basic drill-down
Hotspot summary
```

but does not promise full high-density reviewer productivity.

---

# 51. Accessibility

Minimum P0:

1. Keyboard navigation.
2. Visible focus state.
3. Labels on all form fields.
4. Status/severity not represented by color only.
5. Accessible table headers.
6. Chart textual summary.
7. Modal focus trap.
8. WCAG 2.1 AA target for primary workflows.

---

# 52. Loading States

Use skeletons for:

```text
KPI
Journey cards
Charts
Tables
Detail panels
```

When filters change:

```text
Keep previous result visible
Show loading state
Replace after response
```

Avoid full-page blank loading.

---

# 53. Empty States

Examples:

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

# 54. Error States

Example:

```text
Couldn't load Customer Journey data.

Request ID: ...
[Retry]
```

Field-level domain errors must appear next to the relevant field.

---

# 55. PII UX

Default:

```text
Masked content
```

Privileged raw view:

```text
View Raw Content
    ↓
Reason required
    ↓
Audited API request
    ↓
Temporary raw display
```

Raw content must not be included in:

- URLs;
- analytics events;
- standard browser telemetry;
- normal dashboard tables.

---

# 56. UI Component System

Core reusable components:

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

# 57. Design Language

The visual style should be:

```text
Professional
Analytical
Enterprise
Calm
Evidence-driven
Modern but not decorative
```

Avoid:

```text
bright consumer gradients everywhere
excessive glassmorphism
large rounded cards for every metric
gaming-style heatmap colors
UI that resembles a helpdesk SaaS
```

Prefer:

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

# 58. Dashboard Hierarchy

Each dashboard should follow:

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

Example:

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

# 59. Navigation Between Dashboards

Required deep-link flow:

```text
CX Overview
→ Customer Journey
→ Service & Pain Points
→ Hotspot & Root Cause
→ Feedback Evidence
```

Filters must persist where semantically applicable.

Example:

```text
Project = Symphony
Date = last 30 days
Location = S2
```

must remain active when moving between dashboards.

---

# 60. URL Routes

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

Do not put raw PII in URLs.

---

# 61. API Mapping

| UI Surface | API |
|---|---|
| CX Overview | `/analytics/summary`, `/analytics/trend`, `/analytics/breakdown`, `/hotspots` |
| Customer Journey | `/analytics/breakdown?dimension=journey_stage&metrics=item_volume,negative_rate,active_hotspots,trend`, same contract for `journey_step` |
| Service & Pain Points | `/analytics/breakdown?dimension=service&metrics=item_volume,negative_rate,active_hotspots,trend`, same contract for `issue`, plus `/feedback-items` |
| Hotspot & RCA [P0] | `/hotspots`, `/hotspots/{id}` |
| Investigation/RCA [P1 only] | `/investigations/{id}` and P1 mutation endpoints |
| Feedback Explorer | `/feedback-items`, `/feedback-items/{id}` |
| Review Queue | `/review-queue`, `/ai/predictions/{id}/review`, `/feedback-items/{id}/decisions` |
| Imports | `/import-jobs/*` |
| Data Quality | `/analytics/data-quality` |
| Taxonomy | taxonomy endpoints |
| Audit | `/audit-events` |

---

# 62. Main User Flow — Manager

```text
Open CX Overview
↓
See Cư trú has highest negative rate
↓
Open Customer Journey
↓
Select RES-03 Ra vào & di chuyển
↓
See SV-07 / IS-07-01 concentration
↓
Open Service & Pain Points
↓
See Elevator Waiting is top symptom
↓
Open Hotspot & Root Cause
↓
See S2 hotspot
↓
Review evidence, owner/status and Candidate Causes
```

---

# 63. Main User Flow — CX Analyst

```text
Open CX Overview
↓
Identify trend anomaly
↓
Drill into Journey
↓
Compare Service / Issue
↓
Open representative feedback
↓
Validate insight
↓
Prepare operational recommendation
```

---

# 64. Main User Flow — Reviewer

```text
Open Review Queue
↓
Read Feedback evidence
↓
Review AI suggestions
↓
Submit one canonical review action
↓
Save Decision
↓
Current Classification updated
↓
Analytics reflects accepted item
```

---

# 65. Main User Flow — Operations Manager

```text
Open Hotspot & Root Cause
↓
Review evidence
↓
Acknowledge hotspot
↓
Assign owner
↓
Update hotspot status / resolve or dismiss

P1 extension:
Start Investigation → add evidence → confirm Root Cause → track Corrective/Preventive Actions
```

---

# 66. Main User Flow — Data Admin

```text
Upload file
↓
Map columns
↓
Preview
↓
Validate
↓
Execute
↓
Review data quality
↓
Run prediction
↓
Monitor unknown / other rate
```

---

# 67. P0 Screen Inventory

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

Total:

```text
4 dashboards
+
4 operational workspaces
+
3 governance screens
=
11 primary P0 screens
```

---

# 68. P0 Build Priority

Recommended frontend order:

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


# 68A. Wireframe Implementation Rule

The four dashboard wireframes in this specification are **normative layout references for P0**.

Engineering/design MAY adjust:

- visual styling;
- typography;
- spacing;
- iconography;
- exact chart library;
- responsive arrangement.

Engineering/design SHOULD NOT change without product/design review:

- dashboard purpose;
- information hierarchy;
- Customer Journey prominence;
- drill-down sequence;
- Service → Issue relationship;
- Evidence access;
- Candidate Cause vs Confirmed Root Cause separation;
- dashboard-to-workspace navigation;
- governed filter persistence.

When implementation details are ambiguous, use the corresponding wireframe plus the section requirements together as the intended P0 behavior.

---

# 69. First Vertical Slice

Build this first:

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

This validates:

```text
Data
→ Taxonomy
→ API
→ Review
→ Analytics
→ CX UI
```

before implementing advanced root cause workflow.

---

# 70. P0 UI/UX Acceptance Criteria

The UI/UX is considered build-ready when:

1. The product clearly looks and behaves like a CX Platform, not a ticketing tool.
2. The 6 Customer Lifecycle stages are central to the experience.
3. Users can drill Stage → Step → Service → Issue → Feedback.
4. The four dashboards answer four distinct CX questions.
5. Feedback is always available as evidence behind aggregated insights.
6. Customer Lifecycle and Service Request Lifecycle are visually separate.
7. AI Prediction is visibly different from accepted Classification.
8. Issue is visibly different from Candidate Cause; Confirmed Root Cause is absent in P0 and distinct when P1 is enabled.
9. P0 Hotspot shows evidence, owner/status and Candidate Cause without RCA mutations; Investigation → Root Cause → Action is P1-only.
10. Analytics filters persist across dashboard drill-down.
11. Taxonomy labels are loaded from API, not hard-coded.
12. PII remains masked by default.
13. Version conflicts cannot silently overwrite another reviewer.
14. Service constrains Issue.
15. Customer Lifecycle Stage is derived from Step.
16. Dashboard and drill-down counts use the same analytics eligibility logic.
17. Journey Step and Service/Issue breakdowns show Feedback Volume, Negative Rate, Active Hotspots and Trend from the multi-metric API contract.
18. Persona is not shown as a P0 filter; Intake Channel and Affected Channel are distinct supported filters.
19. Review Queue submits exactly seven canonical action values and reflects Decision-versus-ReviewEvent behavior.
20. The UI supports wide desktop analysis efficiently.
21. Core workflows have loading, empty, error and permission states.
22. All operational mutations map to defined API endpoints.
23. The UI can be implemented without changing the domain model.

---

# 71. P1 Extension Points

Later versions may add:

- formal CX Score / CX Health model;
- persona segmentation;
- NPS/CSAT/CES integrations;
- journey comparison across projects;
- anomaly detection;
- saved dashboards;
- notification center;
- SLA/escalation inbox;
- geographic/map visualization;
- action effectiveness tracking;
- before/after CX impact;
- advanced RCA knowledge graph;
- collaborative comments;
- mobile operations workflow;
- connector health monitoring;
- taxonomy editing workflow.

These must preserve the P0 analytical flow:

```text
Experience
→ Journey
→ Pain Point
→ Evidence
→ Root Cause
→ Improvement
```
