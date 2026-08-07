"""A compact orchestration layer with explicit stage boundaries."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import UTC, datetime, time

from engagement_platform.config import PipelineConfig
from engagement_platform.delivery import MockDeliveryClient, ReliableDeliveryService
from engagement_platform.features import build_customer_features
from engagement_platform.models import Customer, DeliveryReceipt, Recommendation, Transaction
from engagement_platform.monitoring import Metrics
from engagement_platform.ranking import make_recommendations
from engagement_platform.reconciliation import ReconciliationSummary, reconcile
from engagement_platform.storage import InMemoryRecommendationStore


@dataclass(frozen=True, slots=True)
class PipelineResult:
    recommendations: list[Recommendation]
    receipts: list[DeliveryReceipt]
    reconciliation: ReconciliationSummary
    metrics: dict[str, int]


class EngagementPipeline:
    def __init__(
        self,
        config: PipelineConfig,
        store: InMemoryRecommendationStore | None = None,
        delivery: ReliableDeliveryService | None = None,
        metrics: Metrics | None = None,
        logger: logging.Logger | None = None,
    ) -> None:
        config.validate()
        self.config = config
        self.store = store or InMemoryRecommendationStore()
        self.delivery = delivery or ReliableDeliveryService(
            client=MockDeliveryClient(),
            max_attempts=config.delivery.max_attempts,
            base_delay_seconds=config.delivery.base_delay_seconds,
        )
        self.metrics = metrics or Metrics()
        self.logger = logger or logging.getLogger("engagement_platform")

    def run(
        self, customers: list[Customer], transactions: list[Transaction]
    ) -> PipelineResult:
        created_at = datetime.combine(self.config.as_of_date, time.min, tzinfo=UTC)
        self.metrics.increment("customers_input", len(customers))
        self.metrics.increment("transactions_input", len(transactions))

        features = build_customer_features(customers, transactions, self.config.as_of_date)
        self.metrics.increment("features_created", len(features))
        recommendations = make_recommendations(
            features, self.config.scoring, self.config.regions, created_at
        )
        self.metrics.increment("recommendations_created", len(recommendations))
        self.metrics.increment("recommendations_inserted", self.store.upsert(recommendations))

        receipts = [self.delivery.deliver(item) for item in recommendations]
        summary = reconcile(receipts)
        self.metrics.increment("deliveries_accepted", summary.accepted)
        self.metrics.increment("deliveries_retry_exhausted", summary.retry_exhausted)
        self.logger.info("pipeline_complete", extra={"context": self.metrics.snapshot()})
        return PipelineResult(recommendations, receipts, summary, self.metrics.snapshot())
