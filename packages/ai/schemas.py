"""Pydantic schemas and contracts for AI classification."""
from __future__ import annotations

from typing import Any, Literal
from pydantic import BaseModel, ConfigDict, Field


class FeedbackItemInput(BaseModel):
    """Input payload for a single feedback item to be classified."""

    item_id: str = Field(description="Unique identifier for the feedback item")
    text: str = Field(description="Raw or masked text content of the feedback")
    location: str | None = Field(default=None, description="Location context (e.g. building, project name)")
    channel: str | None = Field(default=None, description="Intake channel context (e.g. App Cư dân, Hotline, Lễ tân)")
    reported_date: str | None = Field(default=None, description="Reported timestamp if available")
    extra_metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata context")


class BatchClassificationInput(BaseModel):
    """Input payload for batch classification."""

    items: list[FeedbackItemInput] = Field(description="List of feedback items to classify")


class FeedbackClassificationResult(BaseModel):
    """Structured classification output produced by LLM for a single item."""

    model_config = ConfigDict(extra="ignore")

    item_id: str = Field(description="Corresponding item_id matching the input")
    is_valid_feedback: bool = Field(
        description="True if the text is a genuine resident feedback/complaint/inquiry. False if it is spam, test, greeting or out-of-scope banter."
    )
    analytic_eligibility: Literal["INCLUDED", "EXCLUDED"] = Field(
        default="INCLUDED",
        description="INCLUDED for actionable resident feedback to be counted in analytics/hotspots. EXCLUDED for spam, test, or non-feedback noise.",
    )
    exclusion_reason: Literal["NONE", "SPAM", "NON_FEEDBACK", "OUT_OF_SCOPE", "TEST_DATA"] = Field(
        default="NONE",
        description="Reason for exclusion when analytic_eligibility is EXCLUDED.",
    )
    primary_service_code: Literal[
        "SV-01", "SV-02", "SV-03", "SV-04", "SV-05",
        "SV-06", "SV-07", "SV-08", "SV-09", "SV-10"
    ] = Field(
        default="SV-10",
        description="Canonical primary service code responsible for the resolution.",
    )
    issue_code: str | None = Field(
        default=None,
        description="Canonical issue code belonging to the primary service (e.g. IS-07-01, IS-05-02). None if no specific failure or unknown.",
    )
    journey_stage_code: Literal["A", "C", "TR", "HO", "RES", "OPS"] = Field(
        default="RES",
        description="Customer lifecycle stage (A: Awareness, C: Consideration, TR: Transaction, HO: Handover, RES: Residence, OPS: Service Usage / Sử dụng dịch vụ).",
    )
    journey_step_code: str = Field(
        default="RES-07",
        description="Customer lifecycle step code (e.g. RES-07 for defect/inquiry reports, RES-03 for access, HO-03 for inspection).",
    )
    touchpoint_code: str | None = Field(
        default=None,
        description="Touchpoint code where the interaction/issue took place (e.g. TP-RES-03-03, TP-RES-07-01).",
    )
    sentiment: Literal["POSITIVE", "NEGATIVE", "NEUTRAL", "UNKNOWN"] = Field(
        default="NEUTRAL",
        description="Sentiment expressed in the feedback.",
    )
    operational_severity: Literal["SEV-1", "SEV-2", "SEV-3", "SEV-4"] = Field(
        default="SEV-4",
        description="Operational severity level. SEV-1: Life-safety/Fire emergency, SEV-2: Major disruption/Elevator entrapment, SEV-3: Medium defect, SEV-4: Low/Routine.",
    )
    confidence: float = Field(
        default=0.9,
        ge=0.0,
        le=1.0,
        description="Confidence score from 0.0 to 1.0.",
    )
    rationale: str = Field(
        default="",
        description="Concise rationale explaining the classification decision.",
    )


class BatchClassificationOutput(BaseModel):
    """Structured output containing classification results for a batch of items."""

    model_config = ConfigDict(extra="ignore")

    results: list[FeedbackClassificationResult] = Field(
        description="List of classification results for each feedback item in the input batch"
    )
