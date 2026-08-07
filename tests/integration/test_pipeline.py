from engagement_platform.config import PipelineConfig
from engagement_platform.delivery import MockDeliveryClient, ReliableDeliveryService
from engagement_platform.orchestration import EngagementPipeline
from engagement_platform.storage import InMemoryRecommendationStore
from engagement_platform.synthetic import generate_customers, generate_transactions


def test_pipeline_runs_end_to_end_and_replay_is_idempotent(
    pipeline_config: PipelineConfig,
) -> None:
    customers = generate_customers(20, pipeline_config.seed, pipeline_config.as_of_date)
    transactions = generate_transactions(
        customers, pipeline_config.seed, pipeline_config.as_of_date
    )
    store = InMemoryRecommendationStore()
    client = MockDeliveryClient()
    delivery = ReliableDeliveryService(client, 3, 0)
    pipeline = EngagementPipeline(pipeline_config, store=store, delivery=delivery)

    first = pipeline.run(customers, transactions)
    second = pipeline.run(customers, transactions)

    assert first.recommendations
    assert len(store.all()) == len(first.recommendations)
    assert client.calls == len(first.recommendations)
    assert second.reconciliation.accepted == len(first.recommendations)
    assert first.metrics["customers_input"] == 20
    assert first.input_quality.passed
    assert first.output_quality.passed
    assert first.metrics["quality_checks_passed"] == 9
