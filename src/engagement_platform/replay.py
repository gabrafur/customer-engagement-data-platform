"""As-of historical rebuilding that never invokes a delivery client."""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import UTC, date, datetime, time

from engagement_platform.config import PipelineConfig
from engagement_platform.features import build_customer_features
from engagement_platform.models import Customer, Recommendation, Transaction
from engagement_platform.quality import validate_inputs, validate_recommendations
from engagement_platform.ranking import make_recommendations
from engagement_platform.storage import InMemoryRecommendationStore


@dataclass(frozen=True, slots=True)
class HistoricalSnapshot:
    as_of_date: date
    recommendations: tuple[Recommendation, ...]
    inserted: int


def rebuild_historical_snapshot(
    customers: list[Customer],
    transactions: list[Transaction],
    config: PipelineConfig,
    as_of_date: date,
    store: InMemoryRecommendationStore | None = None,
) -> HistoricalSnapshot:
    """Recompute a bounded snapshot and persist it without external side effects."""

    bounded_transactions = [
        transaction for transaction in transactions if transaction.transaction_date <= as_of_date
    ]
    replay_config = replace(config, as_of_date=as_of_date)
    validate_inputs(customers, bounded_transactions, as_of_date).require_pass()
    features = build_customer_features(customers, bounded_transactions, as_of_date)
    recommendations = make_recommendations(
        features,
        replay_config.scoring,
        replay_config.regions,
        datetime.combine(as_of_date, time.min, tzinfo=UTC),
    )
    validate_recommendations(
        recommendations,
        {name: value.recommendation_limit for name, value in replay_config.regions.items()},
    ).require_pass()
    target = store or InMemoryRecommendationStore()
    inserted = target.upsert(recommendations)
    return HistoricalSnapshot(as_of_date, tuple(recommendations), inserted)
