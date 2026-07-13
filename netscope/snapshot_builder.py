"""
Snapshot builder.

The builder converts a session, an inspection result, and optional runtime
objects into the immutable Snapshot data model.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .context import ExecutionContext
from .environment import Environment
from .exceptions import SnapshotBuildError
from .inspection_result import InspectionResult
from .resources import Workspace
from .session import Session
from .snapshot import Snapshot
from .snapshot_artifact import SnapshotArtifact
from .snapshot_builder_config import SnapshotBuilderConfig
from .snapshot_metadata import SnapshotMetadata
from .snapshot_summary import SnapshotSummary
from .state import RuntimeState


class SnapshotBuilder:
    """
    Build immutable snapshots from sessions or inspection results.
    """

    def __init__(
        self,
        config: SnapshotBuilderConfig | None = None,
        *,
        workspace: Workspace | None = None,
    ) -> None:
        self._config = config or SnapshotBuilderConfig()
        self._workspace = workspace

    @property
    def config(self) -> SnapshotBuilderConfig:
        """Return the snapshot builder configuration."""

        return self._config

    def from_session(
        self,
        session: Session,
        *,
        target: Any | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Snapshot:
        """
        Build a snapshot directly from a live session.
        """

        return self.build(
            session=session,
            target=target,
            metadata=metadata,
        )

    def from_result(
        self,
        result: InspectionResult,
        *,
        session: Session | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Snapshot:
        """
        Build a snapshot from an inspection result.
        """

        return self.build(
            result=result,
            session=session,
            metadata=metadata,
        )

    def build(
        self,
        *,
        session: Session | None = None,
        result: InspectionResult | None = None,
        target: Any | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Snapshot:
        """
        Build a snapshot from the provided inputs.

        At least one of `session`, `result`, or `target` must be provided.
        """

        if session is None and result is None and target is None:
            raise SnapshotBuildError(
                "At least one of session, result, or target must be provided."
            )

        session_payload = self._session_payload(session=session, result=result)
        context_payload = self._context_payload(session=session, session_payload=session_payload)
        environment_payload = self._environment_payload(
            session=session,
            session_payload=session_payload,
            result=result,
        )
        runtime_payload = self._runtime_payload(
            session=session,
            session_payload=session_payload,
        )
        target_payload = self._target_payload(
            target=target,
            result=result,
            session_payload=session_payload,
        )
        merged_metadata = self._merged_metadata(result=result, metadata=metadata)
        artifacts = self._collect_artifacts(session=session, session_payload=session_payload)
        diagnostics = self._build_diagnostics(
            session=session,
            session_payload=session_payload,
            result=result,
            target_payload=target_payload,
            artifacts=artifacts,
        )

        snapshot_metadata = self._build_metadata(
            session=session,
            result=result,
            target_payload=target_payload,
            merged_metadata=merged_metadata,
        )
        summary = self._build_summary(
            session=session,
            session_payload=session_payload,
            target_payload=target_payload,
            merged_metadata=merged_metadata,
        )

        snapshot = Snapshot(
            metadata=snapshot_metadata,
            summary=summary,
            artifacts=artifacts,
            context=context_payload if self._config.include_context else {},
            environment=environment_payload if self._config.include_environment else {},
            session=session_payload if self._config.include_session else {},
            runtime_state=runtime_payload if self._config.include_runtime_state else {},
            target=target_payload if self._config.include_target else {},
            diagnostics=diagnostics if self._config.include_diagnostics else {},
        )

        return snapshot

    def _build_metadata(
        self,
        *,
        session: Session | None,
        result: InspectionResult | None,
        target_payload: dict[str, Any],
        merged_metadata: dict[str, Any],
    ) -> SnapshotMetadata:
        """
        Build snapshot metadata.
        """

        session_id = ""
        session_state = ""
        target_type = ""
        target_name = ""
        inspector_name = "inspector"
        created_at = datetime.now(timezone.utc)
        completed_at = None
        snapshot_id = result.inspection_id if result is not None else None

        if result is not None:
            inspector_name = result.inspector_name or inspector_name
            session_id = result.session_id
            session_state = result.session_state
            target_type = result.target_type
            target_name = self._as_string(result.target.get("name"))
            created_at = result.started_at
            completed_at = result.finished_at if self._config.auto_complete_metadata else None
            if not merged_metadata and result.metadata:
                merged_metadata = dict(result.metadata)

        if session is not None:
            session_id = session.session_id or session_id
            session_state = session.session_state.value
            inspector_name = merged_metadata.get("inspector_name", inspector_name)
            if not target_name:
                target_name = self._as_string(target_payload.get("name"))
            if not target_type:
                target_type = self._as_string(target_payload.get("type"))

        if not target_name:
            target_name = self._as_string(target_payload.get("name"))

        if not target_type:
            target_type = self._as_string(target_payload.get("type"))

        metadata = SnapshotMetadata(
            snapshot_id=snapshot_id or self._generate_snapshot_id(),
            inspector_name=inspector_name,
            session_id=session_id,
            session_state=session_state,
            target_type=target_type,
            target_name=target_name,
            created_at=created_at,
            completed_at=completed_at
            if completed_at is not None
            else (
                datetime.now(timezone.utc)
                if self._config.auto_complete_metadata
                else None
            ),
            version=self._config.snapshot_version,
            tags=merged_metadata,
        )
        return metadata

    def _build_summary(
        self,
        *,
        session: Session | None,
        session_payload: dict[str, Any],
        target_payload: dict[str, Any],
        merged_metadata: dict[str, Any],
    ) -> SnapshotSummary:
        """
        Build the compact snapshot summary.
        """

        session_identity = session_payload.get("identity")
        session_name = ""
        if isinstance(session_identity, dict):
            session_name = self._as_string(session_identity.get("name"))

        model_name = self._as_string(target_payload.get("name")) or session_name
        model_type = self._as_string(target_payload.get("type")) or self._as_string(
            merged_metadata.get("target_type")
        )
        if not model_name:
            model_name = self._as_string(merged_metadata.get("model_name")) or session_name
        if not model_type:
            model_type = self._as_string(merged_metadata.get("model_type")) or "unknown"

        num_parameters = self._optional_int(
            merged_metadata.get("num_parameters"),
        )
        trainable_parameters = self._optional_int(
            merged_metadata.get("trainable_parameters"),
        )
        num_buffers = self._optional_int(
            merged_metadata.get("num_buffers"),
        )
        num_layers = self._optional_int(
            merged_metadata.get("num_layers"),
        )
        trainable_ratio = self._optional_float(
            merged_metadata.get("trainable_ratio"),
        )

        notes = self._as_string(
            merged_metadata.get("notes")
            or merged_metadata.get("summary")
            or ""
        )

        summary = SnapshotSummary(
            model_name=model_name,
            model_type=model_type,
            framework=self._config.framework,
            num_parameters=num_parameters,
            trainable_parameters=trainable_parameters,
            num_buffers=num_buffers,
            num_layers=num_layers,
            trainable_ratio=trainable_ratio,
            notes=notes,
            metadata=dict(merged_metadata),
        )
        return summary

    def _collect_artifacts(
        self,
        *,
        session: Session | None,
        session_payload: dict[str, Any],
    ) -> tuple[SnapshotArtifact, ...]:
        """
        Collect artifact descriptors from the session or session payload.
        """

        if not self._config.include_artifacts:
            return ()

        artifacts: list[SnapshotArtifact] = []

        if session is not None:
            artifact_snapshot = session.workspace.artifact_snapshot()
            for name, path in artifact_snapshot.items():
                artifacts.append(
                    SnapshotArtifact(
                        name=name,
                        path=Path(path),
                        kind="file",
                    )
                )
            return tuple(artifacts)

        workspace_payload = session_payload.get("workspace")
        if isinstance(workspace_payload, dict):
            artifact_manager = workspace_payload.get("artifact_manager")
            if isinstance(artifact_manager, dict):
                for name, path in artifact_manager.items():
                    artifacts.append(
                        SnapshotArtifact(
                            name=str(name),
                            path=Path(str(path)),
                            kind="file",
                        )
                    )

        return tuple(artifacts)

    def _build_diagnostics(
        self,
        *,
        session: Session | None,
        session_payload: dict[str, Any],
        result: InspectionResult | None,
        target_payload: dict[str, Any],
        artifacts: tuple[SnapshotArtifact, ...],
    ) -> dict[str, Any]:
        """
        Build the diagnostics section.
        """

        diagnostics: dict[str, Any] = {
            "builder": {
                "framework": self._config.framework,
                "snapshot_version": self._config.snapshot_version,
                "include_session": self._config.include_session,
                "include_context": self._config.include_context,
                "include_environment": self._config.include_environment,
                "include_runtime_state": self._config.include_runtime_state,
                "include_workspace": self._config.include_workspace,
                "include_artifacts": self._config.include_artifacts,
                "include_target": self._config.include_target,
            }
        }

        if result is not None:
            diagnostics["inspection"] = {
                "inspection_id": result.inspection_id,
                "status": result.status,
                "success": result.success,
                "duration_seconds": result.duration_seconds,
                "error": result.error,
            }

        if self._config.include_workspace:
            if session is not None:
                diagnostics["workspace"] = {
                    "resolver": session.workspace.resolver.to_dict(),
                    "cache": session.workspace.cache.stats(),
                    "artifacts": session.workspace.artifact_snapshot(),
                    "tempdir": (
                        None
                        if session.workspace.tempdir is None
                        else session.workspace.tempdir.to_dict()
                    ),
                }
            else:
                workspace_payload = session_payload.get("workspace")
                if isinstance(workspace_payload, dict):
                    diagnostics["workspace"] = dict(workspace_payload)

        diagnostics["target"] = dict(target_payload)
        diagnostics["artifacts"] = [artifact.to_dict() for artifact in artifacts]
        return diagnostics

    def _session_payload(
        self,
        *,
        session: Session | None,
        result: InspectionResult | None,
    ) -> dict[str, Any]:
        """
        Resolve the session payload.
        """

        if session is not None:
            return session.to_dict()

        if result is not None:
            return dict(result.session)

        return {}

    def _context_payload(
        self,
        *,
        session: Session | None,
        session_payload: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Resolve the execution context payload.
        """

        if not self._config.include_context:
            return {}

        if session is not None and session.context is not None:
            return session.context.to_dict()

        context_payload = session_payload.get("context")
        return dict(context_payload) if isinstance(context_payload, dict) else {}

    def _environment_payload(
        self,
        *,
        session: Session | None,
        session_payload: dict[str, Any],
        result: InspectionResult | None,
    ) -> dict[str, Any]:
        """
        Resolve the environment payload.
        """

        if not self._config.include_environment:
            return {}

        if session is not None:
            return session.environment.to_dict()

        if result is not None:
            environment_payload = result.environment
            if isinstance(environment_payload, dict):
                return dict(environment_payload)

        environment_payload = session_payload.get("environment")
        return dict(environment_payload) if isinstance(environment_payload, dict) else {}

    def _runtime_payload(
        self,
        *,
        session: Session | None,
        session_payload: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Resolve the runtime-state payload.
        """

        if not self._config.include_runtime_state:
            return {}

        if session is not None:
            return session.runtime_state.to_dict()

        runtime_payload = session_payload.get("runtime_state")
        return dict(runtime_payload) if isinstance(runtime_payload, dict) else {}

    def _target_payload(
        self,
        *,
        target: Any | None,
        result: InspectionResult | None,
        session_payload: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Resolve the target payload.
        """

        if result is not None:
            target_payload = result.target
            if isinstance(target_payload, dict):
                return dict(target_payload)

        if target is not None:
            return self._summarize_target(target)

        target_payload = session_payload.get("target")
        return dict(target_payload) if isinstance(target_payload, dict) else {}

    def _merged_metadata(
        self,
        *,
        result: InspectionResult | None,
        metadata: dict[str, Any] | None,
    ) -> dict[str, Any]:
        """
        Merge builder, inspection, and user metadata.
        """

        merged = dict(self._config.metadata)

        if result is not None and result.metadata:
            merged.update(result.metadata)

        if metadata is not None:
            merged.update(metadata)

        return merged

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

    @staticmethod
    def _as_string(value: Any) -> str:
        """
        Coerce a value into a stripped string.
        """

        if not isinstance(value, str):
            return ""
        return value.strip()

    @staticmethod
    def _optional_int(value: Any) -> int | None:
        """
        Coerce a value into an integer when possible.
        """

        if value is None:
            return None
        try:
            return int(value)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _optional_float(value: Any) -> float | None:
        """
        Coerce a value into a float when possible.
        """

        if value is None:
            return None
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _generate_snapshot_id() -> str:
        """
        Generate a stable snapshot identifier.
        """

        from uuid import uuid4

        return uuid4().hex


__all__ = [
    "SnapshotBuilder",
]