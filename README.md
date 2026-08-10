# Analyst Data Workspace

Repository cho pilot **Trusted CSV to Dashboard** của CX Intelligence Platform.

## Bắt đầu

1. Đọc [START HERE](./docs/00_START_HERE.md).
2. Đọc [Team Build Playbook](./docs/TEAM_BUILD_PLAYBOOK.md).
3. Điền/pass [Pilot Kickoff Checklist](./docs/PILOT_KICKOFF_CHECKLIST.md).
4. Mở feature spec được giao trong [`docs/features`](./docs/features).
5. Checkout đúng remote branch của feature; không code trực tiếp trên `main` hoặc `dev`.

## Nhánh tích hợp

- `main`: baseline đã được chấp nhận; chỉ nhận thay đổi từ `dev` sau release gate.
- `dev`: nhánh tích hợp của pilot tuần đầu.
- `codex/feat-data-foundation`: workspace/app shells, auth context, contract, domain, migration và seed.
- `codex/feat-csv-import`: upload, validation, dedupe và import worker.
- `codex/feat-analytics-api`: feedback query, metric và drill-down API.
- `codex/feat-pilot-web-ui`: import control, dashboard, filter và feedback drill-down UI.
- `codex/feat-release-quality`: CI, E2E, staging, reconciliation và runbook.

Ví dụ checkout:

```bash
git fetch origin --prune
git switch --track origin/codex/feat-csv-import
```

Trước khi bắt đầu code, feature branch phải rebase trên `origin/dev` và đạt Definition of Ready trong feature spec.

## Trạng thái hiện tại

Baseline tài liệu và code layout được chuẩn bị trên `dev`. Code scaffold và dependency được triển khai trong `FEAT-010`; các feature còn lại phát triển theo contract đã duyệt và merge vào `dev` theo dependency graph trong playbook.
