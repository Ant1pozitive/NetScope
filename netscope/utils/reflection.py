"""
Reflection helpers.
"""

from __future__ import annotations

import inspect
from types import ModuleType
from typing import Any


def public_members(obj: Any) -> dict[str, Any]:
    """
    Return public members of an object.
    """

    result: dict[str, Any] = {}

    for name, value in inspect.getmembers(obj):

        if name.startswith("_"):
            continue

        result[name] = value

    return result


def module_name(module: ModuleType) -> str:
    """
    Return fully qualified module name.
    """

    return module.__name__


def qualified_name(obj: Any) -> str:
    """
    Return fully qualified object name.
    """

    cls = obj.__class__

    return f"{cls.__module__}.{cls.__qualname__}"