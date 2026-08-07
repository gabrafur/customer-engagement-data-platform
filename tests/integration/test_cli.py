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
