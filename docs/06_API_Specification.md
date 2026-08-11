# 06 — API Specification

# CX Journey, Service & Root Cause Intelligence Platform

**Version:** 1.0  
**Status:** P0 Pilot Build Baseline  
**Derived from:** `05_Data_Model.md`, `docs/System_Design.md`, `docs/Business_Rules.md`, `docs/service_taxonomy.md`  
**API style:** REST/JSON over HTTPS  
**Backend:** FastAPI + Pydantic v2  
**Base path:** `/api/v1`

---

## 1. Purpose

This document defines the P0 HTTP contract used by:

```text
apps/web
workers / internal clients
future approved connectors
```

The API MUST preserve domain invariants rather than exposing database CRUD directly.

Key rules:

- clients select stable taxonomy IDs/codes, not localized labels;
- taxonomy row CRUD is not exposed in P0;
- raw Feedback is immutable;
- Feedback Item is the unit of review and analytics;
- prediction does not change current classification;
- accepted classification writes create immutable Decision versions;
- mutation endpoints enforce authorization, audit and optimistic concurrency;
- KPI/chart/drill-down endpoints use one analytics eligibility definition.

---

# 2. Common Conventions

## 2.1 Base URL

```text
/api/v1
```

Example:

```http
GET /api/v1/feedback-items
```

---

## 2.2 Content Type

```http
Content-Type: application/json
Accept: application/json
```

File upload endpoints use `multipart/form-data`.

---

## 2.3 Authentication

P0 uses SSO-backed authentication.

API receives/derives principal context:

```json
{
  "user_id": "uuid",
  "role_ids": ["REVIEWER"],
  "privileges": [
    "feedback:read",
    "classification:review"
  ],
  "allowed_project_ids": ["uuid"],
  "raw_pii_allowed": false,
  "export_allowed": false
}
```

Minimum application roles:

```text
PILOT_ADMIN
ANALYST
REVIEWER
VIEWER
```

Authorization MUST be enforced server-side.

---

## 2.4 Correlation ID

Clients MAY send:

```http
X-Correlation-ID: <uuid-or-client-id>
```

If absent, API creates one.

Every response SHOULD return:

```http
X-Correlation-ID: ...
```

and include `request_id` in response metadata/errors.

---

## 2.5 Idempotency

Retryable mutation endpoints SHOULD accept:

```http
Idempotency-Key: <client-generated-key>
```

Typical use:

- create import job;
- execute/retry import;
- create prediction job;
- mutation where duplicate submission would be harmful.

Conflicting reuse:

```text
409 IDEMPOTENCY_CONFLICT
```

---

## 2.6 Optimistic Concurrency

Mutable operational resources use one of:

```text
expected_version
expected_current_decision_id
expected_projection_version
```

A stale mutation returns:

```text
409 VERSION_CONFLICT
```

The server MUST NOT silently apply a stale review or hotspot update.

---

# 3. Standard Response Envelope

Resource endpoints MAY return the resource directly. Collection/operation endpoints SHOULD use:

```json
{
  "data": {},
  "meta": {
    "request_id": "uuid",
    "timestamp": "2026-08-11T09:00:00Z"
  }
}
```

Collections:

```json
{
  "data": [],
  "page": {
    "limit": 50,
    "next_cursor": "opaque-or-null",
    "total": 1200
  },
  "meta": {
    "request_id": "uuid"
  }
}
```

`total` MAY be omitted for expensive cursor queries.

---

# 4. Standard Error Contract

```json
{
  "error": {
    "code": "DOMAIN_RULE_VIOLATION",
    "message": "Issue does not belong to selected Primary Service.",
    "field_errors": [
      {
        "field": "issue_id",
        "code": "ISSUE_SERVICE_MISMATCH",
        "message": "IS-07-01 must belong to SV-07 in the selected taxonomy release."
      }
    ],
    "details": {},
    "request_id": "uuid"
  }
}
```

