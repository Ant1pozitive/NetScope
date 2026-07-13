"""
Session manager.

The session manager owns multiple sessions and tracks the active one.
"""

from __future__ import annotations

from collections.abc import Iterator
from threading import RLock
from typing import Any

from .context import ExecutionContext
from .environment import Environment
from .resources import Workspace
from .registry import Registry
from .session import Session
from .session_config import SessionConfig


class SessionManager:
    """
    Thread-safe manager for sessions.
    """

    def __init__(self) -> None:
        self._sessions: Registry[Session] = Registry()
        self._active_session_id: str | None = None
        self._lock = RLock()

    @property
    def active_session_id(self) -> str | None:
        """Return the currently active session identifier."""

        return self._active_session_id

    @property
    def active_session(self) -> Session | None:
        """Return the currently active session, if any."""

        if self._active_session_id is None:
            return None
        return self.get(self._active_session_id)

    def create(
        self,
        name: str = "session",
        *,
        config: SessionConfig | None = None,
        context: ExecutionContext | None = None,
        environment: Environment | None = None,
        workspace: Workspace | None = None,
        metadata: dict[str, Any] | None = None,
        session_id: str | None = None,
        autostart: bool | None = None,
    ) -> Session:
        """
        Create, register, and optionally start a new session.
        """

        session = Session(
            name=name,
            config=config,
            context=context,
            environment=environment,
            workspace=workspace,
            metadata=metadata,
            session_id=session_id,
        )
        session.attach_manager(self)

        with self._lock:
            self._sessions.register(session.session_id, session)

        should_autostart = (
            session.config.autostart if autostart is None else autostart
        )

        if should_autostart:
            session.start()
            self._mark_active(session.session_id)

        return session

    def register(self, session: Session, *, overwrite: bool = False) -> Session:
        """
        Register an externally created session.
        """

        session.attach_manager(self)

        with self._lock:
            self._sessions.register(session.session_id, session, overwrite=overwrite)

        return session

    def get(self, session_id: str) -> Session:
        """Return a session by identifier."""

        with self._lock:
            return self._sessions.get(session_id)

    def try_get(self, session_id: str, default: Session | None = None) -> Session | None:
        """Return a session by identifier or default."""

        with self._lock:
            return self._sessions.try_get(session_id, default)

    def contains(self, session_id: str) -> bool:
        """Return whether a session exists."""

        with self._lock:
            return self._sessions.contains(session_id)

    def list_sessions(self) -> tuple[str, ...]:
        """Return the registered session identifiers."""

        with self._lock:
            return tuple(sorted(self._sessions.keys()))

    def list(self) -> tuple[Session, ...]:
        """Return all registered sessions."""

        with self._lock:
            return tuple(self._sessions.values())

    def start(self, session_id: str) -> Session:
        """Start a session by identifier."""

        session = self.get(session_id)
        session.start()
        self._mark_active(session_id)
        return session

    def prepare(self, session_id: str) -> Session:
        """Prepare a session by identifier."""

        session = self.get(session_id)
        session.prepare()
        return session

    def stop(self, session_id: str) -> Session:
        """Stop a session by identifier."""

        session = self.get(session_id)
        session.stop()

        if self._active_session_id == session_id:
            self._active_session_id = None

        return session

    def close(self, session_id: str) -> Session:
        """Dispose and unregister a session by identifier."""

        session = self.get(session_id)
        session.close()
        return session

    def remove(self, session_id: str) -> Session:
        """Remove a session from the manager without changing its lifecycle."""

        with self._lock:
            session = self._sessions.unregister(session_id)
            if self._active_session_id == session_id:
                self._active_session_id = None
            return session

    def close_all(self) -> None:
        """Close all sessions managed by this instance."""

        for session_id in self.list_sessions():
            self.close(session_id)

    def snapshot(self) -> dict[str, dict[str, Any]]:
        """Return a snapshot of registered sessions."""

        with self._lock:
            return {
                session_id: session.to_dict()
                for session_id, session in self._sessions.items()
            }

    def clear(self) -> None:
        """Remove all sessions from the manager."""

        with self._lock:
            self._sessions.clear()
            self._active_session_id = None

    def _mark_active(self, session_id: str) -> None:
        self._active_session_id = session_id

    def _unmark_active(self, session_id: str) -> None:
        if self._active_session_id == session_id:
            self._active_session_id = None

    def _unregister(self, session_id: str) -> None:
        with self._lock:
            self._sessions.unregister(session_id)

    def __contains__(self, session_id: object) -> bool:
        return isinstance(session_id, str) and self.contains(session_id)

    def __len__(self) -> int:
        return len(self.list_sessions())

    def __iter__(self) -> Iterator[Session]:
        return iter(self.list())


GLOBAL_SESSION_MANAGER = SessionManager()

__all__ = [
    "SessionManager",
    "GLOBAL_SESSION_MANAGER",
]