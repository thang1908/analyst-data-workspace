"""Unit tests for AI classification module."""
from __future__ import annotations

import pytest

from packages.ai.classifier import FeedbackClassifier
from packages.ai.schemas import (
    BatchClassificationInput,
    BatchClassificationOutput,
    FeedbackClassificationResult,
    FeedbackItemInput,
)


def test_schema_valid_classification_result() -> None:
    result = FeedbackClassificationResult(
        item_id="item_1",
        is_valid_feedback=True,
        analytic_eligibility="INCLUDED",
        exclusion_reason="NONE",
        primary_service_code="SV-07",
        issue_code="IS-07-01",
        journey_stage_code="RES",
        journey_step_code="RES-07",
        touchpoint_code="TP-RES-03-03",
        sentiment="NEGATIVE",
        operational_severity="SEV-2",
        confidence=0.96,
        rationale="Kẹt thang máy",
    )
    assert result.item_id == "item_1"
    assert result.is_valid_feedback is True
    assert result.analytic_eligibility == "INCLUDED"
    assert result.primary_service_code == "SV-07"
    assert result.operational_severity == "SEV-2"


def test_schema_spam_exclusion_result() -> None:
    result = FeedbackClassificationResult(
        item_id="item_spam",
        is_valid_feedback=False,
        analytic_eligibility="EXCLUDED",
        exclusion_reason="SPAM",
        primary_service_code="SV-10",
        issue_code=None,
        journey_stage_code="RES",
        journey_step_code="RES-07",
        touchpoint_code=None,
        sentiment="NEUTRAL",
        operational_severity="SEV-4",
        confidence=0.99,
        rationale="Spam quảng cáo",
    )
    assert result.is_valid_feedback is False
    assert result.analytic_eligibility == "EXCLUDED"
    assert result.exclusion_reason == "SPAM"
    assert result.primary_service_code == "SV-10"


@pytest.mark.asyncio
async def test_classifier_fallback_handles_various_intents() -> None:
    classifier = FeedbackClassifier(provider="none")  # forces fallback mode

    items = [
        FeedbackItemInput(
            item_id="1",
            text="Thang máy toà S10 sáng nay rung lắc mạnh và kẹt ở tầng 15",
            location="Toà S10",
            channel="App",
        ),
        FeedbackItemInput(
            item_id="2",
            text="alo alo 123",
            location="",
            channel="Web",
        ),
        FeedbackItemInput(
            item_id="3",
            text="Bảo vệ toà nhà rất chu đáo và nhiệt tình hỗ trợ",
            location="S8",
            channel="Trực tiếp",
        ),
        FeedbackItemInput(
            item_id="4",
            text="Bãi đỗ xe tầng hầm bị hết chỗ và ngập nước",
            location="Bãi xe B1",
            channel="Hotline",
        ),
    ]

    output: BatchClassificationOutput = await classifier.classify_batch(items)
    assert len(output.results) == 4

    # Item 1: Elevator issue
    r1 = output.results[0]
    assert r1.item_id == "1"
    assert r1.is_valid_feedback is True
    assert r1.primary_service_code == "SV-07"
    assert r1.sentiment == "NEGATIVE"
    assert r1.operational_severity in ("SEV-1", "SEV-2", "SEV-3")

    # Item 2: Spam / test
    r2 = output.results[1]
    assert r2.item_id == "2"
    assert r2.is_valid_feedback is False
    assert r2.analytic_eligibility == "EXCLUDED"
    assert r2.exclusion_reason == "NON_FEEDBACK"

    # Item 3: Positive security
    r3 = output.results[2]
    assert r3.item_id == "3"
    assert r3.is_valid_feedback is True
    assert r3.sentiment == "POSITIVE"

    # Item 4: Parking issue
    r4 = output.results[3]
    assert r4.item_id == "4"
    assert r4.is_valid_feedback is True
    assert r4.primary_service_code == "SV-05"
