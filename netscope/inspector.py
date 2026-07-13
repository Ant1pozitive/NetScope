"""
Inspector facade.

The inspector orchestrates the session lifecycle and produces the first
high-level inspection result. It is intentionally lightweight and designed to
be extended by later phases with snapshotting, collection, and analysis.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, ClassVar
from uuid import uuid4

from .component import BaseComponent
from .context import ExecutionContext
from .environment import Environment
from .exceptions import InspectorError
from .inspection_result import InspectionResult
from .inspector_config import InspectorConfig
from .lifecycle import ComponentState
from .resources import Workspace
from .session import Session
from .session_config import SessionConfig
from .session_manager import GLOBAL_SESSION_MANAGER, SessionManager
from .session_state import SessionState


class Inspector(BaseComponent):
    """
    High-level inspection facade.

    The inspector creates or reuses a session, prepares the execution context,
    captures target metadata, and returns an immutable inspection result.
    """

    component_kind: ClassVar[str] = "inspector"

    __slots__ = (
        "_config",
        "_session_manager",
        "_session",
        "_last_result",
        "_environment",
        "_workspace",
    )

    def __init__(
        self,
        target_name: str = "inspector",
        *,
        config: InspectorConfig | None = None,
        session_manager: SessionManager | None = None,
        session: Session | None = None,
        context: ExecutionContext | None = None,
        environment: Environment | None = None,
        workspace: Workspace | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            name=target_name,
            metadata=metadata,
            context=context,
        )

        self._config = config or InspectorConfig()
        self._session_manager = session_manager or GLOBAL_SESSION_MANAGER
        self._session = session
        self._last_result: InspectionResult | None = None
        self._environment = environment
        self._workspace = workspace

        if self._session is not None:
            self._session.attach_manager(self._session_manager)

    @property
    def config(self) -> InspectorConfig:
        """Return the inspector configuration."""

        return self._config

    @property
    def session_manager(self) -> SessionManager:
        """Return the session manager used by the inspector."""

        return self._session_manager

    @property
    def session(self) -> Session | None:
        """Return the current session, if any."""

        return self._session

    @property
    def last_result(self) -> InspectionResult | None:
        """Return the last inspection result, if available."""

        return self._last_result

    @property
    def environment(self) -> Environment | None:
        """Return the explicitly provided environment, if any."""

        return self._environment

    @property
    def workspace(self) -> Workspace | None:
        """Return the explicitly provided workspace, if any."""

        return self._workspace

    def inspect(
        self,
        target: Any,
        *,
        metadata: dict[str, Any] | None = None,
        session: Session | None = None,
    ) -> InspectionResult:
        """
        Inspect a target object and return an immutable result.
        """

        started_at = datetime.now(timezone.utc)
        merged_metadata = dict(self._config.metadata)
        if metadata is not None:
            merged_metadata.update(metadata)

        created_session = False

        if session is not None:
            working_session = session
            working_session.attach_manager(self._session_manager)
        elif self._session is not None:
            working_session = self._session
        else:
            working_session = self._create_session(
                target=target,
                metadata=merged_metadata,
            )
            created_session = True

        self._session = working_session

        try:
            if (
                self._config.auto_prepare
                and working_session.session_state is SessionState.CREATED
            ):
                working_session.prepare()

            if self._config.auto_start and not working_session.is_running:
                working_session.start()

            working_session.workspace.ensure_ready()

            target_summary = self._summarize_target(target)

            if self._config.capture_target_summary:
                working_session.workspace.cache_set(
                    "inspection.target",
                    target_summary,
                )

            if merged_metadata:
                working_session.workspace.cache_set(
                    "inspection.metadata",
                    merged_metadata,
                )

            if self._config.auto_stop and working_session.is_running:
                working_session.stop()

            if created_session and self._config.auto_close_session and not working_session.is_closed:
                working_session.close()

            finished_at = datetime.now(timezone.utc)
            result = InspectionResult(
                inspection_id=uuid4().hex,
                inspector_name=self.name,
                session=working_session.to_dict(),
                target=target_summary,
                metadata=merged_metadata,
                started_at=started_at,
                finished_at=finished_at,
                duration_seconds=(finished_at - started_at).total_seconds(),
                success=True,
                error=None,
            )
            self._last_result = result
            return result

        except Exception as exc:  # noqa: BLE001
            if not working_session.is_disposed:
                try:
                    working_session.fail()
                except Exception:  # noqa: BLE001
                    pass

            if working_session.is_running:
                try:
                    working_session.stop()
                except Exception:  # noqa: BLE001
                    pass

            if created_session and self._config.auto_close_session and not working_session.is_closed:
                try:
                    working_session.close()
                except Exception:  # noqa: BLE001
                    pass

            finished_at = datetime.now(timezone.utc)
            result = InspectionResult(
                inspection_id=uuid4().hex,
                inspector_name=self.name,
                session=working_session.to_dict(),
                target=self._summarize_target(target),
                metadata=merged_metadata,
                started_at=started_at,
                finished_at=finished_at,
                duration_seconds=(finished_at - started_at).total_seconds(),
                success=False,
                error=f"{exc.__class__.__name__}: {exc}",
            )
            self._last_result = result
            raise InspectorError("Inspection failed.") from exc

    def _create_session(
        self,
        *,
        target: Any,
        metadata: dict[str, Any],
    ) -> Session:
        """
        Create a new session for the inspection run.
        """

        session_config = self._effective_session_config()
        session_metadata = dict(metadata)
        session_metadata.setdefault("inspector_name", self.name)
        session_metadata.setdefault("target_type", type(target).__name__)

        session = self._session_manager.create(
            name=self._config.session_name,
            config=session_config,
            context=self.context,
            environment=self._environment,
            workspace=self._workspace,
            metadata=session_metadata,
            autostart=False,
        )
        return session

    def _effective_session_config(self) -> SessionConfig:
        """
        Return a session configuration with inspector-controlled autostart disabled.
        """

        config = self._config.session_config
        if config.autostart:
            return SessionConfig(
                autostart=False,
                keep_workspace_temp=config.keep_workspace_temp,
                workspace_cache_max_size=config.workspace_cache_max_size,
                workspace_cache_ttl_seconds=config.workspace_cache_ttl_seconds,
                session_id_prefix=config.session_id_prefix,
                metadata=dict(config.metadata),
            )
        return config

    @staticmethod
    def _summarize_target(target: Any) -> dict[str, Any]:
        """
        Build a lightweight, serializable target summary.
        """

        target_type = type(target)
        try:
            target_repr = repr(target)
        except Exception as exc:  # noqa: BLE001
            target_repr = f"<repr failed: {exc.__class__.__name__}>"

        if len(target_repr) > 512:
            target_repr = f"{target_repr[:509]}..."

        summary: dict[str, Any] = {
            "type": target_type.__name__,
            "module": target_type.__module__,
            "repr": target_repr,
        }

        candidate_name = getattr(target, "__name__", None)
        if not isinstance(candidate_name, str) or not candidate_name.strip():
            candidate_name = getattr(target, "name", None)

        if isinstance(candidate_name, str) and candidate_name.strip():
            summary["name"] = candidate_name.strip()

        return summary

    def _on_initialize(self) -> None:
        """Inspector initialization hook."""

    def _on_start(self) -> None:
        """Inspector start hook."""

    def _on_stop(self) -> None:
        """Inspector stop hook."""

    def _on_reset(self) -> None:
        """Inspector reset hook."""

    def _on_dispose(self) -> None:
        """Inspector dispose hook."""

        self._last_result = None

    def __call__(
        self,
        target: Any,
        *,
        metadata: dict[str, Any] | None = None,
        session: Session | None = None,
    ) -> InspectionResult:
        return self.inspect(target, metadata=metadata, session=session)

    def to_dict(self) -> dict[str, Any]:
        """Serialize the inspector state."""

        payload = super().to_dict()
        payload.update(
            {
                "config": {
                    "session_name": self._config.session_name,
                    "auto_prepare": self._config.auto_prepare,
                    "auto_start": self._config.auto_start,
                    "auto_stop": self._config.auto_stop,
                    "auto_close_session": self._config.auto_close_session,
                    "capture_target_summary": self._config.capture_target_summary,
                    "metadata": dict(self._config.metadata),
                    "session_config": {
                        "autostart": self._config.session_config.autostart,
                        "keep_workspace_temp": self._config.session_config.keep_workspace_temp,
                        "workspace_cache_max_size": self._config.session_config.workspace_cache_max_size,
                        "workspace_cache_ttl_seconds": self._config.session_config.workspace_cache_ttl_seconds,
                        "session_id_prefix": self._config.session_config.session_id_prefix,
                        "metadata": dict(self._config.session_config.metadata),
                    },
                },
                "session": None if self._session is None else self._session.to_dict(),
                "last_result": None if self._last_result is None else self._last_result.to_dict(),
            }
        )
        return payload


__all__ = [
    "Inspector",
]