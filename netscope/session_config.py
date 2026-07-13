"""
Session configuration models.

SessionConfig defines high-level runtime preferences for a diagnostic session.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True, frozen=True)
class SessionConfig:
    """
    Configuration for a NetScope session.
    """

    autostart: bool = False
    keep_workspace_temp: bool = False
    workspace_cache_max_size: int = 1024
    workspace_cache_ttl_seconds: float | None = None
    session_id_prefix: str = "sess"
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.workspace_cache_max_size <= 0:
            raise ValueError("workspace_cache_max_size must be greater than zero.")
        if self.workspace_cache_ttl_seconds is not None and self.workspace_cache_ttl_seconds <= 0:
            raise ValueError("workspace_cache_ttl_seconds must be greater than zero.")
        if not self.session_id_prefix.strip():
            raise ValueError("session_id_prefix cannot be empty.")


__all__ = [
    "SessionConfig",
]