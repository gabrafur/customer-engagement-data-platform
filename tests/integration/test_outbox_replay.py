from datetime import UTC, datetime

from engagement_platform.config import PipelineConfig
from engagement_platform.models import Recommendation, RecommendationType
from engagement_platform.outbox import InMemoryOutbox, OutboxState
from engagement_platform.replay import rebuild_historical_snapshot
from engagement_platform.synthetic import generate_customers, generate_transactions


def recommendation(key: str, sequence: int) -> Recommendation:
    return Recommendation(
        f"rec-{sequence}",
        "c1",
        "north",
        RecommendationType.COMMUNITY_UPDATE,
        0.5,
        1,
        key,
        datetime(2026, 8, 1, tzinfo=UTC),
    )


def test_outbox_keeps_history_and_dispatches_latest_event_per_key() -> None:
    outbox = InMemoryOutbox()
    first = outbox.append(recommendation("key-1", 1))
    second = outbox.append(recommendation("key-1", 2))

    assert first.event_id != second.event_id
    assert outbox.pending_batch() == [second]
    outbox.transition("key-1", OutboxState.DISPATCHED, "accepted by simulator")
    assert outbox.pending_batch() == []
    assert len(outbox.transitions()) == 3


def test_historical_rebuild_is_bounded_and_has_no_delivery(
    pipeline_config: PipelineConfig,
) -> None:
    customers = generate_customers(20, pipeline_config.seed, pipeline_config.as_of_date)
    transactions = generate_transactions(
        customers, pipeline_config.seed, pipeline_config.as_of_date
    )
    earlier = pipeline_config.as_of_date.replace(month=6, day=1)

    snapshot = rebuild_historical_snapshot(
        customers, transactions, pipeline_config, earlier
    )

    assert snapshot.as_of_date == earlier
    assert snapshot.recommendations
    assert snapshot.inserted == len(snapshot.recommendations)
