from datetime import date

import pytest

from engagement_platform.benchmark import benchmark_operation
from engagement_platform.provenance import RunContext, batch_fingerprint


def test_run_context_is_deterministic_and_does_not_mutate_record() -> None:
    first = RunContext.create("demo", "0.1.0", date(2026, 8, 1), {"region": "north"})
    second = RunContext.create("demo", "0.1.0", date(2026, 8, 1), {"region": "north"})
    record = {"customer_id": "c1"}

    stamped = first.stamp(record)

    assert first.run_id == second.run_id
    assert record == {"customer_id": "c1"}
    assert stamped["_run_id"] == first.run_id
    assert stamped["_source_version"] == "0.1.0"


def test_batch_fingerprint_is_order_independent() -> None:
    first = [{"id": 1, "value": "a"}, {"id": 2, "value": "b"}]
    second = list(reversed(first))

    assert batch_fingerprint(first) == batch_fingerprint(second)


def test_benchmark_uses_injected_clock() -> None:
    ticks = iter([10.0, 10.5])
    output, result = benchmark_operation(
        "demo", 100, lambda: [1, 2], len, clock=lambda: next(ticks)
    )

    assert output == [1, 2]
    assert result.elapsed_seconds == 0.5
    assert result.records_per_second == 200.0
    assert result.output_records == 2


def test_benchmark_rejects_negative_input() -> None:
    with pytest.raises(ValueError, match="cannot be negative"):
        benchmark_operation("demo", -1, list, len)
