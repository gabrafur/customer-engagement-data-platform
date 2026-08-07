from pathlib import Path

import pytest

from engagement_platform.config import PipelineConfig, ScoringConfig, load_config


def test_load_config_from_public_example() -> None:
    config = load_config(Path("configs/development.yml"))

    assert config.seed == 20260807
    assert config.regions["north"].recommendation_limit == 10


def test_scoring_weights_must_sum_to_one() -> None:
    scoring = ScoringConfig(recency=0.4, frequency=0.4, value=0.4, engagement=0.4)

    with pytest.raises(ValueError, match="sum to 1.0"):
        scoring.validate()


def test_pipeline_rejects_non_mock_delivery(pipeline_config: PipelineConfig) -> None:
    invalid = PipelineConfig(
        seed=pipeline_config.seed,
        as_of_date=pipeline_config.as_of_date,
        delivery=type(pipeline_config.delivery)("http", 2, 0),
        regions=pipeline_config.regions,
        scoring=pipeline_config.scoring,
    )

    with pytest.raises(ValueError, match="only permits mock"):
        invalid.validate()


def test_pipeline_validates_regions_and_attempts(pipeline_config: PipelineConfig) -> None:
    no_regions = PipelineConfig(
        pipeline_config.seed,
        pipeline_config.as_of_date,
        pipeline_config.delivery,
        {},
        pipeline_config.scoring,
    )
    bad_attempts = PipelineConfig(
        pipeline_config.seed,
        pipeline_config.as_of_date,
        type(pipeline_config.delivery)("mock", 0, 0),
        pipeline_config.regions,
        pipeline_config.scoring,
    )

    with pytest.raises(ValueError, match="At least one region"):
        no_regions.validate()
    with pytest.raises(ValueError, match="max_attempts"):
        bad_attempts.validate()


def test_load_config_requires_mappings(tmp_path: Path) -> None:
    path = tmp_path / "invalid.yml"
    path.write_text("- not\n- a\n- mapping\n", encoding="utf-8")

    with pytest.raises(ValueError, match="configuration must be a mapping"):
        load_config(path)
