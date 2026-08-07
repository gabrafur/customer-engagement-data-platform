"""Deterministic deduplication and regional ranking."""

from __future__ import annotations

import hashlib
from collections import defaultdict
from dataclasses import replace
from datetime import datetime

from engagement_platform.config import RegionConfig, ScoringConfig
from engagement_platform.models import CustomerFeatures, Recommendation
from engagement_platform.rules import choose_recommendation
from engagement_platform.scoring import score_customer


def _stable_key(customer_id: str, recommendation_type: str, run_date: str) -> str:
    material = f"{run_date}|{customer_id}|{recommendation_type}".encode()
    return hashlib.sha256(material).hexdigest()


def make_recommendations(
    features: list[CustomerFeatures],
    scoring: ScoringConfig,
    regions: dict[str, RegionConfig],
    created_at: datetime,
) -> list[Recommendation]:
    candidates: dict[tuple[str, str], Recommendation] = {}
    for row in features:
        region_config = regions.get(row.region)
        if region_config is None or not region_config.enabled:
            continue
        recommendation_type = choose_recommendation(row)
        key = _stable_key(row.customer_id, recommendation_type, created_at.date().isoformat())
        candidate = Recommendation(
            recommendation_id=f"rec_{key[:20]}",
            customer_id=row.customer_id,
            region=row.region,
            recommendation_type=recommendation_type,
            score=score_customer(row, scoring),
            regional_rank=0,
            idempotency_key=key,
            created_at=created_at,
        )
        dedup_key = (candidate.customer_id, candidate.recommendation_type)
        previous = candidates.get(dedup_key)
        if previous is None or candidate.score > previous.score:
            candidates[dedup_key] = candidate

    by_region: dict[str, list[Recommendation]] = defaultdict(list)
    for candidate in candidates.values():
        by_region[candidate.region].append(candidate)

    ranked: list[Recommendation] = []
    for region, items in sorted(by_region.items()):
        limit = regions[region].recommendation_limit
        ordered = sorted(items, key=lambda item: (-item.score, item.customer_id))[:limit]
        ranked.extend(replace(item, regional_rank=index) for index, item in enumerate(ordered, 1))
    return ranked
