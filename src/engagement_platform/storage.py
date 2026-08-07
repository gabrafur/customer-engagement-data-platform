"""Idempotent local storage plus an optional Delta Lake adapter."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from engagement_platform.models import Recommendation


class InMemoryRecommendationStore:
    def __init__(self) -> None:
        self._rows: dict[str, Recommendation] = {}

    def upsert(self, recommendations: Iterable[Recommendation]) -> int:
        changed = 0
        for recommendation in recommendations:
            if recommendation.idempotency_key not in self._rows:
                self._rows[recommendation.idempotency_key] = recommendation
                changed += 1
        return changed

    def all(self) -> list[Recommendation]:
        return sorted(self._rows.values(), key=lambda item: item.idempotency_key)


def merge_recommendations_to_delta(spark: Any, dataframe: Any, table_name: str) -> None:
    """Merge a recommendation DataFrame by its deterministic idempotency key."""

    from delta.tables import DeltaTable

    if spark.catalog.tableExists(table_name):
        target = DeltaTable.forName(spark, table_name)
        (
            target.alias("target")
            .merge(dataframe.alias("source"), "target.idempotency_key = source.idempotency_key")
            .whenNotMatchedInsertAll()
            .execute()
        )
    else:
        (
            dataframe.write.format("delta")
            .option("delta.enableChangeDataFeed", "true")
            .saveAsTable(table_name)
        )
