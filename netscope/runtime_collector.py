"""
Runtime collector.

This collector summarizes runtime telemetry in an observation-only way.
It accepts mappings, sequences, nested structures, or objects exposing common
runtime fields, and converts them into structured collector records.
"""

from __future__ import annotations

import importlib.util
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from .base_collector import BaseCollector
from .collector_kind import CollectorKind
from .collector_result import CollectorResult
from .runtime_metric import RuntimeMetric
from .runtime_metric_kind import RuntimeMetricKind
from .runtime_summary import RuntimeSummary


@dataclass(slots=True, frozen=True)
class RuntimeFieldSpec:
    """
    Descriptor for a known runtime field.
    """

    name: str
    unit: str = ""
    kind: RuntimeMetricKind = RuntimeMetricKind.CUSTOM


class RuntimeCollector(BaseCollector):
    """
    Collect structured runtime telemetry.
    """

    collector_kind = CollectorKind.RUNTIME

    _FIELD_SPECS: tuple[RuntimeFieldSpec, ...] = (
        RuntimeFieldSpec("latency_ms", unit="ms", kind=RuntimeMetricKind.LATENCY),
        RuntimeFieldSpec("step_time_ms", unit="ms", kind=RuntimeMetricKind.STEP_TIME),
        RuntimeFieldSpec("elapsed_ms", unit="ms", kind=RuntimeMetricKind.LATENCY),
        RuntimeFieldSpec("cpu_percent", unit="%", kind=RuntimeMetricKind.CPU),
        RuntimeFieldSpec("cpu_usage", unit="%", kind=RuntimeMetricKind.CPU),
        RuntimeFieldSpec("memory_mb", unit="MB", kind=RuntimeMetricKind.MEMORY),
        RuntimeFieldSpec("memory_percent", unit="%", kind=RuntimeMetricKind.MEMORY),
        RuntimeFieldSpec("gpu_percent", unit="%", kind=RuntimeMetricKind.GPU),
        RuntimeFieldSpec("gpu_memory_mb", unit="MB", kind=RuntimeMetricKind.GPU),
        RuntimeFieldSpec("vram_mb", unit="MB", kind=RuntimeMetricKind.VRAM),
        RuntimeFieldSpec("throughput", unit="items/s", kind=RuntimeMetricKind.THROUGHPUT),
        RuntimeFieldSpec(
            "samples_per_second",
            unit="items/s",
            kind=RuntimeMetricKind.THROUGHPUT,
        ),
        RuntimeFieldSpec("flops", unit="FLOPs", kind=RuntimeMetricKind.FLOPS),
        RuntimeFieldSpec("queue_depth", unit="items", kind=RuntimeMetricKind.CUSTOM),
        RuntimeFieldSpec("temperature_c", unit="°C", kind=RuntimeMetricKind.CUSTOM),
        RuntimeFieldSpec("power_watts", unit="W", kind=RuntimeMetricKind.CUSTOM),
    )

    def collect(
        self,
        target: Any,
        *,
        context: Any | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> CollectorResult:
        """
        Collect runtime telemetry from a target payload.
        """

        merged_metadata = dict(self.metadata)
        if metadata is not None:
            merged_metadata.update(metadata)

        if self.config.include_context and context is not None:
            merged_metadata["context"] = self._safe_context(context)

        entries = list(self._iter_entries(target))
        records = []
        runtime_metrics: list[RuntimeMetric] = []

        metric_count = 0
        numeric_metric_count = 0
        tensor_metric_count = 0
        non_numeric_metric_count = 0

        for index, (path, value) in enumerate(entries):
            metric = self._build_metric(
                path=path,
                value=value,
                index=index,
            )
            runtime_metrics.append(metric)

            metric_count += 1
            if metric.is_numeric:
                numeric_metric_count += 1
            elif metric.kind in {RuntimeMetricKind.GPU, RuntimeMetricKind.VRAM} and self._is_tensor(value):
                tensor_metric_count += 1
            else:
                non_numeric_metric_count += 1

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

            record = self._new_record(
                target=target_obj,
                value=metric.to_dict(),
                value_type="runtime_metric",
                metadata={
                    "path": path,
                    "index": index,
                    "metric_kind": metric.kind.value,
                    "is_numeric": metric.is_numeric,
                    "source_type": type(value).__name__,
                    "collector_kind": self.collector_type.value,
                },
                collector_kind=self.collector_type,
            )
            records.append(record)

        summary_model = RuntimeSummary.from_metrics(
            collector_name=self.name,
            metrics=runtime_metrics,
            metadata=merged_metadata,
        )

        batch = self._new_batch(
            records=records,
            metadata={
                "collector_kind": self.collector_type.value,
                "metric_count": metric_count,
                "numeric_metric_count": numeric_metric_count,
                "tensor_metric_count": tensor_metric_count,
                "non_numeric_metric_count": non_numeric_metric_count,
                "entry_count": len(entries),
                "runtime_summary": summary_model.to_dict(),
                **merged_metadata,
            },
        ).complete()

        return self._new_result(
            batches=[batch],
            metadata={
                "collector_kind": self.collector_type.value,
                "metric_count": metric_count,
                "numeric_metric_count": numeric_metric_count,
                "tensor_metric_count": tensor_metric_count,
                "non_numeric_metric_count": non_numeric_metric_count,
                "entry_count": len(entries),
                "runtime_summary": summary_model.to_dict(),
                **merged_metadata,
            },
        )

    def _iter_entries(self, target: Any, *, path: str = "root") -> tuple[tuple[str, Any], ...]:
        """
        Flatten nested payloads into leaf entries.
        """

        if self._is_runtime_object(target):
            return self._iter_runtime_object(target)

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

    def _iter_runtime_object(self, target: Any) -> tuple[tuple[str, Any], ...]:
        """
        Extract known runtime fields from an object.
        """

        entries: list[tuple[str, Any]] = []

        for spec in self._FIELD_SPECS:
            if not hasattr(target, spec.name):
                continue

            value = getattr(target, spec.name)
            if callable(value):
                continue

            entries.append((spec.name, value))

        if entries:
            return tuple(entries)

        if hasattr(target, "to_dict") and callable(getattr(target, "to_dict")):
            try:
                payload = target.to_dict()
            except Exception:  # noqa: BLE001
                payload = None
            if isinstance(payload, Mapping):
                return self._iter_entries(payload, path="root")

        return ((target.__class__.__name__, target),)

    @staticmethod
    def _is_sequence(value: Any) -> bool:
        """
        Return whether the value is a non-string sequence that should be flattened.
        """

        if isinstance(value, (str, bytes, bytearray)):
            return False
        return isinstance(value, Sequence)

    @staticmethod
    def _is_runtime_object(value: Any) -> bool:
        """
        Return whether the value looks like a runtime telemetry object.
        """

        field_names = {
            "latency_ms",
            "step_time_ms",
            "elapsed_ms",
            "cpu_percent",
            "memory_mb",
            "throughput",
            "samples_per_second",
            "flops",
            "queue_depth",
        }
        return any(hasattr(value, field_name) for field_name in field_names)

    @staticmethod
    def _is_tensor(value: Any) -> bool:
        """
        Return whether the value is a torch.Tensor without hard failing if torch is absent.
        """

        if importlib.util.find_spec("torch") is None:
            return False

        try:
            import torch # type: ignore
        except Exception:  # noqa: BLE001
            return False

        return isinstance(value, torch.Tensor)

    def _build_metric(
        self,
        *,
        path: str,
        value: Any,
        index: int,
    ) -> RuntimeMetric:
        """
        Build a runtime metric from a leaf value.
        """

        kind, unit = self._infer_kind_and_unit(path, value)
        summary_value = self._summarize_value(value)

        return RuntimeMetric(
            name=path,
            kind=kind,
            value=summary_value,
            unit=unit,
            scope="runtime",
            source=type(value).__name__,
            metadata={
                "index": index,
                "path": path,
            },
        )

    def _infer_kind_and_unit(self, path: str, value: Any) -> tuple[RuntimeMetricKind, str]:
        """
        Infer metric kind and unit from path and value.
        """

        inferred = RuntimeMetricKind.from_name(path)
        unit = ""

        for spec in self._FIELD_SPECS:
            if spec.name in path.lower():
                inferred = spec.kind
                unit = spec.unit
                break

        if self._is_tensor(value):
            inferred = inferred if inferred is not RuntimeMetricKind.CUSTOM else RuntimeMetricKind.GPU

        if unit == "" and inferred is RuntimeMetricKind.LATENCY:
            unit = "ms"
        elif unit == "" and inferred in {RuntimeMetricKind.CPU, RuntimeMetricKind.MEMORY}:
            unit = "%"
        elif unit == "" and inferred in {RuntimeMetricKind.THROUGHPUT}:
            unit = "items/s"

        return inferred, unit

    def _summarize_value(self, value: Any) -> Any:
        """
        Build a structured value for a runtime metric.
        """

        if self._is_tensor(value):
            return self._summarize_tensor(value)

        if isinstance(value, bool):
            return value

        if isinstance(value, (int, float)):
            return float(value)

        if isinstance(value, Mapping):
            return {str(key): self._summarize_value(item) for key, item in value.items()}

        if self._is_sequence(value):
            return [self._summarize_value(item) for item in value]

        return self._safe_repr(value)

    def _summarize_tensor(self, tensor: Any) -> dict[str, Any]:
        """
        Build a structured summary for a tensor payload.
        """

        import torch # type: ignore

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
                    "l1_norm": None,
                    "l2_norm": None,
                    "linf_norm": None,
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
            }
        )
        return summary

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
    "RuntimeCollector",
    "RuntimeFieldSpec",
]