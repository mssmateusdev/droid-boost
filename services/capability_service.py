from __future__ import annotations

from app.core.enums import DeviceConnectionStatus
from app.domain.capabilities import DeviceCapabilities
from app.domain.device import DeviceInfo
from app.domain.root import RootInfo


class CapabilityService:
    @staticmethod
    def from_device(device: DeviceInfo, root: RootInfo) -> DeviceCapabilities:
        connected = device.status == DeviceConnectionStatus.CONNECTED
        root_ready = connected and root.operational
        return DeviceCapabilities(
            can_use_root_commands=root_ready,
            can_manage_packages=connected,
            can_change_animations=connected,
            can_clear_cache=connected,
            can_run_advanced_profiles=root_ready,
            can_read_diagnostics=connected,
        )

