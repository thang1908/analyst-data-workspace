# Teamwork Preview Reviewer 2 — Handoff Report

**Date:** 2026-08-17  
**Reviewer:** teamwork_preview_reviewer_2  
**Role:** Adversarial Reviewer & QA  
**Integrity Mode:** Development  

---

## 1. Executive Summary & Verification Verdict

All remaining P0 backlog features for the CX Journey, Service & Hotspot Intelligence Platform specified in `docs/08_Operating_Dashboard_Spec.md`, PRD, API, and UI/UX specs have been thoroughly verified, tested, and hardened.

- **Automated Test Suite:** 92 unit and integration tests passing (`pytest tests/unit tests/integration`).
- **Frontend App:** TypeScript compilation and Vite production build pass cleanly with 0 errors.
- **Git Branch:** Clean working state on `dev` branch with all features implemented.

---

## 2. Issues Discovered and Resolved in Round 2

### Issue 1: Self-Transition Validation Bug on Resolved / Dismissed Hotspots
- **Input:** Updating the `resolution_summary` of an already `RESOLVED` hotspot (`src=RESOLVED`, `dst=RESOLVED`) or updating notes on a `DISMISSED` hotspot (`src=DISMISSED`, `dst=DISMISSED`).
- **Expected:** Allow update if valid `resolution_summary` or `reason` is supplied without rejecting.
- **Actual:** Raised `InvalidStateTransitionError: A reason is required to reopen a hotspot.` because the reopen condition incorrectly checked `src in (HotspotStatus.RESOLVED, HotspotStatus.DISMISSED)` without verifying that the destination state was actually a reopening target (`INVESTIGATING` or `REOPENED`).
- **Root Cause:** In `packages/domain/hotspot/engine.py`, `validate_hotspot_transition` checked `(dst == HotspotStatus.REOPENED or src in (HotspotStatus.RESOLVED, HotspotStatus.DISMISSED))` which evaluated to `True` even for non-reopening state updates.
- **Fix:** Refined `is_reopening` condition to `(dst == HotspotStatus.REOPENED) or (src in (HotspotStatus.RESOLVED, HotspotStatus.DISMISSED) and dst in (HotspotStatus.INVESTIGATING, HotspotStatus.REOPENED))`. Added unit tests for self-updates.

### Issue 2: API Date Range Validation & Parameter Handling Inconsistency
- **Input:** Calling `GET /api/v1/hotspots` with `date_from=2026-08-20&date_to=2026-08-10` or passing calendar date strings.
- **Expected:** Return `422 Unprocessable Content` when `date_from > date_to`, consistent with `/api/v1/analytics` and `/api/v1/feedback-items`. When `date_to` is a calendar date (e.g. `2026-08-17`), include items through the end of that calendar day.
- **Actual:** `GET /api/v1/hotspots` accepted inverted date ranges without validation, and evaluated `h.last_seen_at <= :date_to`, dropping items that occurred later in the day when `date_to` was parsed at midnight.
- **Root Cause:** Missing `date_from > date_to` validation and boundary interval adjustment in `apps/api/routers/hotspot.py` and `HotspotRepository.list_hotspots`.
- **Fix:** Added 422 validation for `date_from > date_to` in `apps/api/routers/hotspot.py`, adjusted boundary filter in `HotspotRepository.list_hotspots` (`< :date_to + INTERVAL '1 day'`), and added automated integration test `test_list_hotspots_invalid_date_range_returns_422`.

### Issue 3: Taxonomy Release Validity & JSON Parameter Serialization in Hotspot Sync
- **Input:** Running `detect_and_sync_hotspots` when taxonomy releases have future or expired effective date bounds.
- **Expected:** Honor the active effective date range `(effective_from IS NULL OR effective_from <= NOW()) AND (effective_to IS NULL OR effective_to > NOW())` consistent with `TaxonomyRepository` and `TAXONOMY_FILTER_OPTIONS_SQL`.
- **Actual:** The query only checked `status = 'PUBLISHED'`, which could select an effective-dated future release before its activation.
- **Root Cause:** Discrepancy in release query across repository implementations.
- **Fix:** Standardized the published taxonomy selection query in `HotspotRepository.detect_and_sync_hotspots` and added explicit `CAST(:dimension_config_json AS jsonb)` for reliable driver serialization.

