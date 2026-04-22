from __future__ import annotations

from dataclasses import dataclass

from app.core.enums import ADBAvailability, DeviceConnectionStatus, RootState
from app.domain.capabilities import DeviceCapabilities
from app.domain.device import DeviceInfo
from app.services.device_detection_service import DeviceReport


@dataclass(frozen=True)
class StatusDisplay:
    text: str
    tone: str


@dataclass(frozen=True)
class DashboardDisplay:
    adb: StatusDisplay
    device: StatusDisplay
    root: StatusDisplay
    connection_title: str
    connection_description: str
    connection_tone: str
    device_name: str
    capabilities_enabled: str


def build_dashboard_display(report: DeviceReport) -> DashboardDisplay:
    return DashboardDisplay(
        adb=_adb_status(report.adb_availability),
        device=_device_status(report.device.status),
        root=_root_status(report.root.state),
        connection_title=_connection_title(report),
        connection_description=" ".join(report.messages),
        connection_tone=_connection_tone(report),
        device_name=_device_name(report.device),
        capabilities_enabled=_capabilities_enabled(report.capabilities),
    )


def _adb_status(availability: ADBAvailability) -> StatusDisplay:
    if availability == ADBAvailability.AVAILABLE:
        return StatusDisplay("ADB: disponivel", "success")
    return StatusDisplay("ADB: ausente", "danger")


def _device_status(status: DeviceConnectionStatus) -> StatusDisplay:
    tones = {
        DeviceConnectionStatus.CONNECTED: "success",
        DeviceConnectionStatus.UNAUTHORIZED: "warning",
        DeviceConnectionStatus.OFFLINE: "warning",
        DeviceConnectionStatus.NOT_FOUND: "neutral",
    }
    return StatusDisplay(f"Device: {status.value}", tones.get(status, "neutral"))


def _root_status(state: RootState) -> StatusDisplay:
    tones = {
        RootState.DETECTED: "success",
        RootState.NOT_DETECTED: "neutral",
        RootState.UNAVAILABLE: "warning",
        RootState.UNKNOWN: "neutral",
    }
    return StatusDisplay(f"Root: {state.value}", tones.get(state, "neutral"))


def _connection_title(report: DeviceReport) -> str:
    if report.adb_availability != ADBAvailability.AVAILABLE:
        return "ADB nao encontrado"
    if report.device.status == DeviceConnectionStatus.CONNECTED:
        return "Dispositivo pronto"
    if report.device.status == DeviceConnectionStatus.UNAUTHORIZED:
        return "Autorizacao pendente"
    if report.device.status == DeviceConnectionStatus.OFFLINE:
        return "Dispositivo offline"
    return "Nenhum device ativo"


def _connection_tone(report: DeviceReport) -> str:
    if report.ready:
        return "success"
    if report.adb_availability != ADBAvailability.AVAILABLE:
        return "danger"
    if report.device.status in (DeviceConnectionStatus.UNAUTHORIZED, DeviceConnectionStatus.OFFLINE):
        return "warning"
    return "neutral"


def _device_name(device: DeviceInfo) -> str:
    if device.status == DeviceConnectionStatus.CONNECTED:
        return device.display_name
    if device.serial:
        return f"Android device {device.serial}"
    return "Aguardando conexao"


def _capabilities_enabled(capabilities: DeviceCapabilities) -> str:
    return f"{capabilities.enabled_count}/6 liberadas"

