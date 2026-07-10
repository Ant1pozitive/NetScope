"""
Validation helpers.
"""

from __future__ import annotations


def ensure(
    condition: bool,
    message: str,
) -> None:

    if not condition:
        raise ValueError(message)