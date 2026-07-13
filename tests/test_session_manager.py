from __future__ import annotations

from pathlib import Path

from netscope.context import ExecutionContext
from netscope.environment import EnvironmentDetector
from netscope.enums import DeviceType, ExecutionMode
from netscope.session_manager import SessionManager


def test_session_manager_create_start_close(tmp_path: Path) -> None:
    context = ExecutionContext(
        mode=ExecutionMode.INFERENCE,
        device=DeviceType.CPU,
        root_dir=tmp_path,
        report_dir=tmp_path / "reports",
        artifact_dir=tmp_path / "artifacts",
        snapshot_dir=tmp_path / "snapshots",
    )
    environment = EnvironmentDetector.detect(metadata={"test": True})

    manager = SessionManager()
    session = manager.create(
        name="managed-session",
        context=context,
        environment=environment,
        autostart=False,
    )

    assert session.session_id in manager
    assert manager.get(session.session_id) is session
    assert manager.active_session is None

    manager.start(session.session_id)
    assert manager.active_session is session
    assert session.is_running is True

    manager.stop(session.session_id)
    assert manager.active_session is None

    manager.close(session.session_id)
    assert session.session_id not in manager
    assert session.is_closed is True


def test_session_manager_snapshot(tmp_path: Path) -> None:
    context = ExecutionContext(
        mode=ExecutionMode.INFERENCE,
        device=DeviceType.CPU,
        root_dir=tmp_path,
        report_dir=tmp_path / "reports",
        artifact_dir=tmp_path / "artifacts",
        snapshot_dir=tmp_path / "snapshots",
    )

    manager = SessionManager()
    session = manager.create(context=context)

    snapshot = manager.snapshot()

    assert session.session_id in snapshot
    assert snapshot[session.session_id]["session_state"] == "created"