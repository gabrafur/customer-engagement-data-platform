from datetime import date

import pytest

from engagement_platform.features import build_customer_features
from engagement_platform.models import (
    Customer,
    CustomerFeatures,
    RecommendationType,
    Transaction,
)
from engagement_platform.rules import choose_recommendation


def test_features_ignore_future_transactions_and_fill_empty_history() -> None:
    as_of = date(2026, 8, 1)
    customers = [Customer("c1", "north", "starter", date(2026, 7, 1), 0.5)]
    transactions = [Transaction("t1", "c1", "i1", date(2026, 8, 2), 99.0)]

    result = build_customer_features(customers, transactions, as_of)

    assert result[0].purchase_frequency == 0
    assert result[0].days_since_last_transaction == 365
    assert result[0].average_order_value == 0.0


def test_features_aggregate_transaction_history() -> None:
    as_of = date(2026, 8, 1)
    customer = Customer("c1", "north", "premium", date(2026, 1, 1), 0.7)
    transactions = [
        Transaction("t1", "c1", "i1", date(2026, 7, 1), 100.0),
        Transaction("t2", "c1", "i2", date(2026, 7, 22), 200.0),
    ]

    result = build_customer_features([customer], transactions, as_of)[0]

    assert result.purchase_frequency == 2
    assert result.average_order_value == 150.0
    assert result.days_since_last_transaction == 10


@pytest.mark.parametrize(
    ("overrides", "expected"),
    [
        ({"customer_age_days": 10}, RecommendationType.WELCOME_JOURNEY),
        ({"days_since_last_transaction": 150}, RecommendationType.RECONNECT),
        (
            {"purchase_frequency": 5, "average_order_value": 180},
            RecommendationType.LOYALTY_THANK_YOU,
        ),
        ({"engagement_score": 0.1}, RecommendationType.RETENTION_CHECKIN),
        ({}, RecommendationType.COMMUNITY_UPDATE),
    ],
)
def test_fictional_rules(overrides: dict[str, float | int], expected: RecommendationType) -> None:
    values: dict[str, object] = {
        "customer_id": "c1",
        "region": "north",
        "segment": "standard",
        "customer_age_days": 100,
        "days_since_last_transaction": 15,
        "purchase_frequency": 2,
        "average_order_value": 50.0,
        "engagement_score": 0.6,
    }
    values.update(overrides)

    assert choose_recommendation(CustomerFeatures(**values)) == expected  # type: ignore[arg-type]
