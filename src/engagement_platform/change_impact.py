"""Resolve a minimal public CI matrix from changed repository paths."""

from __future__ import annotations

import fnmatch
import tomllib
from dataclasses import dataclass
from pathlib import Path, PurePosixPath


@dataclass(frozen=True, slots=True)
class ModuleSpec:
    module_id: str
    version: str
    path_patterns: tuple[str, ...]
    checks: tuple[str, ...]

    def matches(self, path: str) -> bool:
        normalized = PurePosixPath(path.replace("\\", "/")).as_posix().lstrip("./")
        return any(fnmatch.fnmatchcase(normalized, pattern) for pattern in self.path_patterns)


@dataclass(frozen=True, slots=True)
class ImpactResolution:
    modules: tuple[ModuleSpec, ...]
    checks: tuple[str, ...]
    unmatched_paths: tuple[str, ...]

    def matrix(self) -> list[dict[str, str]]:
        return [
            {"module": module.module_id, "version": module.version, "check": check}
            for module in self.modules
            for check in module.checks
        ]


def load_module_registry(path: str | Path) -> tuple[ModuleSpec, ...]:
    with Path(path).open("rb") as stream:
        raw = tomllib.load(stream)
    modules = raw.get("modules")
    if not isinstance(modules, list) or not modules:
        raise ValueError("Module registry must contain at least one [[modules]] entry")
    specs = tuple(
        ModuleSpec(
            module_id=str(module["id"]),
            version=str(module["version"]),
            path_patterns=tuple(str(value) for value in module["paths"]),
            checks=tuple(str(value) for value in module["checks"]),
        )
        for module in modules
    )
    if len({module.module_id for module in specs}) != len(specs):
        raise ValueError("Module identifiers must be unique")
    return specs


def resolve_change_impact(
    changed_paths: list[str], registry: tuple[ModuleSpec, ...]
) -> ImpactResolution:
    matched_modules: list[ModuleSpec] = []
    unmatched: list[str] = []
    for path in changed_paths:
        matches = [module for module in registry if module.matches(path)]
        if not matches:
            unmatched.append(path)
        for module in matches:
            if module not in matched_modules:
                matched_modules.append(module)
    checks = tuple(sorted({check for module in matched_modules for check in module.checks}))
    return ImpactResolution(tuple(matched_modules), checks, tuple(sorted(unmatched)))


def format_artifact_tag(module: ModuleSpec, build_id: str) -> str:
    if not build_id or any(character.isspace() for character in build_id):
        raise ValueError("build_id must be non-empty and contain no whitespace")
    return f"{module.module_id}@v{module.version}+build.{build_id}"
