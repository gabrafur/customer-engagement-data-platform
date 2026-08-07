"""Strict configuration loading for the demonstration pipeline."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True, slots=True)
class RegionConfig:
    enabled: bool
    recommendation_limit: int


@dataclass(frozen=True, slots=True)
class DeliveryConfig:
    mode: str
    max_attempts: int
    base_delay_seconds: float


@dataclass(frozen=True, slots=True)
class ScoringConfig:
    recency: float
    frequency: float
    value: float
    engagement: float

    def validate(self) -> None:
        weights = (self.recency, self.frequency, self.value, self.engagement)
        if any(weight < 0 for weight in weights):
            raise ValueError("Scoring weights must be non-negative")
        if abs(sum(weights) - 1.0) > 1e-9:
            raise ValueError("Scoring weights must sum to 1.0")


@dataclass(frozen=True, slots=True)
class PipelineConfig:
    seed: int
    as_of_date: date
    delivery: DeliveryConfig
    regions: dict[str, RegionConfig]
    scoring: ScoringConfig

    def validate(self) -> None:
        if not self.regions:
            raise ValueError("At least one region must be configured")
        if not any(region.enabled for region in self.regions.values()):
            raise ValueError("At least one region must be enabled")
        if any(region.recommendation_limit < 1 for region in self.regions.values()):
            raise ValueError("Recommendation limits must be positive")
        if self.delivery.mode != "mock":
            raise ValueError("The portfolio configuration only permits mock delivery")
        if self.delivery.max_attempts < 1:
            raise ValueError("Delivery max_attempts must be positive")
        if self.delivery.base_delay_seconds < 0:
            raise ValueError("Delivery delay cannot be negative")
        self.scoring.validate()


def _mapping(value: object, field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{field} must be a mapping")
    return value


def load_config(path: str | Path) -> PipelineConfig:
    """Load and validate a YAML pipeline configuration."""

    raw = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    data = _mapping(raw, "configuration")
    delivery = _mapping(data.get("delivery"), "delivery")
    scoring = _mapping(data.get("scoring"), "scoring")
    regions_raw = _mapping(data.get("regions"), "regions")

    regions = {
        str(name): RegionConfig(
            enabled=bool(_mapping(value, f"regions.{name}").get("enabled")),
            recommendation_limit=int(
                _mapping(value, f"regions.{name}")["recommendation_limit"]
            ),
        )
        for name, value in regions_raw.items()
    }
    config = PipelineConfig(
        seed=int(data["seed"]),
        as_of_date=date.fromisoformat(str(data["as_of_date"])),
        delivery=DeliveryConfig(
            mode=str(delivery["mode"]),
            max_attempts=int(delivery["max_attempts"]),
            base_delay_seconds=float(delivery["base_delay_seconds"]),
        ),
        regions=regions,
        scoring=ScoringConfig(
            recency=float(scoring["recency"]),
            frequency=float(scoring["frequency"]),
            value=float(scoring["value"]),
            engagement=float(scoring["engagement"]),
        ),
    )
    config.validate()
    return config
