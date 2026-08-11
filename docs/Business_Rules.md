# 03 — Business Rules

# CX Journey, Service & Root Cause Intelligence Platform

**Version:** 1.1  
**Status:** Draft for Engineering Baseline  
**Derived from:** `docs/PRD.md` v1.3 and `docs/service_taxonomy.md` v3.0.0  
**Scope:** P0 Pilot Build Baseline, with selected P1 rules explicitly marked  
**Purpose:** Convert product/taxonomy decisions into enforceable domain rules that can be implemented in schema, API, jobs, UI validation, and automated tests.

---

## 1. Document Role

This document is the normative business-rule layer between the PRD/taxonomy and implementation.

```text
PRD
  ↓ defines product behavior and scope
Taxonomy
  ↓ defines canonical vocabulary and label boundaries
Business Rules
  ↓ defines invariants and allowed state transitions
System Design
  ↓ maps those rules into architecture/schema/API/jobs
Implementation
```

The PRD remains authoritative for product scope. `service_taxonomy.md` remains authoritative for canonical lifecycle/service/issue wording. If this document conflicts with either source, the conflict must be resolved by a versioned decision before implementation.

---

## 2. Normative Language

- **MUST / MUST NOT** — mandatory invariant.
- **SHOULD / SHOULD NOT** — expected default; deviation requires a documented reason.
- **MAY** — optional behavior.
- **P0** — required for pilot.
- **P1** — operational expansion.
- **P2** — advanced intelligence.

---

## 3. Core Value Status Model

Classification fields that may be unknown or inapplicable MUST use an explicit value-status model.

```text
KNOWN
UNKNOWN
MISSING
NOT_APPLICABLE
```

Rules:

1. `KNOWN` MUST have a valid referenced ID.
2. `UNKNOWN`, `MISSING`, and `NOT_APPLICABLE` MUST have the referenced ID set to `null`.
3. `UNKNOWN` means the field was assessed but cannot yet be determined.
4. `MISSING` means required source/context is absent.
5. `NOT_APPLICABLE` means the field does not logically apply to the item.
6. The system MUST NOT silently convert missing or ambiguous data into a taxonomy value.

---

# 4. Feedback & Atomic Item Rules

## BR-FB-001 — Raw Feedback Is Immutable

**Priority:** P0  
**Rule:** `content_raw` MUST NOT be edited after ingestion.

Derived artifacts such as masking, normalization, splitting, predictions, and decisions MUST be stored separately.

**Enforcement**
- Database update policy/service layer.
- Audit privileged raw-content access.
- Tests must prove correction/split does not modify the envelope.

---

## BR-FB-002 — Feedback Is an Envelope; Feedback Item Is the Analytic Unit

**Priority:** P0  
**Rule:** One `Feedback` MUST contain one or more `Feedback Item` records.

```text
Feedback 1 ─── N Feedback Item
```

Analytics, classification review, and hotspot detection MUST operate on `feedback_item_id`, not directly on the feedback envelope.

---

## BR-FB-003 — One Item, One Atomic Intent or Observable Failure

**Priority:** P0  
**Rule:** A `Feedback Item` MUST represent one customer intent or one observable failure.

If a source feedback contains multiple independent problems, it MUST be split before those problems receive different Primary Service/Issue classifications.

**Example**

```text
"Thang máy chậm và app cư dân không đăng nhập được."
```

must become at least:

```text
Item 1 → elevator problem
Item 2 → resident app problem
```

---

## BR-FB-004 — Split Must Preserve Provenance

**Priority:** P0  
**Rule:** Splitting MUST:
- preserve the original `feedback_id`;
- preserve `content_raw`;
- create new item identity/index;
- record `split_source`, actor, timestamp, and audit event;
- never erase previous decision/prediction history.

---

## BR-FB-005 — Location Cardinality

**Priority:** P0  
**Rule:** A Feedback Item MAY have zero or one normalized `location_id`.

The system MUST NOT attach multiple classification locations to one atomic item. If a record truly describes separate failures at separate locations, split the item or preserve additional text as evidence/context.

---

## BR-FB-006 — Affected Channel Cardinality

**Priority:** P0  
**Rule:** A Feedback Item MAY have zero to many Affected Channels.

