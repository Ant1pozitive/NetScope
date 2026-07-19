from __future__ import annotations

from pathlib import Path

from netscope.protocols import (
    RuntimeMetricProtocol,
    RuntimeSampleProtocol,
    RuntimeSeriesProtocol,
    RuntimeSnapshotProtocol,
)
from netscope.runtime_metric import RuntimeMetric
from netscope.runtime_metric_kind import RuntimeMetricKind
from netscope.runtime_sample import RuntimeSample
from netscope.runtime_series import RuntimeSeries
from netscope.runtime_snapshot import RuntimeSnapshot


def test_runtime_metric_to_dict() -> None:
    metric = RuntimeMetric(
        name="latency_ms",
        kind=RuntimeMetricKind.LATENCY,
        value=12.5,
        unit="ms",
        scope="batch",
        source="profiler",
        metadata={"suite": "runtime"},
    )

    payload = metric.to_dict()

    assert payload["name"] == "latency_ms"
    assert payload["kind"] == RuntimeMetricKind.LATENCY.value
    assert payload["numeric_value"] == 12.5
    assert payload["is_numeric"] is True
    assert payload["metadata"]["suite"] == "runtime"


def test_runtime_sample_from_metric_and_to_dict() -> None:
    metric = RuntimeMetric(
        name="cpu_percent",
        kind=RuntimeMetricKind.CPU,
        value=48.0,
        unit="%",
        scope="process",
        source="psutil",
        metadata={"suite": "runtime"},
    )

    sample = RuntimeSample.from_metric(
        metric,
        step=2,
        batch_index=1,
        iteration=4,
        tags={"device": "cpu"},
    )

    payload = sample.to_dict()

    assert sample.name == "cpu_percent"
    assert sample.kind is RuntimeMetricKind.CPU
    assert sample.numeric_value == 48.0
    assert sample.has_step is True
    assert payload["step"] == 2
    assert payload["tags"]["device"] == "cpu"
    assert payload["metadata"]["metric_id"] == metric.metric_id


def test_runtime_series_statistics_and_persistence(tmp_path: Path) -> None:
    metric_1 = RuntimeMetric(
        name="latency_ms",
        kind=RuntimeMetricKind.LATENCY,
        value=10.0,
        unit="ms",
        scope="batch",
        source="profiler",
    )
    metric_2 = RuntimeMetric(
        name="latency_ms",
        kind=RuntimeMetricKind.LATENCY,
        value=20.0,
        unit="ms",
        scope="batch",
        source="profiler",
    )

    series = RuntimeSeries(
        series_id="latency-series",
        name="latency_ms",
        kind=RuntimeMetricKind.LATENCY,
        samples=(
            RuntimeSample.from_metric(metric_1, step=1),
            RuntimeSample.from_metric(metric_2, step=2),
        ),
    )

    payload = series.to_dict()

    assert series.sample_count == 2
    assert series.min_numeric_value == 10.0
    assert series.max_numeric_value == 20.0
    assert series.mean_numeric_value == 15.0
    assert payload["sample_count"] == 2

    saved = series.save_json(tmp_path / "series.json")
    assert saved.exists()


def test_runtime_snapshot_builds_summary_and_serializes(tmp_path: Path) -> None:
    metric = RuntimeMetric(
        name="throughput",
        kind=RuntimeMetricKind.THROUGHPUT,
        value=153.0,
        unit="items/s",
        scope="batch",
        source="profiler",
    )
    sample = RuntimeSample.from_metric(metric, step=1)
    series = RuntimeSeries(
        series_id="throughput-series",
        name="throughput",
        kind=RuntimeMetricKind.THROUGHPUT,
        samples=(sample,),
    )

    snapshot = RuntimeSnapshot(
        name="runtime_snapshot",
        metrics=(metric,),
        samples=(sample,),
        series=(series,),
        metadata={"suite": "runtime"},
    ).complete()

    payload = snapshot.to_dict()

    assert snapshot.is_completed is True
    assert snapshot.metric_count == 1
    assert snapshot.sample_count == 1
    assert snapshot.series_count == 1
    assert snapshot.summary.metric_count == 1
    assert payload["summary"]["collector_name"] == "runtime_snapshot"
    assert payload["metadata"]["suite"] == "runtime"

    saved = snapshot.save_json(tmp_path / "snapshot.json")
    assert saved.exists()
    assert '"runtime_snapshot"' in saved.read_text(encoding="utf-8")


def test_runtime_protocols_compatibility() -> None:
    metric = RuntimeMetric(
        name="latency_ms",
        kind=RuntimeMetricKind.LATENCY,
        value=12.5,
        unit="ms",
        scope="batch",
        source="profiler",
    )
    sample = RuntimeSample.from_metric(metric)
    series = RuntimeSeries(
        series_id="series-1",
        name="latency_ms",
        kind=RuntimeMetricKind.LATENCY,
        samples=(sample,),
    )
    snapshot = RuntimeSnapshot(
        name="runtime_snapshot",
        metrics=(metric,),
        samples=(sample,),
        series=(series,),
    )

    assert isinstance(metric, RuntimeMetricProtocol)
    assert isinstance(sample, RuntimeSampleProtocol)
    assert isinstance(series, RuntimeSeriesProtocol)
    assert isinstance(snapshot, RuntimeSnapshotProtocol)