Standard HTTP mapping:

| HTTP | Code | Meaning |
|---:|---|---|
| 400 | VALIDATION_ERROR | malformed/basic request validation |
| 401 | UNAUTHENTICATED | no valid identity |
| 403 | FORBIDDEN | privilege/project scope denied |
| 404 | NOT_FOUND | resource not found/in scope |
| 409 | VERSION_CONFLICT | optimistic concurrency |
| 409 | IDEMPOTENCY_CONFLICT | reused key with different payload |
| 422 | DOMAIN_RULE_VIOLATION | valid JSON but violates domain invariant |
| 429 | RATE_LIMITED | throttled |
| 500 | INTERNAL_ERROR | unexpected server failure |

Raw PII MUST NOT be echoed in error payloads.

---

# 5. Pagination, Sorting and Filtering

## 5.1 Cursor Pagination

Preferred for large Feedback Item lists:

```http
GET /feedback-items?limit=50&cursor=<opaque>
```

Default:

```text
limit = 50
max   = 200
```

---

## 5.2 Sorting

Allowlisted syntax:

```http
?sort=-reported_at
?sort=operational_severity,-reported_at
```

Clients MUST NOT pass arbitrary SQL column names.

---

## 5.3 Stable Filter Values

Use IDs/codes:

```http
?service_code=SV-07
?issue_code=IS-07-01
?customer_lifecycle_step_code=RES-03
?service_request_step_code=SRV-02
```

Do not filter by translated label text.

---

# 6. Reference / Taxonomy APIs

All normal read endpoints return published values unless `taxonomy_release_id` is explicitly supplied and caller has permission.

## 6.1 Customer Lifecycle Stages

```http
GET /api/v1/customer-lifecycle/stages
```

Query:

```text
taxonomy_release_id?
active=true
```

Response item:

```json
{
  "id": "uuid",
  "code": "RES",
  "name_vi": "Cư trú",
  "name_en": "Residence",
  "sort_order": 5
}
```

---

## 6.2 Customer Lifecycle Steps

```http
GET /api/v1/customer-lifecycle/steps
```

Filters:

```text
stage_code
taxonomy_release_id
active
```

Response:

```json
{
  "id": "uuid",
  "code": "RES-03",
  "stage": {
    "id": "uuid",
    "code": "RES"
  },
  "name_vi": "Ra vào & di chuyển",
  "definition": "..."
}
```

---

## 6.3 Service Request Steps

```http
GET /api/v1/service-request-lifecycle/steps
```

---

## 6.4 Services

```http
GET /api/v1/services
GET /api/v1/services/{service_id}
```

Response item:

```json
{
  "id": "uuid",
  "code": "SV-07",
  "name_vi": "Kỹ thuật, tiện ích & tài sản chung",
  "name_en": "Engineering, Utilities & Common Assets",
  "default_severity": "SEV-3"
}
```

---

## 6.5 Issues by Service

```http
GET /api/v1/services/{service_id}/issues
```

Alternative filter:

```http
GET /api/v1/issues?service_code=SV-07
```

Response item:

```json
{
  "id": "uuid",
  "code": "IS-07-01",
  "service_id": "uuid",
  "name_vi": "Hệ thống ngừng hoặc suy giảm",
  "safety_critical": false,
  "severity_override": null
}
```

---

## 6.6 Candidate Causes

```http
GET /api/v1/issues/{issue_id}/candidate-causes
```

Response:

```json
{
  "data": [
    {
      "cause_id": "uuid",
      "cause_code": "CAUSE-ELEVATOR-CAPACITY",
      "name_vi": "...",
      "rank_hint": 1,
      "required_evidence": "..."
    }
  ]
}
```

This endpoint returns possible hypotheses only.

---

## 6.7 Lifecycle-Service Mappings

```http
GET /api/v1/lifecycle-service-mappings
```

Filters:

