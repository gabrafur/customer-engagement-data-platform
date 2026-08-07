"""Safe literal partition predicates for concurrency-aware Delta merges."""

from __future__ import annotations

import re
from collections.abc import Mapping

IDENTIFIER = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def _literal(value: str | int) -> str:
    if isinstance(value, int):
        return str(value)
    return "'" + value.replace("'", "''") + "'"


def build_partition_scope(alias: str, values: Mapping[str, str | int]) -> str:
    """Build a static target predicate so a merge declares its narrow read slice."""

    if not IDENTIFIER.fullmatch(alias):
        raise ValueError("Invalid table alias")
    if not values:
        raise ValueError("At least one partition value is required")
    predicates: list[str] = []
    for column, value in sorted(values.items()):
        if not IDENTIFIER.fullmatch(column):
            raise ValueError(f"Invalid partition column: {column}")
        predicates.append(f"{alias}.{column} = {_literal(value)}")
    return " AND ".join(predicates)
