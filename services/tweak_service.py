from __future__ import annotations

import logging
from dataclasses import dataclass

from app.adb.executor import ADBExecutor
from app.adb.result import CommandResult
from app.core.constants import APP_NAME, QUICK_ADB_TIMEOUT_SECONDS
from app.core.enums import ADBAvailability, DeviceConnectionStatus
from app.domain.tweak_presets import TWEAK_PRESETS
from app.domain.tweaks import (
    TweakActionKind,
    TweakAvailability,
    TweakDefinition,
    TweakExecutionResult,
)
from app.services.device_detection_service import DeviceDetectionService, DeviceReport


@dataclass(frozen=True)
class TweakStatus:
    tweak: TweakDefinition
    availability: TweakAvailability


@dataclass(frozen=True)
class TweakCatalog:
    report: DeviceReport
    statuses: tuple[TweakStatus, ...]


class TweakService:
    def __init__(self, executor: ADBExecutor, device_service: DeviceDetectionService) -> None:
        self._executor = executor
        self._device_service = device_service
        self._tweaks = {tweak.key: tweak for tweak in TWEAK_PRESETS}
        self._logger = logging.getLogger(APP_NAME).getChild("tweaks")

    def list_tweaks(self) -> tuple[TweakDefinition, ...]:
        return tuple(self._tweaks.values())

    def get_tweak(self, tweak_key: str) -> TweakDefinition:
        return self._tweaks[tweak_key]

    def catalog(self) -> TweakCatalog:
        report = self._device_service.detect()
        return TweakCatalog(
            report=report,
            statuses=tuple(
                TweakStatus(tweak=tweak, availability=self.availability(tweak, report))
                for tweak in self.list_tweaks()
            ),
        )

    def availability(self, tweak: TweakDefinition, report: DeviceReport) -> TweakAvailability:
        if report.adb_availability != ADBAvailability.AVAILABLE:
            return TweakAvailability(False, "ADB nao esta disponivel.")

        for requirement in tweak.requirements:
            if requirement.requires_device and report.device.status != DeviceConnectionStatus.CONNECTED:
                return TweakAvailability(False, "Conecte e autorize um dispositivo Android.")
            if requirement.requires_root and not report.capabilities.can_use_root_commands:
                return TweakAvailability(False, "Este tweak exige root operacional.")
            if requirement.capability and not bool(getattr(report.capabilities, requirement.capability)):
                return TweakAvailability(False, f"Requisito indisponivel: {requirement.label}.")

        return TweakAvailability(True)

    def execute(self, tweak_key: str) -> TweakExecutionResult:
        tweak = self.get_tweak(tweak_key)
        report = self._device_service.detect()
        availability = self.availability(tweak, report)
        if not availability.enabled:
            return TweakExecutionResult(
                tweak=tweak,
                success=False,
                message=availability.reason,
            )

        serial = report.device.serial
        if tweak.action_kind == TweakActionKind.ADB:
            result = self._restart_adb(tweak)
        elif tweak.action_kind == TweakActionKind.DIAGNOSTIC_PROPERTIES:
            result = self._read_useful_properties(tweak, serial)
        elif tweak.action_kind == TweakActionKind.DIAGNOSTIC_MEMORY_STORAGE:
            result = self._read_memory_storage(tweak, serial)
        else:
            result = self._run_shell_tweak(tweak, serial)

        self._logger.info(
            "tweak.done | key=%s | success=%s | message=%s",
            tweak.key,
            result.success,
            result.message,
        )
        return result

    def _run_shell_tweak(self, tweak: TweakDefinition, serial: str | None) -> TweakExecutionResult:
        results: list[CommandResult] = []
        for command in tweak.commands:
            if command.requires_root:
                result = self._executor.run_root_shell(command.command, serial=serial, label=f"tweak {tweak.key}")
            else:
                result = self._executor.run_shell(
                    command.command,
                    serial=serial,
                    timeout_seconds=QUICK_ADB_TIMEOUT_SECONDS,
                    label=f"tweak {tweak.key}",
                )
            results.append(result)
            if not result.ok:
                return TweakExecutionResult(
                    tweak=tweak,
                    success=False,
                    message=f"Falha em {command.description}: {result.user_message}",
                    output=result.combined_output,
                    command_results=tuple(results),
                )

        return TweakExecutionResult(
            tweak=tweak,
            success=True,
            message=f"{tweak.name} executado com sucesso.",
            output="\n".join(result.combined_output for result in results if result.combined_output),
            command_results=tuple(results),
        )

    def _restart_adb(self, tweak: TweakDefinition) -> TweakExecutionResult:
        kill = self._executor.run(["kill-server"], timeout_seconds=QUICK_ADB_TIMEOUT_SECONDS, label="tweak restart adb kill")
        start = self._executor.run(["start-server"], timeout_seconds=QUICK_ADB_TIMEOUT_SECONDS, label="tweak restart adb start")
        success = kill.ok and start.ok
        return TweakExecutionResult(
            tweak=tweak,
            success=success,
            message="Servidor ADB reiniciado." if success else "Falha ao reiniciar servidor ADB.",
            output="\n".join(part for part in (kill.combined_output, start.combined_output) if part),
            command_results=(kill, start),
        )

    def _read_useful_properties(self, tweak: TweakDefinition, serial: str | None) -> TweakExecutionResult:
        props = self._executor.read_properties(serial=serial)
        keys = (
            "ro.product.manufacturer",
            "ro.product.model",
            "ro.build.version.release",
            "ro.build.version.sdk",
            "ro.product.cpu.abi",
            "ro.build.fingerprint",
            "ro.build.version.security_patch",
        )
        lines = [f"{key}: {props.get(key, '-')}" for key in keys]
        return TweakExecutionResult(
            tweak=tweak,
            success=bool(props),
            message="Propriedades lidas." if props else "Nao foi possivel ler propriedades.",
            output="\n".join(lines),
        )

    def _read_memory_storage(self, tweak: TweakDefinition, serial: str | None) -> TweakExecutionResult:
        memory = self._executor.read_memory_info(serial=serial)
        storage = self._executor.read_storage_info(serial=serial)
        lines: list[str] = []
        if memory:
            if memory.total_gb is not None:
                lines.append(f"RAM total: {memory.total_gb:.2f} GB")
            if memory.available_gb is not None:
                lines.append(f"RAM disponivel: {memory.available_gb:.2f} GB")
        if storage:
            lines.append(f"/data usado: {storage.used_gb:.1f} GB")
            lines.append(f"/data total: {storage.total_gb:.1f} GB")
            lines.append(f"/data livre: {storage.available_gb:.1f} GB")
        return TweakExecutionResult(
            tweak=tweak,
            success=bool(lines),
            message="Estado de memoria/armazenamento lido." if lines else "Nao foi possivel ler recursos.",
            output="\n".join(lines),
        )