```text
lifecycle_type
lifecycle_step_code
service_code
taxonomy_release_id
```

---

## 6.8 Locations

```http
GET /api/v1/locations
```

Filters:

```text
project_id   # required unless principal has exactly one project
parent_id
location_type
q
active
```

---

## 6.9 Taxonomy Release Validation

Admin only:

```http
POST /api/v1/taxonomy-versions/{taxonomy_release_id}/validate
```

Response:

```json
{
  "data": {
    "valid": true,
    "checks": [
      {"code": "SERVICE_COUNT", "status": "PASS", "actual": 10, "expected": 10},
      {"code": "ISSUE_COUNT", "status": "PASS", "actual": 28, "expected": 28}
    ],
    "checksum": "..."
  }
}
```

---

## 6.10 Publish Taxonomy

Admin only:

```http
POST /api/v1/taxonomy-versions/{taxonomy_release_id}/publish
```

Request:

```json
{
  "expected_status": "APPROVED",
  "effective_from": "2026-08-12T00:00:00Z",
  "reason": "Publish taxonomy 3.0.0 for P0 pilot."
}
```

Rules:

- validation must pass;
- state transition must be valid;
- audit mandatory.

---

# 7. Import APIs

## 7.1 Create Import Job

```http
POST /api/v1/import-jobs
Content-Type: multipart/form-data
Idempotency-Key: ...
```

Fields:

```text
file
project_id
source_system
mapping_profile_id? 
```

Response `202 Accepted`:

```json
{
  "data": {
    "import_job_id": "uuid",
    "status": "UPLOADED",
    "filename": "feedback.xlsx",
    "file_size_bytes": 123456,
    "created_at": "..."
  }
}
```

---

## 7.2 Save/Update Mapping

```http
PUT /api/v1/import-jobs/{id}/mapping
```

Request:

```json
{
  "expected_version": 1,
  "mapping": {
    "ticket_id": "source_record_key",
    "reported_date": "reported_at",
    "content_masked": "content",
    "project": "project",
    "channel": "intake_channel"
  }
}
```

Response sets job to `MAPPED`.

---

## 7.3 Preview Import

```http
POST /api/v1/import-jobs/{id}/preview
```

Request:

```json
{
  "sample_rows": 50
}
```

Response shows normalized preview without committing Feedback.

---

## 7.4 Validate Import

```http
POST /api/v1/import-jobs/{id}/validate
Idempotency-Key: ...
```

Response:

```text
202 Accepted
```

```json
{
  "data": {
    "import_job_id": "uuid",
    "status": "VALIDATING"
  }
}
```

---

## 7.5 Get Import Job

```http
GET /api/v1/import-jobs/{id}
```

Response:

```json
{
  "data": {
    "import_job_id": "uuid",
    "status": "VALIDATED",
    "total_rows": 18546,
    "valid_rows": 18110,
    "invalid_rows": 436,
    "committed_rows": 0,
    "version": 4
  }
}
```

---

## 7.6 Import Errors

```http
GET /api/v1/import-jobs/{id}/errors
```

Filters:

```text
field_name
error_code
limit
cursor
```

---

## 7.7 Execute Import

```http
POST /api/v1/import-jobs/{id}/execute
Idempotency-Key: ...
```

Request:

```json
{
  "expected_version": 4,
  "allow_partial": true
}
```

Response:

```text
202 Accepted
```

---

## 7.8 Retry Import

```http
POST /api/v1/import-jobs/{id}/retry
```

Retry only failed/uncommitted work according to idempotency rules.

---

## 7.9 Cancel Import

```http
POST /api/v1/import-jobs/{id}/cancel
```

Queued/processing job transitions to `CANCELLING` then `CANCELLED` when safely stopped.

---

# 8. Feedback Workspace APIs

## 8.1 List Feedback Items

```http
GET /api/v1/feedback-items
```

Main filters:

