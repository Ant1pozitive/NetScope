from __future__ import annotations

from netscope.environment import (
    DeviceResolver,
    Environment,
    EnvironmentDetector,
    PlatformInfo,
    TorchInfo,
    VersionInfo,
)
from netscope.enums import DeviceType


def test_platform_info_detect() -> None:
    info = PlatformInfo.detect()

    assert info.system
    assert info.hostname
    assert info.python_version
    assert info.platform


def test_torch_info_detect() -> None:
    info = TorchInfo.detect()

    assert isinstance(info.available, bool)
    assert isinstance(info.cuda_available, bool)
    assert isinstance(info.mps_available, bool)
    assert info.device_count >= 0
    assert isinstance(info.device_names, tuple)


def test_version_info_detect() -> None:
    torch_info = TorchInfo.detect()
    info = VersionInfo.detect(torch_info=torch_info)

    assert info.netscope
    assert info.python
    assert info.platform


def test_environment_detect() -> None:
    env = EnvironmentDetector.detect(metadata={"run": "test"})

    assert isinstance(env, Environment)
    assert env.platform.system
    assert env.versions.netscope
    assert env.device in {
        DeviceType.CPU,
        DeviceType.CUDA,
        DeviceType.MPS,
    }
    assert env.metadata["run"] == "test"


def test_environment_to_dict() -> None:
    env = EnvironmentDetector.detect()
    data = env.to_dict()

    assert data["platform"]["system"]
    assert data["versions"]["netscope"]
    assert data["device"] in {"cpu", "cuda", "mps"}


def test_device_resolver_returns_device_type() -> None:
    device = DeviceResolver.resolve()

    assert device in {
        DeviceType.CPU,
        DeviceType.CUDA,
        DeviceType.MPS,
    }