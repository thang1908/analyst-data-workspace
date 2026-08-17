"""SQL persistence for immutable Feedback envelopes and atomic items."""
from __future__ import annotations

import json
from collections import defaultdict
from dataclasses import dataclass
from datetime import date
from typing import Any
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from packages.domain.feedback import Feedback, FeedbackDomainError, FeedbackItem, FeedbackSplitResult, SplitSource
from packages.domain.shared.enums import AnalyticEligibility, FeedbackItemStatus


@dataclass(frozen=True, slots=True)
class FeedbackItemListFilters:
    project_id: UUID
    date_from: date | None = None
    date_to: date | None = None
    source_system: str | None = None
    intake_channel_code: str | None = None
    affected_channel_code: str | None = None
    location_id: UUID | None = None
    q: str | None = None
    limit: int = 50
    offset: int = 0


@dataclass(frozen=True, slots=True)
class FeedbackItemWorkspaceRow:
    feedback_item_id: UUID
    feedback_id: UUID
    reported_at: Any
    source_system: str
    content_masked: str
    location_id: UUID | None
    location_code: str | None
    location_name: str | None
    service_code: str | None
    service_name_vi: str | None
    issue_code: str | None
    issue_name_vi: str | None
    sentiment: str | None
    operational_severity: str | None
    classification_state: str | None
    projection_version: int | None
    status: str
    analytic_eligibility: str
    parent_item_id: UUID | None
    affected_channel_codes: tuple[str, ...]


