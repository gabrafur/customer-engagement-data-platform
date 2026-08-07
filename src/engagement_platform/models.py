"""Domain models for the fictional customer engagement example."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from enum import StrEnum


class RecommendationType(StrEnum):
    """Generic recommendation categories invented for this demonstration."""

    WELCOME_JOURNEY = "WELCOME_JOURNEY"
    RECONNECT = "RECONNECT"
    LOYALTY_THANK_YOU = "LOYALTY_THANK_YOU"
    COMMUNITY_UPDATE = "COMMUNITY_UPDATE"
    RETENTION_CHECKIN = "RETENTION_CHECKIN"


class DeliveryState(StrEnum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    RETRY_EXHAUSTED = "RETRY_EXHAUSTED"


@dataclass(frozen=True, slots=True)
class Customer:
    customer_id: str
    region: str
    segment: str
    registration_date: date
    engagement_score: float


@dataclass(frozen=True, slots=True)
class Transaction:
    transaction_id: str
    customer_id: str
    product_id: str
    transaction_date: date
    amount: float


@dataclass(frozen=True, slots=True)
class CustomerFeatures:
    customer_id: str
    region: str
    segment: str
    customer_age_days: int
    days_since_last_transaction: int
    purchase_frequency: int
    average_order_value: float
    engagement_score: float


@dataclass(frozen=True, slots=True)
class Recommendation:
    recommendation_id: str
    customer_id: str
    region: str
    recommendation_type: RecommendationType
    score: float
    regional_rank: int
    idempotency_key: str
    created_at: datetime


@dataclass(frozen=True, slots=True)
class DeliveryReceipt:
    idempotency_key: str
    state: DeliveryState
    status_code: int
    attempts: int
    delivered_at: datetime | None
