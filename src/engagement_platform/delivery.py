"""Simulated downstream delivery with retries and idempotency."""

from __future__ import annotations

import json
import time
from abc import ABC, abstractmethod
from collections.abc import Callable, Iterable
from datetime import UTC, datetime
from urllib.request import Request, urlopen

from engagement_platform.models import DeliveryReceipt, DeliveryState, Recommendation


class RecommendationDeliveryClient(ABC):
    @abstractmethod
    def send(self, recommendation: Recommendation) -> int:
        """Return an HTTP-like status code for one recommendation."""


class MockDeliveryClient(RecommendationDeliveryClient):
    """Deterministic delivery simulator used by every default configuration."""

    def __init__(self, outcomes: Iterable[int | Exception] | None = None) -> None:
        self._outcomes = iter(outcomes or ())
        self.calls = 0

    def send(self, recommendation: Recommendation) -> int:
        self.calls += 1
        outcome = next(self._outcomes, 202)
        if isinstance(outcome, Exception):
            raise outcome
        return outcome


class HttpDeliveryClient(RecommendationDeliveryClient):
    """Optional standard-library client; no endpoint is bundled with the project."""

    def __init__(self, endpoint: str, timeout_seconds: float = 5.0) -> None:
        if not endpoint.startswith(("http://", "https://")):
            raise ValueError("endpoint must use http or https")
        self.endpoint = endpoint
        self.timeout_seconds = timeout_seconds

    def send(self, recommendation: Recommendation) -> int:
        body = json.dumps(
            {
                "recommendation_id": recommendation.recommendation_id,
                "customer_id": recommendation.customer_id,
                "recommendation_type": recommendation.recommendation_type,
                "idempotency_key": recommendation.idempotency_key,
            }
        ).encode()
        request = Request(
            self.endpoint,
            data=body,
            method="POST",
            headers={
                "Content-Type": "application/json",
                "Idempotency-Key": recommendation.idempotency_key,
            },
        )
        with urlopen(request, timeout=self.timeout_seconds) as response:  # noqa: S310
            return int(response.status)


class ReliableDeliveryService:
    """Retry transient outcomes and return the prior receipt for duplicate keys."""

    def __init__(
        self,
        client: RecommendationDeliveryClient,
        max_attempts: int,
        base_delay_seconds: float,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        if max_attempts < 1:
            raise ValueError("max_attempts must be positive")
        self.client = client
        self.max_attempts = max_attempts
        self.base_delay_seconds = base_delay_seconds
        self.sleep = sleep
        self._receipts: dict[str, DeliveryReceipt] = {}

    def deliver(self, recommendation: Recommendation) -> DeliveryReceipt:
        existing = self._receipts.get(recommendation.idempotency_key)
        if existing is not None:
            return existing

        status_code = 599
        attempts = 0
        for attempts in range(1, self.max_attempts + 1):
            try:
                status_code = self.client.send(recommendation)
            except (TimeoutError, OSError):
                status_code = 599
            if status_code == 202:
                receipt = DeliveryReceipt(
                    idempotency_key=recommendation.idempotency_key,
                    state=DeliveryState.ACCEPTED,
                    status_code=status_code,
                    attempts=attempts,
                    delivered_at=datetime.now(UTC),
                )
                self._receipts[recommendation.idempotency_key] = receipt
                return receipt
            if attempts < self.max_attempts:
                self.sleep(self.base_delay_seconds * (2 ** (attempts - 1)))

        receipt = DeliveryReceipt(
            idempotency_key=recommendation.idempotency_key,
            state=DeliveryState.RETRY_EXHAUSTED,
            status_code=status_code,
            attempts=attempts,
            delivered_at=None,
        )
        self._receipts[recommendation.idempotency_key] = receipt
        return receipt
