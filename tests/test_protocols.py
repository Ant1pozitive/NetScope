from __future__ import annotations

from pathlib import Path

from netscope import (
    ExecutionContext,
    Inspector,
    Snapshot,
    SnapshotArtifact,
    SnapshotBuilder,
    SnapshotMetadata,
    SnapshotSummary,
)
from netscope.protocols import (
    InspectionResultProtocol,
    SnapshotBuilderProtocol,
    SnapshotProtocol,
)


def test_inspection_result_protocol_compatibility(tmp_path: Path) -> None:
    context = ExecutionContext.from_config(metadata={"test": True})
    inspector = Inspector(context=context)
    result = inspector.inspect({"hello": "world"})

    assert isinstance(result, InspectionResultProtocol)


def test_snapshot_protocol_compatibility(tmp_path: Path) -> None:
    snapshot = Snapshot(
        metadata=SnapshotMetadata(
            inspector_name="demo",
            session_id="sess-001",
            session_state="running",
            target_type="dict",
        ),
        summary=SnapshotSummary(model_name="example", model_type="dict"),
        artifacts=(
            SnapshotArtifact(
                name="report",
                path=tmp_path / "report.json",
            ),
        ),
    )

    assert isinstance(snapshot, SnapshotProtocol)


def test_snapshot_builder_protocol_compatibility() -> None:
    builder = SnapshotBuilder()

    assert isinstance(builder, SnapshotBuilderProtocol)