"""A small transactional-outbox model with an immutable transition log."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from uuid import NAMESPACE_URL, uuid5

from engagement_platform.models import Recommendation


class OutboxState(StrEnum):
    PENDING = "PENDING"
    DISPATCHED = "DISPATCHED"
    FAILED = "FAILED"


@dataclass(frozen=True, slots=True)
class OutboxRecord:
    event_id: str
    sequence: int
    idempotency_key: str
    recommendation: Recommendation
    created_at: datetime


@dataclass(frozen=True, slots=True)
class StateTransition:
    sequence: int
    idempotency_key: str
    state: OutboxState
    occurred_at: datetime
    detail: str


class InMemoryOutbox:
    """Append events and derive current state without overwriting history."""

    def __init__(self) -> None:
        self._records: list[OutboxRecord] = []
        self._transitions: list[StateTransition] = []

    def append(self, recommendation: Recommendation) -> OutboxRecord:
        sequence = len(self._records) + 1
        event_id = str(uuid5(NAMESPACE_URL, f"{recommendation.idempotency_key}:{sequence}"))
        record = OutboxRecord(
            event_id,
            sequence,
            recommendation.idempotency_key,
            recommendation,
            datetime.now(UTC),
        )
        self._records.append(record)
        self.transition(recommendation.idempotency_key, OutboxState.PENDING, "queued")
        return record

    def transition(self, idempotency_key: str, state: OutboxState, detail: str) -> None:
        self._transitions.append(
            StateTransition(
                len(self._transitions) + 1,
                idempotency_key,
                state,
                datetime.now(UTC),
                detail,
            )
        )

    def current_state(self, idempotency_key: str) -> OutboxState | None:
        states = [
            transition.state
            for transition in self._transitions
            if transition.idempotency_key == idempotency_key
        ]
        return states[-1] if states else None

    def pending_batch(self) -> list[OutboxRecord]:
        """Return the newest event per key when that key is currently pending."""

        latest: dict[str, OutboxRecord] = {}
        for record in self._records:
            latest[record.idempotency_key] = record
        return [
            latest[key]
            for key in sorted(latest)
            if self.current_state(key) == OutboxState.PENDING
        ]

    def transitions(self) -> tuple[StateTransition, ...]:
        return tuple(self._transitions)
