# Staging Deployment Runbook — Trusted CSV to Dashboard Pilot

- **Status:** Active
- **Target Audience:** Release Engineers, DevOps, Quality Leads

---

## 1. Pre-deployment Checklist

Before triggering a deployment to the staging environment, ensure:

1. All PR checks on GitHub Actions are **GREEN** (`lint`, `typecheck`, `test`, `web-build`).
2. Release commit SHA is tagged or explicitly identified on `dev` branch.
3. Database migrations in `packages/db/alembic/versions` have passed clean migration tests.
4. Masked test dataset checksum matches `trusted-feedback-csv/v1` specifications.

---

## 2. Deployment Steps

Execute the following commands in the deployment pipeline or staging server:

```bash
# 1. Clone/Fetch the release SHA
git fetch origin --prune
git checkout <RELEASE_COMMIT_SHA>

# 2. Build and start containers with Docker Compose
cd infra/docker
docker-compose down --remove-orphans
docker-compose build --no-cache
docker-compose up -d

# 3. Run Alembic Database Migrations
docker-compose exec -T api alembic upgrade head

# 4. Verify Health Status
curl -f http://localhost:8000/health/live
curl -f http://localhost:8000/health/ready
```

---

## 3. Post-Deployment Verification (UAT)

1. Upload the pilot CSV dataset (`trusted-feedback-csv/v1`) via the `/imports` UI.
2. Confirm validation summary reports:
   - `total_rows == valid_rows + invalid_rows + duplicate_rows`
3. Trigger **Execute Import** and confirm status reaches `COMMITTED`.
4. Open `/dashboard` and verify KPI cards, Trend chart, and Breakdown bar charts match the imported records.
5. Click a chart segment to drill-down to `/feedback` list and inspect single item detail provenance (`import_job_id`, `source_reference`, `decision: SOURCE_TRUSTED`).
