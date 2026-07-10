"""
Component identity primitives.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from uuid import uuid4


@dataclass(slots=True, frozen=True)
class ComponentIdentity:
    """
    Stable identity descriptor for a component.
    """

    name: str
    namespace: str = "netscope"
    version: str = "0.1.0"
    uid: str = field(default_factory=lambda: uuid4().hex)

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("Component name cannot be empty.")
        if not self.namespace.strip():
            raise ValueError("Component namespace cannot be empty.")
        if not self.version.strip():
            raise ValueError("Component version cannot be empty.")

    @property
    def qualified_name(self) -> str:
        """Return namespace-qualified component name."""

        return f"{self.namespace}.{self.name}"