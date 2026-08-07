import json
import logging
from datetime import UTC, date, datetime
from pathlib import Path

import pytest

from engagement_platform.models import Recommendation, RecommendationType
from engagement_platform.monitoring import JsonFormatter, Metrics, configure_logging
from engagement_platform.storage import InMemoryRecommendationStore
from engagement_platform.synthetic import generate_customers, generate_transactions, write_csv


def recommendation() -> Recommendation:
    return Recommendation(
        "rec_1",
        "c1",
        "north",
        RecommendationType.COMMUNITY_UPDATE,
        0.5,
        1,
        "key-1",
        datetime(2026, 8, 1, tzinfo=UTC),
    )


def test_synthetic_generation_is_deterministic_and_writable(tmp_path: Path) -> None:
    customers = generate_customers(5, 42, date(2026, 8, 1))
    repeated = generate_customers(5, 42, date(2026, 8, 1))
    transactions = generate_transactions(customers, 42, date(2026, 8, 1))

    assert customers == repeated
    assert all(item.customer_id.startswith("customer_") for item in customers)
    write_csv(customers, tmp_path / "customers.csv")
    assert (tmp_path / "customers.csv").read_text().count("\n") == 6
    assert all(item.transaction_date <= date(2026, 8, 1) for item in transactions)


def test_generation_validates_counts() -> None:
    with pytest.raises(ValueError, match="positive"):
        generate_customers(0, 1, date(2026, 8, 1))


def test_store_inserts_each_idempotency_key_once() -> None:
    store = InMemoryRecommendationStore()
    item = recommendation()

    assert store.upsert([item, item]) == 1
    assert store.all() == [item]


def test_metrics_and_json_formatter() -> None:
    metrics = Metrics()
    metrics.increment("records", 2)
    record = logging.LogRecord("demo", logging.INFO, "", 1, "complete", (), None)
    record.context = metrics.snapshot()

    payload = json.loads(JsonFormatter().format(record))

    assert payload["message"] == "complete"
    assert payload["context"] == {"records": 2}


def test_configure_logging_replaces_handlers() -> None:
    logger = configure_logging("DEBUG")
    repeated = configure_logging("INFO")

    assert logger is repeated
    assert logger.level == logging.INFO
    assert len(logger.handlers) == 1
