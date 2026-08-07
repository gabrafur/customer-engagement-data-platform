from datetime import UTC, datetime

from engagement_platform.config import PipelineConfig
from engagement_platform.models import CustomerFeatures
from engagement_platform.ranking import make_recommendations
from engagement_platform.scoring import score_customer


def feature(customer_id: str, region: str, engagement: float) -> CustomerFeatures:
    return CustomerFeatures(customer_id, region, "standard", 100, 20, 4, 125.0, engagement)


def test_score_is_normalized(pipeline_config: PipelineConfig) -> None:
    low = CustomerFeatures("low", "north", "standard", 100, 365, 0, 0, -1)
    high = CustomerFeatures("high", "north", "premium", 100, 0, 99, 9999, 2)

    assert score_customer(low, pipeline_config.scoring) == 0
    assert score_customer(high, pipeline_config.scoring) == 1


def test_ranking_deduplicates_and_applies_region_limits(
    pipeline_config: PipelineConfig,
) -> None:
    features = [
        feature("c1", "north", 0.8),
        feature("c1", "north", 0.8),
        feature("c2", "north", 0.7),
        feature("c3", "north", 0.6),
        feature("c4", "unknown", 1.0),
    ]

    result = make_recommendations(
        features,
        pipeline_config.scoring,
        pipeline_config.regions,
        datetime(2026, 8, 1, tzinfo=UTC),
    )

    assert [item.customer_id for item in result] == ["c1", "c2"]
    assert [item.regional_rank for item in result] == [1, 2]
    assert len({item.idempotency_key for item in result}) == 2
