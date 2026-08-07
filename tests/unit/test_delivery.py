from datetime import UTC, datetime

import pytest

from engagement_platform.delivery import (
    HttpDeliveryClient,
    MockDeliveryClient,
    ReliableDeliveryService,
)
from engagement_platform.models import DeliveryState, Recommendation, RecommendationType


@pytest.fixture
def recommendation() -> Recommendation:
    return Recommendation(
        "rec_1",
        "customer_1",
        "north",
        RecommendationType.COMMUNITY_UPDATE,
        0.5,
        1,
        "stable-key",
        datetime(2026, 8, 1, tzinfo=UTC),
    )


def test_retries_transient_results_then_accepts(recommendation: Recommendation) -> None:
    client = MockDeliveryClient([TimeoutError(), 500, 202])
    delays: list[float] = []
    service = ReliableDeliveryService(client, 3, 0.25, delays.append)

    receipt = service.deliver(recommendation)

    assert receipt.state == DeliveryState.ACCEPTED
    assert receipt.attempts == 3
    assert delays == [0.25, 0.5]


def test_duplicate_key_returns_cached_receipt(recommendation: Recommendation) -> None:
    client = MockDeliveryClient()
    service = ReliableDeliveryService(client, 2, 0)

    first = service.deliver(recommendation)
    second = service.deliver(recommendation)

    assert first is second
    assert client.calls == 1


def test_exhausted_delivery_is_reconciliable(recommendation: Recommendation) -> None:
    service = ReliableDeliveryService(MockDeliveryClient([500, 500]), 2, 0)

    receipt = service.deliver(recommendation)

    assert receipt.state == DeliveryState.RETRY_EXHAUSTED
    assert receipt.delivered_at is None


def test_http_client_requires_explicit_valid_endpoint() -> None:
    with pytest.raises(ValueError, match="http or https"):
        HttpDeliveryClient("not-an-endpoint")
