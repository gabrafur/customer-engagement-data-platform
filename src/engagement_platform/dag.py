"""Dependency-aware local orchestration with explicit readiness gates."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from enum import StrEnum
from typing import Any


class DependencyMode(StrEnum):
    ALL_SUCCESS = "ALL_SUCCESS"
    AT_LEAST_ONE_SUCCESS = "AT_LEAST_ONE_SUCCESS"


class TaskState(StrEnum):
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"


@dataclass(frozen=True, slots=True)
class GateResult:
    name: str
    ready: bool
    detail: str


@dataclass(frozen=True, slots=True)
class ReadinessGate:
    name: str
    check: Callable[[], bool]
    blocked_detail: str

    def evaluate(self) -> GateResult:
        ready = self.check()
        return GateResult(self.name, ready, "ready" if ready else self.blocked_detail)


@dataclass(frozen=True, slots=True)
class TaskSpec:
    name: str
    operation: Callable[[], Mapping[str, Any] | None]
    dependencies: tuple[str, ...] = ()
    dependency_mode: DependencyMode = DependencyMode.ALL_SUCCESS
    gates: tuple[ReadinessGate, ...] = ()


@dataclass(frozen=True, slots=True)
class TaskExecution:
    task_name: str
    state: TaskState
    output: Mapping[str, Any]
    gate_results: tuple[GateResult, ...]
    error_type: str | None = None


class InvalidDagError(ValueError):
    """Raised when task dependencies do not form a valid DAG."""


class DagRunner:
    def __init__(self, tasks: list[TaskSpec]) -> None:
        self._tasks = {task.name: task for task in tasks}
        if len(self._tasks) != len(tasks):
            raise InvalidDagError("Task names must be unique")
        self._order = self._topological_order()

    def _topological_order(self) -> tuple[str, ...]:
        for task in self._tasks.values():
            unknown = set(task.dependencies) - self._tasks.keys()
            if unknown:
                raise InvalidDagError(
                    f"Task {task.name} has unknown dependencies: {sorted(unknown)}"
                )

        temporary: set[str] = set()
        permanent: set[str] = set()
        order: list[str] = []

        def visit(name: str) -> None:
            if name in permanent:
                return
            if name in temporary:
                raise InvalidDagError("Dependency cycle detected")
            temporary.add(name)
            for dependency in self._tasks[name].dependencies:
                visit(dependency)
            temporary.remove(name)
            permanent.add(name)
            order.append(name)

        for name in self._tasks:
            visit(name)
        return tuple(order)

    @staticmethod
    def _dependencies_satisfied(task: TaskSpec, states: Mapping[str, TaskState]) -> bool:
        if not task.dependencies:
            return True
        dependency_states = [states[name] for name in task.dependencies]
        if task.dependency_mode == DependencyMode.ALL_SUCCESS:
            return all(state == TaskState.SUCCESS for state in dependency_states)
        return any(state == TaskState.SUCCESS for state in dependency_states)

    def run(self) -> tuple[TaskExecution, ...]:
        executions: list[TaskExecution] = []
        states: dict[str, TaskState] = {}
        for name in self._order:
            task = self._tasks[name]
            gate_results = tuple(gate.evaluate() for gate in task.gates)
            dependencies_ready = self._dependencies_satisfied(task, states)
            gates_ready = all(result.ready for result in gate_results)
            if not dependencies_ready or not gates_ready:
                execution = TaskExecution(name, TaskState.SKIPPED, {}, gate_results)
            else:
                try:
                    output = dict(task.operation() or {})
                    execution = TaskExecution(name, TaskState.SUCCESS, output, gate_results)
                except Exception as error:
                    execution = TaskExecution(
                        name,
                        TaskState.FAILED,
                        {},
                        gate_results,
                        type(error).__name__,
                    )
            states[name] = execution.state
            executions.append(execution)
        return tuple(executions)
