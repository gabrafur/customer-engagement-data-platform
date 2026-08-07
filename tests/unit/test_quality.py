from datetime import UTC, date, datetime

import pytest

from engagement_platform.models import (
    Customer,
    Recommendation,
    RecommendationType,
    Transaction,
)
from engagement_platform.quality import DataQualityError, validate_inputs, validate_recommendations


def test_input_quality_reports_multiple_failures() -> None:
    customers = [
        Customer("duplicate", "north", "standard", date(2026, 1, 1), 1.2),
        Customer("duplicate", "south", "starter", date(2026, 1, 1), 0.4),
    ]
    transactions = [
        Transaction("t1", "missing", "i1", date(2026, 8, 2), -2.0),
    ]

    report = validate_inputs(customers, transactions, date(2026, 8, 1))

    assert not report.passed
    assert report.failure_count == 5
    with pytest.raises(DataQualityError, match="Data quality checks failed"):
        report.require_pass()


def test_recommendation_quality_accepts_valid_batch() -> None:
    recommendation = Recommendation(
        "r1",
        "c1",
        "north",
        RecommendationType.COMMUNITY_UPDATE,
        0.5,
        1,
        "key-1",
        datetime(2026, 8, 1, tzinfo=UTC),
    )

    report = validate_recommendations([recommendation], {"north": 1})

    assert report.passed
    report.require_pass()
