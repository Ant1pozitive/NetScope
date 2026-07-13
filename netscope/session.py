"""
Session infrastructure.

A session binds together the execution context, runtime environment, workspace,
and runtime state for a single diagnostic run.
"""

from __future__ import annotations

from dataclasses import asdict
from typing import TYPE_CHECKING, Any, ClassVar
from uuid import uuid4

from .component import BaseComponent
from .context import ExecutionContext
from .environment import Environment, EnvironmentDetector
from .exceptions import ComponentDisposedError
from .lifecycle import ComponentState
from .resources import Workspace
from .session_config import SessionConfig
from .session_state import SessionState
from .state import GLOBAL_STATE, RuntimeState

if TYPE_CHECKING:
    from .session_manager import SessionManager


class Session(BaseComponent):
    """
    High-level execution session.

    The session acts as the unit of work for the current diagnostics flow.
    It owns the workspace and maintains the active runtime state.
    """

    component_kind: ClassVar[str] = "session"

    __slots__ = (
        "_config",
        "_session_id",
        "_session_state",
        "_environment",
        "_workspace",
        "_runtime_state",
        "_manager",
    )

    def __init__(
        self,
        name: str = "session",
        *,
        config: SessionConfig | None = None,
        context: ExecutionContext | None = None,
        environment: Environment | None = None,
        workspace: Workspace | None = None,
        runtime_state: RuntimeState | None = None,
        metadata: dict[str, Any] | None = None,
        session_id: str | None = None,
    ) -> None:
        self._config = config or SessionConfig()

        combined_metadata = dict(self._config.metadata)
        if metadata is not None:
            combined_metadata.update(metadata)

        resolved_context = context or ExecutionContext.from_config(
            metadata={"session_id": session_id or "pending"}
        )

        super().__init__(
            name=name,
            metadata=combined_metadata,
            context=resolved_context,
        )

        self._session_id = self._resolve_session_id(
            session_id=session_id,
            prefix=self._config.session_id_prefix,
        )
        self._session_state = SessionState.CREATED

        resolved_environment = environment or EnvironmentDetector.detect(
            metadata={"session_id": self._session_id}
        )

        self._environment = resolved_environment
        self._runtime_state = runtime_state or RuntimeState(
            session_id=self._session_id,
            context=resolved_context,
            environment=resolved_environment,
        )

        if workspace is None:
            self._workspace = Workspace(
                name=f"{name}-workspace",
                context=resolved_context,
                cache_max_size=self._config.workspace_cache_max_size,
                cache_ttl_seconds=self._config.workspace_cache_ttl_seconds,
                keep_temp=self._config.keep_workspace_temp,
                metadata={
                    "session_id": self._session_id,
                    "session_name": name,
                },
            )
        else:
            self._workspace = workspace
            if self._workspace.context is None:
                self._workspace.attach_context(resolved_context)

        self._manager: SessionManager | None = None

    @staticmethod
    def _resolve_session_id(*, session_id: str | None, prefix: str) -> str:
        if session_id is not None:
            normalized = session_id.strip()
            if not normalized:
                raise ValueError("session_id cannot be empty.")
            return normalized

        return f"{prefix}-{uuid4().hex}"

    @property
    def config(self) -> SessionConfig:
        """Return the session configuration."""

        return self._config

    @property
    def session_id(self) -> str:
        """Return the stable session identifier."""

        return self._session_id

    @property
    def session_state(self) -> SessionState:
        """Return the high-level session state."""

        return self._session_state

    @property
    def environment(self) -> Environment:
        """Return the detected runtime environment."""

        return self._environment

    @property
    def runtime_state(self) -> RuntimeState:
        """Return the session runtime state."""

        return self._runtime_state

    @property
    def workspace(self) -> Workspace:
        """Return the workspace bound to this session."""

        return self._workspace

    @property
    def is_running(self) -> bool:
        """Return whether the session is currently running."""

        return self._session_state is SessionState.RUNNING

    @property
    def is_closed(self) -> bool:
        """Return whether the session is closed."""

        return self._session_state is SessionState.CLOSED

    def attach_manager(self, manager: SessionManager) -> None:
        """
        Attach the session manager that owns this session.
        """

        self._manager = manager

    def prepare(self) -> Session:
        """
        Prepare the session for execution.

        This initializes the workspace and synchronizes runtime state.
        """

        with self._lock:
            self._ensure_not_disposed()

            if self.state is ComponentState.CREATED:
                super().initialize()
            elif self.state is ComponentState.STOPPED:
                super().reset()
            elif self.state is ComponentState.STARTED:
                return self

            self._session_state = SessionState.PREPARED
            self._sync_runtime_state()
            return self

    def start(self) -> Session:
        """
        Start the session.

        The session is prepared automatically if needed.
        """

        with self._lock:
            self._ensure_not_disposed()

            if self.state is ComponentState.CREATED:
                super().initialize()
            elif self.state is ComponentState.STOPPED:
                super().reset()

            if self.state is ComponentState.INITIALIZED:
                super().start()

            self._session_state = SessionState.RUNNING
            self._runtime_state.set_flag("running", True)
            self._runtime_state.set_flag("closed", False)

            if self._manager is not None:
                self._manager._mark_active(self._session_id)

            return self

    def stop(self) -> Session:
        """
        Stop the session.
        """

        with self._lock:
            self._ensure_not_disposed()

            if self.state is ComponentState.STARTED:
                super().stop()

            self._session_state = SessionState.STOPPED
            self._runtime_state.set_flag("running", False)

            if self._manager is not None:
                self._manager._unmark_active(self._session_id)

            return self

    def reset(self) -> Session:
        """
        Reset the session lifecycle to the prepared state.
        """

        with self._lock:
            self._ensure_not_disposed()

            if self.state is ComponentState.STARTED:
                raise ComponentDisposedError(
                    "Cannot reset a running session. Stop it first."
                )

            if self.state is ComponentState.CREATED:
                super().initialize()
            else:
                super().reset()

            self._session_state = SessionState.PREPARED
            self._sync_runtime_state()
            return self

    def fail(self) -> Session:
        """
        Mark the session as failed.
        """

        with self._lock:
            super().fail()
            self._session_state = SessionState.FAILED
            self._runtime_state.set_flag("running", False)
            self._runtime_state.set_flag("failed", True)
            if self._manager is not None:
                self._manager._unmark_active(self._session_id)
            return self

    def close(self) -> Session:
        """
        Close the session and release resources.

        This is an explicit alias for dispose().
        """

        return self.dispose()

    def dispose(self) -> Session:
        """
        Dispose the session and its workspace.
        """

        with self._lock:
            if self.state is ComponentState.DISPOSED:
                return self

            if self.state is ComponentState.STARTED:
                super().stop()

            super().dispose()

            self._session_state = SessionState.CLOSED
            self._runtime_state.set_flag("running", False)
            self._runtime_state.set_flag("closed", True)

            if self._manager is not None:
                self._manager._unregister(self._session_id)
                self._manager._unmark_active(self._session_id)

            return self

    def _sync_runtime_state(self) -> None:
        """Synchronize the global and session runtime states."""

        self._runtime_state.attach_context(self.context)
        self._runtime_state.attach_environment(self._environment)
        self._runtime_state.session_id = self._session_id
        self._runtime_state.set_flag("prepared", True)
        self._runtime_state.set_flag("closed", False)

        GLOBAL_STATE.attach_context(self.context)
        GLOBAL_STATE.attach_environment(self._environment)
        GLOBAL_STATE.session_id = self._session_id
        GLOBAL_STATE.set_flag("prepared", True)
        GLOBAL_STATE.set_flag("closed", False)

    def _on_initialize(self) -> None:
        """Initialize the workspace and runtime state."""

        self._workspace.attach_context(self.context)
        self._workspace.initialize()
        self._sync_runtime_state()

    def _on_start(self) -> None:
        """Start the workspace along with the session."""

        self._workspace.start()

    def _on_stop(self) -> None:
        """Stop the workspace when the session stops."""

        self._workspace.stop()

    def _on_reset(self) -> None:
        """Reset the workspace state if needed."""

        self._sync_runtime_state()

    def _on_dispose(self) -> None:
        """Dispose runtime resources."""

        self._workspace.dispose()
        self._runtime_state.set_flag("running", False)
        self._runtime_state.set_flag("closed", True)

    def to_dict(self) -> dict[str, Any]:
        """Serialize the session into a dictionary."""

        return {
            **super().to_dict(),
            "session_id": self._session_id,
            "session_state": self._session_state.value,
            "config": asdict(self._config),
            "environment": self._environment.to_dict(),
            "runtime_state": self._runtime_state.to_dict(),
            "workspace": self._workspace.to_dict(),
        }


__all__ = [
    "Session",
]