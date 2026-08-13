"""Immutable DTOs shared by analytics application use cases."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from typing import Iterable, TypeAlias

from packages.domain.shared.enums import Sentiment

TimeBucket: TypeAlias = date | datetime | str
SentimentValue: TypeAlias = Sentiment | str


def _sentiment_value(value: SentimentValue) -> str:
    return str(value)


@dataclass(frozen=True, slots=True)
class SummaryDTO:
    """P0 summary metrics calculated on eligible feedback items only.

    ``csat_score`` is the P0 sentiment-based CSAT proxy: the share of known
    sentiment items that are positive.  The product does not yet have a
    dedicated survey CSAT instrument, so this is intentionally identical to
    ``positive_rate``.  ``UNKNOWN`` is excluded from both rate denominators,
    as required by BR-ANA-003.
    """

    total: int
    csat_score: float
    positive_rate: float
    negative_rate: float
    sentiment_unknown_rate: float
    active_hotspots: int = 0

    @property
    def unknown_rate(self) -> float:
        """API-contract alias for the sentiment-specific unknown rate."""
        return self.sentiment_unknown_rate

    @classmethod
    def from_sentiments(cls, sentiments: Iterable[SentimentValue]) -> SummaryDTO:
        """Build a summary while excluding unknown sentiment from rate bases."""
        values = [_sentiment_value(sentiment) for sentiment in sentiments]
        known = [
            sentiment
            for sentiment in values
            if sentiment
            in {Sentiment.POSITIVE, Sentiment.NEUTRAL, Sentiment.NEGATIVE}
        ]
        known_total = len(known)
        positive_rate = (
            sum(sentiment == Sentiment.POSITIVE for sentiment in known) / known_total
            if known_total
            else 0.0
        )
        negative_rate = (
            sum(sentiment == Sentiment.NEGATIVE for sentiment in known) / known_total
            if known_total
            else 0.0
        )
        total = len(values)
        return cls(
            total=total,
            csat_score=positive_rate,
            positive_rate=positive_rate,
            negative_rate=negative_rate,
            sentiment_unknown_rate=(
                sum(sentiment == Sentiment.UNKNOWN for sentiment in values) / total
                if total
                else 0.0
            ),
        )


@dataclass(frozen=True, slots=True)
class TrendPointDTO:
    """One volume observation in an analytics time bucket."""

    time_bucket: TimeBucket
    volume: int
    negative_rate: float = 0.0
    unknown_rate: float = 0.0
    active_hotspots: int = 0


@dataclass(frozen=True, slots=True)
class BreakdownItemDTO:
    """A dimension bucket and its share of the eligible item total."""

    dimension_key: str
    count: int
    percentage: float
    dimension_name: str | None = None
    negative_rate: float = 0.0
    active_hotspots: int = 0

    @classmethod
    def from_count(
        cls,
        *,
        dimension_key: str,
        count: int,
        total: int,
    ) -> BreakdownItemDTO:
        """Build a breakdown bucket, avoiding division by zero for empty data."""
        if count < 0:
            raise ValueError("count must not be negative")
        if total < 0:
            raise ValueError("total must not be negative")
        if count > total:
            raise ValueError("count must not exceed total")
        return cls(
            dimension_key=dimension_key,
            count=count,
            percentage=count / total if total else 0.0,
        )


@dataclass(frozen=True, slots=True)
class FilterOptionDTO:
    """A selectable analytics filter value with a human-readable label."""

    code: str
    name: str
    id: str | None = None
