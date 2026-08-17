from __future__ import annotations

import sys
from enum import Enum

if sys.version_info >= (3, 11):
    from enum import StrEnum
else:

    class StrEnum(str, Enum):
        pass


class ValueStatus(StrEnum):
    KNOWN = "KNOWN"
    UNKNOWN = "UNKNOWN"
    MISSING = "MISSING"
    NOT_APPLICABLE = "NOT_APPLICABLE"


class TaxonomyReleaseStatus(StrEnum):
    DRAFT = "DRAFT"
    APPROVED = "APPROVED"
    PUBLISHED = "PUBLISHED"
    RETIRED = "RETIRED"


class ClassificationState(StrEnum):
    PENDING_REVIEW = "PENDING_REVIEW"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    SUPERSEDED = "SUPERSEDED"


class DecisionSource(StrEnum):
    MANUAL = "MANUAL"
    SOURCE_TRUSTED = "SOURCE_TRUSTED"
    HUMAN_ACCEPTED_AI = "HUMAN_ACCEPTED_AI"
    HUMAN_CORRECTED_AI = "HUMAN_CORRECTED_AI"
    POLICY_AUTO_APPLIED = "POLICY_AUTO_APPLIED"
    SYSTEM_MIGRATION = "SYSTEM_MIGRATION"


class Sentiment(StrEnum):
    POSITIVE = "POSITIVE"
    NEUTRAL = "NEUTRAL"
    NEGATIVE = "NEGATIVE"
    UNKNOWN = "UNKNOWN"


class OperationalSeverity(StrEnum):
    SEV_1 = "SEV-1"
    SEV_2 = "SEV-2"
    SEV_3 = "SEV-3"
    SEV_4 = "SEV-4"


class CauseDeterminationStatus(StrEnum):
    NOT_ASSESSED = "NOT_ASSESSED"
    UNKNOWN = "UNKNOWN"
    SUGGESTED = "SUGGESTED"
    UNDER_INVESTIGATION = "UNDER_INVESTIGATION"
    CONFIRMED = "CONFIRMED"
    NOT_APPLICABLE = "NOT_APPLICABLE"


class AnalyticEligibility(StrEnum):
    INCLUDED = "INCLUDED"
    EXCLUDED = "EXCLUDED"
    PENDING = "PENDING"


class FeedbackItemStatus(StrEnum):
    ACTIVE = "ACTIVE"
    SPLIT_PARENT = "SPLIT_PARENT"
    RETIRED = "RETIRED"


class ImportJobStatus(StrEnum):
    UPLOADED = "UPLOADED"
    MAPPED = "MAPPED"
    VALIDATING = "VALIDATING"
    VALIDATED = "VALIDATED"
    QUEUED = "QUEUED"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    PARTIAL = "PARTIAL"
    FAILED = "FAILED"
    CANCELLING = "CANCELLING"
    CANCELLED = "CANCELLED"


class HotspotStatus(StrEnum):
    CANDIDATE = "CANDIDATE"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    INVESTIGATING = "INVESTIGATING"
    RESOLVED = "RESOLVED"
    DISMISSED = "DISMISSED"
    REOPENED = "REOPENED"


class ActionPriority(StrEnum):
    IMMEDIATE = "IMMEDIATE"
    URGENT = "URGENT"
    PLANNED = "PLANNED"
    MONITOR = "MONITOR"


class MappingType(StrEnum):
    PRIMARY = "PRIMARY"
    SECONDARY = "SECONDARY"


class ReviewAction(StrEnum):
    ACCEPT = "ACCEPT"
    CORRECT = "CORRECT"
    MARK_UNKNOWN = "MARK_UNKNOWN"
    MARK_MISSING = "MARK_MISSING"
    MARK_NOT_APPLICABLE = "MARK_NOT_APPLICABLE"
    SPLIT_REQUIRED = "SPLIT_REQUIRED"
    SKIP = "SKIP"