```text
project_id
date_from
date_to

source_system
intake_channel_code
location_id

customer_lifecycle_stage_code
customer_lifecycle_step_code
service_request_step_code

service_code
issue_code
sentiment
operational_severity

classification_state
cause_determination_status
analytic_eligibility

has_prediction
needs_review
q

sort
limit
cursor
```

Default item response:

```json
{
  "feedback_item_id": "uuid",
  "feedback_id": "uuid",
  "reported_at": "2026-05-31T03:20:00Z",
  "source_system": "internal_csv",
  "content_masked": "S10512 hỗ trợ gọi KT sửa cửa",
  "location": {
    "id": "uuid",
    "code": "S10512",
    "name": "S10 / Unit 512"
  },
  "current_classification": {
    "service": {"id": "uuid", "code": "SV-07", "name_vi": "..."},
    "issue": {"id": "uuid", "code": "IS-07-03", "name_vi": "..."},
    "sentiment": "NEUTRAL",
    "operational_severity": "SEV-3",
    "classification_state": "ACCEPTED",
    "projection_version": 3
  },
  "review": {
    "needs_review": false,
    "latest_prediction_confidence": 0.91
  }
}
```

Raw content is never returned by this collection endpoint.

---

## 8.2 Get Feedback Envelope

```http
GET /api/v1/feedback/{feedback_id}
```

Default response returns masked content and provenance.

Raw content requires explicit endpoint/privilege; see §8.5.

---

## 8.3 Get Feedback Item Detail

```http
GET /api/v1/feedback-items/{feedback_item_id}
```

Includes:

```text
masked text
source provenance
location
affected channels
current classification
latest predictions summary
decision/review summary
hotspot links
split lineage
```

---

## 8.4 Affected Channels

```http
PUT /api/v1/feedback-items/{id}/affected-channels
```

Request:

```json
{
  "expected_version": 2,
  "channel_ids": ["uuid", "uuid"]
}
```

This is operational context; taxonomy labels are not created here.

---

## 8.5 Privileged Raw View

```http
POST /api/v1/feedback/{feedback_id}/raw-view
```

Request:

```json
{
  "reason": "Investigating source discrepancy for case #123."
}
```

Requirements:

```text
raw_pii_allowed = true
reason required
audit mandatory
```

Response:

```json
{
  "data": {
    "feedback_id": "uuid",
    "content_raw": "...",
    "view_token_expires_at": "..."
  }
}
```

Do not expose raw content through generic GET endpoints.

---

# 9. Feedback Item Split API

```http
POST /api/v1/feedback/{feedback_id}/items/split
```

Request:

```json
{
  "source_feedback_item_id": "uuid",
  "expected_projection_version": 3,
  "reason": "Two independent observable failures.",
  "items": [
    {
      "item_text_masked": "Thang máy chậm vào buổi sáng",
      "symptom_detail": "Chờ thang máy lâu",
      "location_id": "uuid"
    },
    {
      "item_text_masked": "App cư dân không đăng nhập được",
      "symptom_detail": "OTP/login failure",
      "location_id": null
    }
  ]
}
```

Response `201 Created`:

```json
{
  "data": {
    "source_item": {
      "id": "uuid",
      "status": "SPLIT_PARENT"
    },
    "created_items": [
      {"id": "uuid", "item_index": 2},
      {"id": "uuid", "item_index": 3}
    ]
  }
}
```

Rules:

- original `content_raw` unchanged;
- source item historical decisions remain;
- audit mandatory.

---

# 10. Prediction APIs

## 10.1 Create Prediction Job

```http
POST /api/v1/ai/prediction-jobs
Idempotency-Key: ...
```

Request:

```json
{
  "project_id": "uuid",
  "taxonomy_release_id": "uuid",
  "selection": {
    "feedback_item_ids": ["uuid"],
    "or_filter": null
  },
  "fields": [
    "customer_lifecycle_step",
    "service_request_step",
    "primary_service",
    "issue",
    "sentiment"
  ]
}
```

