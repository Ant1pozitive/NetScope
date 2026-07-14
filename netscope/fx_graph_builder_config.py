"""
FX graph builder configuration.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True, frozen=True)
class FXGraphBuilderConfig:
    """
    Immutable configuration for the FX graph builder.
    """

    name: str = "fx_graph"
    strict: bool = True
    include_module_metadata: bool = True
    include_fx_metadata: bool = True
    include_operation_metadata: bool = True
    concrete_args: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("name cannot be empty.")


__all__ = [
    "FXGraphBuilderConfig",
]