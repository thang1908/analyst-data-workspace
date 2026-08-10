from datetime import datetime
from uuid import UUID
from typing import Any

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from cx_db.src.models.base import Base, TimestampMixin


class ProjectModel(Base, TimestampMixin):
    __tablename__ = "project"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    code: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class ReferenceReleaseModel(Base):
    __tablename__ = "reference_release"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    kind: Mapped[str] = mapped_column(String(32), nullable=False)  # TAXONOMY | LOCATION | SOURCE_TRUST
    version: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="PUBLISHED", nullable=False)
    checksum_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    published_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        UniqueConstraint("kind", "version", name="uq_reference_release_kind_version"),
    )


class LocationNodeModel(Base):
    __tablename__ = "location_node"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    release_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("reference_release.id"), nullable=False)
    project_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("project.id"), nullable=False)
    code: Mapped[str] = mapped_column(String(64), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    node_type: Mapped[str] = mapped_column(String(64), nullable=False)
    parent_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("location_node.id"), nullable=True)

    __table_args__ = (
        UniqueConstraint("release_id", "project_id", "code", name="uq_location_node_rel_proj_code"),
    )


class TaxonomyServiceModel(Base):
    __tablename__ = "taxonomy_service"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    release_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("reference_release.id"), nullable=False)
    code: Mapped[str] = mapped_column(String(64), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    __table_args__ = (
        UniqueConstraint("release_id", "code", name="uq_taxonomy_service_release_code"),
    )


class TaxonomyIssueModel(Base):
    __tablename__ = "taxonomy_issue"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    release_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("reference_release.id"), nullable=False)
    code: Mapped[str] = mapped_column(String(64), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    __table_args__ = (
        UniqueConstraint("release_id", "code", name="uq_taxonomy_issue_release_code"),
    )


class TaxonomyServiceIssueModel(Base):
    __tablename__ = "taxonomy_service_issue"

    release_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("reference_release.id"), primary_key=True)
    service_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("taxonomy_service.id"), primary_key=True)
    issue_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("taxonomy_issue.id"), primary_key=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class SourceTrustPolicyModel(Base):
    __tablename__ = "source_trust_policy"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    release_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("reference_release.id"), nullable=False)
    source: Mapped[str] = mapped_column(String(64), nullable=False)
    project_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("project.id"), nullable=False)
    allowed_contract_version: Mapped[str] = mapped_column(String(64), nullable=False)
    active_from: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    active_to: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    approved_by: Mapped[str] = mapped_column(String(255), nullable=False)
    approved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    __table_args__ = (
        UniqueConstraint("release_id", "source", "project_id", name="uq_source_trust_policy"),
    )


class ImportJobModel(Base, TimestampMixin):
    __tablename__ = "import_job"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    actor_id: Mapped[str] = mapped_column(String(255), nullable=False)
    project_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("project.id"), nullable=False)
    idempotency_key: Mapped[str] = mapped_column(String(255), nullable=False)
    contract_version: Mapped[str] = mapped_column(String(64), nullable=False)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    storage_key: Mapped[str] = mapped_column(String(512), nullable=False)
    state: Mapped[str] = mapped_column(String(32), nullable=False)
    total_rows: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    valid_rows: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    invalid_rows: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    duplicate_rows: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    committed_rows: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        UniqueConstraint("actor_id", "idempotency_key", name="uq_import_job_actor_idempotency"),
    )


class ImportRowModel(Base):
    __tablename__ = "import_row"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    import_job_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("import_job.id"), nullable=False)
    row_number: Mapped[int] = mapped_column(Integer, nullable=False)
    row_checksum: Mapped[str] = mapped_column(String(64), nullable=False)
    normalized_payload: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    outcome: Mapped[str] = mapped_column(String(32), nullable=False)  # VALID | INVALID | DUPLICATE
    errors: Mapped[list[dict[str, Any]] | None] = mapped_column(JSONB, nullable=True)

    __table_args__ = (
        UniqueConstraint("import_job_id", "row_number", name="uq_import_row_job_rownum"),
    )


class SourceRecordModel(Base, TimestampMixin):
    __tablename__ = "source_record"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    source: Mapped[str] = mapped_column(String(64), nullable=False)
    source_reference: Mapped[str] = mapped_column(String(255), nullable=False)
    import_job_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("import_job.id"), nullable=False)
    import_row_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("import_row.id"), unique=True, nullable=False)
    payload_checksum: Mapped[str] = mapped_column(String(64), nullable=False)

    __table_args__ = (
        UniqueConstraint("source", "source_reference", name="uq_source_record_source_ref"),
    )


class FeedbackModel(Base):
    __tablename__ = "feedback"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    source_record_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("source_record.id"), unique=True, nullable=False)
    project_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("project.id"), nullable=False)
    reported_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    content_masked: Mapped[str] = mapped_column(Text, nullable=False)
    ingested_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class FeedbackItemModel(Base):
    __tablename__ = "feedback_item"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    feedback_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("feedback.id"), nullable=False)
    item_index: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    item_text_masked: Mapped[str] = mapped_column(Text, nullable=False)
    analytic_eligibility: Mapped[str] = mapped_column(String(32), default="INCLUDED", nullable=False)

    __table_args__ = (
        UniqueConstraint("feedback_id", "item_index", name="uq_feedback_item_feedback_index"),
    )


class ClassificationDecisionModel(Base):
    __tablename__ = "classification_decision"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    feedback_item_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("feedback_item.id"), nullable=False)
    decision_version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    primary_service_value_status: Mapped[str] = mapped_column(String(32), nullable=False)
    primary_service_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("taxonomy_service.id"), nullable=True)
    issue_value_status: Mapped[str] = mapped_column(String(32), nullable=False)
    issue_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("taxonomy_issue.id"), nullable=True)
    location_value_status: Mapped[str] = mapped_column(String(32), nullable=False)
    location_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("location_node.id"), nullable=True)
    sentiment: Mapped[str] = mapped_column(String(32), nullable=False)
    severity: Mapped[str] = mapped_column(String(32), nullable=False)
    decision_source: Mapped[str] = mapped_column(String(32), nullable=False)
    decided_by: Mapped[str] = mapped_column(String(255), nullable=False)
    decided_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    __table_args__ = (
        UniqueConstraint("feedback_item_id", "decision_version", name="uq_class_decision_item_version"),
    )


class ClassificationCurrentModel(Base):
    __tablename__ = "classification_current"

    feedback_item_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("feedback_item.id"), primary_key=True)
    current_decision_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("classification_decision.id"), unique=True, nullable=False)
    primary_service_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("taxonomy_service.id"), nullable=True)
    issue_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("taxonomy_issue.id"), nullable=True)
    location_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("location_node.id"), nullable=True)
    sentiment: Mapped[str] = mapped_column(String(32), nullable=False)
    severity: Mapped[str] = mapped_column(String(32), nullable=False)
    last_decision_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class OutboxEventModel(Base):
    __tablename__ = "outbox_event"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    dedupe_key: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    event_type: Mapped[str] = mapped_column(String(64), nullable=False)
    schema_version: Mapped[str] = mapped_column(String(32), nullable=False)
    aggregate_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    payload: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class AuditEventModel(Base):
    __tablename__ = "audit_event"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    actor_id: Mapped[str] = mapped_column(String(255), nullable=False)
    action: Mapped[str] = mapped_column(String(64), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(64), nullable=False)
    entity_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    outcome: Mapped[str] = mapped_column(String(32), nullable=False)
    correlation_id: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