Response:

```text
202 Accepted
```

---

## 10.2 Prediction Job Status

```http
GET /api/v1/ai/prediction-jobs/{job_id}
```

---

## 10.3 Feedback Item Predictions

```http
GET /api/v1/feedback-items/{id}/predictions
```

Filters:

```text
field_name
prediction_run_id
latest_only
```

Response groups candidates by field and retains model/taxonomy version.

---

# 11. Classification Decision APIs

## 11.1 Decision History

```http
GET /api/v1/feedback-items/{id}/decisions
```

Returns immutable versions newest first.

---

## 11.2 Current Classification

```http
GET /api/v1/feedback-items/{id}/current-classification
```

Response:

```json
{
  "data": {
    "feedback_item_id": "uuid",
    "current_decision_id": "uuid",
    "current_decision_version": 3,
    "projection_version": 3,
    "taxonomy_release_id": "uuid",
    "customer_lifecycle": {
      "value_status": "KNOWN",
      "stage": {"id": "uuid", "code": "RES", "name_vi": "Cư trú"},
      "step": {"id": "uuid", "code": "RES-03", "name_vi": "Ra vào & di chuyển"}
    },
    "service_request": {
      "value_status": "NOT_APPLICABLE",
      "step": null
    },
    "primary_service": {
      "value_status": "KNOWN",
      "service": {"id": "uuid", "code": "SV-07"}
    },
    "issue": {
      "value_status": "KNOWN",
      "issue": {"id": "uuid", "code": "IS-07-01"}
    },
    "sentiment": "NEGATIVE",
    "operational_severity": "SEV-3",
    "cause_determination_status": "UNKNOWN",
    "candidate_causes": []
  }
}
```

---

## 11.3 Create Classification Decision

Canonical review write:

```http
POST /api/v1/feedback-items/{id}/decisions
```

Request:

```json
{
  "expected_current_decision_id": "uuid-or-null",
  "expected_projection_version": 3,
  "taxonomy_release_id": "uuid",

  "customer_lifecycle": {
    "value_status": "KNOWN",
    "step_id": "uuid"
  },

  "service_request": {
    "value_status": "NOT_APPLICABLE",
    "step_id": null
  },

  "primary_service": {
    "value_status": "KNOWN",
    "service_id": "uuid"
  },

  "issue": {
    "value_status": "KNOWN",
    "issue_id": "uuid"
  },

  "sentiment": "NEGATIVE",
  "operational_severity": "SEV-3",

  "cause_determination_status": "CANDIDATE_AVAILABLE",
  "candidate_causes": [
    {
      "cause_id": "uuid",
      "rank": 1,
      "confidence": 0.72,
      "rationale_masked": "..."
    }
  ],

  "other_reason": null,
  "prediction_refs": ["prediction_event_uuid"],
  "decision_source": "AI_ACCEPTED",
  "decision_reason": "Accepted service/issue; corrected lifecycle."
}
```

Server behavior:

```text
validate expected version
validate taxonomy release
derive lifecycle stage from step
validate issue belongs to service
validate value_status/FK pairs
validate SV-10 rule
insert immutable decision
update current projection
write review + audit
commit
```

Response `201 Created` returns new decision and projection.

---

## 11.4 Review Prediction Shortcut

System Design exposes:

```http
POST /api/v1/ai/predictions/{prediction_id}/review
```

This endpoint is a UI convenience only. It MUST internally call the same decision application service as `POST /feedback-items/{id}/decisions`.

Request:

```json
{
  "action": "ACCEPT",
  "expected_projection_version": 3,
  "overrides": {},
  "comment": "Prediction is correct."
}
```

Allowed actions:

```text
ACCEPT
CORRECT
MARK_UNKNOWN
```

No separate mutable "prediction review state" may become an alternative source of truth.

---

# 12. Review Queue APIs

Recommended P0 query abstraction:

