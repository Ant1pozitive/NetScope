"""
Global configuration models.

Configuration is intentionally immutable.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class LoggingConfig:
    level: str = "INFO"
    enable_console: bool = True
    enable_file: bool = False
    filename: str = "netscope.log"


@dataclass(slots=True, frozen=True)
class RuntimeConfig:
    use_cuda: bool = True
    deterministic: bool = False
    num_workers: int = 0


@dataclass(slots=True, frozen=True)
class ExportConfig:
    save_json: bool = True
    save_html: bool = True
    compress: bool = False


@dataclass(slots=True, frozen=True)
class NetScopeConfig:
    logging: LoggingConfig = LoggingConfig()
    runtime: RuntimeConfig = RuntimeConfig()
    export: ExportConfig = ExportConfig()


DEFAULT_CONFIG = NetScopeConfig()

__all__ = [
    "LoggingConfig",
    "RuntimeConfig",
    "ExportConfig",
    "NetScopeConfig",
    "DEFAULT_CONFIG",
]