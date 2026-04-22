from __future__ import annotations

import sys
from collections.abc import Sequence

from app.adb.executor import ADBExecutor
from app.adb.queue import ADBCommandQueue
from app.core.logging import configure_logging
from app.services.adb_discovery_service import ADBDiscoveryService
from app.services.app_context import AppContext
from app.services.device_detection_service import DeviceDetectionService
from app.services.device_list_service import DeviceListService
from app.services.optimization_profile_service import OptimizationProfileService
from app.services.root_detection_service import RootDetectionService
from app.services.tweak_service import TweakService
from app.storage.snapshot_store import SnapshotStore
from app.storage.paths import AppPaths


def build_context() -> AppContext:
    paths = AppPaths.create()
    logger = configure_logging(paths.logs_dir)
    adb_discovery_service = ADBDiscoveryService()
    adb = adb_discovery_service.discover()
    adb_executor = ADBExecutor(adb.executable or "adb")
    adb_queue = ADBCommandQueue(adb_executor)
    device_list_service = DeviceListService(adb_executor)
    root_service = RootDetectionService(adb_executor)
    device_service = DeviceDetectionService(
        adb_executor,
        adb_discovery_service,
        device_list_service,
        root_service,
    )
    snapshot_store = SnapshotStore(paths.snapshots_dir)
    profile_service = OptimizationProfileService(adb_executor, device_service, snapshot_store)
    tweak_service = TweakService(adb_executor, device_service)
    return AppContext(
        paths=paths,
        logger=logger,
        adb_discovery_service=adb_discovery_service,
        adb_executor=adb_executor,
        adb_queue=adb_queue,
        device_list_service=device_list_service,
        root_service=root_service,
        device_service=device_service,
        profile_service=profile_service,
        tweak_service=tweak_service,
    )


def run(argv: Sequence[str] | None = None) -> int:
    from PySide6.QtWidgets import QApplication

    from app.ui.main_window import MainWindow
    from app.ui.theme import apply_dark_theme

    app = QApplication(list(argv or sys.argv))
    app.setApplicationName("DroidBoost")
    app.setOrganizationName("DroidBoost")
    apply_dark_theme(app)

    context = build_context()
    app.aboutToQuit.connect(context.adb_queue.shutdown)
    window = MainWindow(context)
    window.show()
    return app.exec()
