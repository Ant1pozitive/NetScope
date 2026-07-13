from __future__ import annotations

from pathlib import Path

from netscope import Snapshot, SnapshotArtifact, SnapshotMetadata, SnapshotSummary


def test_snapshot_to_dict_and_json(tmp_path: Path) -> None:
    snapshot = Snapshot(
        metadata=SnapshotMetadata(
            inspector_name="demo",
            session_id="sess-001",
            session_state="running",
            target_type="dict",
            target_name="payload",
        ),
        summary=SnapshotSummary(
            model_name="example-model",
            model_type="dict",
            num_parameters=10,
            trainable_parameters=8,
            num_buffers=2,
            num_layers=3,
            trainable_ratio=0.8,
            notes="baseline snapshot",
        ),
        artifacts=(
            SnapshotArtifact(
                name="report",
                path=tmp_path / "report.json",
                kind="json",
                media_type="application/json",
            ),
        ),
        context={"mode": "inference"},
        environment={"device": "cpu"},
        session={"session_state": "running"},
        runtime_state={"running": True},
        target={"type": "dict", "repr": "{'x': 1}"},
        diagnostics={"health": {"score": 97}},
    )

    data = snapshot.to_dict()

    assert data["metadata"]["inspector_name"] == "demo"
    assert data["summary"]["model_name"] == "example-model"
    assert data["artifacts"][0]["name"] == "report"
    assert data["target"]["type"] == "dict"
    assert data["diagnostics"]["health"]["score"] == 97

    json_text = snapshot.to_json()
    assert '"snapshot_id"' in json_text

    saved = snapshot.save_json(tmp_path / "snapshot.json")
    assert saved.exists()


def test_snapshot_with_helpers() -> None:
    snapshot = Snapshot(
        metadata=SnapshotMetadata(
            inspector_name="demo",
            session_id="sess-002",
            session_state="prepared",
            target_type="list",
        )
    )

    updated = (
        snapshot
        .with_metadata(run="alpha")
        .with_section("graph", {"layers": 12})
        .with_target(type="list", length=3)
    )

    assert updated.metadata.tags["run"] == "alpha"
    assert updated.diagnostics["graph"]["layers"] == 12
    assert updated.target["length"] == 3