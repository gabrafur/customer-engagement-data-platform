import pytest

from engagement_platform.partitioning import build_partition_scope
from engagement_platform.retry import (
    ConcurrentMutationError,
    RetryPolicy,
    run_with_retry,
)
from engagement_platform.workflow_config import deep_merge


def test_retry_recovers_from_transient_concurrency_error() -> None:
    attempts = 0
    delays: list[float] = []

    def operation() -> str:
        nonlocal attempts
        attempts += 1
        if attempts < 3:
            raise ConcurrentMutationError("synthetic collision")
        return "written"

    result = run_with_retry(
        operation,
        RetryPolicy(max_attempts=4, initial_delay_seconds=0.1, maximum_delay_seconds=0.15),
        sleep=delays.append,
    )

    assert result == "written"
    assert delays == [0.1, 0.15]


def test_retry_does_not_hide_permanent_error() -> None:
    with pytest.raises(ValueError, match="permanent"):
        run_with_retry(lambda: (_ for _ in ()).throw(ValueError("permanent")), RetryPolicy())


def test_partition_scope_is_static_sorted_and_escaped() -> None:
    result = build_partition_scope("target", {"region": "north's", "batch_year": 2026})

    assert result == "target.batch_year = 2026 AND target.region = 'north''s'"


def test_partition_scope_rejects_unsafe_identifiers() -> None:
    with pytest.raises(ValueError, match="Invalid partition column"):
        build_partition_scope("target", {"region;drop": "north"})


def test_workflow_defaults_deep_merge_without_mutation() -> None:
    defaults = {"task": {"timeout": 60, "retry": 2}, "tags": ["demo"]}
    override = {"task": {"timeout": 120}, "tags": ["portfolio"]}

    result = deep_merge(defaults, override)

    assert result == {"task": {"timeout": 120, "retry": 2}, "tags": ["portfolio"]}
    assert defaults["task"]["timeout"] == 60
