import pytest

from engagement_platform.dag import (
    DagRunner,
    DependencyMode,
    InvalidDagError,
    ReadinessGate,
    TaskSpec,
    TaskState,
)


def test_dag_runs_dependencies_in_topological_order() -> None:
    events: list[str] = []
    runner = DagRunner(
        [
            TaskSpec("publish", lambda: events.append("publish") or {"rows": 2}, ("prepare",)),
            TaskSpec("prepare", lambda: events.append("prepare") or {"rows": 4}),
        ]
    )

    executions = runner.run()

    assert events == ["prepare", "publish"]
    assert [execution.state for execution in executions] == [
        TaskState.SUCCESS,
        TaskState.SUCCESS,
    ]


def test_dag_skips_blocked_gate_and_all_success_dependent() -> None:
    blocked = ReadinessGate("input-ready", lambda: False, "synthetic input is unavailable")
    executions = DagRunner(
        [
            TaskSpec("prepare", lambda: {}, gates=(blocked,)),
            TaskSpec("publish", lambda: {}, ("prepare",)),
        ]
    ).run()

    assert executions[0].state == TaskState.SKIPPED
    assert executions[0].gate_results[0].detail == "synthetic input is unavailable"
    assert executions[1].state == TaskState.SKIPPED


def test_at_least_one_success_allows_recovery_path() -> None:
    def fail() -> None:
        raise RuntimeError("synthetic failure")

    executions = DagRunner(
        [
            TaskSpec("primary", fail),
            TaskSpec("fallback", lambda: {"mode": "fallback"}),
            TaskSpec(
                "finalize",
                lambda: {"done": True},
                ("primary", "fallback"),
                DependencyMode.AT_LEAST_ONE_SUCCESS,
            ),
        ]
    ).run()

    assert executions[0].state == TaskState.FAILED
    assert executions[0].error_type == "RuntimeError"
    assert executions[2].state == TaskState.SUCCESS


@pytest.mark.parametrize(
    "tasks, message",
    [
        ([TaskSpec("same", lambda: {}), TaskSpec("same", lambda: {})], "unique"),
        ([TaskSpec("a", lambda: {}, ("missing",))], "unknown dependencies"),
        (
            [TaskSpec("a", lambda: {}, ("b",)), TaskSpec("b", lambda: {}, ("a",))],
            "cycle",
        ),
    ],
)
def test_invalid_dag_is_rejected(tasks: list[TaskSpec], message: str) -> None:
    with pytest.raises(InvalidDagError, match=message):
        DagRunner(tasks)
