# Architecture Documentation

Directory này chứa các quyết định kiến trúc (**Architecture Decision Records - ADR**) cho **CX Intelligence Platform**.

## Mục đích

ADR được sử dụng để:

- Ghi lại các quyết định kiến trúc quan trọng và lâu dài
- Giải thích **context**, **decision** và **consequences** của mỗi quyết định
- Là **source of truth** khi PRD hoặc taxonomy chưa đủ rõ ràng
- Giúp team mới hiểu lý do thiết kế hiện tại
- Tránh tái diễn các cuộc tranh luận đã được giải quyết

ADR không thay thế PRD, Build Rules hoặc feature spec. Nó bổ sung và làm rõ các khái niệm domain còn mơ hồ hoặc các quyết định technical architecture.

## Format ADR

Mỗi ADR tuân theo format:

```markdown
# ADR-XXX — Tên quyết định ngắn gọn

- **Status:** Proposed | Accepted | Deprecated | Superseded by ADR-YYY
- **Date:** YYYY-MM-DD
- **Decision owners:** Danh sách người phê duyệt
- **Scope:** MVP baseline | P0 | P1 | ...
- **Related:** Links tới PRD, Taxonomy, Build Rules, Features

## Context

Mô tả vấn đề, constraint, requirement và các giả định hiện tại.

## Decision

Quyết định cụ thể được chấp nhận. Rõ ràng, ngắn gọn, có thể thực thi.

## Consequences

- **Positive:** Lợi ích và khả năng mới
- **Negative:** Tradeoff và hạn chế
- **Risks:** Rủi ro cần theo dõi

## Alternatives considered (optional)

Các lựa chọn khác đã được xem xét và lý do không chọn.

## Implementation notes (optional)

Hướng dẫn triển khai hoặc migration path nếu cần.
```

## Baseline ADRs

| ADR | Tên | Status | Scope |
| --- | --- | --- | --- |
| [ADR-001](./adr/ADR-001-journey-dimensions.md) | Tách hai chiều Lifecycle độc lập | Accepted | MVP baseline |
| [ADR-002](./adr/ADR-002-classification-model.md) | Raw Feedback → Item → Prediction/Decision/Current | Accepted | MVP baseline |
| [ADR-003](./adr/ADR-003-data-dashboard-stack-and-code-layout.md) | Data-to-Dashboard Stack & Code Layout | Accepted | Pilot tuần đầu |

## ADR lifecycle

```text
Proposed → Review → Accepted → Active
                        ↓
                   Deprecated/Superseded
```

### Status definitions

- **Proposed:** Đang được thảo luận, chưa là quyết định chính thức
- **Accepted:** Đã được phê duyệt và áp dụng cho code mới
- **Deprecated:** Không dùng cho thay đổi mới, nhưng chưa bị thay thế
- **Superseded by ADR-XXX:** Đã bị thay thế bởi ADR mới

## Khi nào tạo ADR?

Tạo ADR khi:

- Có nhiều cách giải quyết hợp lý và cần chọn một cách duy nhất
- Quyết định ảnh hưởng đến nhiều feature hoặc module
- Domain concept còn mơ hồ và có thể hiểu theo nhiều cách
- Cần thay đổi stack, framework hoặc kiến trúc đã khóa
- PRD hoặc Taxonomy mâu thuẫn và cần disambiguate
- Có tradeoff quan trọng giữa performance, security, maintainability

**Không** tạo ADR cho:

- Implementation details nội bộ của một feature
- Coding style hoặc naming convention (dùng Build Rules)
- Bug fix hoặc refactoring không đổi hành vi
- Quyết định tạm thời chỉ áp dụng trong pilot

## Cách đề xuất ADR

1. Copy template ở trên vào file mới `ADR-XXX-short-title.md`
2. Điền đầy đủ Context, Decision và Consequences
3. Đặt Status là `Proposed` và thêm date
4. Tạo PR, tag decision owners và related feature owners
5. Sau khi được phê duyệt, đổi Status thành `Accepted`
6. Cập nhật related features, Build Rules hoặc specs nếu cần

## ADR vs Build Rules vs Feature Spec

| Tài liệu | Mục đích | Ví dụ |
| --- | --- | --- |
| **ADR** | Quyết định kiến trúc lâu dài, domain model, stack choice | "Feedback là immutable, correction tạo decision mới" |
| **Build Rules** | Engineering standards áp dụng cho mọi feature | "Mọi write API phải idempotent", "Raw PII không được log" |
| **Feature Spec** | Hành vi cụ thể của một feature | "CSV import endpoint validate exact header" |

Khi ba tài liệu mâu thuẫn:

1. Dừng implementation bị ảnh hưởng
2. Ghi vấn đề vào feature spec hoặc open-decision log
3. Nếu cần quyết định domain/architecture → tạo/cập nhật ADR
4. Sau khi quyết định, cập nhật tất cả contract liên quan

## Tài liệu liên quan

- [START HERE](../00_START_HERE.md#4-source-of-truth) — Source of truth hierarchy
- [PRD](../PRD.md) — Product requirements
- [Service Taxonomy](../service_taxonomy.md) — Domain dictionary
- [Build Rules](../BUILD_RULES.md) — Engineering standards
- [Team Build Playbook](../TEAM_BUILD_PLAYBOOK.md) — Coordination
- [Features](../features/) — Feature specifications

## Contributing

Mọi ADR mới phải:

- Có title rõ ràng, decision cụ thể
- Link tới PRD/taxonomy/features liên quan
- Có decision owner được ghi tên
- Được review bởi affected feature owners
- Pass acceptance trước khi status chuyển `Accepted`

ADR không phải bureaucracy. Nó là công cụ để team làm việc hiệu quả hơn bằng cách ghi lại những gì đã đồng ý thay vì tranh luận lại từ đầu.
