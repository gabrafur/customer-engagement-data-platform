"""Generic bounded retry behavior for transient storage mutations."""

from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import dataclass
from typing import TypeVar

T = TypeVar("T")


class ConcurrentMutationError(RuntimeError):
    """Represents a retryable optimistic-concurrency conflict."""


class MetadataRefreshError(RuntimeError):
    """Represents a retryable table-metadata change."""


@dataclass(frozen=True, slots=True)
class RetryPolicy:
    max_attempts: int = 4
    initial_delay_seconds: float = 0.1
    multiplier: float = 2.0
    maximum_delay_seconds: float = 2.0

    def validate(self) -> None:
        if self.max_attempts < 1:
            raise ValueError("max_attempts must be positive")
        if self.initial_delay_seconds < 0 or self.maximum_delay_seconds < 0:
            raise ValueError("retry delays cannot be negative")
        if self.multiplier < 1:
            raise ValueError("retry multiplier must be at least one")


def is_retryable_mutation_error(error: Exception) -> bool:
    return isinstance(error, (ConcurrentMutationError, MetadataRefreshError))


def run_with_retry(
    operation: Callable[[], T],
    policy: RetryPolicy,
    *,
    should_retry: Callable[[Exception], bool] = is_retryable_mutation_error,
    sleep: Callable[[float], None] = time.sleep,
) -> T:
    policy.validate()
    delay = policy.initial_delay_seconds
    for attempt in range(1, policy.max_attempts + 1):
        try:
            return operation()
        except Exception as error:
            if attempt == policy.max_attempts or not should_retry(error):
                raise
            sleep(delay)
            delay = min(delay * policy.multiplier, policy.maximum_delay_seconds)
    raise AssertionError("unreachable retry state")
