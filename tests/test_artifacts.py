from __future__ import annotations

import json
from pathlib import Path

from netscope.resources import ArtifactManager


def test_artifact_manager_write_text(tmp_path: Path) -> None:
    manager = ArtifactManager(root=tmp_path)

    path = manager.write_text("report", "hello", "report.txt")

    assert path.exists()
    assert path.read_text(encoding="utf-8") == "hello"
    assert manager.get("report") == path


def test_artifact_manager_write_json(tmp_path: Path) -> None:
    manager = ArtifactManager(root=tmp_path)

    path = manager.write_json("payload", {"x": 1}, "payload.json")

    assert json.loads(path.read_text(encoding="utf-8")) == {"x": 1}
    assert manager.contains("payload") is True


def test_artifact_manager_snapshot(tmp_path: Path) -> None:
    manager = ArtifactManager(root=tmp_path)
    manager.write_bytes("blob", b"abc", "blob.bin")

    snapshot = manager.snapshot()

    assert snapshot["blob"].endswith("blob.bin")