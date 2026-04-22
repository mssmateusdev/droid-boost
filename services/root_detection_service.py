from __future__ import annotations

from app.adb.executor import ADBExecutor
from app.domain.root import RootInfo


class RootDetectionService:
    def __init__(self, executor: ADBExecutor) -> None:
        self._executor = executor

    def detect(self, serial: str) -> RootInfo:
        return self._executor.probe_root(serial)
