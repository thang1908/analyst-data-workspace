# Original User Request

## 2026-08-17T15:56:26Z

This is a single self-contained fix; keep it small and focused.
Implement and verify the remaining P0 backlog features for the CX Journey, Service & Hotspot Intelligence Platform according to `docs/08_Operating_Dashboard_Spec.md`, PRD, System Design, Data Model, API, and UI/UX specs, ensuring all automated tests pass and changes merge cleanly into the `dev` branch.

Working directory: /Users/thangnguyen/Documents/analyst-data-workspace
Integrity mode: development

## Requirements

### R1. Touchpoint Taxonomy & Step-Touchpoint-Service Mapping (P0.1)
- Extend database migrations, seed data, and domain models to support Touchpoint entities (`code`, `name_vi`, `definition`, `lifecycle_step_id`, `active_from`, `active_to`) and mapping to Primary Services (`touchpoint_service_map`).
- Expose taxonomy API endpoints and filter options for touchpoint dimension.

### R2. Deterministic Hotspot Engine & Action Priority Queue (P0.3 & P0.4)
- Implement deterministic clustering rule for Hotspots based on `primary_service + issue + normalized_location + rolling_window + rule_version` with threshold $N$ items within window $W$ days on accepted/eligible feedback items.
- Implement Hotspot lifecycle state transitions (`CANDIDATE -> ACKNOWLEDGED -> INVESTIGATING -> RESOLVED / DISMISSED`) and Action Priority categorization (`IMMEDIATE`, `URGENT`, `PLANNED`, `MONITOR`).
- Support Hotspot acknowledgement, assignment, resolution, and dismiss mutation with audit logging.

### R3. CX Operating Dashboard & Feedback Explorer Drill-down Integration
- Unify CX Operating Dashboard with Touchpoint hierarchy expansion, Hotspot Action Queue, and seamless Drill-down filter context into the Feedback Explorer workspace.
- Preserve zero-state rendering for all 10 services and 6 journey stages.

### R4. Automated Testing & Clean Merge into Dev Branch
- Run existing and new test suites (`pytest tests/unit tests/integration` and web frontend typecheck/build).
- Verify zero regressions across API, database, and UI.
- Merge the feature commits cleanly into `dev` branch with clear commit messages.

## Acceptance Criteria

### Taxonomy & Touchpoint
- [ ] Database migration applies cleanly with Touchpoint table and seed data according to `docs/08_Operating_Dashboard_Spec.md`.
- [ ] API returns touchpoints mapped to journey steps and primary services.

### Hotspot Engine
- [ ] Hotspot rule detects clusters matching threshold $N$ within $W$ days without creating duplicates on retry.
- [ ] Action priority correctly reflects priority levels without altering operational severity.
- [ ] Status transitions record audit history with actor, timestamp, and reason.

### UI & Verification
- [ ] Operating Dashboard renders 10 services, 6 stages, touchpoints, and Hotspot Action Queue.
- [ ] Selecting a hotspot, service, or touchpoint opens Feedback Explorer with the exact filter context preserved.
- [ ] All automated tests pass (`pytest` unit and integration tests).
- [ ] Web frontend builds cleanly without TypeScript or lint errors.
- [ ] Changes are committed and merged into branch `dev`.