class FeedbackRepository:
    """Persist Feedback aggregates using only existing P0 operational tables.

    The current schema models split lineage on ``feedback_item`` and records
    the immutable split event in ``audit_event``; there is no ``feedback_split``
    table to duplicate that provenance.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create_feedback(self, feedback: Feedback) -> Feedback:
        """Insert the immutable envelope and its initial item set."""
        await self._session.execute(
            text("""
                INSERT INTO feedback (
                    feedback_id, project_id, source_system, source_record_key,
                    intake_channel_id, source_url, external_ticket_id, reported_at,
                    ingested_at, content_raw, content_masked, source_metadata_json,
                    raw_content_checksum, created_at
                ) VALUES (
                    :feedback_id, :project_id, :source_system, :source_record_key,
                    :intake_channel_id, :source_url, :external_ticket_id, :reported_at,
                    :ingested_at, :content_raw, :content_masked,
                    CAST(:source_metadata_json AS jsonb), :raw_content_checksum, :created_at
                )
            """),
            _feedback_parameters(feedback),
        )
        await self._insert_items(feedback.items)
        return feedback

    async def get_feedback(self, feedback_id: UUID) -> Feedback | None:
        """Rehydrate a Feedback aggregate and its affected-channel collections."""
        feedback_result = await self._session.execute(
            text("SELECT * FROM feedback WHERE feedback_id = :feedback_id"),
            {"feedback_id": feedback_id},
        )
        feedback_row = feedback_result.mappings().one_or_none()
        if feedback_row is None:
            return None

        items_result = await self._session.execute(
            text("""
                SELECT * FROM feedback_item
                WHERE feedback_id = :feedback_id
                ORDER BY item_index
            """),
            {"feedback_id": feedback_id},
        )
        item_rows = items_result.mappings().all()
        channel_result = await self._session.execute(
            text("""
                SELECT feedback_item_id, interaction_channel_id
                FROM feedback_item_affected_channel
                WHERE feedback_item_id IN (
                    SELECT feedback_item_id FROM feedback_item WHERE feedback_id = :feedback_id
                )
            """),
            {"feedback_id": feedback_id},
        )
        channels_by_item: dict[UUID, list[UUID]] = defaultdict(list)
        for row in channel_result.mappings().all():
            channels_by_item[row["feedback_item_id"]].append(row["interaction_channel_id"])
        return Feedback(
            feedback_id=feedback_row["feedback_id"],
            project_id=feedback_row["project_id"],
            source_system=feedback_row["source_system"],
            source_record_key=feedback_row["source_record_key"],
            intake_channel_id=feedback_row["intake_channel_id"],
            source_url=feedback_row["source_url"],
            external_ticket_id=feedback_row["external_ticket_id"],
            reported_at=feedback_row["reported_at"],
            ingested_at=feedback_row["ingested_at"],
            content_raw=feedback_row["content_raw"],
            content_masked=feedback_row["content_masked"],
            source_metadata=feedback_row["source_metadata_json"] or {},
            raw_content_checksum=feedback_row["raw_content_checksum"],
            created_at=feedback_row["created_at"],
            items=tuple(_as_feedback_item(row, channels_by_item[row["feedback_item_id"]]) for row in item_rows),
        )

    async def list_workspace_items(
        self, filters: FeedbackItemListFilters
    ) -> tuple[list[FeedbackItemWorkspaceRow], int]:
        """List masked workspace rows; raw content is intentionally absent."""
        where, params = _workspace_where(filters)
        count_result = await self._session.execute(
            text(f"""SELECT COUNT(*) FROM feedback_item fi
                INNER JOIN feedback f ON f.feedback_id = fi.feedback_id
                LEFT JOIN interaction_channel intake ON intake.interaction_channel_id = f.intake_channel_id
                WHERE {where}"""),
            params,
        )
        result = await self._session.execute(
            text(f"""
                SELECT fi.feedback_item_id, fi.feedback_id, f.reported_at, f.source_system,
                       fi.item_text_masked AS content_masked, fi.status, fi.analytic_eligibility,
                       fi.parent_item_id, loc.location_id, loc.location_code, loc.name AS location_name,
                       service.service_code, service.name_vi AS service_name_vi,
                       issue.issue_code, issue.name_vi AS issue_name_vi,
                       cc.sentiment, cc.operational_severity, cc.classification_state,
                       cc.projection_version,
                       COALESCE(ARRAY_AGG(DISTINCT affected.channel_code)
                         FILTER (WHERE affected.channel_code IS NOT NULL), ARRAY[]::text[]) AS affected_channel_codes
                FROM feedback_item fi
                INNER JOIN feedback f ON f.feedback_id = fi.feedback_id
                LEFT JOIN interaction_channel intake ON intake.interaction_channel_id = f.intake_channel_id
                LEFT JOIN location loc ON loc.location_id = fi.location_id
                LEFT JOIN classification_current cc ON cc.feedback_item_id = fi.feedback_item_id
                LEFT JOIN service ON service.service_id = cc.primary_service_id
                LEFT JOIN issue ON issue.issue_id = cc.issue_id
                LEFT JOIN feedback_item_affected_channel fiac ON fiac.feedback_item_id = fi.feedback_item_id
                LEFT JOIN interaction_channel affected ON affected.interaction_channel_id = fiac.interaction_channel_id
                WHERE {where}
                GROUP BY fi.feedback_item_id, f.feedback_id, f.reported_at, f.source_system,
                         fi.item_text_masked, fi.status, fi.analytic_eligibility, fi.parent_item_id,
                         loc.location_id, loc.location_code, loc.name, service.service_code, service.name_vi,
                         issue.issue_code, issue.name_vi, cc.sentiment, cc.operational_severity,
                         cc.classification_state, cc.projection_version
                ORDER BY f.reported_at DESC, fi.feedback_item_id DESC
                LIMIT :limit OFFSET :offset
            """),
            {**params, "limit": filters.limit, "offset": filters.offset},
        )
        return ([_as_workspace_row(row) for row in result.mappings().all()], int(count_result.scalar_one()))

    async def get_workspace_item(self, feedback_item_id: UUID) -> FeedbackItemWorkspaceRow | None:
        """Return one masked workspace item, including its split parent reference."""
        result = await self._session.execute(
            text("""
                SELECT fi.feedback_item_id, fi.feedback_id, f.reported_at, f.source_system,
                       fi.item_text_masked AS content_masked, fi.status, fi.analytic_eligibility,
                       fi.parent_item_id, loc.location_id, loc.location_code, loc.name AS location_name,
                       service.service_code, service.name_vi AS service_name_vi, issue.issue_code,
                       issue.name_vi AS issue_name_vi, cc.sentiment, cc.operational_severity,
                       cc.classification_state, cc.projection_version,
                       COALESCE(ARRAY_AGG(DISTINCT affected.channel_code)
                         FILTER (WHERE affected.channel_code IS NOT NULL), ARRAY[]::text[]) AS affected_channel_codes
                FROM feedback_item fi
                INNER JOIN feedback f ON f.feedback_id = fi.feedback_id
                LEFT JOIN location loc ON loc.location_id = fi.location_id
                LEFT JOIN classification_current cc ON cc.feedback_item_id = fi.feedback_item_id
                LEFT JOIN service ON service.service_id = cc.primary_service_id
                LEFT JOIN issue ON issue.issue_id = cc.issue_id
                LEFT JOIN feedback_item_affected_channel fiac ON fiac.feedback_item_id = fi.feedback_item_id
                LEFT JOIN interaction_channel affected ON affected.interaction_channel_id = fiac.interaction_channel_id
                WHERE fi.feedback_item_id = :feedback_item_id
                GROUP BY fi.feedback_item_id, f.feedback_id, f.reported_at, f.source_system,
                         fi.item_text_masked, fi.status, fi.analytic_eligibility, fi.parent_item_id,
                         loc.location_id, loc.location_code, loc.name, service.service_code, service.name_vi,
                         issue.issue_code, issue.name_vi, cc.sentiment, cc.operational_severity,
                         cc.classification_state, cc.projection_version
            """),
            {"feedback_item_id": feedback_item_id},
        )
        row = result.mappings().one_or_none()
        return _as_workspace_row(row) if row else None

    async def apply_split(
        self,
        result: FeedbackSplitResult,
        *,
        actor_role: str,
        correlation_id: str,
    ) -> None:
        """Persist parent status, child rows and an append-only audit event.

        All statements use the caller's AsyncSession transaction.  A stale
        source cannot be split twice because the parent update requires ACTIVE.
        """
        source_item = result.source_item
        updated = await self._session.execute(
            text("""
                UPDATE feedback_item
                SET status = 'SPLIT_PARENT', analytic_eligibility = 'EXCLUDED',
                    eligibility_reason = 'SPLIT_PARENT'
                WHERE feedback_item_id = :feedback_item_id
                  AND feedback_id = :feedback_id
                  AND status = 'ACTIVE'
                RETURNING feedback_item_id
            """),
            {
                "feedback_item_id": source_item.feedback_item_id,
                "feedback_id": result.feedback.feedback_id,
            },
        )
        if updated.scalar_one_or_none() is None:
            raise FeedbackDomainError("FeedbackItem is no longer ACTIVE and cannot be split.")
        await self._insert_items(result.created_items)
        event = result.audit_event
        await self._session.execute(
            text("""
                INSERT INTO audit_event (
                    audit_event_id, occurred_at, actor_user_id, actor_role, action,
                    resource_type, resource_id, project_id, correlation_id, reason,
                    before_ref, after_ref, metadata_json
                ) VALUES (
                    :audit_event_id, :occurred_at, :actor_user_id, :actor_role,
                    'feedback_item.split', 'feedback_item', :resource_id, :project_id,
                    :correlation_id, :reason, CAST(:before_ref AS jsonb),
                    CAST(:after_ref AS jsonb), CAST(:metadata_json AS jsonb)
                )
            """),
            {
                "audit_event_id": event.event_id,
                "occurred_at": event.occurred_at,
                "actor_user_id": event.actor_id,
                "actor_role": actor_role,
                "resource_id": str(event.source_feedback_item_id),
                "project_id": result.feedback.project_id,
                "correlation_id": correlation_id,
                "reason": event.reason,
                "before_ref": json.dumps({"status": FeedbackItemStatus.ACTIVE}),
                "after_ref": json.dumps({"status": FeedbackItemStatus.SPLIT_PARENT}),
                "metadata_json": json.dumps({
                    "feedback_id": str(event.feedback_id),
                    "created_feedback_item_ids": [str(item_id) for item_id in event.created_feedback_item_ids],
                    "split_source": event.split_source,
                }),
            },
        )

    async def _insert_items(self, items: tuple[FeedbackItem, ...]) -> None:
        for item in items:
            await self._session.execute(
                text("""
                    INSERT INTO feedback_item (
                        feedback_item_id, feedback_id, item_index, parent_item_id,
                        item_text_masked, symptom_detail, location_id, status,
                        analytic_eligibility, eligibility_reason, split_source,
                        split_by, split_at, created_at, created_by
                    ) VALUES (
                        :feedback_item_id, :feedback_id, :item_index, :parent_item_id,
                        :item_text_masked, :symptom_detail, :location_id, :status,
                        :analytic_eligibility, :eligibility_reason, :split_source,
                        :split_by, :split_at, :created_at, :created_by
                    )
                """),
                _item_parameters(item),
            )
            for channel_id in item.affected_channel_ids:
                await self._session.execute(
                    text("""
                        INSERT INTO feedback_item_affected_channel (
                            feedback_item_id, interaction_channel_id
                        ) VALUES (:feedback_item_id, :interaction_channel_id)
                    """),
                    {
                        "feedback_item_id": item.feedback_item_id,
                        "interaction_channel_id": channel_id,
                    },
                )


def _feedback_parameters(feedback: Feedback) -> dict[str, Any]:
    return {
        "feedback_id": feedback.feedback_id,
        "project_id": feedback.project_id,
        "source_system": feedback.source_system,
        "source_record_key": feedback.source_record_key,
        "intake_channel_id": feedback.intake_channel_id,
        "source_url": feedback.source_url,
        "external_ticket_id": feedback.external_ticket_id,
        "reported_at": feedback.reported_at,
        "ingested_at": feedback.ingested_at,
        "content_raw": feedback.content_raw,
        "content_masked": feedback.content_masked,
        "source_metadata_json": json.dumps(dict(feedback.source_metadata)),
        "raw_content_checksum": feedback.raw_content_checksum,
        "created_at": feedback.created_at,
    }


def _item_parameters(item: FeedbackItem) -> dict[str, Any]:
    return {
        "feedback_item_id": item.feedback_item_id,
        "feedback_id": item.feedback_id,
        "item_index": item.item_index,
        "parent_item_id": item.parent_item_id,
        "item_text_masked": item.item_text_masked,
        "symptom_detail": item.symptom_detail,
        "location_id": item.location_id,
        "status": item.status,
        "analytic_eligibility": item.analytic_eligibility,
        "eligibility_reason": item.eligibility_reason,
        "split_source": item.split_source,
        "split_by": item.split_by,
        "split_at": item.split_at,
        "created_at": item.created_at,
        "created_by": item.created_by,
    }


def _as_feedback_item(row: Any, affected_channel_ids: list[UUID]) -> FeedbackItem:
    split_source = row["split_source"]
    return FeedbackItem(
        feedback_item_id=row["feedback_item_id"],
        feedback_id=row["feedback_id"],
        item_index=row["item_index"],
        parent_item_id=row["parent_item_id"],
        item_text_masked=row["item_text_masked"],
        symptom_detail=row["symptom_detail"],
        location_id=row["location_id"],
        affected_channel_ids=tuple(affected_channel_ids),
        status=FeedbackItemStatus(row["status"]),
        analytic_eligibility=AnalyticEligibility(row["analytic_eligibility"]),
        eligibility_reason=row["eligibility_reason"],
        split_source=SplitSource(split_source) if split_source else None,
        split_by=row["split_by"],
        split_at=row["split_at"],
        created_at=row["created_at"],
        created_by=row["created_by"],
    )


def _workspace_where(filters: FeedbackItemListFilters) -> tuple[str, dict[str, Any]]:
    clauses = ["f.project_id = :project_id"]
    params: dict[str, Any] = {"project_id": filters.project_id}
    if filters.date_from is not None:
        clauses.append("f.reported_at >= :date_from")
        params["date_from"] = filters.date_from
    if filters.date_to is not None:
        clauses.append("f.reported_at < (:date_to + INTERVAL '1 day')")
        params["date_to"] = filters.date_to
    if filters.source_system:
        clauses.append("f.source_system = :source_system")
        params["source_system"] = filters.source_system
    if filters.intake_channel_code:
        clauses.append("intake.channel_code = :intake_channel_code")
        params["intake_channel_code"] = filters.intake_channel_code
    if filters.affected_channel_code:
        clauses.append("EXISTS (SELECT 1 FROM feedback_item_affected_channel filter_fiac "
                       "JOIN interaction_channel filter_channel "
                       "ON filter_channel.interaction_channel_id = filter_fiac.interaction_channel_id "
                       "WHERE filter_fiac.feedback_item_id = fi.feedback_item_id "
                       "AND filter_channel.channel_code = :affected_channel_code)")
        params["affected_channel_code"] = filters.affected_channel_code
    if filters.location_id:
        clauses.append("fi.location_id = :location_id")
        params["location_id"] = filters.location_id
    if filters.q:
        clauses.append("fi.item_text_masked ILIKE :q")
        params["q"] = f"%{filters.q.strip()}%"
    return " AND ".join(clauses), params


def _as_workspace_row(row: Any) -> FeedbackItemWorkspaceRow:
    return FeedbackItemWorkspaceRow(
        feedback_item_id=row["feedback_item_id"], feedback_id=row["feedback_id"],
        reported_at=row["reported_at"], source_system=row["source_system"],
        content_masked=row["content_masked"], location_id=row["location_id"],
        location_code=row["location_code"], location_name=row["location_name"],
        service_code=row["service_code"], service_name_vi=row["service_name_vi"],
        issue_code=row["issue_code"], issue_name_vi=row["issue_name_vi"],
        sentiment=row["sentiment"], operational_severity=row["operational_severity"],
        classification_state=row["classification_state"], projection_version=row["projection_version"],
        status=row["status"], analytic_eligibility=row["analytic_eligibility"],
        parent_item_id=row["parent_item_id"],
        affected_channel_codes=tuple(row["affected_channel_codes"] or ()),
    )
