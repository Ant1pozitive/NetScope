from __future__ import annotations

from pathlib import Path

from netscope.resources import PathResolver


def test_path_resolver_from_root(tmp_path: Path) -> None:
    resolver = PathResolver.from_config(root=tmp_path)

    assert resolver.root == tmp_path.resolve()
    assert resolver.reports_dir() == (tmp_path / "reports").resolve()
    assert resolver.artifacts_dir() == (tmp_path / "artifacts").resolve()
    assert resolver.snapshots_dir() == (tmp_path / "snapshots").resolve()


def test_path_resolver_ensure_parent(tmp_path: Path) -> None:
    resolver = PathResolver.from_config(root=tmp_path)
    target = resolver.ensure_parent("reports/run1/report.html")

    assert target == (tmp_path / "reports" / "run1" / "report.html").resolve()
    assert target.parent.exists()