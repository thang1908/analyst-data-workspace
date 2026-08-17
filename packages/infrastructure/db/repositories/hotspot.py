"""SQL repository for Hotspot persistence, deterministic clustering and timeline events."""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from packages.domain.hotspot.engine import (
    FeedbackClusterItem,
    calculate_action_priority,
    calculate_operational_severity,
    cluster_eligible_items,
    generate_dimension_key,
    parse_severity,
    validate_hotspot_transition,
)
from packages.domain.hotspot.entities import Hotspot, HotspotTimelineEvent
from packages.domain.hotspot.exceptions import (
    ConcurrencyConflictError,
    HotspotNotFoundError,
)
from packages.domain.shared.enums import ActionPriority, HotspotStatus, OperationalSeverity


@dataclass(frozen=True, slots=True)
class HotspotListFilters:
    project_id: UUID
    status: str | None = None
    action_priority: str | None = None
    service_code: str | None = None
    issue_code: str | None = None
    location_id: UUID | None = None
    operational_severity: str | None = None
    date_from: Any | None = None
    date_to: Any | None = None
    limit: int = 50
    offset: int = 0


@dataclass(frozen=True, slots=True)
class HotspotEvidenceItem:
    feedback_item_id: UUID
    reported_at: datetime
    content_masked: str
    sentiment: str
    operational_severity: str
    evidence_role: str


@dataclass(frozen=True, slots=True)
class HotspotTimelineItem:
    timeline_event_id: UUID
    hotspot_id: UUID
    from_status: str | None
    to_status: str
    action: str
    actor_user_id: UUID
    reason: str | None
    metadata_json: dict[str, Any] | None
    correlation_id: str
    created_at: datetime


@dataclass(frozen=True, slots=True)
class HotspotListItem:
    hotspot_id: UUID
    project_id: UUID
    dimension_key: str
    service_id: UUID
    service_code: str
    service_name_vi: str
    issue_id: UUID
    issue_code: str
    issue_name_vi: str
    location_id: UUID | None
    location_code: str | None
    location_name: str | None
    status: str
    action_priority: str
    operational_severity: str
    evidence_count: int
    assigned_user_id: UUID | None
    assigned_team_key: str | None
    first_seen_at: datetime
    last_seen_at: datetime
    resolved_at: datetime | None
    resolution_summary: str | None
    window_start: datetime
    window_end: datetime
    version: int
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True, slots=True)
class HotspotDetail:
    hotspot: HotspotListItem
    evidence: list[HotspotEvidenceItem]
    timeline: list[HotspotTimelineItem]


