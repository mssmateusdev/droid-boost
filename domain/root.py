from __future__ import annotations

from dataclasses import dataclass

from app.core.enums import RootState


@dataclass(frozen=True)
class RootInfo:
    state: RootState = RootState.UNKNOWN
    su_binary_found: bool = False
    su_command_works: bool = False
    adb_shell_is_root: bool = False
    details: str = ""

    @property
    def operational(self) -> bool:
        return self.su_command_works or self.adb_shell_is_root

