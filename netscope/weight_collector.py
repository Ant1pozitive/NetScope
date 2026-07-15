"""
Weight collector.

This collector summarizes model parameters and weight-like tensors in an
observation-only way. It accepts torch.nn.Module objects, tensors, nested
mappings/sequences, or arbitrary objects and converts them into structured
collector records.
"""

from __future__ import annotations

import importlib.util
from collections.abc import Mapping, Sequence
from typing import Any

from .base_collector import BaseCollector
from .collector_kind import CollectorKind
from .collector_result import CollectorResult


class WeightCollector(BaseCollector):
    """
    Collect structured weight summaries.
    """

    collector_kind = CollectorKind.WEIGHT

    def collect(
        self,
        target: Any,
        *,
        context: Any | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> CollectorResult:
        """
        Collect weight summaries from a target payload.

        If the target is a torch.nn.Module and torch is available, the collector
        prefers named parameters. Otherwise it falls back to generic flattening.
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
        parameter_object_count = 0
        trainable_parameter_object_count = 0
        parameter_element_count = 0
        trainable_parameter_element_count = 0

        for index, (path, value) in enumerate(entries):
            is_tensor = self._is_tensor(value)
            if is_tensor:
                tensor_count += 1
            else:
                non_tensor_count += 1

            if is_tensor:
                parameter_object_count += 1
                if bool(getattr(value, "requires_grad", False)):
                    trainable_parameter_object_count += 1

                element_count = int(getattr(value, "numel", lambda: 1)())
                parameter_element_count += element_count
                if bool(getattr(value, "requires_grad", False)):
                    trainable_parameter_element_count += element_count

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
                value_type="tensor_weight" if is_tensor else "weight_leaf",
                metadata={
                    "path": path,
                    "index": index,
                    "is_tensor": is_tensor,
                    "source_type": type(value).__name__,
                    "collector_kind": self.collector_type.value,
                    "requires_grad": bool(getattr(value, "requires_grad", False)),
                },
                collector_kind=self.collector_type,
            )
            records.append(record)

        module_summary = self._summarize_module(target)

        batch = self._new_batch(
            records=records,
            metadata={
                "collector_kind": self.collector_type.value,
                "tensor_count": tensor_count,
                "non_tensor_count": non_tensor_count,
                "parameter_object_count": parameter_object_count,
                "trainable_parameter_object_count": trainable_parameter_object_count,
                "parameter_element_count": parameter_element_count,
                "trainable_parameter_element_count": trainable_parameter_element_count,
                "entry_count": len(entries),
                **module_summary,
                **merged_metadata,
            },
        ).complete()

        return self._new_result(
            batches=[batch],
            metadata={
                "collector_kind": self.collector_type.value,
                "tensor_count": tensor_count,
                "non_tensor_count": non_tensor_count,
                "parameter_object_count": parameter_object_count,
                "trainable_parameter_object_count": trainable_parameter_object_count,
                "parameter_element_count": parameter_element_count,
                "trainable_parameter_element_count": trainable_parameter_element_count,
                "entry_count": len(entries),
                **module_summary,
                **merged_metadata,
            },
        )

    def _iter_entries(self, target: Any, *, path: str = "root") -> tuple[tuple[str, Any], ...]:
        """
        Flatten target payloads into leaf entries.

        For torch.nn.Module inputs, named parameters are preferred when available.
        """

        if self._is_module(target):
            return self._iter_module_parameters(target)

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

    def _iter_module_parameters(self, module: Any) -> tuple[tuple[str, Any], ...]:
        """
        Return named parameters for a torch.nn.Module when possible.
        """

        entries: list[tuple[str, Any]] = []

        named_parameters = getattr(module, "named_parameters", None)
        if callable(named_parameters):
            try:
                for name, parameter in named_parameters(recurse=True):
                    entries.append((name or "parameter", parameter))
            except Exception:  # noqa: BLE001
                pass

        if entries:
            return tuple(entries)

        named_buffers = getattr(module, "named_buffers", None)
        if callable(named_buffers):
            try:
                for name, buffer in named_buffers(recurse=True):
                    entries.append((f"buffer.{name}" if name else "buffer", buffer))
            except Exception:  # noqa: BLE001
                pass

        if entries:
            return tuple(entries)

        return ((module.__class__.__name__, module),)

    @staticmethod
    def _is_sequence(value: Any) -> bool:
        """
        Return whether the value is a non-string sequence that should be flattened.
        """

        if isinstance(value, (str, bytes, bytearray)):
            return False
        return isinstance(value, Sequence)

    @staticmethod
    def _is_module(value: Any) -> bool:
        """
        Return whether the value is a torch.nn.Module without hard failing if torch is absent.
        """

        if importlib.util.find_spec("torch") is None:
            return False

        try:
            import torch.nn as nn
        except Exception:  # noqa: BLE001
            return False

        return isinstance(value, nn.Module)

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
        requires_grad = bool(getattr(tensor, "requires_grad", False))

        summary: dict[str, Any] = {
            "kind": "tensor",
            "type": type(tensor).__name__,
            "dtype": dtype,
            "device": device,
            "shape": shape,
            "rank": rank,
            "numel": numel,
            "requires_grad": requires_grad,
            "is_leaf": bool(getattr(tensor, "is_leaf", False)),
            "is_frozen": not requires_grad,
        }

        if numel == 0:
            summary.update(
                {
                    "mean": None,
                    "std": None,
                    "min": None,
                    "max": None,
                    "abs_mean": None,
                    "l1_norm": None,
                    "l2_norm": None,
                    "linf_norm": None,
                    "zero_fraction": None,
                    "finite_fraction": None,
                    "sparsity": None,
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
            l1_norm = None
            l2_norm = None
            linf_norm = None
        else:
            mean = float(finite_values.mean().item())
            std = (
                float(finite_values.std(unbiased=False).item())
                if finite_values.numel() > 1
                else 0.0
            )
            min_value = float(finite_values.min().item())
            max_value = float(finite_values.max().item())
            abs_values = finite_values.abs()
            abs_mean = float(abs_values.mean().item())
            l1_norm = float(abs_values.sum().item())
            l2_norm = float(torch.linalg.vector_norm(finite_values).item())
            linf_norm = float(abs_values.max().item())

        zero_fraction = float((flat == 0).float().mean().item())
        finite_fraction = float(finite_mask.float().mean().item())
        sparsity = zero_fraction

        summary.update(
            {
                "mean": mean,
                "std": std,
                "min": min_value,
                "max": max_value,
                "abs_mean": abs_mean,
                "l1_norm": l1_norm,
                "l2_norm": l2_norm,
                "linf_norm": linf_norm,
                "zero_fraction": zero_fraction,
                "finite_fraction": finite_fraction,
                "sparsity": sparsity,
            }
        )
        return summary

    def _summarize_module(self, target: Any) -> dict[str, Any]:
        """
        Return module-level summary metadata when the target is a module.
        """

        if not self._is_module(target):
            return {}

        parameters = list(getattr(target, "named_parameters", lambda **kwargs: [])(recurse=True))
        buffers = list(getattr(target, "named_buffers", lambda **kwargs: [])(recurse=True))

        parameter_object_count = 0
        parameter_element_count = 0
        trainable_parameter_object_count = 0
        trainable_parameter_element_count = 0

        for _, parameter in parameters:
            parameter_object_count += 1
            numel = int(getattr(parameter, "numel", lambda: 1)())
            parameter_element_count += numel
            if bool(getattr(parameter, "requires_grad", False)):
                trainable_parameter_object_count += 1
                trainable_parameter_element_count += numel

        return {
            "module_class": type(target).__name__,
            "module_qualname": f"{type(target).__module__}.{type(target).__qualname__}",
            "module_parameter_count": parameter_object_count,
            "module_buffer_count": len(buffers),
            "module_parameter_element_count": parameter_element_count,
            "module_trainable_parameter_count": trainable_parameter_object_count,
            "module_trainable_parameter_element_count": trainable_parameter_element_count,
            "module_training": bool(getattr(target, "training", False)),
        }

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
            return {
                str(key): WeightCollector._safe_context(value)
                for key, value in context.items()
            }

        if isinstance(context, Sequence) and not isinstance(context, (str, bytes, bytearray)):
            return [WeightCollector._safe_context(item) for item in context]

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
    "WeightCollector",
]