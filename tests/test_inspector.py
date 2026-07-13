from __future__ import annotations

from pathlib import Path

from netscope import ExecutionContext, Inspector, InspectorConfig, SessionConfig
from netscope.enums import DeviceType, ExecutionMode


def test_inspector_inspect_returns_result(tmp_path: Path) -> None:
    context = ExecutionContext(
        mode=ExecutionMode.INFERENCE,
        device=DeviceType.CPU,
        root_dir=tmp_path,
        report_dir=tmp_path / "reports",
        artifact_dir=tmp_path / "artifacts",
        snapshot_dir=tmp_path / "snapshots",
    )

    inspector = Inspector(
        context=context,
        config=InspectorConfig(
            session_name="demo-inspection",
            session_config=SessionConfig(
                keep_workspace_temp=False,
            ),
        ),
    )

    result = inspector.inspect(
        target={"hello": "world"},
        metadata={"run": "alpha"},
    )

    assert result.success is True
    assert result.target_type == "dict"
    assert result.target["type"] == "dict"
    assert result.session_id
    assert result.session["session_state"] == "closed"
    assert result.session["workspace"]["resolver"]["root"] == str(tmp_path.resolve())
    assert result.metadata["run"] == "alpha"
    assert inspector.last_result is result


def test_inspector_result_save_json(tmp_path: Path) -> None:
    context = ExecutionContext(
        mode=ExecutionMode.INFERENCE,
        device=DeviceType.CPU,
        root_dir=tmp_path,
        report_dir=tmp_path / "reports",
        artifact_dir=tmp_path / "artifacts",
        snapshot_dir=tmp_path / "snapshots",
    )

    inspector = Inspector(context=context)
    result = inspector.inspect(target=[1, 2, 3])

    destination = tmp_path / "reports" / "inspection.json"
    saved = result.save_json(destination)

    assert saved.exists()
    assert saved.read_text(encoding="utf-8")