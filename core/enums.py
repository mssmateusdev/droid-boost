from __future__ import annotations

from enum import StrEnum


class ADBAvailability(StrEnum):
    UNKNOWN = "unknown"
    AVAILABLE = "available"
    MISSING = "missing"


class DeviceConnectionStatus(StrEnum):
    UNKNOWN = "unknown"
    NOT_FOUND = "not_found"
    CONNECTED = "connected"
    UNAUTHORIZED = "unauthorized"
    OFFLINE = "offline"
    RECOVERY = "recovery"
    SIDELOAD = "sideload"


class RootState(StrEnum):
    UNKNOWN = "unknown"
    DETECTED = "detected"
    NOT_DETECTED = "not_detected"
    UNAVAILABLE = "unavailable"


class CommandOutcome(StrEnum):
    SUCCESS = "success"
    ERROR = "error"
    TIMEOUT = "timeout"
    ADB_MISSING = "adb_missing"
    DEVICE_NOT_FOUND = "device_not_found"
    DEVICE_UNAUTHORIZED = "device_unauthorized"
    DEVICE_OFFLINE = "device_offline"
    ROOT_UNAVAILABLE = "root_unavailable"
