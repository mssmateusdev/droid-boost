from __future__ import annotations

from PySide6.QtCore import QThread, Signal

from app.services.optimization_profile_service import OptimizationProfileService


class ProfileApplyThread(QThread):
    completed = Signal(object)
    failed = Signal(str)

    def __init__(self, service: OptimizationProfileService, profile_key: str) -> None:
        super().__init__()
        self._service = service
        self._profile_key = profile_key

    def run(self) -> None:
        try:
            self.completed.emit(self._service.apply_profile(self._profile_key))
        except Exception as exc:
            self.failed.emit(str(exc))


class ProfileRestoreThread(QThread):
    completed = Signal(object)
    failed = Signal(str)

    def __init__(
        self,
        service: OptimizationProfileService,
        profile_key: str,
        *,
        restore_defaults: bool,
    ) -> None:
        super().__init__()
        self._service = service
        self._profile_key = profile_key
        self._restore_defaults = restore_defaults

    def run(self) -> None:
        try:
            if self._restore_defaults:
                self.completed.emit(self._service.restore_defaults(self._profile_key))
            else:
                self.completed.emit(self._service.restore_latest_snapshot(self._profile_key))
        except Exception as exc:
            self.failed.emit(str(exc))