`intake_channel` and `affected_channel` are different concepts.

---

## BR-FB-007 — Source System Is Not a Channel

**Priority:** P0  
**Rule:** CRM, ERP, BMS, CMMS, contact-center platforms, crawler pipelines, and sensor feeds MUST be represented as `source_system`, not as canonical `CH-*` channels.

---

## BR-FB-008 — Symptom Detail Is Free Text

**Priority:** P0  
**Rule:** `symptom_detail` is descriptive text and MUST NOT be promoted into a new Service/Issue solely for dashboard granularity.

---

# 5. Lifecycle Rules

## BR-LIFE-001 — Two Independent Lifecycle Dimensions

**Priority:** P0  
**Rule:** Customer Lifecycle and Service Request Lifecycle MUST be stored and queried as independent dimensions.

```text
CUSTOMER_LIFECYCLE
SERVICE_REQUEST_LIFECYCLE
```

An `SRV-*` code MUST NOT be stored as a Customer Lifecycle stage/step.

---

## BR-LIFE-002 — Customer Lifecycle Cardinality

**Priority:** P0  
**Rule:** A Feedback Item MAY have at most one current Customer Lifecycle Step.

Customer Lifecycle Stage MUST be derived from the selected Step within the same taxonomy release.

The system SHOULD NOT ask an AI model or reviewer to independently choose both stage and step when step is known.

---

## BR-LIFE-003 — Service Request Lifecycle Cardinality

**Priority:** P0  
**Rule:** A Feedback Item MAY have at most one current Service Request Step.

The field MAY be `NOT_APPLICABLE` when the item is not describing a service-request flow.

---

## BR-LIFE-004 — Lifecycle-to-Service Is N:N

**Priority:** P0  
**Rule:** A Lifecycle Step can map to multiple Services, and a Service can map to multiple Lifecycle Steps.

Mapping MUST include:
- lifecycle type;
- stable IDs;
- effective date;
- version/release;
- active/published state.

---

## BR-LIFE-005 — Lifecycle Mapping Does Not Auto-Classify

**Priority:** P0  
**Rule:** Lifecycle-Service mapping is a constraint/suggestion space, not proof that a Service is correct.

The system MAY use the mapping to narrow candidate values but MUST NOT silently create an accepted classification solely because a mapping exists.

---

# 6. Taxonomy Rules

## BR-TAX-001 — Canonical Release Shape

**Priority:** P0  
**Rule:** A publishable taxonomy release MUST contain:

- 6 Customer Lifecycle Stages;
- 36 Customer Journey Steps;
- 8 Service Request Steps;
- 10 active Services;
- 28 active Issues.

Additionally:
- `SV-01` through `SV-09` MUST each contain exactly 3 Issues.
- `SV-10` MUST contain exactly 1 Issue: `IS-10-01`.

---

## BR-TAX-002 — Issue Belongs to Exactly One Service

**Priority:** P0  
**Rule:** Each canonical Issue MUST belong to exactly one canonical Service in a taxonomy release.

---

## BR-TAX-003 — Stable Codes Are Never Reused

**Priority:** P0  
**Rule:** Published taxonomy codes/IDs MUST NOT be reassigned to a different semantic meaning.

Retired values remain historically resolvable.

---

## BR-TAX-004 — No Hard Delete After Historical Use

**Priority:** P0  
**Rule:** Taxonomy records and mappings referenced by historical data MUST NOT be hard-deleted.

Use `RETIRED`/effective-date semantics.

---

## BR-TAX-005 — Publish State Controls New Decisions

**Priority:** P0  
**Rule:** Taxonomy state MUST support:

```text
DRAFT → APPROVED → PUBLISHED → RETIRED
```

Only `PUBLISHED` values/releases may be used by new production classification decisions.

---

## BR-TAX-006 — Taxonomy Must Be Versioned

**Priority:** P0  
**Rule:** Feedback decisions, predictions, mappings, metrics, and hotspot rules MUST retain the relevant taxonomy/rule version required to reproduce historical behavior.

---

## BR-TAX-007 — Application Must Not Hard-Code Labels

**Priority:** P0  
**Rule:** UI/API/business logic MUST use stable IDs/codes from published reference data rather than embedding canonical wording in application code.

---

