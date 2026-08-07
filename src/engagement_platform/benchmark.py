"""Small reproducible benchmark harness for local portfolio demonstrations."""

from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import dataclass
from typing import TypeVar

T = TypeVar("T")


@dataclass(frozen=True, slots=True)
class BenchmarkResult:
    name: str
    input_records: int
    output_records: int
    elapsed_seconds: float
    records_per_second: float


def benchmark_operation(
    name: str,
    input_records: int,
    operation: Callable[[], T],
    output_size: Callable[[T], int],
    *,
    clock: Callable[[], float] = time.perf_counter,
) -> tuple[T, BenchmarkResult]:
    if input_records < 0:
        raise ValueError("input_records cannot be negative")
    started = clock()
    output = operation()
    elapsed = max(clock() - started, 1e-12)
    result = BenchmarkResult(
        name=name,
        input_records=input_records,
        output_records=output_size(output),
        elapsed_seconds=elapsed,
        records_per_second=input_records / elapsed,
    )
    return output, result