```http
GET /api/v1/review-queue
```

Filters:

```text
project_id
field_name
confidence_lt
service_code
severity
age_gt_minutes
q
limit
cursor
```

Queue item:

```json
{
  "feedback_item_id": "uuid",
  "reported_at": "...",
  "content_masked": "...",
  "prediction": {
    "service": {"code": "SV-07", "confidence": 0.93},
    "issue": {"code": "IS-07-01", "confidence": 0.81}
  },
  "current_projection_version": 2,
  "risk_flags": ["LOW_CONFIDENCE"]
}
```

Ordering baseline:

```text
safety/hard trigger
→ severity
→ oldest pending review
→ lower confidence
```

---

# 13. Analytics APIs

Analytics endpoints MUST read the governed semantic layer.

## 13.1 Shared Filter Contract

All dashboard endpoints accept a common serialized filter context:

```text
project_id
date_from
date_to
source_system
intake_channel_code
location_id/location_scope
customer_lifecycle_stage_code
customer_lifecycle_step_code
service_request_step_code
service_code
issue_code
sentiment
operational_severity
```

The same filter object MUST be reusable for drill-down to `/feedback-items`.

---

## 13.2 Dashboard Summary

```http
GET /api/v1/analytics/summary
```

Response:

```json
{
  "data": {
    "item_volume": 18546,
    "negative_rate": 0.342,
    "unknown_rate": 0.074,
    "active_hotspots": 7,
    "top_service": {
      "code": "SV-07",
      "name_vi": "Kỹ thuật, tiện ích & tài sản chung",
      "count": 3620
    },
    "top_issue": {
      "code": "IS-07-01",
      "count": 1490
    },
    "top_location": {
      "id": "uuid",
      "name": "S2",
      "count": 620
    },
    "eligibility_definition_version": "v1"
  }
}
```

---

## 13.3 Trend

```http
GET /api/v1/analytics/trend
```

Query:

```text
metric=item_volume|negative_rate|unknown_rate
grain=day|week|month
<shared filters>
```

---

## 13.4 Breakdown

```http
GET /api/v1/analytics/breakdown
```

Query:

```text
dimension=service|issue|location|journey_stage|journey_step|service_request_step|channel|sentiment|severity
metric=item_volume
limit=20
<shared filters>
```

---

## 13.5 Data Quality

```http
GET /api/v1/analytics/data-quality
```

Returns:

```text
missing/unknown by field
SV-10 usage rate
ineligible count
unclassified count
low-confidence prediction count
stale review queue count
```

---

## 13.6 Drill-down Consistency

Each analytics result MAY return:

```json
{
  "drilldown": {
    "resource": "/api/v1/feedback-items",
    "filter_context": "opaque-or-json-safe-filter"
  }
}
```

UI MUST reuse this context rather than reconstructing filter logic from chart labels.

---

# 14. Hotspot APIs

## 14.1 List Hotspots

```http
GET /api/v1/hotspots
```

Filters:

```text
project_id
status
service_code
issue_code
location_id
severity
assigned_to_me
date_from
date_to
sort
limit
cursor
```

---

## 14.2 Hotspot Detail

```http
GET /api/v1/hotspots/{id}
```

Response includes:

```text
dimensions
rule/version
status
severity
owner
first_seen/last_seen
evidence_count
evidence feedback items
timeline
investigation summary if any
```

---

## 14.3 Acknowledge

```http
POST /api/v1/hotspots/{id}/acknowledge
```

Request:

```json
{
  "expected_version": 4,
  "reason": "Operations team has accepted triage."
}
```

---

## 14.4 Assign

```http
POST /api/v1/hotspots/{id}/assign
```

```json
{
  "expected_version": 5,
  "owner_user_id": "uuid",
  "owner_team_key": null,
  "reason": "Assign to engineering duty manager."
}
```

---

## 14.5 Dismiss

