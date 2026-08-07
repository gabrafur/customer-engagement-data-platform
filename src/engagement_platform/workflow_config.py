"""Recursive defaults used by public workflow configuration examples."""

from __future__ import annotations

from collections.abc import Mapping
from copy import deepcopy
from typing import Any


def deep_merge(defaults: Mapping[str, Any], override: Mapping[str, Any]) -> dict[str, Any]:
    """Merge nested mappings while replacing scalar and list values."""

    merged = deepcopy(dict(defaults))
    for key, value in override.items():
        current = merged.get(key)
        if isinstance(current, Mapping) and isinstance(value, Mapping):
            merged[key] = deep_merge(current, value)
        else:
            merged[key] = deepcopy(value)
    return merged
