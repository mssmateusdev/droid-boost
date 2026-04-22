from __future__ import annotations

from PySide6.QtCore import QThread, Signal

from app.services.tweak_service import TweakService


class TweakCatalogThread(QThread):
    completed = Signal(object)
    failed = Signal(str)

    def __init__(self, service: TweakService) -> None:
        super().__init__()
        self._service = service

    def run(self) -> None:
        try:
            self.completed.emit(self._service.catalog())
        except Exception as exc:
            self.failed.emit(str(exc))


class TweakExecuteThread(QThread):
    completed = Signal(object)
    failed = Signal(str)

    def __init__(self, service: TweakService, tweak_key: str) -> None:
        super().__init__()
        self._service = service
        self._tweak_key = tweak_key

    def run(self) -> None:
        try:
            self.completed.emit(self._service.execute(self._tweak_key))
        except Exception as exc:
            self.failed.emit(str(exc))