```http
POST /api/v1/hotspots/{id}/dismiss
```

Reason is mandatory.

---

## 14.6 Start Investigation

Recommended explicit endpoint:

```http
POST /api/v1/hotspots/{id}/investigations
```

Request:

```json
{
  "expected_version": 6,
  "title": "Investigate recurrent elevator wait-time degradation",
  "owner_user_id": "uuid"
}
```

Hotspot transitions to `INVESTIGATING` in the same transaction when valid.

---

## 14.7 Resolve

```http
POST /api/v1/hotspots/{id}/resolve
```

Request:

```json
{
  "expected_version": 8,
  "reason": "Root cause confirmed and corrective action completed.",
  "resolution_summary": "..."
}
```

---

## 14.8 Reopen

```http
POST /api/v1/hotspots/{id}/reopen
```

Allowed from:

```text
RESOLVED
DISMISSED
```

Reason required.

---

# 15. Investigation / Root Cause APIs

## 15.1 Investigation Detail

```http
GET /api/v1/investigations/{id}
```

---

## 15.2 Add Evidence

```http
POST /api/v1/investigations/{id}/evidence
```

May use JSON external reference or multipart upload.

---

## 15.3 Confirm Root Cause

Restricted privilege:

```http
POST /api/v1/investigations/{id}/root-causes
```

Request:

```json
{
  "expected_version": 3,
  "cause_id": "uuid-or-null",
  "root_cause_text": "Door sensor calibration drift caused repeated abnormal stops.",
  "evidence_summary": "Maintenance logs + inspection result + reproduced failure.",
  "corrective_actions": [
    {
      "description": "Recalibrate affected sensors",
      "owner_user_id": "uuid",
      "due_at": "..."
    }
  ],
  "preventive_actions": [
    {
      "description": "Add calibration check to preventive maintenance",
      "owner_team_key": "ENGINEERING",
      "due_at": "..."
    }
  ]
}
```

AI MUST NOT call this endpoint as an autonomous confirmer.

---

# 16. Audit APIs

Admin/auditor:

```http
GET /api/v1/audit-events
```

Filters:

```text
project_id
actor_user_id
action
resource_type
resource_id
date_from
date_to
limit
cursor
```

Raw PII is not returned in audit metadata by default.

---

# 17. Export APIs

P0 exports SHOULD be asynchronous for large datasets.

```http
POST /api/v1/exports
GET  /api/v1/exports/{id}
```

Request:

```json
{
  "resource": "feedback_items",
  "filters": {},
  "columns": [
    "reported_at",
    "service_code",
    "issue_code",
    "location_code",
    "sentiment"
  ],
  "include_raw_content": false
}
```

Rules:

- `export_allowed` required;
- `include_raw_content=true` additionally requires `raw_pii_allowed`;
- raw export reason mandatory;
- raw export is audited;
- resulting object uses short-lived signed download URL.

---

# 18. API Permission Matrix

| Capability | VIEWER | ANALYST | REVIEWER | PILOT_ADMIN |
|---|:---:|:---:|:---:|:---:|
| View dashboard | ✓ | ✓ | ✓ | ✓ |
| View masked feedback | ✓ | ✓ | ✓ | ✓ |
| Run analytics filters | ✓ | ✓ | ✓ | ✓ |
| Export masked data | policy | ✓ | ✓ | ✓ |
| View raw content | — | policy | policy | policy |
| Run AI prediction | — | ✓ | ✓ | ✓ |
| Create classification decision | — | — | ✓ | ✓ |
| Split Feedback Item | — | — | ✓ | ✓ |
| Manage hotspot | — | policy | ✓ | ✓ |
| Confirm root cause | — | — | privilege | ✓ |
| Validate/publish taxonomy | — | — | — | ✓ |
| View audit | — | — | — | ✓ |

`policy` means explicit privilege and project scope are still required.

---

# 19. API-to-Database Mapping

