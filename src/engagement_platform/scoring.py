"""Transparent scoring for the fictional demonstration domain."""

from engagement_platform.config import ScoringConfig
from engagement_platform.models import CustomerFeatures


def _clamp(value: float) -> float:
    return min(max(value, 0.0), 1.0)


def score_customer(features: CustomerFeatures, config: ScoringConfig) -> float:
    recency = 1.0 - _clamp(features.days_since_last_transaction / 180.0)
    frequency = _clamp(features.purchase_frequency / 8.0)
    value = _clamp(features.average_order_value / 250.0)
    engagement = _clamp(features.engagement_score)
    score = (
        recency * config.recency
        + frequency * config.frequency
        + value * config.value
        + engagement * config.engagement
    )
    return round(score, 6)
