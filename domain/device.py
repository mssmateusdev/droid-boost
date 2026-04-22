from __future__ import annotations

from dataclasses import dataclass

from app.core.enums import DeviceConnectionStatus


@dataclass(frozen=True)
class MemoryInfo:
    total_kb: int | None = None
    available_kb: int | None = None
    free_kb: int | None = None

    @property
    def total_gb(self) -> float | None:
        if self.total_kb is None:
            return None
        return self.total_kb / 1024 / 1024

    @property
    def available_gb(self) -> float | None:
        if self.available_kb is None:
            return None
        return self.available_kb / 1024 / 1024


@dataclass(frozen=True)
class StorageInfo:
    total_kb: int
    used_kb: int
    available_kb: int

    @property
    def total_gb(self) -> float:
        return self.total_kb / 1024 / 1024

    @property
    def used_gb(self) -> float:
        return self.used_kb / 1024 / 1024

    @property
    def available_gb(self) -> float:
        return self.available_kb / 1024 / 1024


@dataclass(frozen=True)
class DeviceInfo:
    serial: str | None
    status: DeviceConnectionStatus
    model: str | None = None
    manufacturer: str | None = None
    android_version: str | None = None
    api_level: str | None = None
    abi: str | None = None
    ram_total_kb: int | None = None
    memory: MemoryInfo | None = None
    storage: StorageInfo | None = None
    battery_level: int | None = None

    @property
    def display_name(self) -> str:
        pieces = [self.manufacturer, self.model]
        name = " ".join(piece for piece in pieces if piece)
        return name or "Unknown Android device"

    @property
    def ram_total_gb(self) -> float | None:
        if self.memory and self.memory.total_gb is not None:
            return self.memory.total_gb
        if self.ram_total_kb is None:
            return None
        return self.ram_total_kb / 1024 / 1024