| API Resource | Primary Data Source |
|---|---|
| `/feedback-items` | `analytics_feedback_item_v1` + workspace joins |
| `/feedback/{id}` | `feedback` |
| `/feedback-items/{id}` | `feedback_item` + projection + ledgers |
| `/predictions` | `prediction_event` |
| `/decisions` | `classification_decision` |
| `/current-classification` | `classification_current` |
| `/analytics/*` | governed semantic layer |
| `/hotspots` | `hotspot` + evidence/timeline |
| `/investigations` | investigation/RCA tables |
| `/audit-events` | `audit_event` |
| taxonomy reads | published reference tables |

---

# 20. OpenAPI Requirements

FastAPI OpenAPI output MUST define:

- all request/response schemas;
- enums;
- validation constraints;
- documented error envelopes;
- authentication scheme;
- pagination contract;
- example payloads;
- operation IDs stable enough for frontend client generation.

Recommended operation IDs:

```text
listFeedbackItems
getFeedbackItem
splitFeedbackItem
createClassificationDecision
listServices
listIssues
createImportJob
executeImportJob
getAnalyticsSummary
listHotspots
acknowledgeHotspot
```

Do not expose ORM models directly as response schemas.

---

# 21. Performance Targets

Subject to pilot sizing:

```text
GET /feedback-items                 p95 < 3s
GET /feedback-items/{id}            p95 < 2s
GET /analytics/summary              p95 < 5s
GET /analytics/breakdown            p95 < 5s
simple taxonomy reads               p95 < 1s
```

Mutation endpoints that enqueue async work should return quickly with `202 Accepted`.

---

# 22. Security Requirements

1. HTTPS only outside local development.
2. Server-side project scope enforcement.
3. No raw PII in logs/errors.
4. Raw view/export requires explicit privilege and audit.
5. Signed object URLs must expire.
6. Rate-limit expensive search/export/prediction endpoints.
7. Validate uploaded file type/size/checksum.
8. Reject unsafe arbitrary sort/filter expressions.
9. Do not trust role claims supplied by frontend UI.
10. Correlation IDs are identifiers, not authorization tokens.

---

# 23. Contract Tests

P0 contract tests MUST prove:

1. unauthorized project access returns 403/404 according to policy;
2. taxonomy reads return published stable IDs/codes;
3. issue-service mismatch returns 422;
4. stale decision write returns 409;
5. prediction review creates a Decision, not an alternate truth record;
6. split does not mutate raw Feedback;
7. raw content endpoint enforces privilege and audit;
8. retrying idempotent import does not duplicate Feedback;
9. analytics drill-down filter context reproduces chart counts;
10. invalid hotspot state transition returns 422;
11. SV-10 without `other_reason` returns 422;
12. `KNOWN` with null reference returns 422;
13. large async operation returns 202 with job resource;
14. API never returns raw PII in standard errors.

---

# 24. P0 Build Order

Recommended implementation sequence:

```text
1. auth principal + error envelope + correlation ID
2. taxonomy read endpoints
3. import job endpoints
4. feedback list/detail
5. prediction job/read endpoints
6. decision/current-classification endpoints
7. review queue
8. analytics summary/breakdown/trend
9. hotspot list/detail/mutations
10. split workflow
11. privileged raw view/export
12. taxonomy validate/publish admin endpoints
13. investigation/root-cause workflow
14. audit query endpoint
```

---

# 25. API Acceptance Criteria

The P0 API is build-ready when:

- OpenAPI schemas match `05_Data_Model.md`;
- no endpoint permits mutation that violates append-only ledgers;
- all classification writes use the same application service;
- version conflict behavior is standardized;
- stable IDs/codes are used in filters;
- taxonomy is not hard-coded in UI/backend handlers;
- analytics and drill-down share one filter semantics;
- raw PII boundary is explicit and audited;
- contract tests pass;
- UI can implement every required P0 flow without direct database assumptions.
