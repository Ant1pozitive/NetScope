"""
Snapshot data model.

A snapshot is the immutable artifact that captures the state of an inspection
run. It is the main payload that later builder, collector, graph, and report
layers will enrich.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Any

from .snapshot_artifact import SnapshotArtifact
from .snapshot_metadata import SnapshotMetadata
from .snapshot_summary import SnapshotSummary


@dataclass(slots=True, frozen=True)
class Snapshot:
    """
    Immutable diagnostics snapshot.
    """

    metadata: SnapshotMetadata
    summary: SnapshotSummary = field(default_factory=SnapshotSummary)
    artifacts: tuple[SnapshotArtifact, ...] = ()
    context: dict[str, Any] = field(default_factory=dict)
    environment: dict[str, Any] = field(default_factory=dict)
    session: dict[str, Any] = field(default_factory=dict)
    runtime_state: dict[str, Any] = field(default_factory=dict)
    target: dict[str, Any] = field(default_factory=dict)
    diagnostics: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.artifacts, tuple):
            object.__setattr__(self, "artifacts", tuple(self.artifacts))

    @property
    def snapshot_id(self) -> str:
        """Return the stable snapshot identifier."""

        return self.metadata.snapshot_id

    @property
    def inspector_name(self) -> str:
        """Return the inspector name."""

        return self.metadata.inspector_name

    @property
    def session_id(self) -> str:
        """Return the associated session identifier."""

        return self.metadata.session_id

    @property
    def session_state(self) -> str:
        """Return the session state string."""

        return self.metadata.session_state

    @property
    def target_type(self) -> str:
        """Return the target type string."""

        return self.metadata.target_type or self.target.get("type", "") or ""

    @property
    def is_completed(self) -> bool:
        """Return whether the snapshot has been completed."""

        return self.metadata.is_completed

    def complete(self) -> Snapshot:
        """
        Return a copy marked as completed.
        """

        return replace(self, metadata=self.metadata.complete())

    def with_metadata(self, **kwargs: Any) -> Snapshot:
        """
        Return a copy with merged metadata tags.
        """

        return replace(self, metadata=self.metadata.with_tags(**kwargs))

    def add_artifact(self, artifact: SnapshotArtifact) -> Snapshot:
        """
        Return a copy with one additional artifact.
        """

        return replace(self, artifacts=self.artifacts + (artifact,))

    def extend_artifacts(
        self,
        artifacts: tuple[SnapshotArtifact, ...] | list[SnapshotArtifact],
    ) -> Snapshot:
        """
        Return a copy with multiple additional artifacts.
        """

        return replace(self, artifacts=self.artifacts + tuple(artifacts))

    def with_section(self, name: str, payload: Any) -> Snapshot:
        """
        Return a copy with an updated diagnostics section.

        The diagnostics map is intended for future graph, hook, and collector
        sections.
        """

        normalized = name.strip()
        if not normalized:
            raise ValueError("Section name cannot be empty.")

        sections = dict(self.diagnostics)
        sections[normalized] = payload
        return replace(self, diagnostics=sections)

    def with_target(self, **kwargs: Any) -> Snapshot:
        """
        Return a copy with an updated target summary.
        """

        target = dict(self.target)
        target.update(kwargs)
        return replace(self, target=target)

    def with_context(self, **kwargs: Any) -> Snapshot:
        """
        Return a copy with an updated execution context payload.
        """

        context = dict(self.context)
        context.update(kwargs)
        return replace(self, context=context)

    def with_environment(self, **kwargs: Any) -> Snapshot:
        """
        Return a copy with an updated environment payload.
        """

        environment = dict(self.environment)
        environment.update(kwargs)
        return replace(self, environment=environment)

    def with_session(self, **kwargs: Any) -> Snapshot:
        """
        Return a copy with an updated session payload.
        """

        session = dict(self.session)
        session.update(kwargs)
        return replace(self, session=session)

    def with_runtime_state(self, **kwargs: Any) -> Snapshot:
        """
        Return a copy with an updated runtime-state payload.
        """

        runtime_state = dict(self.runtime_state)
        runtime_state.update(kwargs)
        return replace(self, runtime_state=runtime_state)

    def to_dict(self) -> dict[str, Any]:
        """
        Serialize the snapshot into a JSON-friendly dictionary.
        """

        return {
            "snapshot_id": self.snapshot_id,
            "metadata": self.metadata.to_dict(),
            "summary": self.summary.to_dict(),
            "artifacts": [artifact.to_dict() for artifact in self.artifacts],
            "context": dict(self.context),
            "environment": dict(self.environment),
            "session": dict(self.session),
            "runtime_state": dict(self.runtime_state),
            "target": dict(self.target),
            "diagnostics": dict(self.diagnostics),
        }

    def to_json(self, *, indent: int = 2) -> str:
        """
        Serialize the snapshot into JSON.
        """

        return json.dumps(
            self.to_dict(),
            indent=indent,
            ensure_ascii=False,
            default=str,
        )

    def save_json(self, destination: str | Path, *, indent: int = 2) -> Path:
        """
        Persist the snapshot to a JSON file.
        """

        path = Path(destination).expanduser().resolve()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.to_json(indent=indent), encoding="utf-8")
        return path


__all__ = [
    "Snapshot",
]