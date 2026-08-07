"""Dependency-free structured logs and counters."""

from __future__ import annotations

import json
import logging
from collections import Counter
from collections.abc import Mapping
from datetime import UTC, datetime
from typing import Any


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        context = getattr(record, "context", None)
        if isinstance(context, Mapping):
            payload["context"] = dict(context)
        return json.dumps(payload, sort_keys=True, default=str)


def configure_logging(level: str = "INFO") -> logging.Logger:
    logger = logging.getLogger("engagement_platform")
    logger.handlers.clear()
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    logger.addHandler(handler)
    logger.setLevel(level.upper())
    logger.propagate = False
    return logger


class Metrics:
    def __init__(self) -> None:
        self._values: Counter[str] = Counter()

    def increment(self, name: str, value: int = 1) -> None:
        self._values[name] += value

    def snapshot(self) -> dict[str, int]:
        return dict(sorted(self._values.items()))
