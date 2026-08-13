"""Seed a durable, isolated analytics demo project for local dashboard preview.

The script only inserts data for ``DEMO_PROJECT_ID`` and is idempotent: a
second run reports the existing sample instead of duplicating it.
"""
from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone
from uuid import UUID, NAMESPACE_URL, uuid5

from sqlalchemy import text

from packages.infrastructure.db.session import AsyncSessionLocal, engine

DEMO_PROJECT_ID = UUID("00000000-0000-0000-0000-000000000001")
DEMO_SOURCE_SYSTEM = "analytics-demo"
DEMO_NAMESPACE = "https://cx-platform.local/analytics-demo"


@dataclass(frozen=True)
class DemoFeedback:
    days_ago: int
    service_code: str
    issue_code: str
    stage_code: str
    step_code: str
    sentiment: str
    severity: str
    intake_channel: str
    affected_channel: str


# Purposefully weighted toward negative feedback so charts have a useful shape.
DEMO_FEEDBACK: tuple[DemoFeedback, ...] = (
    DemoFeedback(1, "SV-05", "IS-05-02", "RES", "RES-03", "NEGATIVE", "SEV-2", "CH-APP", "CH-HOTLINE"),
    DemoFeedback(1, "SV-05", "IS-05-02", "RES", "RES-03", "NEGATIVE", "SEV-2", "CH-APP", "CH-HOTLINE"),
    DemoFeedback(2, "SV-02", "IS-02-01", "RES", "RES-02", "NEGATIVE", "SEV-2", "CH-APP", "CH-APP"),
    DemoFeedback(2, "SV-06", "IS-06-03", "TR", "TR-02", "NEGATIVE", "SEV-3", "CH-WEB", "CH-WEB"),
    DemoFeedback(3, "SV-05", "IS-05-01", "RES", "RES-03", "NEGATIVE", "SEV-2", "CH-HOTLINE", "CH-HOTLINE"),
    DemoFeedback(3, "SV-07", "IS-07-01", "OPS", "OPS-01", "UNKNOWN", "SEV-2", "CH-APP", "CH-APP"),
    DemoFeedback(4, "SV-02", "IS-02-01", "RES", "RES-02", "NEGATIVE", "SEV-3", "CH-APP", "CH-APP"),
    DemoFeedback(4, "SV-05", "IS-05-02", "RES", "RES-03", "NEGATIVE", "SEV-2", "CH-APP", "CH-HOTLINE"),
    DemoFeedback(5, "SV-06", "IS-06-01", "TR", "TR-02", "NEUTRAL", "SEV-3", "CH-WEB", "CH-WEB"),
    DemoFeedback(5, "SV-07", "IS-07-02", "OPS", "OPS-02", "POSITIVE", "SEV-4", "CH-FRONTDESK", "CH-INPERSON"),
    DemoFeedback(6, "SV-05", "IS-05-03", "HO", "HO-02", "NEGATIVE", "SEV-2", "CH-HOTLINE", "CH-HOTLINE"),
    DemoFeedback(7, "SV-02", "IS-02-02", "RES", "RES-02", "NEGATIVE", "SEV-2", "CH-APP", "CH-APP"),
    DemoFeedback(8, "SV-06", "IS-06-03", "TR", "TR-02", "NEGATIVE", "SEV-2", "CH-WEB", "CH-WEB"),
    DemoFeedback(8, "SV-05", "IS-05-02", "RES", "RES-03", "NEGATIVE", "SEV-1", "CH-APP", "CH-HOTLINE"),
    DemoFeedback(9, "SV-07", "IS-07-01", "OPS", "OPS-01", "UNKNOWN", "SEV-2", "CH-APP", "CH-APP"),
    DemoFeedback(10, "SV-02", "IS-02-03", "RES", "RES-02", "POSITIVE", "SEV-4", "CH-APP", "CH-APP"),
    DemoFeedback(11, "SV-05", "IS-05-01", "HO", "HO-02", "NEGATIVE", "SEV-3", "CH-HOTLINE", "CH-HOTLINE"),
    DemoFeedback(12, "SV-06", "IS-06-02", "TR", "TR-02", "NEGATIVE", "SEV-2", "CH-WEB", "CH-WEB"),
    DemoFeedback(13, "SV-02", "IS-02-01", "RES", "RES-02", "NEGATIVE", "SEV-2", "CH-APP", "CH-APP"),
    DemoFeedback(14, "SV-07", "IS-07-03", "OPS", "OPS-01", "NEUTRAL", "SEV-3", "CH-FRONTDESK", "CH-INPERSON"),
    DemoFeedback(15, "SV-05", "IS-05-02", "RES", "RES-03", "NEGATIVE", "SEV-2", "CH-APP", "CH-HOTLINE"),
    DemoFeedback(16, "SV-06", "IS-06-03", "TR", "TR-02", "POSITIVE", "SEV-4", "CH-WEB", "CH-WEB"),
    DemoFeedback(17, "SV-02", "IS-02-02", "RES", "RES-02", "UNKNOWN", "SEV-3", "CH-APP", "CH-APP"),
    DemoFeedback(18, "SV-05", "IS-05-03", "HO", "HO-02", "NEGATIVE", "SEV-2", "CH-HOTLINE", "CH-HOTLINE"),
    DemoFeedback(19, "SV-07", "IS-07-02", "OPS", "OPS-02", "POSITIVE", "SEV-4", "CH-FRONTDESK", "CH-INPERSON"),
    DemoFeedback(20, "SV-06", "IS-06-01", "TR", "TR-02", "NEUTRAL", "SEV-3", "CH-WEB", "CH-WEB"),
    DemoFeedback(21, "SV-02", "IS-02-01", "RES", "RES-02", "NEGATIVE", "SEV-2", "CH-APP", "CH-APP"),
    DemoFeedback(22, "SV-05", "IS-05-01", "HO", "HO-02", "POSITIVE", "SEV-4", "CH-HOTLINE", "CH-HOTLINE"),
    DemoFeedback(23, "SV-06", "IS-06-02", "TR", "TR-02", "NEGATIVE", "SEV-2", "CH-WEB", "CH-WEB"),
    DemoFeedback(24, "SV-02", "IS-02-03", "RES", "RES-02", "POSITIVE", "SEV-4", "CH-APP", "CH-APP"),
    DemoFeedback(25, "SV-05", "IS-05-02", "RES", "RES-03", "NEGATIVE", "SEV-1", "CH-APP", "CH-HOTLINE"),
    DemoFeedback(26, "SV-07", "IS-07-01", "OPS", "OPS-01", "NEUTRAL", "SEV-3", "CH-FRONTDESK", "CH-INPERSON"),
    DemoFeedback(27, "SV-06", "IS-06-03", "TR", "TR-02", "POSITIVE", "SEV-4", "CH-WEB", "CH-WEB"),
    DemoFeedback(28, "SV-02", "IS-02-02", "RES", "RES-02", "NEGATIVE", "SEV-2", "CH-APP", "CH-APP"),
)