## BR-TAX-008 — Do Not Create Taxonomy From Operational Metadata

**Priority:** P0  
**Rule:** A new Service or Issue MUST NOT be created merely because of a different:
- location;
- channel;
- source system;
- vendor;
- contractor;
- resolver;
- handling unit;
- asset;
- building.

---

## BR-TAX-009 — SV-10 Is Controlled Fallback, Not Unknown

**Priority:** P0  
**Rule:** `SV-10 / IS-10-01` MUST be used only when the item is understandable but outside `SV-01..SV-09`.

It MUST NOT be used for missing/ambiguous records.

When used:
- `other_reason` is mandatory;
- human review is mandatory;
- usage rate SHOULD be monitored.

---

# 7. Classification Decision Rules

## BR-CLS-001 — One Current Primary Service

**Priority:** P0  
**Rule:** If `primary_service_value_status=KNOWN`, the current projection MUST contain exactly one `primary_service_id`.

There is no Secondary Service in P0.

---

## BR-CLS-002 — Issue Must Match Primary Service

**Priority:** P0  
**Rule:** If `issue_value_status=KNOWN`, the Issue MUST belong to the selected Primary Service in the same taxonomy release.

If Primary Service changes and invalidates the current Issue, the write MUST:
1. require a new valid Issue, or
2. set Issue status to `UNKNOWN` with `issue_id=null`.

---

## BR-CLS-003 — Decision Snapshot Is Atomic

**Priority:** P0  
**Rule:** A classification decision MUST represent one complete versioned snapshot of the item's accepted classification state.

A correction MUST create a new `decision_version`; previous decisions MUST remain immutable.

---

## BR-CLS-004 — Current Projection Is Derived State

**Priority:** P0  
**Rule:** `classification_current` is a rebuildable read projection, not the audit source of truth.

Source of truth is the append-only decision/review history.

---

## BR-CLS-005 — Prediction Is Not an Accepted Decision

**Priority:** P0  
**Rule:** AI prediction MUST NOT update current classification or analytics directly.

P0 is suggest-only for all confidence values.

---

## BR-CLS-006 — Accepted Sources

**Priority:** P0  
**Rule:** `decision_source` MUST use exactly this canonical enum across rules, database, API and UI:

```text
MANUAL
SOURCE_TRUSTED
HUMAN_ACCEPTED_AI
HUMAN_CORRECTED_AI
POLICY_AUTO_APPLIED
SYSTEM_MIGRATION
```

For P0, `POLICY_AUTO_APPLIED` MUST remain disabled unless explicitly approved for a specific low-risk field.

---

## BR-CLS-007 — Canonical Human Review Actions

**Priority:** P0  
**Rule:** AI review MUST use exactly:

```text
ACCEPT
CORRECT
MARK_UNKNOWN
MARK_MISSING
MARK_NOT_APPLICABLE
SPLIT_REQUIRED
SKIP
```

- `ACCEPT`, `CORRECT`, `MARK_UNKNOWN`, `MARK_MISSING`, `MARK_NOT_APPLICABLE` MUST create one immutable `ClassificationDecision` and one `ReviewEvent`.
- `SPLIT_REQUIRED` and `SKIP` MUST create only a `ReviewEvent`.
- Actual split MUST use a separate split mutation; it creates child Feedback Items and MUST NOT create a decision for the split-parent.
- API/UI labels MAY be localized, but wire values MUST remain the canonical enum above.

---

## BR-CLS-008 — Stale Concurrent Decision Writes Are Rejected

**Priority:** P0  
**Rule:** A decision mutation MUST include/validate the expected previous decision or projection version.

If another actor changed the item first, the stale write MUST fail with a conflict response rather than overwrite the latest decision.

---

## BR-CLS-009 — Manual Override Requires Audit

**Priority:** P0  
**Rule:** Any manual correction or override MUST include:
- actor;
- timestamp;
- reason;
- previous decision reference;
- resulting decision reference.

---

# 8. Cause & Root Cause Rules

## BR-CAUSE-001 — Issue Is Not Cause

**Priority:** P0  
**Rule:** Issue represents observed failure/symptom. Cause represents an investigation hypothesis.

Cause data MUST NOT be encoded into the Issue catalog.

---

## BR-CAUSE-002 — Candidate Cause Is 0:N

