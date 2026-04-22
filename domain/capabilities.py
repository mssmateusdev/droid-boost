from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DeviceCapabilities:
    can_use_root_commands: bool = False
    can_manage_packages: bool = False
    can_change_animations: bool = False
    can_clear_cache: bool = False
    can_run_advanced_profiles: bool = False
    can_read_diagnostics: bool = False

    @property
    def enabled_count(self) -> int:
        return sum(
            (
                self.can_use_root_commands,
                self.can_manage_packages,
                self.can_change_animations,
                self.can_clear_cache,
                self.can_run_advanced_profiles,
                self.can_read_diagnostics,
            )
        )

