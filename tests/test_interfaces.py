from __future__ import annotations

import json
from pathlib import Path

from netscope.context import ExecutionContext
from netscope.enums import DeviceType, ExecutionMode
from netscope.interfaces import (
    BaseAnalyzer,
    BaseCollector,
    BaseExporter,
    BasePlugin,
    BaseSerializer,
)


class DummyCollector(BaseCollector):
    def collect(
        self,
        model: object,
        *,
        context: ExecutionContext | None = None,
    ) -> dict[str, object]:
        return {
            "model_type": type(model).__name__,
            "context_mode": None if context is None else context.mode.value,
        }


class DummyAnalyzer(BaseAnalyzer):
    def analyze(
        self,
        target: object,
        *,
        context: ExecutionContext | None = None,
    ) -> dict[str, object]:
        return {
            "target_type": type(target).__name__,
            "context_device": None if context is None else context.device.value,
        }


class DummyPlugin(BasePlugin):
    pass


class DummyExporter(BaseExporter):
    def export(
        self,
        payload: object,
        destination: Path | str,
        *,
        context: ExecutionContext | None = None,
    ) -> Path:
        path = Path(destination)
        path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        return path


class DummySerializer(BaseSerializer):
    def serialize(
        self,
        payload: object,
        *,
        context: ExecutionContext | None = None,
    ) -> bytes:
        return json.dumps(payload, ensure_ascii=False).encode("utf-8")

    def deserialize(
        self,
        data: bytes,
        *,
        context: ExecutionContext | None = None,
    ) -> object:
        return json.loads(data.decode("utf-8"))


def test_collector_collects(tmp_path: Path) -> None:
    context = ExecutionContext(
        mode=ExecutionMode.INFERENCE,
        device=DeviceType.CPU,
        root_dir=tmp_path,
        report_dir=tmp_path / "reports",
        artifact_dir=tmp_path / "artifacts",
        snapshot_dir=tmp_path / "snapshots",
    )
    collector = DummyCollector(name="dummy_collector", context=context)

    result = collector.collect(object(), context=context)

    assert result["model_type"] == "object"
    assert result["context_mode"] == "inference"


def test_analyzer_analyzes(tmp_path: Path) -> None:
    context = ExecutionContext(
        mode=ExecutionMode.TRAIN,
        device=DeviceType.CPU,
        root_dir=tmp_path,
        report_dir=tmp_path / "reports",
        artifact_dir=tmp_path / "artifacts",
        snapshot_dir=tmp_path / "snapshots",
    )
    analyzer = DummyAnalyzer(name="dummy_analyzer", context=context)

    result = analyzer.analyze(object(), context=context)

    assert result["target_type"] == "object"
    assert result["context_device"] == "cpu"


def test_plugin_activate_deactivate(tmp_path: Path) -> None:
    context = ExecutionContext(
        mode=ExecutionMode.INFERENCE,
        device=DeviceType.CPU,
        root_dir=tmp_path,
        report_dir=tmp_path / "reports",
        artifact_dir=tmp_path / "artifacts",
        snapshot_dir=tmp_path / "snapshots",
    )
    plugin = DummyPlugin(name="dummy_plugin", context=context)

    plugin.activate()

    assert plugin.is_active_plugin is True

    plugin.deactivate()

    assert plugin.is_active_plugin is False


def test_exporter_exports(tmp_path: Path) -> None:
    exporter = DummyExporter(name="dummy_exporter")

    destination = tmp_path / "payload.json"
    result = exporter.export({"a": 1}, destination)

    assert result == destination
    assert destination.exists()
    assert destination.read_text(encoding="utf-8") == '{"a": 1}'


def test_serializer_roundtrip() -> None:
    serializer = DummySerializer(name="dummy_serializer")

    data = serializer.serialize({"x": 1})
    payload = serializer.deserialize(data)

    assert payload == {"x": 1}