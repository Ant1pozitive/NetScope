from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from netscope.collector_kind import CollectorKind
from netscope.protocols import (
    BaseCollectorProtocol,
    CollectorBatchProtocol,
    CollectorRecordProtocol,
    CollectorResultProtocol,
    CollectorSummaryProtocol,
    CollectorTargetProtocol,
)
from netscope.runtime_collector import RuntimeCollector
from netscope.runtime_metric_kind import RuntimeMetricKind


@dataclass
class RuntimeState:
    latency_ms: float
    cpu_percent: float
    memory_mb: float
    throughput: float
    gpu_memory_mb: float
    temperature_c: float
    flops: float
    queue_depth: int
    step_time_ms: float
    custom_message: str = "healthy"


def test_runtime_collector_collects_object_telemetry(tmp_path: Path) -> None:
    collector = RuntimeCollector(name="runtime_collector")

    state = RuntimeState(
        latency_ms=12.5,
        cpu_percent=48.0,
        memory_mb=812.3,
        throughput=153.0,
        gpu_memory_mb=4096.0,
        temperature_c=67.2,
        flops=1.25e12,
        queue_depth=7,
        step_time_ms=11.8,
    )

    result = collector.collect(
        state,
        context={"run_id": "demo"},
        metadata={"suite": "runtime"},
    )

    assert result.collector_kind is CollectorKind.RUNTIME
    assert result.batch_count == 1
    assert result.record_count >= 8
    assert result.success_rate == 1.0
    assert collector.last_result is result
    assert len(collector.history) == 1

    batch = result.batches[0]
    assert isinstance(batch, CollectorBatchProtocol)
    assert batch.record_count >= 8
    assert batch.metadata["collector_kind"] == CollectorKind.RUNTIME.value
    assert batch.metadata["metric_count"] >= 8
    assert "runtime_summary" in batch.metadata

    records = result.records
    assert records
    first_record = records[0]
    assert isinstance(first_record, CollectorRecordProtocol)
    assert isinstance(first_record.target, CollectorTargetProtocol)
    assert first_record.value["kind"] in {"tensor", "non_tensor"}
    assert first_record.metadata["collector_kind"] == CollectorKind.RUNTIME.value

    summary = result.summary
    assert isinstance(summary, CollectorSummaryProtocol)
    assert summary.collector_name == "runtime_collector"
    assert summary.collector_kind is CollectorKind.RUNTIME
    assert summary.record_count == result.record_count

    payload_dict = result.to_dict()
    assert payload_dict["collector_kind"] == "runtime"
    assert payload_dict["metadata"]["suite"] == "runtime"
    assert payload_dict["summary"]["record_count"] == result.record_count

    saved = result.save_json(tmp_path / "runtime_result.json")
    assert saved.exists()
    assert '"collector_kind"' in saved.read_text(encoding="utf-8")


def test_runtime_collector_collects_nested_mappings_and_sequences() -> None:
    collector = RuntimeCollector(name="runtime_collector")

    payload = {
        "cpu": {
            "usage": 42.0,
            "temperature_c": 61.5,
        },
        "memory_mb": [128.0, 256.0, 512.0],
        "throughput": 99.5,
    }

    result = collector.collect(payload)

    assert result.record_count == 5
    assert any(record.metadata["metric_kind"] == RuntimeMetricKind.CPU.value for record in result.records)
    assert any(record.metadata["metric_kind"] == RuntimeMetricKind.MEMORY.value for record in result.records)
    assert any(record.metadata["metric_kind"] == RuntimeMetricKind.THROUGHPUT.value for record in result.records)
    assert result.summary.metric_count == 5


def test_runtime_collector_protocol_compatibility() -> None:
    collector = RuntimeCollector(name="runtime_collector")

    result = collector.collect(
        {
            "latency_ms": 3.2,
            "cpu_percent": 21.0,
            "memory_mb": 128.0,
        }
    )

    assert isinstance(collector, BaseCollectorProtocol)
    assert isinstance(result, CollectorResultProtocol)
    assert isinstance(result.summary, CollectorSummaryProtocol)
    assert isinstance(result.batches[0], CollectorBatchProtocol)
    assert isinstance(result.records[0], CollectorRecordProtocol)
    assert isinstance(result.records[0].target, CollectorTargetProtocol)