from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path

from app.adb.executor import ADBExecutor
from app.adb.result import CommandResult
from app.core.constants import APP_NAME
from app.core.enums import DeviceConnectionStatus
from app.domain.profile_presets import PROFILE_PRESETS
from app.domain.profiles import OptimizationAction, OptimizationProfile
from app.domain.snapshots import DeviceSnapshot, SnapshotEntry
from app.services.device_detection_service import DeviceDetectionService
from app.storage.snapshot_store import SnapshotStore


@dataclass(frozen=True)
class ProfileActionResult:
    action: OptimizationAction
    result: CommandResult


@dataclass(frozen=True)
class ProfilePreview:
    profile: OptimizationProfile
    commands: tuple[str, ...]
    blocked_reason: str | None = None


@dataclass(frozen=True)
class ProfileExecutionResult:
    profile: OptimizationProfile
    success: bool
    message: str
    action_results: tuple[ProfileActionResult, ...] = field(default_factory=tuple)
    snapshot: DeviceSnapshot | None = None
    snapshot_path: Path | None = None


class OptimizationProfileService:
    def __init__(
        self,
        executor: ADBExecutor,
        device_service: DeviceDetectionService,
        snapshot_store: SnapshotStore,
    ) -> None:
        self._executor = executor
        self._device_service = device_service
        self._snapshot_store = snapshot_store
        self._profiles = {profile.key: profile for profile in PROFILE_PRESETS}
        self._logger = logging.getLogger(APP_NAME).getChild("profiles")

    def list_profiles(self) -> tuple[OptimizationProfile, ...]:
        return tuple(self._profiles.values())

    def get_profile(self, profile_key: str) -> OptimizationProfile:
        return self._profiles[profile_key]

    def preview(self, profile_key: str) -> ProfilePreview:
        profile = self.get_profile(profile_key)
        commands = tuple(command for action in profile.actions for command in action.commands)
        return ProfilePreview(profile=profile, commands=commands)

    def apply_profile(self, profile_key: str) -> ProfileExecutionResult:
        profile = self.get_profile(profile_key)
        report = self._device_service.detect()
        if not report.ready or not report.device.serial:
            return ProfileExecutionResult(
                profile=profile,
                success=False,
                message="Conecte e autorize um dispositivo Android antes de aplicar perfis.",
            )
        if profile.requires_root and not report.capabilities.can_use_root_commands:
            return ProfileExecutionResult(
                profile=profile,
                success=False,
                message="Este perfil exige root operacional, mas root nao esta liberado.",
            )

        snapshot_entries = self._create_snapshot_entries(profile, report.device.serial)
        snapshot = DeviceSnapshot(
            serial=report.device.serial,
            reason=profile.key,
            entries=tuple(snapshot_entries),
        )
        snapshot_path = self._snapshot_store.save(snapshot)
        self._logger.info(
            "profile.snapshot.created | profile=%s | serial=%s | entries=%s | path=%s",
            profile.key,
            report.device.serial,
            len(snapshot.entries),
            snapshot_path,
        )

        results: list[ProfileActionResult] = []
        for action in profile.actions:
            result = self._run_action(action, report.device.serial)
            results.append(ProfileActionResult(action=action, result=result))
            self._logger.info(
                "profile.action.done | profile=%s | action=%s | outcome=%s | command=%s",
                profile.key,
                action.key,
                result.outcome.value,
                result.display_command,
            )
            if not result.ok:
                return ProfileExecutionResult(
                    profile=profile,
                    success=False,
                    message=f"Falha ao aplicar '{action.title}': {result.user_message}",
                    action_results=tuple(results),
                    snapshot=snapshot,
                    snapshot_path=snapshot_path,
                )

        return ProfileExecutionResult(
            profile=profile,
            success=True,
            message=f"Perfil {profile.title} aplicado com sucesso.",
            action_results=tuple(results),
            snapshot=snapshot,
            snapshot_path=snapshot_path,
        )

    def restore_latest_snapshot(self, profile_key: str) -> ProfileExecutionResult:
        profile = self.get_profile(profile_key)
        report = self._device_service.detect()
        if not report.ready or not report.device.serial:
            return ProfileExecutionResult(
                profile=profile,
                success=False,
                message="Conecte e autorize um dispositivo Android antes de restaurar.",
            )
        snapshot = self._snapshot_store.latest_for_profile(report.device.serial, profile.key)
        if snapshot is None:
            return ProfileExecutionResult(
                profile=profile,
                success=False,
                message="Nao ha snapshot anterior para este perfil e dispositivo.",
            )

        results = [
            ProfileActionResult(
                action=self._restore_action_for_entry(profile, entry),
                result=self._executor.run_shell(entry.restore_command, serial=report.device.serial),
            )
            for entry in snapshot.entries
            if entry.restore_command
        ]
        success = all(item.result.ok for item in results)
        return ProfileExecutionResult(
            profile=profile,
            success=success,
            message="Snapshot restaurado." if success else "Algumas acoes de restore falharam.",
            action_results=tuple(results),
            snapshot=snapshot,
        )

    def restore_defaults(self, profile_key: str) -> ProfileExecutionResult:
        profile = self.get_profile(profile_key)
        report = self._device_service.detect()
        if not report.ready or not report.device.serial:
            return ProfileExecutionResult(
                profile=profile,
                success=False,
                message="Conecte e autorize um dispositivo Android antes de restaurar padroes.",
            )

        results: list[ProfileActionResult] = []
        for action in profile.actions:
            if not action.snapshot or not action.snapshot.default_restore_shell:
                continue
            result = self._executor.run_shell(
                action.snapshot.default_restore_shell,
                serial=report.device.serial,
                label=f"restore default {action.key}",
            )
            results.append(ProfileActionResult(action=action, result=result))
        success = all(item.result.ok for item in results)
        return ProfileExecutionResult(
            profile=profile,
            success=success,
            message="Padroes restaurados." if success else "Algumas restauracoes falharam.",
            action_results=tuple(results),
        )

    def _create_snapshot_entries(
        self,
        profile: OptimizationProfile,
        serial: str,
    ) -> list[SnapshotEntry]:
        entries: list[SnapshotEntry] = []
        for action in profile.actions:
            if not action.snapshot:
                continue
            read_result = self._executor.run_shell(
                action.snapshot.read_shell,
                serial=serial,
                label=f"snapshot {action.key}",
            )
            previous_value = read_result.stdout.strip() if read_result.ok else None
            restore_command = (
                action.snapshot.build_restore_shell(previous_value)
                if previous_value not in (None, "")
                else action.snapshot.default_restore_shell
            )
            entries.append(
                SnapshotEntry(
                    key=action.snapshot.key,
                    previous_value=previous_value,
                    restore_command=restore_command,
                    metadata={
                        "profile": profile.key,
                        "action": action.key,
                        "read_command": action.snapshot.read_shell,
                        "read_ok": read_result.ok,
                    },
                )
            )
        return entries

    def _run_action(self, action: OptimizationAction, serial: str) -> CommandResult:
        if action.requires_root:
            return self._executor.run_root_shell(
                action.command.shell,
                serial=serial,
                label=f"profile action {action.key}",
            )
        return self._executor.run_shell(
            action.command.shell,
            serial=serial,
            label=f"profile action {action.key}",
        )

    @staticmethod
    def _restore_action_for_entry(
        profile: OptimizationProfile,
        entry: SnapshotEntry,
    ) -> OptimizationAction:
        for action in profile.actions:
            if action.snapshot and action.snapshot.key == entry.key:
                return action
        return OptimizationAction(
            key=entry.key,
            title=f"Restore {entry.key}",
            description="Restore de snapshot logico.",
            command=profile.actions[0].command,
        )

