from __future__ import annotations

from pathlib import Path

from netscope import (
    ExecutionContext,
    Inspector,
    Session,
    SessionConfig,
    SnapshotBuilder,
)
from netscope.enums import DeviceType, ExecutionMode


def test_snapshot_builder_from_session_collects_artifacts(tmp_path: Path) -> None:
    context = ExecutionContext(
        mode=ExecutionMode.INFERENCE,
        device=DeviceType.CPU,
        root_dir=tmp_path,
        report_dir=tmp_path / "reports",
        artifact_dir=tmp_path / "artifacts",
        snapshot_dir=tmp_path / "snapshots",
    )

    session = Session(
        name="builder-session",
        config=SessionConfig(keep_workspace_temp=False),
        context=context,
    )
    session.prepare()
    session.workspace.save_text("summary", "hello", "reports/summary.txt")

    builder = SnapshotBuilder()
    snapshot = builder.from_session(
        session,
        target={"type": "dict", "name": "payload"},
        metadata={"run": "alpha"},
    )

    assert snapshot.metadata.session_id == session.session_id
    assert snapshot.metadata.session_state == "prepared"
    assert snapshot.summary.model_type == "dict"
    assert snapshot.summary.model_name == "payload"
    assert snapshot.metadata.tags["run"] == "alpha"
    assert any(artifact.name == "summary" for artifact in snapshot.artifacts)
    assert snapshot.diagnostics["builder"]["framework"] == "pytorch"
    assert snapshot.diagnostics["target"]["type"] == "dict"


def test_snapshot_builder_from_result(tmp_path: Path) -> None:
    context = ExecutionContext(
        mode=ExecutionMode.INFERENCE,
        device=DeviceType.CPU,
        root_dir=tmp_path,
        report_dir=tmp_path / "reports",
        artifact_dir=tmp_path / "artifacts",
        snapshot_dir=tmp_path / "snapshots",
    )

    inspector = Inspector(context=context)
    result = inspector.inspect({"hello": "world"})

    snapshot = SnapshotBuilder().from_result(result)

    assert snapshot.snapshot_id == result.inspection_id
    assert snapshot.metadata.inspector_name == result.inspector_name
    assert snapshot.summary.model_type == "dict"
    assert snapshot.session_id == result.session_id
    assert snapshot.target_type == "dict"
    assert snapshot.is_completed is True