"""
Inspection result model.

This is the first immutable result object produced by the NetScope execution
flow. Later phases will complement it with richer snapshots and reports.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4


@dataclass(slots=True, frozen=True)
class InspectionResult:
    """
    Immutable result of a single inspector run.
    """

    inspection_id: str = field(default_factory=lambda: uuid4().hex)
    inspector_name: str = "inspector"
    session: dict[str, Any] = field(default_factory=dict)
    target: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    finished_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    duration_seconds: float = 0.0
    success: bool = True
    error: str | None = None

    @property
    def status(self) -> str:
        """Return human-readable status."""

        return "success" if self.success else "failed"

    @property
    def session_id(self) -> str:
        """Return the associated session identifier."""

        value = self.session.get("session_id")
        return "" if value is None else str(value)

    @property
    def session_state(self) -> str:
        """Return the session state string."""

        value = self.session.get("session_state")
        return "" if value is None else str(value)

    @property
    def target_type(self) -> str:
        """Return the target type string."""

        value = self.target.get("type")
        return "" if value is None else str(value)

    @property
    def environment(self) -> dict[str, Any]:
        """Return environment snapshot extracted from the session payload."""

        value = self.session.get("environment")
        return value if isinstance(value, dict) else {}

    @property
    def runtime_state(self) -> dict[str, Any]:
        """Return runtime state extracted from the session payload."""

        value = self.session.get("runtime_state")
        return value if isinstance(value, dict) else {}

    @property
    def workspace(self) -> dict[str, Any]:
        """Return workspace snapshot extracted from the session payload."""

        value = self.session.get("workspace")
        return value if isinstance(value, dict) else {}

    def summary(self) -> str:
        """Return a concise human-readable summary."""

        target = self.target_type or "unknown target"
        session = self.session_id or "unknown session"
        return (
            f"{self.status.title()} inspection "
            f"{self.inspection_id} for {target} "
            f"(session={session}, duration={self.duration_seconds:.3f}s)"
        )

    def to_dict(self) -> dict[str, Any]:
        """Serialize the inspection result into a plain dictionary."""

        return {
            "inspection_id": self.inspection_id,
            "inspector_name": self.inspector_name,
            "status": self.status,
            "success": self.success,
            "error": self.error,
            "session_id": self.session_id,
            "session_state": self.session_state,
            "target_type": self.target_type,
            "target": self.target,
            "session": self.session,
            "metadata": dict(self.metadata),
            "started_at": self.started_at.isoformat(),
            "finished_at": self.finished_at.isoformat(),
            "duration_seconds": self.duration_seconds,
        }

    def to_json(self, *, indent: int = 2) -> str:
        """Serialize the result into JSON text."""

        return json.dumps(
            self.to_dict(),
            indent=indent,
            ensure_ascii=False,
            default=str,
        )

    def save_json(self, destination: str | Path, *, indent: int = 2) -> Path:
        """Persist the result as JSON."""

        path = Path(destination).expanduser().resolve()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.to_json(indent=indent), encoding="utf-8")
        return path


__all__ = [
    "InspectionResult",
]