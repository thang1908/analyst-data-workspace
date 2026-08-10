# 00 — Bắt đầu từ đây

- **Sản phẩm:** CX Journey, Service & Root Cause Intelligence Platform
- **Phiên bản hướng dẫn:** 0.1
- **Trạng thái:** Active — Build Baseline
- **Đối tượng:** Product, BA, UX, Engineering, Data/AI, QA, Security, Operations
- **Cập nhật:** 2026-08-10

## 1. Mục đích

Tài liệu này là bản đồ đọc tài liệu và điểm vào chung cho mọi người tham gia build nền tảng CX.

Mục tiêu của bộ tài liệu là để một thành viên mới có thể trả lời được bốn câu hỏi trước khi bắt đầu làm việc:

1. Sản phẩm giải quyết vấn đề gì và MVP không làm gì?
2. Các khái niệm Journey, Service, Issue, Candidate Cause và Root Cause khác nhau thế nào?
3. Feature hiện tại phải đi xuyên UI, API, data, security, test và vận hành ra sao?
4. Tài liệu nào là source of truth khi có khác biệt?

## 2. Thứ tự đọc bắt buộc

Đọc theo thứ tự sau trước khi nhận feature đầu tiên:

1. [PRD](./PRD.md) — mục tiêu sản phẩm, persona, user story, phạm vi P0/P1/P2 và non-goal.
2. [Service Taxonomy](./service_taxonomy.md) — dictionary Journey, Service, Issue, Cause Group và mapping baseline.
3. [ADR-001: Hai chiều Lifecycle độc lập](./architecture/adr/ADR-001-journey-dimensions.md) — cách mô hình hóa Customer Lifecycle và Service Request Lifecycle.
4. [ADR-002: Mô hình Classification](./architecture/adr/ADR-002-classification-model.md) — cách tách raw feedback, feedback item, prediction, decision và current projection.
5. [Build Rules](./BUILD_RULES.md) — quy tắc kiến trúc, data, API, security, AI, test, observability và release.
6. [FEAT-001: Elevator Manual Intake-to-Insight](./features/FEAT-001-elevator-manual-slice.md) — vertical slice đầu tiên để kiểm chứng toàn bộ nền tảng.

Khi làm một feature cụ thể, luôn đọc lại PRD/taxonomy liên quan, ADR áp dụng, Build Rules và feature spec. Không bắt đầu từ mockup hoặc API riêng lẻ mà bỏ qua domain rule.

## 3. Trạng thái tài liệu hiện tại

| Tài liệu | Trạng thái | Ý nghĩa |
| --- | --- | --- |
| PRD v1.1 | Pilot Build Baseline / Pending Named Stakeholder Decisions | Có thể dùng để lập backlog pilot; các decision được đánh dấu `Blocks P0` phải đóng trước build/release tương ứng. |
| Service Taxonomy v1.0.0 | Draft / Pilot Baseline | Có thể dùng làm seed/pilot; SLA, handling unit, severity, hard trigger và evidence vẫn cần owner xác nhận. |
| ADR-001 | Accepted cho MVP baseline | Hai chiều Journey được lưu và phân tích độc lập. |
| ADR-002 | Accepted cho MVP baseline | Prediction không phải decision; raw feedback không bị sửa. |
| Build Rules | Active | Áp dụng cho mọi feature mới và mọi pull request. |
| FEAT-001 | Ready for refinement | Chỉ được kéo vào sprint khi pass Definition of Ready trong feature spec. |

Các trạng thái chuẩn dùng trong bộ tài liệu:

- `Proposed`: đang xin ý kiến, chưa được dùng làm quyết định cuối.
- `Accepted`: đã là quyết định baseline; muốn thay đổi phải tạo ADR hoặc phiên bản mới.
- `Ready for refinement`: scope đã đủ để refinement nhưng còn checklist DoR cần xác nhận.
- `Ready for build`: đã pass DoR và có owner thực thi.
- `In delivery`: đang được build/test.
- `Pilot`: đã phát hành cho phạm vi pilot có kiểm soát.
- `Done`: đạt Definition of Done và tiêu chí release đã duyệt.
- `Deprecated`: không dùng cho thay đổi mới; phải có tài liệu thay thế.

## 4. Source of truth

| Nội dung | Source of truth | Ghi chú |
| --- | --- | --- |
| Product outcome, persona, priority, MVP/non-goal | [PRD](./PRD.md) | Feature spec không được tự mở rộng phạm vi sản phẩm. |
| Giá trị Journey, Service, Issue, Cause Group baseline | [Service Taxonomy](./service_taxonomy.md) | Khi có seed machine-readable, seed + validator là nguồn thực thi; Markdown được generate hoặc đối soát từ nguồn đó. |
| Cách diễn giải domain còn mơ hồ | ADR đã `Accepted` | ADR được dùng để giải quyết mâu thuẫn hoặc khoảng trống trong PRD/taxonomy. |
| Hành vi của một feature | Feature spec tương ứng | Acceptance criteria phải truy vết được về PRD và ADR. |
| API runtime | OpenAPI đã review | Ví dụ endpoint trong PRD/feature spec không thay thế OpenAPI. |
| Database runtime | Migration + constraint đã review | ERD/tài liệu mô tả phải khớp migration. |
| Metric runtime | Metric Catalog phiên bản đã duyệt | Mọi dashboard phải dùng cùng numerator, denominator, event time và exclusion rule. |
| Engineering/delivery policy | [Build Rules](./BUILD_RULES.md) | Ngoại lệ cần ghi rõ lý do và người phê duyệt trong ADR/feature spec. |

Khi hai source of truth mâu thuẫn:

