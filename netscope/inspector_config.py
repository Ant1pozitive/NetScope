"""
Inspector configuration models.

The inspector facade is intentionally configurable through a compact,
immutable dataclass.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .session_config import SessionConfig


@dataclass(slots=True, frozen=True)
class InspectorConfig:
    """
    Configuration for the inspector facade.
    """

    session_name: str = "inspection"
    auto_prepare: bool = True
    auto_start: bool = True
    auto_stop: bool = True
    auto_close_session: bool = True
    capture_target_summary: bool = True
    metadata: dict[str, object] = field(default_factory=dict)
    session_config: SessionConfig = field(default_factory=SessionConfig)

    def __post_init__(self) -> None:
        if not self.session_name.strip():
            raise ValueError("session_name cannot be empty.")


__all__ = [
    "InspectorConfig",
]