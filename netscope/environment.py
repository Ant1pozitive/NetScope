"""
Runtime environment discovery infrastructure.

This module captures information about the current host, Python runtime,
Torch installation, and selected execution device.
"""

from __future__ import annotations

import importlib
import importlib.util
import platform as platform_module
import socket
from dataclasses import dataclass, field, replace
from typing import Any

from ._version import __version__
from .constants import PACKAGE_NAME
from .enums import DeviceType


@dataclass(slots=True, frozen=True)
class PlatformInfo:
    """
    Operating-system and host-level environment information.
    """

    system: str
    release: str
    version: str
    machine: str
    processor: str
    architecture: str
    hostname: str
    python_version: str
    python_implementation: str
    platform: str

    @classmethod
    def detect(cls) -> PlatformInfo:
        """
        Detect the current platform.
        """

        return cls(
            system=platform_module.system(),
            release=platform_module.release(),
            version=platform_module.version(),
            machine=platform_module.machine(),
            processor=platform_module.processor(),
            architecture=platform_module.architecture()[0],
            hostname=socket.gethostname(),
            python_version=platform_module.python_version(),
            python_implementation=platform_module.python_implementation(),
            platform=platform_module.platform(),
        )

    def to_dict(self) -> dict[str, str]:
        """
        Serialize the platform info into a plain dictionary.
        """

        return {
            "system": self.system,
            "release": self.release,
            "version": self.version,
            "machine": self.machine,
            "processor": self.processor,
            "architecture": self.architecture,
            "hostname": self.hostname,
            "python_version": self.python_version,
            "python_implementation": self.python_implementation,
            "platform": self.platform,
        }


@dataclass(slots=True, frozen=True)
class TorchInfo:
    """
    Torch runtime information.

    The detection logic is intentionally defensive: if torch is not installed,
    the object still returns a valid non-error result.
    """

    available: bool
    version: str | None
    cuda_available: bool
    cuda_version: str | None
    cudnn_version: str | None
    mps_available: bool
    device_count: int
    device_names: tuple[str, ...]
    backend: str | None

    @classmethod
    def detect(cls) -> TorchInfo:
        """
        Detect torch availability and hardware backends.
        """

        if importlib.util.find_spec("torch") is None:
            return cls(
                available=False,
                version=None,
                cuda_available=False,
                cuda_version=None,
                cudnn_version=None,
                mps_available=False,
                device_count=0,
                device_names=(),
                backend=None,
            )

        torch = importlib.import_module("torch")

        cuda_available = bool(torch.cuda.is_available())
        mps_available = bool(
            getattr(torch.backends, "mps", None) is not None
            and torch.backends.mps.is_available()
        )

        device_count = int(torch.cuda.device_count()) if cuda_available else 0
        device_names = tuple(
            torch.cuda.get_device_name(index)
            for index in range(device_count)
        ) if cuda_available else ()

        cuda_version = getattr(torch.version, "cuda", None)
        cudnn_version_raw = None
        if getattr(torch.backends, "cudnn", None) is not None:
            cudnn_version_raw = torch.backends.cudnn.version()

        backend: str | None
        if cuda_available:
            backend = "cuda"
        elif mps_available:
            backend = "mps"
        else:
            backend = "cpu"

        return cls(
            available=True,
            version=getattr(torch, "__version__", None),
            cuda_available=cuda_available,
            cuda_version=cuda_version,
            cudnn_version=None if cudnn_version_raw is None else str(cudnn_version_raw),
            mps_available=mps_available,
            device_count=device_count,
            device_names=device_names,
            backend=backend,
        )

    def to_dict(self) -> dict[str, Any]:
        """
        Serialize the torch info into a JSON-friendly dictionary.
        """

        return {
            "available": self.available,
            "version": self.version,
            "cuda_available": self.cuda_available,
            "cuda_version": self.cuda_version,
            "cudnn_version": self.cudnn_version,
            "mps_available": self.mps_available,
            "device_count": self.device_count,
            "device_names": list(self.device_names),
            "backend": self.backend,
        }


@dataclass(slots=True, frozen=True)
class VersionInfo:
    """
    Version snapshot for the current runtime.
    """

    netscope: str
    python: str
    torch: str | None
    numpy: str | None
    platform: str

    @classmethod
    def detect(
        cls,
        *,
        torch_info: TorchInfo | None = None,
    ) -> VersionInfo:
        """
        Detect versions for the current runtime.
        """

        if torch_info is None:
            torch_info = TorchInfo.detect()

        numpy_version = None
        if importlib.util.find_spec("numpy") is not None:
            numpy = importlib.import_module("numpy")
            numpy_version = getattr(numpy, "__version__", None)

        return cls(
            netscope=__version__,
            python=platform_module.python_version(),
            torch=torch_info.version,
            numpy=numpy_version,
            platform=platform_module.platform(),
        )

    def to_dict(self) -> dict[str, str | None]:
        """
        Serialize the version info into a plain dictionary.
        """

        return {
            "netscope": self.netscope,
            "python": self.python,
            "torch": self.torch,
            "numpy": self.numpy,
            "platform": self.platform,
        }


@dataclass(slots=True, frozen=True)
class Environment:
    """
    Full runtime environment snapshot.
    """

    platform: PlatformInfo
    torch: TorchInfo
    versions: VersionInfo
    device: DeviceType
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def detect(
        cls,
        *,
        metadata: dict[str, Any] | None = None,
    ) -> Environment:
        """
        Detect the current runtime environment.
        """

        platform_info = PlatformInfo.detect()
        torch_info = TorchInfo.detect()
        version_info = VersionInfo.detect(torch_info=torch_info)
        device = DeviceResolver.resolve(torch_info=torch_info)

        return cls(
            platform=platform_info,
            torch=torch_info,
            versions=version_info,
            device=device,
            metadata=dict(metadata or {}),
        )

    def with_metadata(self, **kwargs: Any) -> Environment:
        """
        Return a copy with merged metadata.
        """

        merged = dict(self.metadata)
        merged.update(kwargs)
        return replace(self, metadata=merged)

    def to_dict(self) -> dict[str, Any]:
        """
        Serialize the environment into a JSON-friendly dictionary.
        """

        return {
            "package": PACKAGE_NAME,
            "platform": self.platform.to_dict(),
            "torch": self.torch.to_dict(),
            "versions": self.versions.to_dict(),
            "device": self.device.value,
            "metadata": dict(self.metadata),
        }


class DeviceResolver:
    """
    Resolve the most appropriate execution device for the current runtime.
    """

    @staticmethod
    def resolve(
        *,
        torch_info: TorchInfo | None = None,
        prefer_gpu: bool = True,
    ) -> DeviceType:
        """
        Resolve the device type using detected runtime capabilities.
        """

        if torch_info is None:
            torch_info = TorchInfo.detect()

        if not torch_info.available:
            return DeviceType.CPU

        if prefer_gpu and torch_info.cuda_available:
            return DeviceType.CUDA

        if torch_info.mps_available:
            return DeviceType.MPS

        if torch_info.cuda_available:
            return DeviceType.CUDA

        return DeviceType.CPU


class EnvironmentDetector:
    """
    High-level environment detector.
    """

    @staticmethod
    def detect(
        *,
        metadata: dict[str, Any] | None = None,
    ) -> Environment:
        """
        Detect the complete environment snapshot.
        """

        return Environment.detect(metadata=metadata)


__all__ = [
    "PlatformInfo",
    "TorchInfo",
    "VersionInfo",
    "Environment",
    "DeviceResolver",
    "EnvironmentDetector",
]