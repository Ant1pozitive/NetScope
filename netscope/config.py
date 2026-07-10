"""
Global configuration system.

The configuration is immutable by default and shared across the
entire NetScope runtime.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from pathlib import Path


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
    benchmark: bool = False
    num_workers: int = 0


@dataclass(slots=True, frozen=True)
class ExportConfig:
    save_json: bool = True
    save_html: bool = True
    compress: bool = False


@dataclass(slots=True, frozen=True)
class PathsConfig:
    root: Path = Path.cwd()
    reports: str = "reports"
    artifacts: str = "artifacts"
    snapshots: str = "snapshots"


@dataclass(slots=True, frozen=True)
class NetScopeConfig:
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    runtime: RuntimeConfig = field(default_factory=RuntimeConfig)
    export: ExportConfig = field(default_factory=ExportConfig)
    paths: PathsConfig = field(default_factory=PathsConfig)


class ConfigManager:
    """
    Global configuration manager.

    The manager owns exactly one configuration instance.
    """

    def __init__(self) -> None:
        self._config = NetScopeConfig()

    @property
    def config(self) -> NetScopeConfig:
        return self._config

    def replace(self, **kwargs: object) -> NetScopeConfig:
        self._config = replace(self._config, **kwargs)
        return self._config

    def reset(self) -> None:
        self._config = NetScopeConfig()


CONFIG = ConfigManager()

__all__ = [
    "LoggingConfig",
    "RuntimeConfig",
    "ExportConfig",
    "PathsConfig",
    "NetScopeConfig",
    "ConfigManager",
    "CONFIG",
]