1. Dừng phần implementation bị ảnh hưởng; không tự chọn cách hiểu thuận tiện nhất.
2. Ghi vấn đề vào feature spec hoặc open-decision log với ví dụ dữ liệu cụ thể.
3. Nếu thay đổi domain/architecture dùng lâu dài, tạo ADR.
4. Sau khi quyết định, cập nhật tất cả contract và link liên quan trong cùng change set hoặc tạo follow-up có owner rõ.

Yêu cầu security, privacy, legal và policy đã được phê duyệt luôn có ưu tiên cao hơn hành vi sản phẩm cũ.

## 5. Feature map

### P0 — MVP foundation và intelligence

| Nhóm | Outcome | Trạng thái |
| --- | --- | --- |
| Identity & Governance | SSO/RBAC tối thiểu, scope theo project/building/service, privileged audit | Planned — bắt buộc trước pilot |
| Taxonomy & Location | Versioned Journey/Service/Issue mapping và location hierarchy | Planned |
| Feedback Intake | CSV/XLSX intake có validate, idempotency, raw record và job audit | CSV đầu tiên nằm trong FEAT-001; realtime API thuộc P1 |
| Manual Classification | Operator tạo/correct accepted classification có audit | [FEAT-001](./features/FEAT-001-elevator-manual-slice.md) |
| Feedback Workspace | List, filter, detail, masked/raw access theo quyền | Bắt đầu trong FEAT-001 |
| AI Classification & Review | Prediction, confidence, review queue, correction dataset | Follow-up sau FEAT-001 |
| Journey/Service Analytics | Metric có định nghĩa, mọi chart drill-down về feedback | Basic insight bắt đầu trong FEAT-001 |
| Hotspot MVP | Rule deterministic theo Service + Issue + Location + Time | Follow-up sau analytics baseline |
| Data Quality | Missing/invalid/duplicate/unknown/low-confidence visibility | Tích lũy theo từng slice |

### P1/P2 — Chưa đưa vào vertical slice đầu tiên

- Ticket, assignment, SLA và escalation.
- Generalized hotspot/anomaly engine, hard trigger và outbound alert; P0 chỉ có lifecycle/owner tối thiểu cho deterministic pilot rule.
- Asset registry, work-order, BMS/IoT và CMMS integration.
- Candidate Cause AI suggestion.
- Investigation, confirmed Root Cause, corrective/preventive action.
- Predictive maintenance, Customer 360 và AI CX Analyst.

## 6. Vertical slice hiện tại

Vertical slice đầu tiên là [FEAT-001](./features/FEAT-001-elevator-manual-slice.md):

```text
CSV feedback
→ preview/validate/commit
→ immutable raw feedback
→ feedback item
→ manual classification
→ SVC-17 / ELV-01 / S2
→ workspace/detail/filter
→ basic insight có drill-down
→ audit + telemetry
```

Feature này cố ý không có AI, hotspot, ticket hay RCA. Nó kiểm chứng hợp đồng dữ liệu và luồng vận hành thủ công trước khi thêm automation.

## 7. Guardrail MVP

MVP ưu tiên một phạm vi pilot hẹp nhưng hoàn chỉnh end-to-end:

- Bắt đầu với dữ liệu thật đã mask của một project/building và một nhóm service có owner xác nhận.
- Hỗ trợ manual workflow trước; AI là lớp trợ giúp có fallback.
- Taxonomy, threshold, role và handling unit là cấu hình có version, không hard-code trong UI.
- Raw feedback là bất biến; mọi correction là decision/audit mới.
- Prediction không được coi là accepted label nếu chưa qua policy hoặc human review.
- Candidate Cause không phải Confirmed Root Cause.
- Mọi KPI/chart phải drill-down về đúng tập feedback tạo ra số liệu.
- Security, audit, test, telemetry và rollback là một phần của feature, không phải phase làm sau.

## 8. Cách dùng tài liệu trong công việc hằng ngày

### Trước refinement

- Xác nhận feature link tới đúng PRD story, taxonomy và ADR.
- Điền đầy đủ template trong [Build Rules](./BUILD_RULES.md).
- Đóng hoặc gán owner cho mọi open decision ảnh hưởng acceptance criteria/data model.

### Trước khi code

- Feature phải pass Definition of Ready.
- OpenAPI/schema/event change phải được review cùng UI flow, không review tách rời theo layer.
- Test data và quyền truy cập của từng actor phải được thống nhất.

### Trong pull request

- Link feature ID và acceptance criteria được triển khai.
- Nêu migration, security, telemetry và rollback impact.
- Nếu phát hiện assumption mới, cập nhật spec/ADR trước hoặc trong cùng pull request.

### Trước release

- Pass Definition of Done và release checklist.
- Đối soát import count, error count, classification count và metric output.
- Có feature flag, owner theo dõi, dashboard và runbook cho pilot.

## 9. Open decisions cần đóng trước production

Danh sách gốc nằm trong mục “Open Decisions for Stakeholder Workshop” của [PRD](./PRD.md). Tối thiểu cần chốt:

- location hierarchy và asset naming;
- role/scope matrix và quyền xem raw PII;
- retention/erasure policy;
- import template, source identity và deduplication rule;
- metric definitions và dữ liệu bị loại khỏi analytics;
- priority matrix, hard trigger và SLA;
- hotspot window, threshold, cooldown, merge/reopen;
- gold-set/evaluation policy cho AI;
- required evidence và authority để xác nhận Root Cause.

Không dùng giá trị mặc định trong taxonomy như một cam kết SLA, safety response hoặc trách nhiệm pháp lý khi owner chưa xác nhận.
