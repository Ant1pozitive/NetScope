"""
Activation collector.

This collector summarizes activation-like payloads in an observation-only way.
It accepts tensors, nested mappings/sequences of tensors, or arbitrary objects
and converts them into structured collector records.
"""

from __future__ import annotations

import importlib.util
from collections.abc import Mapping, Sequence
from typing import Any

from .base_collector import BaseCollector
from .collector_kind import CollectorKind
from .collector_result import CollectorResult


class ActivationCollector(BaseCollector):
    """
    Collect structured activation summaries.
    """

    collector_kind = CollectorKind.ACTIVATION

    def collect(
        self,
        target: Any,
        *,
        context: Any | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> CollectorResult:
        """
        Collect activation summaries from a target payload.

        The target may be:
        - a torch.Tensor;
        - a nested mapping / sequence containing tensors;
        - any arbitrary object, which will be recorded as a non-tensor leaf.
        """

        merged_metadata = dict(self.metadata)
        if metadata is not None:
            merged_metadata.update(metadata)

        if self.config.include_context and context is not None:
            merged_metadata["context"] = self._safe_context(context)

        entries = list(self._iter_entries(target))
        records = []

        tensor_count = 0
        non_tensor_count = 0

        for index, (path, value) in enumerate(entries):
            is_tensor = self._is_tensor(value)
            if is_tensor:
                tensor_count += 1
            else:
                non_tensor_count += 1

            target_obj = self._new_target(
                value,
                target_id=path,
                name=path,
                metadata={
                    "path": path,
                    "source_type": type(value).__name__,
                    "collector_kind": self.collector_type.value,
                },
            )

            summary = self._summarize_value(value)
            record = self._new_record(
                target=target_obj,
                value=summary,
                value_type="tensor_activation" if is_tensor else "activation_leaf",
                metadata={
                    "path": path,
                    "index": index,
                    "is_tensor": is_tensor,
                    "source_type": type(value).__name__,
                    "collector_kind": self.collector_type.value,
                },
                collector_kind=self.collector_type,
            )
            records.append(record)

        batch = self._new_batch(
            records=records,
            metadata={
                "collector_kind": self.collector_type.value,
                "tensor_count": tensor_count,
                "non_tensor_count": non_tensor_count,
                "entry_count": len(entries),
                **merged_metadata,
            },
        ).complete()

        return self._new_result(
            batches=[batch],
            metadata={
                "collector_kind": self.collector_type.value,
                "tensor_count": tensor_count,
                "non_tensor_count": non_tensor_count,
                "entry_count": len(entries),
                **merged_metadata,
            },
        )

    def _iter_entries(self, target: Any, *, path: str = "root") -> tuple[tuple[str, Any], ...]:
        """
        Flatten nested payloads into leaf entries.
        """

        entries: list[tuple[str, Any]] = []

        if isinstance(target, Mapping):
            for key, value in target.items():
                child_path = f"{path}.{key}" if path else str(key)
                entries.extend(self._iter_entries(value, path=child_path))
            return tuple(entries)

        if self._is_sequence(target):
            for index, value in enumerate(target):
                child_path = f"{path}[{index}]"
                entries.extend(self._iter_entries(value, path=child_path))
            return tuple(entries)

        entries.append((path, target))
        return tuple(entries)

    @staticmethod
    def _is_sequence(value: Any) -> bool:
        """
        Return whether the value is a non-string sequence that should be flattened.
        """

        if isinstance(value, (str, bytes, bytearray)):
            return False
        return isinstance(value, Sequence)

    @staticmethod
    def _is_tensor(value: Any) -> bool:
        """
        Return whether the value is a torch.Tensor without hard failing if torch is absent.
        """

        if importlib.util.find_spec("torch") is None:
            return False

        try:
            import torch
        except Exception:  # noqa: BLE001
            return False

        return isinstance(value, torch.Tensor)

    def _summarize_value(self, value: Any) -> dict[str, Any]:
        """
        Build a structured summary for a leaf payload.
        """

        if self._is_tensor(value):
            return self._summarize_tensor(value)

        return {
            "kind": "non_tensor",
            "type": type(value).__name__,
            "repr": self._safe_repr(value),
        }

    def _summarize_tensor(self, tensor: Any) -> dict[str, Any]:
        """
        Build a structured summary for a tensor payload.
        """

        import torch

        data = tensor.detach()

        device = str(data.device)
        dtype = str(data.dtype)
        shape = list(data.shape)
        rank = len(shape)
        numel = int(data.numel())

        summary: dict[str, Any] = {
            "kind": "tensor",
            "type": type(tensor).__name__,
            "dtype": dtype,
            "device": device,
            "shape": shape,
            "rank": rank,
            "numel": numel,
            "requires_grad": bool(getattr(tensor, "requires_grad", False)),
            "is_leaf": bool(getattr(tensor, "is_leaf", False)),
        }

        if numel == 0:
            summary.update(
                {
                    "mean": None,
                    "std": None,
                    "min": None,
                    "max": None,
                    "abs_mean": None,
                    "zero_fraction": None,
                    "finite_fraction": None,
                }
            )
            return summary

        numeric = data
        if numeric.is_complex():
            numeric = numeric.abs()
        if not torch.is_floating_point(numeric):
            numeric = numeric.float()

        flat = numeric.reshape(-1)
        finite_mask = torch.isfinite(flat)
        finite_values = flat[finite_mask]

        if finite_values.numel() == 0:
            mean = None
            std = None
            min_value = None
            max_value = None
            abs_mean = None
        else:
            mean = float(finite_values.mean().item())
            std = float(finite_values.std(unbiased=False).item()) if finite_values.numel() > 1 else 0.0
            min_value = float(finite_values.min().item())
            max_value = float(finite_values.max().item())
            abs_mean = float(finite_values.abs().mean().item())

        zero_fraction = float((flat == 0).float().mean().item())
        finite_fraction = float(finite_mask.float().mean().item())

        summary.update(
            {
                "mean": mean,
                "std": std,
                "min": min_value,
                "max": max_value,
                "abs_mean": abs_mean,
                "zero_fraction": zero_fraction,
                "finite_fraction": finite_fraction,
            }
        )
        return summary

    @staticmethod
    def _safe_context(context: Any) -> Any:
        """
        Convert a context object into a JSON-friendly representation.
        """

        if context is None:
            return None

        if isinstance(context, (str, int, float, bool)):
            return context

        if isinstance(context, Mapping):
            return {str(key): ActivationCollector._safe_context(value) for key, value in context.items()}

        if isinstance(context, Sequence) and not isinstance(context, (str, bytes, bytearray)):
            return [ActivationCollector._safe_context(item) for item in context]

        try:
            return repr(context)
        except Exception as exc:  # noqa: BLE001
            return f"<repr failed: {exc.__class__.__name__}>"

    @staticmethod
    def _safe_repr(value: Any) -> str:
        """
        Return a bounded repr for non-tensor values.
        """

        try:
            text = repr(value)
        except Exception as exc:  # noqa: BLE001
            text = f"<repr failed: {exc.__class__.__name__}>"

        if len(text) > 512:
            return f"{text[:509]}..."
        return text


__all__ = [
    "ActivationCollector",
]