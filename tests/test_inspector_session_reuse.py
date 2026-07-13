from __future__ import annotations

from pathlib import Path

from netscope import ExecutionContext, Inspector, Session, SessionConfig
from netscope.enums import DeviceType, ExecutionMode


def test_inspector_reuses_external_session_without_closing_it(tmp_path: Path) -> None:
    context = ExecutionContext(
        mode=ExecutionMode.INFERENCE,
        device=DeviceType.CPU,
        root_dir=tmp_path,
        report_dir=tmp_path / "reports",
        artifact_dir=tmp_path / "artifacts",
        snapshot_dir=tmp_path / "snapshots",
    )

    session = Session(
        name="external-session",
        config=SessionConfig(keep_workspace_temp=False),
        context=context,
    )

    inspector = Inspector(context=context)

    result = inspector.inspect(
        target={"x": 1},
        session=session,
    )

    assert result.success is True
    assert session.is_closed is False
    assert session.session_id == result.session_id
    assert inspector.session is session