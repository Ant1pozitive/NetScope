"""
Component lifecycle definitions and transition rules.
"""

from __future__ import annotations

from enum import Enum


class ComponentState(str, Enum):
    """Lifecycle states for NetScope components."""

    CREATED = "created"
    INITIALIZED = "initialized"
    STARTED = "started"
    STOPPED = "stopped"
    FAILED = "failed"
    DISPOSED = "disposed"


_ALLOWED_TRANSITIONS: dict[ComponentState, set[ComponentState]] = {
    ComponentState.CREATED: {
        ComponentState.INITIALIZED,
        ComponentState.DISPOSED,
        ComponentState.FAILED,
    },
    ComponentState.INITIALIZED: {
        ComponentState.STARTED,
        ComponentState.STOPPED,
        ComponentState.DISPOSED,
        ComponentState.FAILED,
    },
    ComponentState.STARTED: {
        ComponentState.STOPPED,
        ComponentState.FAILED,
        ComponentState.DISPOSED,
    },
    ComponentState.STOPPED: {
        ComponentState.INITIALIZED,
        ComponentState.STARTED,
        ComponentState.DISPOSED,
        ComponentState.FAILED,
    },
    ComponentState.FAILED: {
        ComponentState.INITIALIZED,
        ComponentState.DISPOSED,
    },
    ComponentState.DISPOSED: set(),
}


def can_transition(
    current: ComponentState,
    target: ComponentState,
) -> bool:
    """Return whether a lifecycle transition is valid."""

    return target in _ALLOWED_TRANSITIONS[current]


def validate_transition(
    current: ComponentState,
    target: ComponentState,
) -> None:
    """Raise a ValueError if the transition is invalid."""

    if not can_transition(current, target):
        raise ValueError(
            f"Invalid lifecycle transition: {current.value} -> {target.value}"
        )


__all__ = [
    "ComponentState",
    "can_transition",
    "validate_transition",
]