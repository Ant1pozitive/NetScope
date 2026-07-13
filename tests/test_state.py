from __future__ import annotations

from pathlib import Path

from netscope.context import ExecutionContext
from netscope.environment import EnvironmentDetector
from netscope.enums import DeviceType, ExecutionMode
from netscope.state import RuntimeState


def test_runtime_state_attach_environment_and_context(tmp_path: Path) -> None:
    context = ExecutionContext(
        mode=ExecutionMode.INFERENCE,
        device=DeviceType.CPU,
        root_dir=tmp_path,
        report_dir=tmp_path / "reports",
        artifact_dir=tmp_path / "artifacts",
        snapshot_dir=tmp_path / "snapshots",
    )
    environment = EnvironmentDetector.detect(metadata={"source": "test"})

    state = RuntimeState()
    state.attach_context(context)
    state.attach_environment(environment)
    state.set_flag("ready", True)

    data = state.to_dict()

    assert data["context"]["mode"] == "inference"
    assert data["environment"]["device"] in {"cpu", "cuda", "mps"}
    assert data["flags"]["ready"] is True