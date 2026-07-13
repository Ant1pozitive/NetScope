from __future__ import annotations

from netscope.resources import TempDirectory


def test_tempdir_cleanup() -> None:
    tempdir = TempDirectory()

    path = tempdir.path
    assert path.exists()

    tempdir.cleanup()
    assert tempdir.closed is True
    assert path.exists() is False