def stable_id(name: str) -> UUID:
    return uuid5(NAMESPACE_URL, f"{DEMO_NAMESPACE}/{name}")


async def main() -> None:
    async with AsyncSessionLocal() as session:
        existing_count = await session.scalar(
            text("""
                SELECT count(*) FROM feedback
                WHERE project_id = :project_id AND source_system = :source_system
            """),
            {"project_id": DEMO_PROJECT_ID, "source_system": DEMO_SOURCE_SYSTEM},
        )
        if existing_count:
            print(f"Analytics demo already exists ({existing_count} feedback items).")
            return

        references = (
            await session.execute(
                text("""
                    SELECT taxonomy_release_id
                    FROM taxonomy_release WHERE version = '3.0.0'
                """)
            )
        ).scalar_one()
        service_request_step_id = (
            await session.execute(
                text("SELECT service_request_step_id FROM service_request_step WHERE step_code = 'SRV-05'")
            )
        ).scalar_one()
        stage_ids = dict(
            (await session.execute(text("SELECT stage_code, customer_lifecycle_stage_id FROM customer_lifecycle_stage"))).all()
        )
        step_ids = dict(
            (await session.execute(text("SELECT step_code, customer_lifecycle_step_id FROM customer_lifecycle_step"))).all()
        )
        service_ids = dict((await session.execute(text("SELECT service_code, service_id FROM service"))).all())
        issue_ids = dict((await session.execute(text("SELECT issue_code, issue_id FROM issue"))).all())
        channel_ids = dict(
            (await session.execute(text("SELECT channel_code, interaction_channel_id FROM interaction_channel"))).all()
        )

        required_codes = {item.stage_code for item in DEMO_FEEDBACK} | {item.step_code for item in DEMO_FEEDBACK}
        if not all(code in stage_ids or code in step_ids for code in required_codes):
            raise RuntimeError("The required lifecycle taxonomy seed is not available.")

        location_id = stable_id("location/residence")
        await session.execute(
            text("""
                INSERT INTO location (
                    location_id, project_id, parent_location_id, location_code,
                    location_type, name, path_code
                ) VALUES (
                    :location_id, :project_id, NULL, 'DEMO-RESIDENCE',
                    'BUILDING', 'Analytics demo residence', 'DEMO-RESIDENCE'
                )
            """),
            {"location_id": location_id, "project_id": DEMO_PROJECT_ID},
        )

        today = date.today()
        actor_id = stable_id("actor/demo-seeder")
        for index, item in enumerate(DEMO_FEEDBACK, start=1):
            feedback_id = stable_id(f"feedback/{index}")
            feedback_item_id = stable_id(f"feedback-item/{index}")
            decision_id = stable_id(f"decision/{index}")
            reported_at = datetime.combine(
                today - timedelta(days=item.days_ago), time(9, index % 50), tzinfo=timezone.utc
            )
            values = {
                "feedback_id": feedback_id,
                "feedback_item_id": feedback_item_id,
                "decision_id": decision_id,
                "project_id": DEMO_PROJECT_ID,
                "source_record_key": f"analytics-demo-{index:03d}",
                "reported_at": reported_at,
                "location_id": location_id,
                "taxonomy_release_id": references,
                "stage_id": stage_ids[item.stage_code],
                "lifecycle_step_id": step_ids[item.step_code],
                "service_request_step_id": service_request_step_id,
                "service_id": service_ids[item.service_code],
                "issue_id": issue_ids[item.issue_code],
                "sentiment": item.sentiment,
                "severity": item.severity,
                "actor_id": actor_id,
                "intake_channel_id": channel_ids[item.intake_channel],
                "affected_channel_id": channel_ids[item.affected_channel],
            }
            await session.execute(
                text("""
                    INSERT INTO feedback (
                        feedback_id, project_id, source_system, source_record_key,
                        intake_channel_id, reported_at, content_raw, content_masked,
                        raw_content_checksum
                    ) VALUES (
                        :feedback_id, :project_id, 'analytics-demo', :source_record_key,
                        :intake_channel_id, :reported_at, 'Demo analytics feedback',
                        'Demo analytics feedback', :source_record_key
                    )
                """),
                values,
            )
            await session.execute(
                text("""
                    INSERT INTO feedback_item (
                        feedback_item_id, feedback_id, item_index, item_text_masked,
                        location_id, status, analytic_eligibility
                    ) VALUES (
                        :feedback_item_id, :feedback_id, 1, 'Demo analytics item',
                        :location_id, 'ACTIVE', 'INCLUDED'
                    )
                """),
                values,
            )
            await session.execute(
                text("""
                    INSERT INTO feedback_item_affected_channel (
                        feedback_item_id, interaction_channel_id
                    ) VALUES (:feedback_item_id, :affected_channel_id)
                """),
                values,
            )
            await session.execute(
                text("""
                    INSERT INTO classification_decision (
                        classification_decision_id, feedback_item_id, decision_version,
                        taxonomy_release_id, customer_lifecycle_value_status,
                        customer_lifecycle_step_id, service_request_value_status,
                        service_request_step_id, primary_service_value_status,
                        primary_service_id, issue_value_status, issue_id, sentiment,
                        operational_severity, cause_determination_status,
                        classification_state, decision_source, decided_by, decided_at
                    ) VALUES (
                        :decision_id, :feedback_item_id, 1, :taxonomy_release_id,
                        'KNOWN', :lifecycle_step_id, 'KNOWN', :service_request_step_id,
                        'KNOWN', :service_id, 'KNOWN', :issue_id, :sentiment, :severity,
                        'NOT_ASSESSED', 'ACCEPTED', 'SOURCE_TRUSTED', :actor_id, :reported_at
                    )
                """),
                values,
            )
            await session.execute(
                text("""
                    INSERT INTO classification_current (
                        feedback_item_id, current_decision_id, current_decision_version,
                        taxonomy_release_id, customer_lifecycle_value_status,
                        customer_lifecycle_stage_id, customer_lifecycle_step_id,
                        service_request_value_status, service_request_step_id,
                        primary_service_value_status, primary_service_id,
                        issue_value_status, issue_id, sentiment, operational_severity,
                        cause_determination_status, classification_state,
                        last_decision_at, projection_version
                    ) VALUES (
                        :feedback_item_id, :decision_id, 1, :taxonomy_release_id,
                        'KNOWN', :stage_id, :lifecycle_step_id, 'KNOWN',
                        :service_request_step_id, 'KNOWN', :service_id, 'KNOWN',
                        :issue_id, :sentiment, :severity, 'NOT_ASSESSED', 'ACCEPTED',
                        :reported_at, 1
                    )
                """),
                values,
            )

        await session.commit()
        print(f"Seeded {len(DEMO_FEEDBACK)} analytics demo feedback items for {DEMO_PROJECT_ID}.")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