**Priority:** P0  
**Rule:** A decision/investigation MAY contain zero to many Candidate Causes.

Each suggested cause SHOULD retain:
- cause ID;
- rank;
- confidence;
- source;
- model/rule version where relevant.

---

## BR-CAUSE-003 — UNKNOWN Cannot Coexist With Specific Candidate Causes

**Priority:** P0  
**Rule:** If cause determination is `UNKNOWN`, the same decision set MUST NOT contain a specific candidate cause.

---

## BR-CAUSE-004 — Canonical Cause Determination Status

**Priority:** P0  
**Rule:** `cause_determination_status` MUST use exactly:

```text
NOT_ASSESSED
UNKNOWN
SUGGESTED
UNDER_INVESTIGATION
CONFIRMED
NOT_APPLICABLE
```

- P0 classification/review MAY write only `NOT_ASSESSED`, `UNKNOWN`, `SUGGESTED`, `NOT_APPLICABLE`.
- `SUGGESTED` requires at least one Candidate Cause; `UNKNOWN` MUST NOT coexist with a concrete Candidate Cause.
- `UNDER_INVESTIGATION` and `CONFIRMED` are P1 states written only by Investigation/RCA workflow.
- Classifier/AI MUST NOT write `UNDER_INVESTIGATION` or `CONFIRMED`.

---

## BR-CAUSE-005 — AI Cannot Confirm Root Cause

**Priority:** P0/P1  
**Rule:** No AI model, prompt, anomaly score, or classifier confidence may independently create a confirmed root cause.

---

## BR-CAUSE-006 — Confirmed Root Cause Requires Evidence

**Priority:** P1  
**Rule:** A confirmed root cause MUST have:
- `confirmed_by`;
- `confirmed_at`;
- evidence;
- investigation/RCA reference;
- authorized confirmer.

---

## BR-CAUSE-007 — Asset and Work Order Are Investigation References

**Priority:** P1  
**Rule:** Asset IDs, BMS objects, CMMS work orders, and technical-system identifiers MAY be linked to investigations but MUST NOT become core Service/Issue classification dimensions.

---

## BR-CAUSE-008 — P0/P1 RCA Boundary

**Priority:** P0/P1  
**Rule:** P0 is limited to Hotspot, evidence Feedback Items, owner, hotspot status and basic Candidate Cause. P1 owns Investigation, Confirmed Root Cause, Corrective Action, Preventive Action and full RCA workflow/storage/API/UI.

P0 MUST NOT expose a mutation that starts an Investigation, confirms Root Cause or manages Corrective/Preventive Actions.

---

# 9. Import & Ingestion Rules

## BR-IMP-001 — Import Is Asynchronous

**Priority:** P0  
**Rule:** CSV/XLSX import MUST run as an asynchronous job.

Canonical lifecycle:

```text
UPLOADED
  → MAPPED
  → VALIDATING
  → VALIDATED
  → QUEUED
  → PROCESSING
      ├── COMPLETED
      ├── PARTIAL
      ├── FAILED
      └── CANCELLED
```

---

## BR-IMP-002 — Preview/Validation Does Not Commit Production Feedback

**Priority:** P0  
**Rule:** Preview and validation MUST NOT create production Feedback records.

---

## BR-IMP-003 — Execute Only From VALIDATED

**Priority:** P0  
**Rule:** Import execution MUST be rejected unless the job is in `VALIDATED`.

---

## BR-IMP-004 — File/Schema Failure Versus Row Failure

**Priority:** P0  
**Rule:**
- file/schema-level blocking error → job becomes `FAILED`;
- row-level validation errors MAY still allow `VALIDATED` if configured to commit valid rows.

---

## BR-IMP-005 — Every Row Has Lineage and Outcome

**Priority:** P0  
**Rule:** Every source row MUST retain:
- `import_job_id`;
- `source_row_number`;
- checksum/idempotency identity;
- processing outcome;
- error code/message when unsuccessful.

No row may be silently dropped.

---

## BR-IMP-006 — Retry Is Idempotent

**Priority:** P0  
**Rule:** Retry MUST process only rows not previously committed successfully and MUST NOT create duplicate Feedback records.

---

## BR-IMP-007 — Event Time Semantics

