from __future__ import annotations

from dataclasses import dataclass

from app.core.enums import ADBAvailability, DeviceConnectionStatus


@dataclass(frozen=True)
class ADBInstallation:
    availability: ADBAvailability
    executable: str | None = None
    source: str = "not_found"
    version: str | None = None
    message: str = ""


@dataclass(frozen=True)
class ADBDeviceEntry:
    serial: str
    status: DeviceConnectionStatus
    product: str | None = None
    model: str | None = None
    device: str | None = None
    transport_id: str | None = None
    raw: str = ""


@dataclass(frozen=True)
class ADBDeviceScan:
    devices: list[ADBDeviceEntry]
    error: str | None = None