### Issue 4: Filter Context Loss on Dashboard Drill-down
- **Input:** User active on CX Operating Dashboard with active project, date range, or location filters clicks "Bằng chứng" on a Hotspot card or Modal, or selects a Step, Touchpoint, or Service.
- **Expected:** Drill down into Feedback Explorer preserving all current filter context (`projectId`, `dateFrom`, `dateTo`, `locationId`, etc.).
- **Actual:** Navigated to hardcoded URLs (`/feedback?service_code=...&issue_code=...`) discarding existing dashboard filter parameters.
- **Root Cause:** Hardcoded query string concatenation without preserving `location.search`.
- **Fix:** Updated `HotspotActionQueue.tsx` and `HotspotDetailModal.tsx` to construct drill-down URLs using `useLocation().search`, and added direct drilldown buttons on selected Steps, Touchpoints, and Services in `OverviewPage.tsx`.

---

## 3. Requirements Verification Matrix

| Requirement | Spec Reference | Implementation / Verification Status |
|---|---|---|
| **R1. Touchpoint Taxonomy & Mapping** | `08_Operating_Dashboard_Spec.md §2, §6.5, §6.6` | **VERIFIED** — Migration 019 creates `touchpoint`, `touchpoint_service_map`, classification projection columns, and seeds 46 canonical touchpoints across 6 stages and 10 services. Endpoints `/api/v1/customer-lifecycle/touchpoints` and `/api/v1/analytics/filter-options` return full mappings. |
| **R2. Deterministic Hotspot Engine** | `08_Operating_Dashboard_Spec.md §4` | **VERIFIED** — `cluster_eligible_items` clusters by `service + issue + location + rule_version` with threshold $N$ within window $W$. Action priorities (`IMMEDIATE`, `URGENT`, `PLANNED`, `MONITOR`) correctly map safety and velocity rules without mutating operational severity. Audit timeline log captures all lifecycle transitions (`CANDIDATE -> ACKNOWLEDGED -> INVESTIGATING -> RESOLVED / DISMISSED / REOPENED`). |
| **R3. CX Operating Dashboard & Feedback Explorer** | `08_Operating_Dashboard_Spec.md §3, §8` | **VERIFIED** — Unified CX Operating Dashboard renders all 10 services, 6 stages, step-touchpoint hierarchy with zero-state preservation, and Hotspot Action Queue. Full URL search param preservation on drilldown into Feedback Explorer. |
| **R4. Automated Testing & Clean Build** | AC & Prompt | **VERIFIED** — 92 unit and integration tests passing; web frontend compiles and builds with Vite in production mode without errors. |

---

## 4. Test Verification Details

### Automated Pytest Suite:
```
92 passed, 3 skipped in 0.61s
- tests/unit/test_touchpoint_domain.py (2 passed)
- tests/unit/test_hotspot_domain.py (6 passed)
- tests/unit/test_hotspot_repository.py (5 passed)
- tests/unit/test_taxonomy_repository.py (3 passed)
- tests/integration/test_hotspot_api.py (6 passed)
- tests/integration/test_taxonomy_api.py (4 passed)
- tests/unit/test_analytics.py (13 passed)
- tests/unit/test_analytics_repository.py (10 passed)
- tests/unit/test_feedback_domain.py (7 passed)
- tests/unit/test_feedback_repository.py (2 passed)
- tests/unit/test_feedback_service.py (3 passed)
- tests/integration/test_analytics_api.py (4 passed)
- tests/integration/test_feedback_api.py (2 passed)
- tests/unit/test_import_infrastructure.py (3 passed)
- tests/unit/test_import_pipeline.py (11 passed)
- tests/unit/test_infrastructure.py (4 passed)
- tests/unit/test_shared_enums.py (5 passed)
```

### Web Frontend Build:
```
npm --prefix apps/web run build
> tsc && vite build
✓ 2090 modules transformed.
✓ built in 1.29s
```
