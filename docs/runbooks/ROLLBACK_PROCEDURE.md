# Rollback & Forward-Fix Procedure — Trusted CSV to Dashboard Pilot

- **Status:** Active
- **Target Audience:** Release Engineers, Data Stewards, On-Call Engineers

---

## 1. Principles of Safe Rollback

1. **No Data Loss**: Ingested `source_record`, `feedback`, `feedback_item`, and `classification_decision` are **immutable**. Rollback never drops or deletes canonical data.
2. **Forward-Fix Priority**: Database schema fixes should prefer forward-fix migrations over destructive downgrades.
3. **Application Version Rollback**: Application containers (API, Worker, Web) can be safely rolled back to the previous compatible container image digest.

---

## 2. Application Rollback Steps

If an application defect is discovered in staging or production:

```bash
# 1. Identify previous verified healthy release SHA
PREV_SHA=<PREVIOUS_GOOD_COMMIT_SHA>

# 2. Roll back container deployment
git checkout $PREV_SHA
cd infra/docker
docker-compose up -d --build

# 3. Verify health checks
curl -f http://localhost:8000/health/live
```

---

## 3. Projection Rebuild Procedure

If the read projection `classification_current` becomes inconsistent with accepted decisions:

```bash
# Execute idempotent projection rebuild
docker-compose exec -T api python -c "
import asyncio
from cx_db.src.repositories.uow import rebuild_all_projections
asyncio.run(rebuild_all_projections())
"
```

---

## 4. Post-Rollback Evidence Logging

Document the incident with:
- Incident Timestamp & Duration.
- Rollback Triggering Reason & Error Correlation ID.
- Root Cause Analysis (RCA) link assigned to responsible Feature owner.
