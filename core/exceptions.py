from __future__ import annotations


class DroidBoostError(Exception):
    """Base application error."""


class ADBError(DroidBoostError):
    """Base error for ADB operations."""


class ADBNotFoundError(ADBError):
    """Raised when the adb executable cannot be found."""


class ADBTimeoutError(ADBError):
    """Raised when an adb operation times out."""


class DeviceUnavailableError(DroidBoostError):
    """Raised when an operation needs a connected authorized device."""


class RootRequiredError(DroidBoostError):
    """Raised when a feature requires root but root is not operational."""

