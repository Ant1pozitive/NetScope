"""
Runtime metric kind definitions.
"""

from __future__ import annotations

from enum import Enum


class RuntimeMetricKind(str, Enum):
    """Supported runtime metric kinds."""

    LATENCY = "latency"
    CPU = "cpu"
    MEMORY = "memory"
    GPU = "gpu"
    VRAM = "vram"
    FLOPS = "flops"
    THROUGHPUT = "throughput"
    STEP_TIME = "step_time"
    CUSTOM = "custom"

    @classmethod
    def from_name(cls, name: str) -> RuntimeMetricKind:
        """
        Infer a metric kind from a metric name.
        """

        normalized = name.strip().lower()
        if not normalized:
            return cls.CUSTOM

        if "latency" in normalized or "duration" in normalized or "elapsed" in normalized:
            return cls.LATENCY
        if normalized.startswith("cpu") or "cpu" in normalized:
            return cls.CPU
        if "memory" in normalized or "ram" in normalized:
            return cls.MEMORY
        if "gpu" in normalized:
            return cls.GPU
        if "vram" in normalized:
            return cls.VRAM
        if "flop" in normalized:
            return cls.FLOPS
        if "throughput" in normalized or "samples_per_second" in normalized:
            return cls.THROUGHPUT
        if "step_time" in normalized or "step-time" in normalized:
            return cls.STEP_TIME

        return cls.CUSTOM


__all__ = [
    "RuntimeMetricKind",
]