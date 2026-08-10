# Feature Specifications

Directory này chứa tài liệu chi tiết cho từng feature của **CX Intelligence Platform**.

## Cách đọc

Mỗi feature có một file `FEAT-XXX-name.md` chứa:

- **Outcome** — Kết quả quan sát được khi feature hoàn tất
- **Scope** — In scope và out of scope rõ ràng
- **Actors và permissions** — Vai trò và quyền hạn
- **Acceptance criteria** — Tiêu chí kiểm tra có thể kiểm chứng
- **Test strategy** — Cách thức test và validation
- **Telemetry và SLI** — Metrics và observability
- **Rollout và rollback** — Chiến lược triển khai và khôi phục

Mọi feature phải pass **Definition of Ready** trước khi build và **Definition of Done** trước khi merge. Xem chi tiết trong [Build Rules](../BUILD_RULES.md).

## Pilot tuần đầu — Trusted CSV to Dashboard

| Feature ID | Tên | Branch | Dependency | Status |
| --- | --- | --- | --- | --- |
| [FEAT-00](./FEAT-00-trusted-csv-to-dashboard-pilot.md) | Master Pilot | `dev` | Không | Ready for refinement |
| [FEAT-01](./FEAT-01-data-foundation.md) | Platform & Data Foundation | `codex/feat-data-foundation` | Không | Ready for refinement |
| [FEAT-02](./FEAT-02-csv-import.md) | CSV Import | `codex/feat-csv-import` | FEAT-01 | Ready for refinement |
| [FEAT-03](./FEAT-03-analytics-api.md) | Analytics API | `codex/feat-analytics-api` | FEAT-01 | Ready for refinement |
| [FEAT-04](./FEAT-04-dashboard-ui.md) | Pilot Web UI | `codex/feat-pilot-web-ui` | FEAT-02, FEAT-03 | Ready for refinement |
| [FEAT-05](./FEAT-05-release-quality.md) | Release Quality | `codex/feat-release-quality` | FEAT-01..04 | Ready for refinement |

### Dependency graph

```text
FEAT-00 (coordination)
          ↓
FEAT-01 Platform & Data Foundation
     ┌────┴───────────────┐
     ↓                    ↓
FEAT-02 CSV Import   FEAT-03 Analytics API
                          ↓
                 FEAT-04 Pilot Web UI
     └────────────┬───────┘
                  ↓
FEAT-05 Release Quality
                  ↓
dev → main (release)
```

### Merge order

1. FEAT-01 merge đầu tiên vào `dev` (Day 1)
2. FEAT-02 và FEAT-03 có thể merge song song sau FEAT-01 (Day 2-3)
3. FEAT-04 chỉ merge sau khi FEAT-02 và FEAT-03 đã có trên `dev` (Day 3-4)
4. FEAT-05 merge cuối cùng sau khi có đủ integration (Day 4-5)
5. `dev` merge vào `main` sau acceptance


## Quy tắc đặt tên

- Prefix: `FEAT-XXX` với số tuần tự
- Format: `FEAT-XXX-short-slug.md`
- Slug: lowercase, dấu gạch ngang, mô tả outcome ngắn gọn
- FEAT-00 đến FEAT-099: MVP và pilot baseline
- FEAT-100+: P1/P2 features

## Branch mapping

Mỗi feature có một integration branch tương ứng:

```bash
# Checkout feature branch
git fetch origin --prune
git switch --track origin/codex/feat-<name>

# Ví dụ
git switch --track origin/codex/feat-csv-import
```

Không tạo branch trùng tên hoặc branch thay thế cho cùng một feature. Xem chi tiết trong [Team Build Playbook](../TEAM_BUILD_PLAYBOOK.md).

## Tài liệu liên quan

- [START HERE](../00_START_HERE.md) — Roadmap đọc tài liệu
- [PRD](../PRD.md) — Product requirements
- [Service Taxonomy](../service_taxonomy.md) — Domain dictionary
- [Build Rules](../BUILD_RULES.md) — Engineering standards
- [Team Build Playbook](../TEAM_BUILD_PLAYBOOK.md) — Coordination và branch strategy
- [Architecture ADRs](../architecture/adr/) — Architecture decisions

## Source of truth

- Feature spec là source of truth cho **hành vi** của feature đó
- Acceptance criteria phải truy vết được về PRD và ADR
- API runtime tuân theo OpenAPI đã review
- Database runtime tuân theo migration + constraint đã review
- Metric tuân theo Metric Catalog phiên bản đã duyệt

Khi feature spec mâu thuẫn với PRD/ADR/Build Rules, giải quyết theo [conflict protocol](../TEAM_BUILD_PLAYBOOK.md#16-conflict-protocol).
