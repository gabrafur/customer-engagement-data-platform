import json
from pathlib import Path

import pytest

from engagement_platform.cli import main


def test_cli_generates_synthetic_csv_files(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    exit_code = main(
        [
            "generate",
            "--customers",
            "5",
            "--config",
            "configs/development.yml",
            "--output",
            str(tmp_path),
        ]
    )

    assert exit_code == 0
    assert (tmp_path / "customers.csv").exists()
    output = json.loads(capsys.readouterr().out)
    assert output["customers"] == 5


def test_cli_runs_pipeline(capsys: pytest.CaptureFixture[str]) -> None:
    exit_code = main(
        ["run", "--customers", "5", "--config", "configs/development.yml"]
    )

    assert exit_code == 0
    output = json.loads(capsys.readouterr().out)
    assert output["customers_input"] == 5


def test_cli_rebuilds_without_delivery(capsys: pytest.CaptureFixture[str]) -> None:
    exit_code = main(
        [
            "rebuild",
            "--customers",
            "5",
            "--config",
            "configs/development.yml",
            "--as-of-date",
            "2026-06-01",
        ]
    )

    assert exit_code == 0
    output = json.loads(capsys.readouterr().out)
    assert output["as_of_date"] == "2026-06-01"
    assert output["external_deliveries"] == 0


def test_cli_resolves_change_impact(capsys: pytest.CaptureFixture[str]) -> None:
    exit_code = main(
        [
            "impact",
            "--registry",
            "configs/modules.toml",
            "--changed",
            "src/engagement_platform/spark_features.py",
            "docs/architecture.md",
        ]
    )

    assert exit_code == 0
    output = json.loads(capsys.readouterr().out)
    assert output["modules"] == [
        "pipeline-core",
        "distributed-runtime",
        "documentation",
    ]
    assert output["unmatched_paths"] == []


def test_cli_benchmark_reports_runtime(capsys: pytest.CaptureFixture[str]) -> None:
    exit_code = main(
        ["benchmark", "--customers", "5", "--config", "configs/development.yml"]
    )

    assert exit_code == 0
    output = json.loads(capsys.readouterr().out)
    assert output["name"] == "synthetic-pipeline"
    assert output["input_records"] >= 5
    assert output["records_per_second"] > 0
