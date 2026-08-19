"""Pipeline service to classify database feedback items with AI and update projections."""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Sequence
from uuid import UUID, uuid4

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from packages.ai.classifier import FeedbackClassifier
from packages.ai.schemas import (
    BatchClassificationOutput,
    FeedbackClassificationResult,
    FeedbackItemInput,
)

logger = logging.getLogger(__name__)


class AIClassificationPipeline:
    """Orchestrates AI classification execution against DB records."""

    def __init__(
        self,
        session: AsyncSession,
        classifier: FeedbackClassifier | None = None,
    ) -> None:
        self._session = session
        self._classifier = classifier or FeedbackClassifier()

    async def classify_items_direct(
        self,
        inputs: Sequence[FeedbackItemInput],
    ) -> BatchClassificationOutput:
        """Classify input items directly without database persistence."""
        return await self._classifier.classify_batch(inputs)

    async def run_batch_classification(
        self,
        project_id: UUID,
        *,
        limit: int = 100,
        batch_size: int = 25,
    ) -> dict[str, int]:
        """Fetch pending/unclassified items from database and apply AI classification."""
        # 1. Fetch items needing classification
        res = await self._session.execute(
            text("""
                SELECT fi.feedback_item_id, fi.item_text_masked, loc.name AS location_name,
                       intake.name_vi AS channel_name, f.reported_at
                FROM feedback_item fi
                INNER JOIN feedback f ON f.feedback_id = fi.feedback_id
                LEFT JOIN location loc ON loc.location_id = fi.location_id
                LEFT JOIN interaction_channel intake ON intake.interaction_channel_id = f.intake_channel_id
                WHERE f.project_id = :project_id
                  AND fi.status = 'ACTIVE'
                ORDER BY f.reported_at DESC
                LIMIT :limit
            """),
            {"project_id": project_id, "limit": limit},
        )
        rows = res.mappings().all()
        if not rows:
            return {"processed": 0, "classified": 0}

        # 2. Fetch taxonomy references
        services_res = await self._session.execute(
            text("SELECT service_id, service_code FROM service")
        )
        service_map = {r["service_code"]: r["service_id"] for r in services_res.mappings().all()}

        issues_res = await self._session.execute(
            text("SELECT issue_id, issue_code FROM issue")
        )
        issue_map = {r["issue_code"]: r["issue_id"] for r in issues_res.mappings().all()}

        steps_res = await self._session.execute(
            text("SELECT customer_lifecycle_step_id, customer_lifecycle_stage_id, step_code FROM customer_lifecycle_step")
        )
        step_map = {r["step_code"]: (r["customer_lifecycle_step_id"], r["customer_lifecycle_stage_id"]) for r in steps_res.mappings().all()}

        stages_res = await self._session.execute(
            text("SELECT customer_lifecycle_stage_id, stage_code FROM customer_lifecycle_stage")
        )
        stage_map = {r["stage_code"]: r["customer_lifecycle_stage_id"] for r in stages_res.mappings().all()}

        # 3. Process in batches
        classified_count = 0
        now = datetime.now(timezone.utc)

        for i in range(0, len(rows), batch_size):
            chunk = rows[i : i + batch_size]
            batch_inputs = [
                FeedbackItemInput(
                    item_id=str(r["feedback_item_id"]),
                    text=r["item_text_masked"],
                    location=r["location_name"],
                    channel=r["channel_name"],
                    reported_date=r["reported_at"].isoformat() if r["reported_at"] else None,
                )
                for r in chunk
            ]
            output = await self._classifier.classify_batch(batch_inputs)

            # Update DB records for this batch
            for res_item in output.results:
                try:
                    f_item_id = UUID(res_item.item_id)
                except ValueError:
                    continue

                svc_id = service_map.get(res_item.primary_service_code)
                iss_id = issue_map.get(res_item.issue_code) if res_item.issue_code else None
                step_info = step_map.get(res_item.journey_step_code)
                step_id = step_info[0] if step_info else None
                stage_id = step_info[1] if step_info else stage_map.get(res_item.journey_stage_code)

                # Update analytic eligibility on feedback_item
                await self._session.execute(
                    text("""
                        UPDATE feedback_item
                        SET analytic_eligibility = :eligibility,
                            eligibility_reason = :reason
                        WHERE feedback_item_id = :item_id
                    """),
                    {
                        "item_id": f_item_id,
                        "eligibility": res_item.analytic_eligibility,
                        "reason": res_item.exclusion_reason if res_item.analytic_eligibility == "EXCLUDED" else None,
                    },
                )

                # Update classification_current
                if svc_id:
                    issue_status = "KNOWN" if iss_id else "NOT_APPLICABLE"
                    await self._session.execute(
                        text("""
                            UPDATE classification_current
                            SET primary_service_id = :service_id,
                                primary_service_value_status = 'KNOWN',
                                issue_id = :issue_id,
                                issue_value_status = :issue_status,
                                customer_lifecycle_step_id = COALESCE(:step_id, customer_lifecycle_step_id),
                                customer_lifecycle_stage_id = COALESCE(:stage_id, customer_lifecycle_stage_id),
                                sentiment = :sentiment,
                                operational_severity = :severity,
                                last_decision_at = :now
                            WHERE feedback_item_id = :item_id
                        """),
                        {
                            "item_id": f_item_id,
                            "service_id": svc_id,
                            "issue_id": iss_id,
                            "issue_status": issue_status,
                            "step_id": step_id,
                            "stage_id": stage_id,
                            "sentiment": res_item.sentiment,
                            "severity": res_item.operational_severity,
                            "now": now,
                        },
                    )
                classified_count += 1

            await self._session.commit()

        return {"processed": len(rows), "classified": classified_count}