**Priority:** P0  
**Rule:** `reported_at` preserves source time/timezone when available.

If unavailable:
- use `ingested_at`;
- set `event_time_inferred=true`.

Storage timestamps SHOULD be UTC. User-facing bucketing MUST respect source/location timezone policy.

---

## BR-IMP-008 — Mask Before AI

**Priority:** P0  
**Rule:** When raw content contains protected personal data that is not necessary for model inference, `content_masked`/`item_text_masked` MUST be generated before AI processing.

---

# 10. Analytics Rules

## BR-ANA-001 — Feedback Item Is Default Metric Grain

**Priority:** P0  
**Rule:** Unless explicitly labeled otherwise, product analytics MUST count distinct eligible `feedback_item_id`.

---

## BR-ANA-002 — Analytics Requires Eligible Current Decision

**Priority:** P0  
**Rule:** An item may enter standard analytics only when:
- item is active;
- `analytic_eligibility=INCLUDED`;
- not duplicate/excluded;
- current projection comes from accepted human/source-trusted decision;
- referenced taxonomy values are valid for the recorded release.

Unreviewed prediction alone is insufficient.

---

## BR-ANA-003 — Unknown Is Not Silently Dropped

**Priority:** P0  
**Rule:** Unknown/missing rates MUST be separately measurable.

For sentiment:
- `negative_rate` denominator uses eligible items with known sentiment;
- unknown sentiment MUST be shown through `sentiment_unknown_rate`.

---

## BR-ANA-004 — Metric Definition Is Versioned

**Priority:** P0  
**Rule:** KPI, chart, drill-down, and export must share:
- filter context;
- eligibility logic;
- event-time semantics;
- `metric_definition_version`.

---

## BR-ANA-005 — No Dead-End Chart

**Priority:** P0  
**Rule:** Every standard dashboard segment MUST drill down to the corresponding filtered Feedback Item list and then to item detail.

---

## BR-ANA-006 — Four Basic P0 Dashboards

**Priority:** P0  
**Rule:** P0 MUST provide four basic dashboards: CX Overview, Customer Journey, Service & Pain Points, and Hotspot & Root Cause.

The fourth dashboard is limited in P0 to hotspot, evidence, owner/status and Candidate Cause. Investigation, confirmed Root Cause and actions remain P1.

---

## BR-ANA-007 — Multi-metric Breakdown Contract

**Priority:** P0  
**Rule:** Analytics breakdown by `journey_stage`, `journey_step`, `service`, `issue`, `location`, `intake_channel` or `affected_channel` MUST support:

```text
item_volume
negative_rate
active_hotspots
trend
```

All metrics and drill-downs MUST share filter context, eligibility logic and metric-definition version.

---

## BR-ANA-008 — Persona Is Not a P0 Analytics Dimension

**Priority:** P0  
**Rule:** P0 API/UI MUST NOT expose Persona filter or segmentation. Product personas are authorization/user roles, not customer analytics data.

---

## BR-ANA-009 — Affected Channel Is Supported in P0 Analytics

**Priority:** P0  
**Rule:** `affected_channel` MUST be available as a P0 filter and breakdown dimension, distinct from `intake_channel`.

---

## BR-ANA-010 — Household Count Is Conditional

**Priority:** P0  
**Rule:** Distinct household count may be displayed only when a valid pseudonymous household key exists and passes its data-quality gate.

Otherwise display `N/A`; do not infer households from feedback count.

---

# 11. Hotspot Rules

## BR-HOT-001 — Deterministic P0 Detection Key

**Priority:** P0  
**Rule:** P0 hotspot detection MUST be based on:

```text
primary_service_id
+ issue_id
+ normalized location at configured level
+ rolling time window
+ rule_version
```

---

## BR-HOT-002 — Only Accepted Eligible Items Count

**Priority:** P0  
**Rule:** Hotspot input MUST exclude:
- unreviewed AI predictions;
- duplicate items;
- excluded/ineligible items;
- records missing required detection dimensions.

---

## BR-HOT-003 — P0 Rule Is Threshold-Based

**Priority:** P0  
**Rule:** In a configured rolling window `W`, if at least `N` eligible deduplicated items share the configured detection key, the system MUST upsert one hotspot candidate.

Pilot vertical-slice default:

