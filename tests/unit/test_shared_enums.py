from packages.domain.shared.enums import (
    AnalyticEligibility,
    CauseDeterminationStatus,
    ClassificationState,
    DecisionSource,
    FeedbackItemStatus,
    HotspotStatus,
    ImportJobStatus,
    OperationalSeverity,
    ReviewAction,
    Sentiment,
    TaxonomyReleaseStatus,
    ValueStatus,
)


def test_value_status_values() -> None:
    assert ValueStatus.KNOWN == "KNOWN"
    assert ValueStatus.UNKNOWN == "UNKNOWN"
    assert ValueStatus.MISSING == "MISSING"
    assert ValueStatus.NOT_APPLICABLE == "NOT_APPLICABLE"


def test_operational_severity_values() -> None:
    assert OperationalSeverity.SEV_1 == "SEV-1"
    assert OperationalSeverity.SEV_2 == "SEV-2"
    assert OperationalSeverity.SEV_3 == "SEV-3"
    assert OperationalSeverity.SEV_4 == "SEV-4"


def test_review_actions_count() -> None:
    actions = list(ReviewAction)
    assert len(actions) == 7
    assert ReviewAction.ACCEPT == "ACCEPT"
    assert ReviewAction.CORRECT == "CORRECT"


def test_decision_source_values() -> None:
    assert DecisionSource.MANUAL == "MANUAL"
    assert DecisionSource.HUMAN_ACCEPTED_AI == "HUMAN_ACCEPTED_AI"


def test_all_canonical_enums_present() -> None:
    assert len(ValueStatus) == 4
    assert len(TaxonomyReleaseStatus) == 4
    assert len(ClassificationState) == 4
    assert len(Sentiment) == 4
    assert len(AnalyticEligibility) == 3
    assert len(FeedbackItemStatus) == 3
    assert len(HotspotStatus) == 6
    assert len(CauseDeterminationStatus) == 6
    assert len(ImportJobStatus) == 11
