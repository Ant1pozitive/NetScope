"""
Safe hook wrapper.

This wrapper executes a hook callback defensively. It captures timing,
exception information, and result payloads while preserving a strict
fail-open/fail-closed policy.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable

from .exceptions import HookExecutionError
from .hook_event import HookEvent
from .hook_kind import HookKind
from .hook_result import HookResult
from .hook_target import HookTarget
from .logging import get_logger

HookCallback = Callable[..., Any]


@dataclass(slots=True)
class SafeHookWrapper:
    """
    Wrap a hook callback with safe execution semantics.
    """

    callback: HookCallback
    hook_kind: HookKind = HookKind.FORWARD
    hook_name: str | None = None
    target: HookTarget | Any | None = None
    fail_open: bool = True
    logger_name: str = "netscope.hooks"
    metadata: dict[str, Any] = field(default_factory=dict)
    _logger: Any = field(default=None, init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        if not callable(self.callback):
            raise ValueError("callback must be callable.")
        if self.hook_name is not None and not self.hook_name.strip():
            raise ValueError("hook_name cannot be empty.")
        object.__setattr__(self, "metadata", dict(self.metadata))
        object.__setattr__(self, "_logger", get_logger(self.logger_name))

    @property
    def resolved_hook_name(self) -> str:
        """Return a stable hook name."""

        if self.hook_name is not None and self.hook_name.strip():
            return self.hook_name.strip()

        candidate = getattr(self.callback, "__name__", "")
        if isinstance(candidate, str) and candidate.strip():
            return candidate.strip()

        return self.hook_kind.value

    def _resolve_target(self, target: Any | None) -> HookTarget | None:
        """Resolve the target for a call."""

        value = self.target if target is None else target
        if value is None:
            return None
        if isinstance(value, HookTarget):
            return value
        return HookTarget.from_object(
            value,
            metadata={
                "source": "SafeHookWrapper",
            },
        )

    def __call__(self, *args: Any, **kwargs: Any) -> HookResult:
        """
        Execute the wrapped callback safely and return a structured result.
        """

        started_at = datetime.now(timezone.utc)
        resolved_target = self._resolve_target(kwargs.pop("target", None))

        event = HookEvent(
            hook_kind=self.hook_kind,
            hook_name=self.resolved_hook_name,
            target=resolved_target,
            metadata=dict(self.metadata),
            payload={
                "args_count": len(args),
                "kwargs_keys": sorted(str(key) for key in kwargs.keys()),
            },
        )

        try:
            value = self.callback(*args, **kwargs)
            finished_at = datetime.now(timezone.utc)
            return HookResult(
                event=event,
                success=True,
                return_value=value,
                started_at=started_at,
                finished_at=finished_at,
                metadata=dict(self.metadata),
            )
        except Exception as exc:  # noqa: BLE001
            finished_at = datetime.now(timezone.utc)
            self._logger.exception(
                "Hook callback failed: kind=%s name=%s target=%s",
                self.hook_kind.value,
                self.resolved_hook_name,
                None if resolved_target is None else resolved_target.target_id,
            )

            if not self.fail_open:
                raise HookExecutionError(
                    f"Hook '{self.resolved_hook_name}' failed."
                ) from exc

            return HookResult(
                event=event,
                success=False,
                return_value=None,
                error_type=exc.__class__.__name__,
                error_message=str(exc),
                started_at=started_at,
                finished_at=finished_at,
                metadata=dict(self.metadata),
            )

    def to_dict(self) -> dict[str, Any]:
        """Serialize the wrapper configuration into a dictionary."""

        return {
            "hook_kind": self.hook_kind.value,
            "hook_name": self.resolved_hook_name,
            "fail_open": self.fail_open,
            "target": (
                None
                if self.target is None
                else (
                    self.target.to_dict()
                    if isinstance(self.target, HookTarget)
                    else HookTarget.from_object(self.target).to_dict()
                )
            ),
            "metadata": dict(self.metadata),
        }


__all__ = [
    "SafeHookWrapper",
]