```text
W = 2 hours
N = 3
Service = SV-07
Issue = IS-07-01
Location level = Building/Zone
```

This is a test/pilot default, not a production-wide threshold.

---

## BR-HOT-004 — Hotspot Upsert Is Idempotent

**Priority:** P0  
**Rule:** The same `dimension_key + rule_version + active window` MUST NOT create duplicate active candidates when a job retries.

---

## BR-HOT-005 — Evidence Must Be Reproducible

**Priority:** P0  
**Rule:** Each hotspot candidate MUST retain the set of evidence Feedback Items used to create/recalculate it.

---

## BR-HOT-006 — Default Owner Comes From Service Configuration

**Priority:** P0  
**Rule:** New candidate owner SHOULD resolve from versioned Service operational ownership configuration.

If no owner exists:
- candidate goes to an unassigned queue;
- the condition is raised as a data-quality/operational configuration error.

`SV-10` has no implicit default owner.

---

## BR-HOT-007 — Hotspot Lifecycle Is Controlled

**Priority:** P0  
**Rule:** Allowed lifecycle:

```text
CANDIDATE → ACKNOWLEDGED → INVESTIGATING → RESOLVED
     └──────────────────────────────→ DISMISSED

RESOLVED/DISMISSED → REOPENED → INVESTIGATING
```

Invalid transitions MUST be rejected.

`INVESTIGATING` here is a Hotspot operational status only; in P0 it MUST NOT create an Investigation/RCA entity or change cause status to `UNDER_INVESTIGATION`.

---

## BR-HOT-008 — State/Ownership Changes Are Audited

**Priority:** P0  
**Rule:** Acknowledge, assign, reassign, dismiss, resolve, and reopen MUST capture actor, timestamp, and reason.

---

## BR-HOT-009 — Safety Hard Trigger Is Independent of Sentiment/Classifier

**Priority:** P1 after sign-off  
**Rule:** Approved safety hard triggers MUST NOT depend on sentiment or waiting for volume/classifier completion.

P0 MUST keep automated hard-trigger execution feature-flagged off until Safety/Legal/BQL approval.

---

# 12. Priority & Severity Rules

## BR-SEV-001 — Delivery Priority Is Not Operational Severity

**Priority:** P0  
**Rule:** These are separate dimensions:

```text
delivery_priority = P0 | P1 | P2
operational_severity = SEV-1 | SEV-2 | SEV-3 | SEV-4
```

They MUST NOT share:
- the same database field;
- the same API meaning;
- the same UI filter;
- the same display semantics.

---

## BR-SEV-002 — Legacy Priority Mapping

**Priority:** P0 migration  
**Rule:** Legacy operational Priority `P1..P4` maps to:

```text
P1 → SEV-1
P2 → SEV-2
P3 → SEV-3
P4 → SEV-4
```

The migration must make the semantic conversion explicit.

---

# 13. Security & Audit Rules

## BR-SEC-001 — Server-Side Authorization

**Priority:** P0  
**Rule:** Permission checks MUST be enforced by API/service layer. Hiding controls in UI is not authorization.

---

## BR-SEC-002 — Minimum Pilot Roles

**Priority:** P0  
**Rule:** Pilot MUST support at least:

```text
PILOT_ADMIN
ANALYST
REVIEWER
VIEWER
```

All users MUST be restricted to the approved pilot project scope.

---

## BR-SEC-003 — Raw PII Is Privileged

**Priority:** P0  
**Rule:** Viewing/exporting `content_raw` or customer identifiers requires an explicit privilege.

Non-privileged users must receive masked content.

---

## BR-SEC-004 — Privileged Actions Are Audited

**Priority:** P0  
**Rule:** Audit MUST cover at least:
- login/admin actions;
- import execution;
- raw PII view/export;
- taxonomy publication;
- Feedback Item split;
- classification decision;
- hotspot owner/state changes;
- hotspot rule changes.

---

## BR-SEC-005 — Audit Records Are Append-Only

**Priority:** P0  
**Rule:** Audit events MUST NOT be overwritten by normal application workflows.

---

# 14. Reliability & Data Quality Rules

## BR-DQ-001 — No Silent Fallback

