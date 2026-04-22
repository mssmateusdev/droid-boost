from __future__ import annotations

from PySide6.QtCore import QThread, Signal

from app.services.device_detection_service import DeviceDetectionService, DeviceReport


class DeviceDetectionThread(QThread):
    detected = Signal(object)
    failed = Signal(str)

    def __init__(self, service: DeviceDetectionService) -> None:
        super().__init__()
        self._service = service

    def run(self) -> None:
        try:
            report = self._service.detect()
        except Exception as exc:  # Defensive UI boundary.
            self.failed.emit(str(exc))
            return
        self.detected.emit(report)


class ADBReconnectThread(QThread):
    completed = Signal()
    failed = Signal(str)

    def __init__(self, service: DeviceDetectionService) -> None:
        super().__init__()
        self._service = service

    def run(self) -> None:
        try:
            self._service.restart_adb_server()
        except Exception as exc:  # Defensive UI boundary.
            self.failed.emit(str(exc))
            return
        self.completed.emit()