class HotspotRepository:
    """Manages Hotspot aggregates, clustering runs, and append-only audit events."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_hotspots(
        self, filters: HotspotListFilters
    ) -> tuple[list[HotspotListItem], int]:
        clauses = ["h.project_id = :project_id"]
        params: dict[str, Any] = {"project_id": filters.project_id}

        if filters.status:
            clauses.append("h.status = :status")
            params["status"] = filters.status
        if filters.action_priority:
            clauses.append("h.action_priority = :action_priority")
            params["action_priority"] = filters.action_priority
        if filters.service_code:
            clauses.append("svc.service_code = :service_code")
            params["service_code"] = filters.service_code
        if filters.issue_code:
            clauses.append("iss.issue_code = :issue_code")
            params["issue_code"] = filters.issue_code
        if filters.location_id:
            clauses.append("h.location_id = :location_id")
            params["location_id"] = filters.location_id
        if filters.operational_severity:
            clauses.append("h.operational_severity = :operational_severity")
            params["operational_severity"] = filters.operational_severity
        if filters.date_from is not None:
            clauses.append("h.last_seen_at >= :date_from")
            params["date_from"] = filters.date_from
        if filters.date_to is not None:
            clauses.append("h.last_seen_at < (:date_to + INTERVAL '1 day')")
            params["date_to"] = filters.date_to

        where_clause = " AND ".join(clauses)

        count_res = await self._session.execute(
            text(f"""
                SELECT COUNT(*)
                FROM hotspot h
                JOIN service svc ON svc.service_id = h.service_id
                JOIN issue iss ON iss.issue_id = h.issue_id
                WHERE {where_clause}
            """),
            params,
        )
        total = int(count_res.scalar_one() or 0)

        # Priority ordering: IMMEDIATE (1), URGENT (2), PLANNED (3), MONITOR (4)
        result = await self._session.execute(
            text(f"""
                SELECT h.hotspot_id, h.project_id, h.dimension_key,
                       h.service_id, svc.service_code, svc.name_vi AS service_name_vi,
                       h.issue_id, iss.issue_code, iss.name_vi AS issue_name_vi,
                       h.location_id, loc.location_code, loc.name AS location_name,
                       h.status, h.action_priority, h.operational_severity,
                       h.evidence_count, h.assigned_user_id, h.assigned_team_key,
                       h.first_seen_at, h.last_seen_at, h.resolved_at,
                       h.resolution_summary, h.window_start, h.window_end,
                       h.version, h.created_at, h.updated_at
                FROM hotspot h
                JOIN service svc ON svc.service_id = h.service_id
                JOIN issue iss ON iss.issue_id = h.issue_id
                LEFT JOIN location loc ON loc.location_id = h.location_id
                WHERE {where_clause}
                ORDER BY
                    CASE h.action_priority
                        WHEN 'IMMEDIATE' THEN 1
                        WHEN 'URGENT' THEN 2
                        WHEN 'PLANNED' THEN 3
                        WHEN 'MONITOR' THEN 4
                        ELSE 5
                    END,
                    h.evidence_count DESC,
                    h.last_seen_at DESC
                LIMIT :limit OFFSET :offset
            """),
            {**params, "limit": filters.limit, "offset": filters.offset},
        )

        items = [
            HotspotListItem(
                hotspot_id=row["hotspot_id"],
                project_id=row["project_id"],
                dimension_key=row["dimension_key"],
                service_id=row["service_id"],
                service_code=row["service_code"],
                service_name_vi=row["service_name_vi"],
                issue_id=row["issue_id"],
                issue_code=row["issue_code"],
                issue_name_vi=row["issue_name_vi"],
                location_id=row["location_id"],
                location_code=row["location_code"],
                location_name=row["location_name"],
                status=row["status"],
                action_priority=row["action_priority"],
                operational_severity=row["operational_severity"],
                evidence_count=row["evidence_count"],
                assigned_user_id=row["assigned_user_id"],
                assigned_team_key=row["assigned_team_key"],
                first_seen_at=row["first_seen_at"],
                last_seen_at=row["last_seen_at"],
                resolved_at=row["resolved_at"],
                resolution_summary=row["resolution_summary"],
                window_start=row["window_start"],
                window_end=row["window_end"],
                version=row["version"],
                created_at=row["created_at"],
                updated_at=row["updated_at"],
            )
            for row in result.mappings().all()
        ]
        return items, total

    async def get_hotspot(self, hotspot_id: UUID) -> HotspotDetail | None:
        result = await self._session.execute(
            text("""
                SELECT h.hotspot_id, h.project_id, h.dimension_key,
                       h.service_id, svc.service_code, svc.name_vi AS service_name_vi,
                       h.issue_id, iss.issue_code, iss.name_vi AS issue_name_vi,
                       h.location_id, loc.location_code, loc.name AS location_name,
                       h.status, h.action_priority, h.operational_severity,
                       h.evidence_count, h.assigned_user_id, h.assigned_team_key,
                       h.first_seen_at, h.last_seen_at, h.resolved_at,
                       h.resolution_summary, h.window_start, h.window_end,
                       h.version, h.created_at, h.updated_at
                FROM hotspot h
                JOIN service svc ON svc.service_id = h.service_id
                JOIN issue iss ON iss.issue_id = h.issue_id
                LEFT JOIN location loc ON loc.location_id = h.location_id
                WHERE h.hotspot_id = :hotspot_id
            """),
            {"hotspot_id": hotspot_id},
        )
        row = result.mappings().one_or_none()
        if not row:
            return None

        hotspot_item = HotspotListItem(
            hotspot_id=row["hotspot_id"],
            project_id=row["project_id"],
            dimension_key=row["dimension_key"],
            service_id=row["service_id"],
            service_code=row["service_code"],
            service_name_vi=row["service_name_vi"],
            issue_id=row["issue_id"],
            issue_code=row["issue_code"],
            issue_name_vi=row["issue_name_vi"],
            location_id=row["location_id"],
            location_code=row["location_code"],
            location_name=row["location_name"],
            status=row["status"],
            action_priority=row["action_priority"],
            operational_severity=row["operational_severity"],
            evidence_count=row["evidence_count"],
            assigned_user_id=row["assigned_user_id"],
            assigned_team_key=row["assigned_team_key"],
            first_seen_at=row["first_seen_at"],
            last_seen_at=row["last_seen_at"],
            resolved_at=row["resolved_at"],
            resolution_summary=row["resolution_summary"],
            window_start=row["window_start"],
            window_end=row["window_end"],
            version=row["version"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

        # Evidence items
        ev_result = await self._session.execute(
            text("""
                SELECT fih.feedback_item_id, fih.evidence_role, f.reported_at,
                       fi.item_text_masked AS content_masked,
                       cc.sentiment, cc.operational_severity
                FROM feedback_item_hotspot fih
                JOIN feedback_item fi ON fi.feedback_item_id = fih.feedback_item_id
                JOIN feedback f ON f.feedback_id = fi.feedback_id
                LEFT JOIN classification_current cc ON cc.feedback_item_id = fi.feedback_item_id
                WHERE fih.hotspot_id = :hotspot_id
                ORDER BY f.reported_at DESC
            """),
            {"hotspot_id": hotspot_id},
        )
        evidence = [
            HotspotEvidenceItem(
                feedback_item_id=erow["feedback_item_id"],
                reported_at=erow["reported_at"],
                content_masked=erow["content_masked"],
                sentiment=erow["sentiment"] or "UNKNOWN",
                operational_severity=erow["operational_severity"] or "SEV-4",
                evidence_role=erow["evidence_role"],
            )
            for erow in ev_result.mappings().all()
        ]

        # Timeline events
        tl_result = await self._session.execute(
            text("""
                SELECT hotspot_timeline_event_id, hotspot_id, from_status, to_status,
                       action, actor_user_id, reason, metadata_json, correlation_id, created_at
                FROM hotspot_timeline_event
                WHERE hotspot_id = :hotspot_id
                ORDER BY created_at ASC
            """),
            {"hotspot_id": hotspot_id},
        )
        timeline = [
            HotspotTimelineItem(
                timeline_event_id=trow["hotspot_timeline_event_id"],
                hotspot_id=trow["hotspot_id"],
                from_status=trow["from_status"],
                to_status=trow["to_status"],
                action=trow["action"],
                actor_user_id=trow["actor_user_id"],
                reason=trow["reason"],
                metadata_json=trow["metadata_json"],
                correlation_id=trow["correlation_id"],
                created_at=trow["created_at"],
            )
            for trow in tl_result.mappings().all()
        ]

        return HotspotDetail(hotspot=hotspot_item, evidence=evidence, timeline=timeline)

    async def mutate_hotspot_status(
        self,
        hotspot_id: UUID,
        *,
        action: str,
        to_status: str,
        actor_user_id: UUID,
        reason: str | None = None,
        resolution_summary: str | None = None,
        assigned_user_id: UUID | None = None,
        assigned_team_key: str | None = None,
        expected_version: int | None = None,
        correlation_id: str | None = None,
    ) -> HotspotDetail:
        # Load current
        curr_res = await self._session.execute(
            text("SELECT status, version FROM hotspot WHERE hotspot_id = :hotspot_id"),
            {"hotspot_id": hotspot_id},
        )
        curr_row = curr_res.mappings().one_or_none()
        if not curr_row:
            raise HotspotNotFoundError(f"Hotspot {hotspot_id} was not found.")

        current_status = curr_row["status"]
        current_version = curr_row["version"]

        if expected_version is not None and expected_version != current_version:
            raise ConcurrencyConflictError(
                f"Optimistic concurrency conflict on Hotspot {hotspot_id}. "
                f"Expected version {expected_version}, but current version is {current_version}."
            )

        validate_hotspot_transition(
            current_status,
            to_status,
            reason=reason,
            resolution_summary=resolution_summary,
        )

        now = datetime.now(timezone.utc)
        corr_id = correlation_id or str(uuid4())

        # Update hotspot
        update_params: dict[str, Any] = {
            "hotspot_id": hotspot_id,
            "to_status": to_status,
            "version": current_version + 1,
            "now": now,
        }

        set_clauses = [
            "status = :to_status",
            "version = :version",
            "updated_at = :now",
        ]

        if to_status == HotspotStatus.RESOLVED:
            set_clauses.append("resolved_at = :now")
            if resolution_summary:
                set_clauses.append("resolution_summary = :resolution_summary")
                update_params["resolution_summary"] = resolution_summary
        elif to_status == HotspotStatus.REOPENED or to_status == HotspotStatus.INVESTIGATING:
            set_clauses.append("resolved_at = NULL")

        if action == "ASSIGN":
            if assigned_user_id is not None:
                set_clauses.append("assigned_user_id = :assigned_user_id")
                update_params["assigned_user_id"] = assigned_user_id
            if assigned_team_key is not None:
                set_clauses.append("assigned_team_key = :assigned_team_key")
                update_params["assigned_team_key"] = assigned_team_key

        sql_update = f"UPDATE hotspot SET {', '.join(set_clauses)} WHERE hotspot_id = :hotspot_id"
        await self._session.execute(text(sql_update), update_params)

        # Record timeline event
        metadata: dict[str, Any] = {}
        if resolution_summary:
            metadata["resolution_summary"] = resolution_summary
        if assigned_user_id:
            metadata["assigned_user_id"] = str(assigned_user_id)
        if assigned_team_key:
            metadata["assigned_team_key"] = assigned_team_key

        await self._session.execute(
            text("""
                INSERT INTO hotspot_timeline_event (
                    hotspot_timeline_event_id, hotspot_id, from_status, to_status,
                    action, actor_user_id, reason, metadata_json, correlation_id, created_at
                ) VALUES (
                    :event_id, :hotspot_id, :from_status, :to_status,
                    :action, :actor_user_id, :reason, CAST(:metadata_json AS jsonb),
                    :correlation_id, :created_at
                )
            """),
            {
                "event_id": uuid4(),
                "hotspot_id": hotspot_id,
                "from_status": current_status,
                "to_status": to_status,
                "action": action,
                "actor_user_id": actor_user_id,
                "reason": reason,
                "metadata_json": json.dumps(metadata) if metadata else None,
                "correlation_id": corr_id,
                "created_at": now,
            },
        )

        detail = await self.get_hotspot(hotspot_id)
        if not detail:
            raise HotspotNotFoundError(f"Hotspot {hotspot_id} not found after mutation.")
        return detail

    async def detect_and_sync_hotspots(
        self,
        project_id: UUID,
        *,
        window_start: datetime,
        window_end: datetime,
        threshold_count: int = 3,
        rule_version: str = "1.0.0",
        actor_user_id: UUID | None = None,
        safety_playbook_approved: bool = False,
    ) -> list[HotspotListItem]:
        """Deterministic clustering and idempotent upsert into hotspot tables."""
        # 1. Fetch published taxonomy release
        rel_res = await self._session.execute(
            text("""
                SELECT taxonomy_release_id
                FROM taxonomy_release
                WHERE status = 'PUBLISHED'
                  AND (effective_from IS NULL OR effective_from <= NOW())
                  AND (effective_to IS NULL OR effective_to > NOW())
                ORDER BY effective_from DESC NULLS LAST, published_at DESC NULLS LAST, created_at DESC
                LIMIT 1
            """)
        )
        rel_id = rel_res.scalar_one_or_none()
        if not rel_id:
            return []

        # 2. Fetch safety critical issues
        safety_res = await self._session.execute(
            text("SELECT issue_id FROM issue WHERE taxonomy_release_id = :rel_id AND safety_critical = true"),
            {"rel_id": rel_id},
        )
        safety_issue_ids = {row[0] for row in safety_res.fetchall()}

        # 3. Fetch or ensure hotspot rule
        rule_res = await self._session.execute(
            text("""
                SELECT hotspot_rule_id
                FROM hotspot_rule
                WHERE (project_id = :project_id OR project_id IS NULL)
                  AND rule_version = :rule_version
                  AND active = true
                LIMIT 1
            """),
            {"project_id": project_id, "rule_version": rule_version},
        )
        rule_id = rule_res.scalar_one_or_none()

        system_actor = actor_user_id or UUID("00000000-0000-0000-0000-000000000001")

        if not rule_id:
            rule_id = uuid4()
            await self._session.execute(
                text("""
                    INSERT INTO hotspot_rule (
                        hotspot_rule_id, project_id, name, rule_version,
                        taxonomy_release_id, window_minutes, threshold_count,
                        location_level, dimension_config_json, eligibility_definition_version,
                        active, created_by, created_at
                    ) VALUES (
                        :rule_id, :project_id, 'Standard Deterministic Clustering Rule', :rule_version,
                        :rel_id, 1440, :threshold_count, 'BUILDING',
                        CAST(:dimension_config_json AS jsonb), 'v1',
                        true, :created_by, NOW()
                    )
                """),
                {
                    "rule_id": rule_id,
                    "project_id": project_id,
                    "rule_version": rule_version,
                    "rel_id": rel_id,
                    "threshold_count": threshold_count,
                    "dimension_config_json": json.dumps({"dimensions": ["service", "issue", "location"]}),
                    "created_by": system_actor,
                },
            )

        # 4. Fetch eligible feedback items in window
        items_res = await self._session.execute(
            text("""
                SELECT fi.feedback_item_id, f.reported_at, cc.operational_severity,
                       cc.primary_service_id, cc.issue_id, fi.location_id
                FROM feedback_item fi
                JOIN feedback f ON f.feedback_id = fi.feedback_id
                JOIN classification_current cc ON cc.feedback_item_id = fi.feedback_item_id
                WHERE f.project_id = :project_id
                  AND fi.status = 'ACTIVE'
                  AND fi.analytic_eligibility = 'INCLUDED'
                  AND cc.current_decision_id IS NOT NULL
                  AND cc.classification_state = 'ACCEPTED'
                  AND cc.primary_service_id IS NOT NULL
                  AND cc.issue_id IS NOT NULL
                  AND f.reported_at >= :window_start
                  AND f.reported_at <= :window_end
            """),
            {
                "project_id": project_id,
                "window_start": window_start,
                "window_end": window_end,
            },
        )

        cluster_input_items = [
            FeedbackClusterItem(
                feedback_item_id=row["feedback_item_id"],
                reported_at=row["reported_at"],
                operational_severity=row["operational_severity"],
                service_id=row["primary_service_id"],
                issue_id=row["issue_id"],
                location_id=row["location_id"],
            )
            for row in items_res.mappings().all()
        ]

        # 5. Cluster
        candidates = cluster_eligible_items(
            cluster_input_items,
            window_start=window_start,
            window_end=window_end,
            threshold_count=threshold_count,
            rule_version=rule_version,
            safety_critical_issue_ids=safety_issue_ids,
            safety_playbook_approved=safety_playbook_approved,
        )

        # 6. Idempotent Upsert
        synced_hotspot_ids: list[UUID] = []
        for cand in candidates:
            existing_res = await self._session.execute(
                text("""
                    SELECT hotspot_id, version, status
                    FROM hotspot
                    WHERE hotspot_rule_id = :rule_id
                      AND dimension_key = :dimension_key
                      AND window_start = :window_start
                      AND window_end = :window_end
                """),
                {
                    "rule_id": rule_id,
                    "dimension_key": cand.dimension_key,
                    "window_start": cand.window_start,
                    "window_end": cand.window_end,
                },
            )
            existing_row = existing_res.mappings().one_or_none()

            if existing_row:
                h_id = existing_row["hotspot_id"]
                await self._session.execute(
                    text("""
                        UPDATE hotspot
                        SET evidence_count = :evidence_count,
                            operational_severity = :severity,
                            action_priority = :action_priority,
                            first_seen_at = :first_seen_at,
                            last_seen_at = :last_seen_at,
                            updated_at = NOW()
                        WHERE hotspot_id = :hotspot_id
                    """),
                    {
                        "hotspot_id": h_id,
                        "evidence_count": cand.evidence_count,
                        "severity": cand.operational_severity.value,
                        "action_priority": cand.action_priority.value,
                        "first_seen_at": cand.first_seen_at,
                        "last_seen_at": cand.last_seen_at,
                    },
                )
            else:
                h_id = uuid4()
                await self._session.execute(
                    text("""
                        INSERT INTO hotspot (
                            hotspot_id, hotspot_rule_id, project_id, taxonomy_release_id,
                            dimension_key, service_id, issue_id, location_id,
                            window_start, window_end, evidence_count, status,
                            action_priority, operational_severity,
                            first_seen_at, last_seen_at, version, created_at, updated_at
                        ) VALUES (
                            :hotspot_id, :rule_id, :project_id, :rel_id,
                            :dimension_key, :service_id, :issue_id, :location_id,
                            :window_start, :window_end, :evidence_count, 'CANDIDATE',
                            :action_priority, :severity,
                            :first_seen_at, :last_seen_at, 1, NOW(), NOW()
                        )
                    """),
                    {
                        "hotspot_id": h_id,
                        "rule_id": rule_id,
                        "project_id": project_id,
                        "rel_id": rel_id,
                        "dimension_key": cand.dimension_key,
                        "service_id": cand.service_id,
                        "issue_id": cand.issue_id,
                        "location_id": cand.location_id,
                        "window_start": cand.window_start,
                        "window_end": cand.window_end,
                        "evidence_count": cand.evidence_count,
                        "action_priority": cand.action_priority.value,
                        "severity": cand.operational_severity.value,
                        "first_seen_at": cand.first_seen_at,
                        "last_seen_at": cand.last_seen_at,
                    },
                )
                # Initial timeline event
                await self._session.execute(
                    text("""
                        INSERT INTO hotspot_timeline_event (
                            hotspot_timeline_event_id, hotspot_id, from_status, to_status,
                            action, actor_user_id, reason, metadata_json, correlation_id, created_at
                        ) VALUES (
                            :event_id, :hotspot_id, NULL, 'CANDIDATE',
                            'DETECTED', :actor_user_id, 'Deterministic cluster matched rule threshold.',
                            CAST(:metadata_json AS jsonb), :correlation_id, NOW()
                        )
                    """),
                    {
                        "event_id": uuid4(),
                        "hotspot_id": h_id,
                        "actor_user_id": system_actor,
                        "metadata_json": json.dumps({"evidence_count": cand.evidence_count, "rule_version": rule_version}),
                        "correlation_id": str(uuid4()),
                    },
                )

            # Link evidence items
            for it in cand.items:
                await self._session.execute(
                    text("""
                        INSERT INTO feedback_item_hotspot (
                            hotspot_id, feedback_item_id, linked_at, evidence_role
                        ) VALUES (
                            :hotspot_id, :feedback_item_id, NOW(), 'PRIMARY'
                        )
                        ON CONFLICT (hotspot_id, feedback_item_id) DO NOTHING
                    """),
                    {"hotspot_id": h_id, "feedback_item_id": it.feedback_item_id},
                )

            synced_hotspot_ids.append(h_id)

        if not synced_hotspot_ids:
            return []

        result = await self._session.execute(
            text("""
                SELECT h.hotspot_id, h.project_id, h.dimension_key,
                       h.service_id, svc.service_code, svc.name_vi AS service_name_vi,
                       h.issue_id, iss.issue_code, iss.name_vi AS issue_name_vi,
                       h.location_id, loc.location_code, loc.name AS location_name,
                       h.status, h.action_priority, h.operational_severity,
                       h.evidence_count, h.assigned_user_id, h.assigned_team_key,
                       h.first_seen_at, h.last_seen_at, h.resolved_at,
                       h.resolution_summary, h.window_start, h.window_end,
                       h.version, h.created_at, h.updated_at
                FROM hotspot h
                JOIN service svc ON svc.service_id = h.service_id
                JOIN issue iss ON iss.issue_id = h.issue_id
                LEFT JOIN location loc ON loc.location_id = h.location_id
                WHERE h.hotspot_id = ANY(:synced_ids)
                ORDER BY
                    CASE h.action_priority
                        WHEN 'IMMEDIATE' THEN 1
                        WHEN 'URGENT' THEN 2
                        WHEN 'PLANNED' THEN 3
                        WHEN 'MONITOR' THEN 4
                        ELSE 5
                    END,
                    h.evidence_count DESC,
                    h.last_seen_at DESC
            """),
            {"synced_ids": synced_hotspot_ids},
        )
        return [
            HotspotListItem(
                hotspot_id=row["hotspot_id"],
                project_id=row["project_id"],
                dimension_key=row["dimension_key"],
                service_id=row["service_id"],
                service_code=row["service_code"],
                service_name_vi=row["service_name_vi"],
                issue_id=row["issue_id"],
                issue_code=row["issue_code"],
                issue_name_vi=row["issue_name_vi"],
                location_id=row["location_id"],
                location_code=row["location_code"],
                location_name=row["location_name"],
                status=row["status"],
                action_priority=row["action_priority"],
                operational_severity=row["operational_severity"],
                evidence_count=row["evidence_count"],
                assigned_user_id=row["assigned_user_id"],
                assigned_team_key=row["assigned_team_key"],
                first_seen_at=row["first_seen_at"],
                last_seen_at=row["last_seen_at"],
                resolved_at=row["resolved_at"],
                resolution_summary=row["resolution_summary"],
                window_start=row["window_start"],
                window_end=row["window_end"],
                version=row["version"],
                created_at=row["created_at"],
                updated_at=row["updated_at"],
            )
            for row in result.mappings().all()
        ]
