from pathlib import Path

import pytest

from engagement_platform.change_impact import (
    ModuleSpec,
    format_artifact_tag,
    load_module_registry,
    resolve_change_impact,
)


def test_registry_resolves_overlapping_modules_and_checks() -> None:
    registry = load_module_registry("configs/modules.toml")

    resolution = resolve_change_impact(
        ["src/engagement_platform/spark_features.py", "notes/unmatched.txt"], registry
    )

    assert [module.module_id for module in resolution.modules] == [
        "pipeline-core",
        "distributed-runtime",
    ]
    assert "spark-tests" in resolution.checks
    assert resolution.unmatched_paths == ("notes/unmatched.txt",)
    assert {entry["module"] for entry in resolution.matrix()} == {
        "pipeline-core",
        "distributed-runtime",
    }


def test_artifact_tag_uses_module_version() -> None:
    module = ModuleSpec("pipeline-core", "1.2.3", ("src/*.py",), ("unit-tests",))

    assert format_artifact_tag(module, "42") == "pipeline-core@v1.2.3+build.42"
    with pytest.raises(ValueError, match="no whitespace"):
        format_artifact_tag(module, "bad id")


def test_registry_requires_unique_modules(tmp_path: Path) -> None:
    path = tmp_path / "modules.toml"
    path.write_text(
        """
[[modules]]
id = "duplicate"
version = "1.0.0"
paths = ["src/*.py"]
checks = ["test"]
[[modules]]
id = "duplicate"
version = "2.0.0"
paths = ["docs/*.md"]
checks = ["docs"]
""".strip(),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="unique"):
        load_module_registry(path)
