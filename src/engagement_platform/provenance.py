"""Deterministic run identity and record-level provenance stamping."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import UTC, date, datetime
from typing import Any
from uuid import NAMESPACE_URL, uuid5


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)


@dataclass(frozen=True, slots=True)
class RunContext:
    run_id: str
    pipeline_name: str
    source_version: str
    as_of_date: date
    parameters: dict[str, Any]
    started_at: datetime

    @classmethod
    def create(
        cls,
        pipeline_name: str,
        source_version: str,
        as_of_date: date,
        parameters: dict[str, Any],
    ) -> RunContext:
        identity = _canonical_json(
            {
                "pipeline_name": pipeline_name,
                "source_version": source_version,
                "as_of_date": as_of_date.isoformat(),
                "parameters": parameters,
            }
        )
        return cls(
            run_id=str(uuid5(NAMESPACE_URL, identity)),
            pipeline_name=pipeline_name,
            source_version=source_version,
            as_of_date=as_of_date,
            parameters=dict(parameters),
            started_at=datetime.now(UTC),
        )

    def stamp(self, record: dict[str, Any]) -> dict[str, Any]:
        return {
            **record,
            "_run_id": self.run_id,
            "_source_version": self.source_version,
            "_as_of_date": self.as_of_date.isoformat(),
            "_processed_at": self.started_at.isoformat(),
        }


def batch_fingerprint(records: list[dict[str, Any]]) -> str:
    """Create an order-independent SHA-256 fingerprint for a batch."""

    canonical_records = sorted(_canonical_json(record) for record in records)
    material = "\n".join(canonical_records).encode()
    return hashlib.sha256(material).hexdigest()
