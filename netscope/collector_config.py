"""
Collector configuration.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .collector_kind import CollectorKind


@dataclass(slots=True, frozen=True)
class CollectorConfig:
    """
    Immutable configuration for collectors.
    """

    name: str = "collector"
    collector_kind: CollectorKind = CollectorKind.CUSTOM
    observation_only: bool = True
    include_context: bool = True
    include_metadata: bool = True
    strict: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("name cannot be empty.")

    def to_dict(self) -> dict[str, Any]:
        """Serialize the configuration into a JSON-friendly dictionary."""

        return {
            "name": self.name,
            "collector_kind": self.collector_kind.value,
            "observation_only": self.observation_only,
            "include_context": self.include_context,
            "include_metadata": self.include_metadata,
            "strict": self.strict,
            "metadata": dict(self.metadata),
        }


__all__ = [
    "CollectorConfig",
]