**Priority:** P0  
**Rule:** Missing taxonomy, location, event time, owner, or invalid mapping MUST produce:
- an explicit value status, or
- an observable data-quality error.

The platform MUST NOT silently guess a replacement value.

---

## BR-DQ-002 — Projection Must Be Rebuildable

**Priority:** P0  
**Rule:** Current classification projection MUST be rebuildable from immutable decisions/review events.

---

## BR-DQ-003 — Async Work Must Be Retryable and Observable

**Priority:** P0  
**Rule:** Import, AI prediction, and hotspot evaluation jobs MUST expose:
- job state;
- retry behavior;
- correlation ID;
- error details;
- idempotency protection.

---

## BR-DQ-004 — Versioned Configuration Must Be Reproducible

**Priority:** P0  
**Rule:** Historical behavior MUST remain reproducible from stored taxonomy/mapping/metric/rule versions.

---

# 15. Rule-to-Enforcement Matrix

| Rule group | DB constraint | API/service validation | Async worker | UI validation | Audit | Automated test |
|---|---:|---:|---:|---:|---:|---:|
| Feedback immutability | ✓ | ✓ |  | ✓ | ✓ | ✓ |
| Atomic item/split |  | ✓ |  | ✓ | ✓ | ✓ |
| Lifecycle separation | ✓ | ✓ |  | ✓ |  | ✓ |
| Issue↔Service consistency | ✓/logical | ✓ |  | ✓ | ✓ | ✓ |
| Decision append-only | ✓ | ✓ |  | ✓ | ✓ | ✓ |
| Prediction suggest-only | ✓/logical | ✓ | ✓ | ✓ | ✓ | ✓ |
| Import idempotency | ✓ | ✓ | ✓ |  | ✓ | ✓ |
| Analytics eligibility |  | ✓ | ✓/query | ✓ |  | ✓ |
| Hotspot idempotency | ✓ | ✓ | ✓ |  | ✓ | ✓ |
| PII privilege |  | ✓ |  | ✓ | ✓ | ✓ |
| Taxonomy publish invariants | ✓/validator | ✓ | ✓ | ✓ | ✓ | ✓ |

---

# 16. Minimum P0 Acceptance Invariants

Before P0 is considered technically valid, automated tests MUST demonstrate at least:

1. Retry of the same import does not duplicate successful feedback.
2. A multi-intent feedback can be split without changing `content_raw`.
3. `SRV-*` cannot be persisted as a Customer Lifecycle step.
4. A known Issue cannot be saved under the wrong Primary Service.
5. A prediction cannot enter current projection without an accepted decision.
6. A manual correction creates a new decision version instead of overwriting history.
7. Current projection can be rebuilt from decision history.
8. `SV-10/IS-10-01` without `other_reason` is rejected.
9. A known taxonomy ID from a retired/non-published release cannot be used for a new decision.
10. Analytics exclude unreviewed predictions and ineligible items.
11. The configured vertical slice creates exactly one hotspot candidate at threshold.
12. Retrying hotspot evaluation does not duplicate that candidate.
13. Hotspot evidence set is traceable back to the exact Feedback Items.
14. Raw PII is denied to a role without raw-view privilege.
15. Every privileged/decision/hotspot-state mutation creates an audit record.

---

# 17. Open Business Decisions That Block or Shape P0

The following must remain explicit configuration/decision records rather than hard-coded assumptions:

- pilot project/building/source/date range/user cohort;
- source-trust policy;
- multi-intent split guideline;
- required versus optional UNKNOWN fields;
- location hierarchy and grouping level;
- Service owner configuration;
- final legacy severity mapping approval;
- PII masking/retention/export policy;
- hotspot `N`, `W`, cooldown, owner and playbook;
- pilot sizing and file-size limit;
- gold-set sampling/adjudication rules;
- operational metric baseline.

---

# 18. Source of Truth

This document is derived from:

1. `docs/PRD.md` — product requirements, domain model, functional requirements, business rules, API baseline, NFRs, MVP acceptance.
2. `docs/service_taxonomy.md` — canonical lifecycle/service/issue definitions and taxonomy publication invariants.

Any new rule that changes canonical taxonomy meaning must first be reflected in `service_taxonomy.md`.  
Any new rule that changes product scope/behavior must first be reflected in `PRD.md` or a linked Decision Record.
