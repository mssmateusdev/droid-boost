from __future__ import annotations

from dataclasses import dataclass, field

from app.adb.executor import ADBExecutor
from app.core.constants import QUICK_ADB_TIMEOUT_SECONDS
from app.core.enums import ADBAvailability, DeviceConnectionStatus, RootState
from app.domain.adb import ADBInstallation
from app.domain.capabilities import DeviceCapabilities
from app.domain.device import DeviceInfo, MemoryInfo, StorageInfo
from app.domain.root import RootInfo
from app.services.adb_discovery_service import ADBDiscoveryService
from app.services.capability_service import CapabilityService
from app.services.device_list_service import DeviceListService
from app.services.root_detection_service import RootDetectionService


@dataclass(frozen=True)
class DeviceReport:
    adb: ADBInstallation
    adb_availability: ADBAvailability
    device: DeviceInfo
    root: RootInfo
    capabilities: DeviceCapabilities
    messages: tuple[str, ...] = field(default_factory=tuple)

    @property
    def ready(self) -> bool:
        return (
            self.adb_availability == ADBAvailability.AVAILABLE
            and self.device.status == DeviceConnectionStatus.CONNECTED
        )


class DeviceDetectionService:
    def __init__(
        self,
        executor: ADBExecutor,
        adb_discovery_service: ADBDiscoveryService,
        device_list_service: DeviceListService,
        root_service: RootDetectionService,
    ) -> None:
        self._executor = executor
        self._adb_discovery_service = adb_discovery_service
        self._device_list_service = device_list_service
        self._root_service = root_service
        self._capability_service = CapabilityService()

    def detect(self) -> DeviceReport:
        adb = self._resolve_adb_installation()
        if adb.executable:
            self._executor.set_adb_path(adb.executable)
        else:
            return self._empty_report(
                adb,
                DeviceConnectionStatus.NOT_FOUND,
                adb.message,
            )

        version = self._executor.run(
            ["version"],
            timeout_seconds=QUICK_ADB_TIMEOUT_SECONDS,
            label="adb version",
        )

        if not version.ok:
            adb = ADBInstallation(
                availability=ADBAvailability.MISSING,
                executable=adb.executable,
                source=adb.source,
                version=None,
                message=version.stderr.strip() or "ADB did not respond correctly.",
            )
            return self._empty_report(
                adb,
                DeviceConnectionStatus.NOT_FOUND,
                adb.message,
            )

        adb = ADBInstallation(
            availability=ADBAvailability.AVAILABLE,
            executable=adb.executable,
            source=adb.source,
            version=self._parse_version_summary(version.stdout),
            message=adb.message,
        )

        device_scan = self._device_list_service.scan()
        if device_scan.error:
            return self._empty_report(
                adb,
                DeviceConnectionStatus.NOT_FOUND,
                device_scan.error,
            )

        devices = device_scan.devices
        if not devices:
            return self._empty_report(
                adb,
                DeviceConnectionStatus.NOT_FOUND,
                "No Android device was found.",
            )

        selected = next(
            (device for device in devices if device.status == DeviceConnectionStatus.CONNECTED),
            devices[0],
        )
        if selected.status != DeviceConnectionStatus.CONNECTED:
            device = DeviceInfo(serial=selected.serial, status=selected.status, model=selected.model)
            root = RootInfo(state=RootState.UNAVAILABLE, details="Device is not authorized/online.")
            capabilities = self._capability_service.from_device(device, root)
            return DeviceReport(
                adb=adb,
                adb_availability=adb.availability,
                device=device,
                root=root,
                capabilities=capabilities,
                messages=(f"Device state is {selected.status.value}.",),
            )

        props = self._read_properties(selected.serial)
        memory = self._read_memory(selected.serial)
        device_info = DeviceInfo(
            serial=selected.serial,
            status=DeviceConnectionStatus.CONNECTED,
            model=props.get("ro.product.model") or selected.model,
            manufacturer=props.get("ro.product.manufacturer"),
            android_version=props.get("ro.build.version.release"),
            api_level=props.get("ro.build.version.sdk"),
            abi=props.get("ro.product.cpu.abi") or props.get("ro.system.product.cpu.abi"),
            ram_total_kb=memory.total_kb if memory else None,
            memory=memory,
            storage=self._read_storage(selected.serial),
            battery_level=self._read_battery_level(selected.serial),
        )
        root = self._root_service.detect(selected.serial)
        capabilities = self._capability_service.from_device(device_info, root)
        return DeviceReport(
            adb=adb,
            adb_availability=adb.availability,
            device=device_info,
            root=root,
            capabilities=capabilities,
            messages=("Device detection completed.",),
        )

    def restart_adb_server(self) -> None:
        self._executor.run(["kill-server"], timeout_seconds=QUICK_ADB_TIMEOUT_SECONDS)
        self._executor.run(["start-server"], timeout_seconds=QUICK_ADB_TIMEOUT_SECONDS)

    def _read_properties(self, serial: str) -> dict[str, str]:
        return self._executor.read_properties(serial=serial)

    def _read_memory(self, serial: str) -> MemoryInfo | None:
        return self._executor.read_memory_info(serial=serial)

    def _read_storage(self, serial: str) -> StorageInfo | None:
        return self._executor.read_storage_info(serial=serial)

    def _read_battery_level(self, serial: str) -> int | None:
        return self._executor.read_battery_level(serial=serial)

    def _empty_report(
        self,
        adb: ADBInstallation,
        status: DeviceConnectionStatus,
        message: str,
    ) -> DeviceReport:
        device = DeviceInfo(serial=None, status=status)
        root = RootInfo(state=RootState.UNAVAILABLE, details=message)
        capabilities = self._capability_service.from_device(device, root)
        return DeviceReport(
            adb=adb,
            adb_availability=adb.availability,
            device=device,
            root=root,
            capabilities=capabilities,
            messages=(message,),
        )

    def _resolve_adb_installation(self) -> ADBInstallation:
        discovered = self._adb_discovery_service.discover()
        current_path = self._executor.adb_path
        if current_path not in ("adb", discovered.executable):
            return self._adb_discovery_service.discover(current_path)
        return discovered

    @staticmethod
    def _parse_version_summary(output: str) -> str | None:
        for line in output.splitlines():
            stripped = line.strip()
            if stripped:
                return stripped
        return None
