from __future__ import annotations

from pathlib import Path

from netscope.context import ExecutionContext
from netscope.enums import DeviceType, ExecutionMode
from netscope.resources import Workspace


def test_workspace_initialization_and_artifacts(tmp_path: Path) -> None:
    context = ExecutionContext(
        mode=ExecutionMode.INFERENCE,
        device=DeviceType.CPU,
        root_dir=tmp_path,
        report_dir=tmp_path / "reports",
        artifact_dir=tmp_path / "artifacts",
        snapshot_dir=tmp_path / "snapshots",
    )

    workspace = Workspace(context=context, root_dir=tmp_path)
    workspace.initialize()
    workspace.start()

    text_path = workspace.save_text("summary", "hello world", "reports/summary.txt")
    json_path = workspace.save_json("meta", {"ok": True}, "artifacts/meta.json")

    assert text_path.exists()
    assert json_path.exists()
    assert "summary" in workspace.list_artifacts()
    assert "meta" in workspace.list_artifacts()

    workspace.stop()
    workspace.dispose()


def test_workspace_cache_roundtrip(tmp_path: Path) -> None:
    workspace = Workspace(root_dir=tmp_path)

    workspace.cache_set("x", 123)

    assert workspace.cache_get("x") == 123