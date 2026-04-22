from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from string import Template


class OptimizationCategory(StrEnum):
    BATTERY = "battery"
    BALANCED = "balanced"
    RESPONSIVENESS = "responsiveness"
    GAMING = "gaming"
    DIAGNOSTIC = "diagnostic"


@dataclass(frozen=True)
class ProfileCommand:
    shell: str
    description: str
    requires_root: bool = False


@dataclass(frozen=True)
class ActionSnapshotPlan:
    key: str
    read_shell: str
    restore_shell_template: str
    default_restore_shell: str | None = None

    def build_restore_shell(self, previous_value: object) -> str:
        return Template(self.restore_shell_template).safe_substitute(value=str(previous_value))


@dataclass(frozen=True)
class OptimizationAction:
    key: str
    title: str
    description: str
    command: ProfileCommand
    requires_root: bool = False
    reversible: bool = True
    snapshot: ActionSnapshotPlan | None = None

    @property
    def commands(self) -> tuple[str, ...]:
        return (self.command.shell,)

@dataclass(frozen=True)
class OptimizationProfile:
    key: str
    title: str
    description: str
    category: OptimizationCategory
    actions: tuple[OptimizationAction, ...] = field(default_factory=tuple)

    @property
    def requires_root(self) -> bool:
        return any(action.requires_root for action in self.actions)


INITIAL_PROFILE_KEYS: tuple[str, ...] = (
    "battery_saver",
    "balanced",
    "responsive",
    "gaming",
)
