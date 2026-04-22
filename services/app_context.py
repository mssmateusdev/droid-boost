from __future__ import annotations

import logging
from dataclasses import dataclass

from app.adb.executor import ADBExecutor
from app.adb.queue import ADBCommandQueue
from app.services.adb_discovery_service import ADBDiscoveryService
from app.services.device_detection_service import DeviceDetectionService
from app.services.device_list_service import DeviceListService
from app.services.optimization_profile_service import OptimizationProfileService
from app.services.root_detection_service import RootDetectionService
from app.services.tweak_service import TweakService
from app.storage.paths import AppPaths


@dataclass(frozen=True)
class AppContext:
    paths: AppPaths
    logger: logging.Logger
    adb_discovery_service: ADBDiscoveryService
    adb_executor: ADBExecutor
    adb_queue: ADBCommandQueue
    device_list_service: DeviceListService
    root_service: RootDetectionService
    device_service: DeviceDetectionService
    profile_service: OptimizationProfileService
    tweak_service: TweakService
