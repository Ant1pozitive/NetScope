"""
Package metadata.
"""

from __future__ import annotations

from ._version import __version__

PACKAGE_NAME = "NetScope"

AUTHOR = "NetScope Developers"

LICENSE = "MIT"

DESCRIPTION = (
    "Universal diagnostics platform for neural networks."
)

HOMEPAGE = "https://github.com/netscope/netscope"

API_VERSION = "v1"

VERSION = __version__

__all__ = [
    "PACKAGE_NAME",
    "AUTHOR",
    "LICENSE",
    "DESCRIPTION",
    "HOMEPAGE",
    "API_VERSION",
    "VERSION",
]