from __future__ import annotations

from pathlib import Path

from netscope.context import ExecutionContext
from netscope.environment import EnvironmentDetector
from netscope.enums import DeviceType, ExecutionMode
from netscope.session import Session
from netscope.session_config import SessionConfig
from netscope.session_state import SessionState


def test_session_lifecycle(tmp_path: Path) -> None:
    context = ExecutionContext(
        mode=ExecutionMode.INFERENCE,
        device=DeviceType.CPU,
        root_dir=tmp_path,
        report_dir=tmp_path / "reports",
        artifact_dir=tmp_path / "artifacts",
        snapshot_dir=tmp_path / "snapshots",
    )
    environment = EnvironmentDetector.detect(metadata={"test": True})

    session = Session(
        name="test-session",
        config=SessionConfig(keep_workspace_temp=False),
        context=context,
        environment=environment,
        metadata={"suite": "session"},
    )

    assert session.session_state == SessionState.CREATED
    assert session.session_id
    assert session.workspace.context is context

    session.prepare()
    assert session.session_state == SessionState.PREPARED

    session.start()
    assert session.session_state == SessionState.RUNNING
    assert session.workspace.tempdir is not None

    session.stop()
    assert session.session_state == SessionState.STOPPED

    session.close()
    assert session.session_state == SessionState.CLOSED
    assert session.is_closed is True


def test_session_to_dict(tmp_path: Path) -> None:
    context = ExecutionContext(
        mode=ExecutionMode.TRAIN,
        device=DeviceType.CPU,
        root_dir=tmp_path,
        report_dir=tmp_path / "reports",
        artifact_dir=tmp_path / "artifacts",
        snapshot_dir=tmp_path / "snapshots",
    )

    session = Session(context=context)
    data = session.to_dict()

    assert data["session_id"] == session.session_id
    assert data["session_state"] == "created"
    assert data["workspace"]["resolver"]["root"] == str(tmp_path.resolve())