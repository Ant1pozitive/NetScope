"""
Reusable mixins.
"""

from __future__ import annotations

from typing import Any


class ReprMixin:

    def __repr__(self) -> str:

        fields = []

        for key, value in vars(self).items():

            fields.append(f"{key}={value!r}")

        joined = ", ".join(fields)

        return f"{self.__class__.__name__}({joined})"


class DictMixin:

    def to_dict(self) -> dict[str, Any]:

        return dict(vars(self))