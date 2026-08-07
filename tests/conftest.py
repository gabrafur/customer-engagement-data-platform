from datetime import date

import pytest

from engagement_platform.config import (
    DeliveryConfig,
    PipelineConfig,
    RegionConfig,
    ScoringConfig,
)


@pytest.fixture
def pipeline_config() -> PipelineConfig:
    return PipelineConfig(
        seed=7,
        as_of_date=date(2026, 8, 1),
        delivery=DeliveryConfig(mode="mock", max_attempts=3, base_delay_seconds=0),
        regions={
            "north": RegionConfig(enabled=True, recommendation_limit=2),
            "south": RegionConfig(enabled=True, recommendation_limit=2),
        },
        scoring=ScoringConfig(recency=0.3, frequency=0.25, value=0.2, engagement=0.25),
    )
