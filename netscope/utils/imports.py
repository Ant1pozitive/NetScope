"""
Dynamic import helpers.
"""

from __future__ import annotations

import importlib
from typing import Any


def import_module(name: str):
    """
    Import module by name.
    """

    return importlib.import_module(name)


def import_object(path: str) -> Any:
    """
    Import object from dotted path.

    Example
    -------
    torch.nn.Linear
    """

    module_name, object_name = path.rsplit(".", 1)

    module = importlib.import_module(module_name)

    return getattr(module, object_name)