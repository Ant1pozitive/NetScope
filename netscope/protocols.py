"""
Shared protocols.

Higher-level modules should depend on protocols instead of
concrete implementations whenever possible.
"""

from __future__ import annotations

from typing import Any, Protocol


class Named(Protocol):

    @property
    def name(self) -> str: ...


class Serializable(Protocol):

    def to_dict(self) -> dict[str, Any]: ...


class Resettable(Protocol):

    def reset(self) -> None: ...


class Configurable(Protocol):

    def configure(self, **kwargs: Any) -> None: ...