"""
Base component implementation.

All major NetScope building blocks should inherit from this class.
"""

from __future__ import annotations

from abc import ABC
from dataclasses import asdict
from threading import RLock
from types import MappingProxyType
from typing import Any

from .config import CONFIG
from .exceptions import (
    ComponentDisposedError,
    ComponentLifecycleError,
)
from .identity import ComponentIdentity
from .lifecycle import ComponentState, validate_transition
from .logging import get_logger


class BaseComponent(ABC):
    """
    Base class for all NetScope runtime components.

    The class provides:
    - stable identity
    - lifecycle management
    - thread-safe state transitions
    - structured metadata
    - logging
    """

    __slots__ = (
        "_identity",
        "_state",
        "_metadata",
        "_lock",
        "_logger",
    )

    def __init__(
        self,
        name: str,
        *,
        namespace: str = "netscope",
        version: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        version_value = version if version is not None else "0.1.0"

        self._identity = ComponentIdentity(
            name=name,
            namespace=namespace,
            version=version_value,
        )
        self._state = ComponentState.CREATED
        self._metadata = dict(metadata or {})
        self._lock = RLock()
        self._logger = get_logger(self._identity.qualified_name)

        self._logger.debug(
            "Component created: %s",
            self._identity.qualified_name,
        )

    @property
    def identity(self) -> ComponentIdentity:
        """Return component identity."""

        return self._identity

    @property
    def name(self) -> str:
        """Return component name."""

        return self._identity.name

    @property
    def namespace(self) -> str:
        """Return component namespace."""

        return self._identity.namespace

    @property
    def version(self) -> str:
        """Return component version."""

        return self._identity.version

    @property
    def uid(self) -> str:
        """Return stable unique identifier."""

        return self._identity.uid

    @property
    def state(self) -> ComponentState:
        """Return current lifecycle state."""

        return self._state

    @property
    def logger(self):
        """Return component logger."""

        return self._logger

    @property
    def metadata(self) -> MappingProxyType[str, Any]:
        """Return read-only view of metadata."""

        return MappingProxyType(self._metadata.copy())

    @property
    def is_disposed(self) -> bool:
        """Return whether the component has been disposed."""

        return self._state is ComponentState.DISPOSED

    @property
    def is_active(self) -> bool:
        """Return whether the component is started."""

        return self._state is ComponentState.STARTED

    def initialize(self) -> BaseComponent:
        """
        Transition the component to INITIALIZED.
        """

        with self._lock:
            self._ensure_not_disposed()
            self._transition(ComponentState.INITIALIZED)
            self._safe_hook(self._on_initialize)
            return self

    def start(self) -> BaseComponent:
        """
        Transition the component to STARTED.
        """

        with self._lock:
            self._ensure_not_disposed()
            self._transition(ComponentState.STARTED)
            self._safe_hook(self._on_start)
            return self

    def stop(self) -> BaseComponent:
        """
        Transition the component to STOPPED.
        """

        with self._lock:
            self._ensure_not_disposed()
            self._transition(ComponentState.STOPPED)
            self._safe_hook(self._on_stop)
            return self

    def reset(self) -> BaseComponent:
        """
        Reset the component back to INITIALIZED.
        """

        with self._lock:
            self._ensure_not_disposed()

            if self._state is ComponentState.STARTED:
                raise ComponentLifecycleError(
                    "Cannot reset a started component. Stop it first."
                )

            self._transition(ComponentState.INITIALIZED)
            self._safe_hook(self._on_reset)
            return self

    def fail(self) -> BaseComponent:
        """
        Mark the component as failed.
        """

        with self._lock:
            if self._state is ComponentState.DISPOSED:
                raise ComponentDisposedError(
                    "Cannot mark a disposed component as failed."
                )

            self._state = ComponentState.FAILED
            self._logger.error("Component marked as failed: %s", self.name)
            return self

    def dispose(self) -> BaseComponent:
        """
        Dispose the component permanently.
        """

        with self._lock:
            if self._state is ComponentState.DISPOSED:
                return self

            self._state = ComponentState.DISPOSED
            self._safe_hook(self._on_dispose)
            self._logger.debug("Component disposed: %s", self.name)
            return self

    def configure(self, **kwargs: Any) -> None:
        """
        Update component metadata.

        Subclasses may override this method if they need typed settings.
        """

        with self._lock:
            self._ensure_not_disposed()
            self._metadata.update(kwargs)
            self._logger.debug(
                "Component configured: %s | keys=%s",
                self.name,
                sorted(kwargs.keys()),
            )

    def to_dict(self) -> dict[str, Any]:
        """Serialize the component into a dictionary."""

        return {
            "identity": asdict(self._identity),
            "state": self._state.value,
            "metadata": dict(self._metadata),
            "class": self.__class__.__name__,
        }

    def _transition(self, target: ComponentState) -> None:
        """Validate and apply a lifecycle transition."""

        try:
            validate_transition(self._state, target)
        except ValueError as exc:
            raise ComponentLifecycleError(str(exc)) from exc

        self._logger.debug(
            "Lifecycle transition: %s -> %s",
            self._state.value,
            target.value,
        )
        self._state = target

    def _ensure_not_disposed(self) -> None:
        """Raise if the component has already been disposed."""

        if self._state is ComponentState.DISPOSED:
            raise ComponentDisposedError(
                f"Component '{self.name}' has already been disposed."
            )

    def _safe_hook(self, hook: Any) -> None:
        """
        Execute a lifecycle hook and fail the component on errors.
        """

        try:
            hook()
        except Exception as exc:  # noqa: BLE001
            self._state = ComponentState.FAILED
            self._logger.exception(
                "Lifecycle hook failed for component '%s'",
                self.name,
            )
            raise ComponentLifecycleError(
                f"Lifecycle hook failed for component '{self.name}'"
            ) from exc

    def _on_initialize(self) -> None:
        """Initialization hook for subclasses."""

    def _on_start(self) -> None:
        """Start hook for subclasses."""

    def _on_stop(self) -> None:
        """Stop hook for subclasses."""

    def _on_reset(self) -> None:
        """Reset hook for subclasses."""

    def _on_dispose(self) -> None:
        """Dispose hook for subclasses."""

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"name={self.name!r}, "
            f"state={self.state.value!r}, "
            f"uid={self.uid!r})"
        )


__all__ = [
    "BaseComponent",
]