from __future__ import annotations

from pathlib import Path

from netscope.context import ExecutionContext
from netscope.enums import DeviceType, ExecutionMode


def test_context_to_dict(tmp_path: Path) -> None:
    context = ExecutionContext(
        mode=ExecutionMode.TRAIN,
        device=DeviceType.CPU,
        seed=42,
        root_dir=tmp_path,
        report_dir=tmp_path / "reports",
        artifact_dir=tmp_path / "artifacts",
        snapshot_dir=tmp_path / "snapshots",
        metadata={"run": "a"},
    )

    data = context.to_dict()

    assert data["mode"] == "train"
    assert data["device"] == "cpu"
    assert data["seed"] == 42
    assert data["root_dir"] == str(tmp_path)


def test_context_with_metadata(tmp_path: Path) -> None:
    context = ExecutionContext(
        root_dir=tmp_path,
        report_dir=tmp_path / "reports",
        artifact_dir=tmp_path / "artifacts",
        snapshot_dir=tmp_path / "snapshots",
    )

    updated = context.with_metadata(epoch=3)

    assert updated.metadata["epoch"] == 3
    assert "epoch" not in context.metadata