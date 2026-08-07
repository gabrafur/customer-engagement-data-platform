"""Synthetic customer engagement data platform."""

from engagement_platform.config import PipelineConfig, load_config
from engagement_platform.orchestration import EngagementPipeline, PipelineResult

__all__ = ["EngagementPipeline", "PipelineConfig", "PipelineResult", "load_config"]
