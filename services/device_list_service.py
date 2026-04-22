from __future__ import annotations

from app.adb.discovery import ADBDeviceDiscovery
from app.adb.executor import ADBExecutor
from app.domain.adb import ADBDeviceEntry, ADBDeviceScan


class DeviceListService:
    """Lists Android devices through the ADB engine layer."""

    def __init__(self, executor: ADBExecutor) -> None:
        self._discovery = ADBDeviceDiscovery(executor)

    def scan(self) -> ADBDeviceScan:
        return self._discovery.scan()

    def list_devices(self) -> list[ADBDeviceEntry]:
        return self.scan().devices
