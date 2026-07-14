"""
Base collector contract.

Collectors are observation components that gather structured diagnostic data
from models, modules, sessions, or runtime targets without mutating the target
behavior.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any, ClassVar

from .component import BaseComponent
from .collector_batch import CollectorBatch
from .collector_config import CollectorConfig
from .collector_kind import CollectorKind
from .collector_record import CollectorRecord
from .collector_result import CollectorResult
from .collector_summary import CollectorSummary
from .collector_target import CollectorTarget
from .context import ExecutionContext


class BaseCollector(BaseComponent, ABC):
    """
    Abstract base class for all collectors.
    """

    component_kind: ClassVar[str] = "collector"
    collector_kind: ClassVar[CollectorKind] = CollectorKind.CUSTOM

    __slots__ = (
        "_config",
        "_history",
        "_last_result",
    )

    def __init__(
        self,
        name: str = "collector",
        *,
        config: CollectorConfig | None = None,
        context: ExecutionContext | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        self._config = config or CollectorConfig(
            name=name,
            collector_kind=self.collector_kind,
        )

        base_metadata = dict(self._config.metadata)
        if metadata is not None:
            base_metadata.update(metadata)

        super().__init__(
            name=name,
            context=context,
            metadata=base_metadata,
        )

        self._history: list[CollectorResult] = []
        self._last_result: CollectorResult | None = None

    @property
    def config(self) -> CollectorConfig:
        """Return the collector configuration."""

        return self._config

    @property
    def collector_type(self) -> CollectorKind:
        """Return the collector kind."""

        return self._config.collector_kind

    @property
    def history(self) -> tuple[CollectorResult, ...]:
        """Return the collection history."""

        return tuple(self._history)

    @property
    def last_result(self) -> CollectorResult | None:
        """Return the last collection result."""

        return self._last_result

    @abstractmethod
    def collect(
        self,
        target: Any,
        *,
        context: Any | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> CollectorResult:
        """
        Collect structured diagnostic data from a target.
        """

    def reset(self) -> None:
        """Reset the collector state."""

        self._history.clear()
        self._last_result = None
        super().reset()

    def snapshot(self) -> dict[str, Any]:
        """Return a JSON-friendly snapshot of the collector state."""

        return {
            "name": self.name,
            "uid": self.uid,
            "collector_kind": self.collector_type.value,
            "config": self._config.to_dict(),
            "history_count": len(self._history),
            "last_result": (
                None if self._last_result is None else self._last_result.to_dict()
            ),
            "metadata": dict(self.metadata),
            "context": None if self.context is None else self.context.to_dict(),
            "component_state": self.state.value,
        }

    def to_dict(self) -> dict[str, Any]:
        """Serialize the collector state."""

        payload = super().to_dict()
        payload.update(
            {
                "collector_kind": self.collector_type.value,
                "config": self._config.to_dict(),
                "history": [result.to_dict() for result in self._history],
                "history_count": len(self._history),
                "last_result": (
                    None if self._last_result is None else self._last_result.to_dict()
                ),
            }
        )
        return payload

    def _record_result(self, result: CollectorResult) -> CollectorResult:
        """Record a result in the collector history."""

        self._history.append(result)
        self._last_result = result
        return result

    def _new_target(
        self,
        target: Any,
        *,
        target_id: str | None = None,
        name: str | None = None,
        module_path: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> CollectorTarget:
        """Build a collector target from an object."""

        return CollectorTarget.from_object(
            target,
            target_id=target_id,
            name=name,
            module_path=module_path,
            metadata=metadata,
        )

    def _new_record(
        self,
        *,
        target: CollectorTarget | None,
        value: Any = None,
        success: bool = True,
        value_type: str = "",
        error_type: str | None = None,
        error_message: str | None = None,
        metadata: dict[str, Any] | None = None,
        collected_at: datetime | None = None,
        collector_kind: CollectorKind | None = None,
    ) -> CollectorRecord:
        """Build a collector record."""

        return CollectorRecord(
            collector_kind=collector_kind or self.collector_type,
            target=target,
            value=value,
            success=success,
            value_type=value_type,
            error_type=error_type,
            error_message=error_message,
            metadata={} if metadata is None else dict(metadata),
            collected_at=collected_at or datetime.now(timezone.utc),
        )

    def _new_batch(
        self,
        *,
        records: tuple[CollectorRecord, ...] | list[CollectorRecord],
        metadata: dict[str, Any] | None = None,
        started_at: datetime | None = None,
        finished_at: datetime | None = None,
    ) -> CollectorBatch:
        """Build a collector batch."""

        return CollectorBatch(
            collector_name=self.name,
            collector_kind=self.collector_type,
            records=tuple(records),
            metadata={} if metadata is None else dict(metadata),
            started_at=started_at or datetime.now(timezone.utc),
            finished_at=finished_at,
        )

    def _new_summary(
        self,
        batches: tuple[CollectorBatch, ...] | list[CollectorBatch],
        *,
        metadata: dict[str, Any] | None = None,
    ) -> CollectorSummary:
        """Build a collector summary."""

        return CollectorSummary.from_batches(
            collector_name=self.name,
            collector_kind=self.collector_type,
            batches=batches,
            metadata=metadata,
        )

    def _new_result(
        self,
        *,
        batches: tuple[CollectorBatch, ...] | list[CollectorBatch],
        metadata: dict[str, Any] | None = None,
        created_at: datetime | None = None,
    ) -> CollectorResult:
        """Build a collector result and record it."""

        result = CollectorResult(
            collector_name=self.name,
            collector_kind=self.collector_type,
            batches=tuple(batches),
            summary=self._new_summary(
                batches,
                metadata=metadata,
            ),
            created_at=created_at or datetime.now(timezone.utc),
            metadata={} if metadata is None else dict(metadata),
        )
        return self._record_result(result)


__all__ = [
    "BaseCollector",
]