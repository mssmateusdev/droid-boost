from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum

from app.adb.result import CommandResult


class TweakCategory(StrEnum):
    ANIMATION = "animation"
    SHORTCUT = "shortcut"
    ADB = "adb"
    DIAGNOSTIC = "diagnostic"
    STORAGE = "storage"


class TweakActionKind(StrEnum):
    SHELL = "shell"
    ADB = "adb"
    DIAGNOSTIC_PROPERTIES = "diagnostic_properties"
    DIAGNOSTIC_MEMORY_STORAGE = "diagnostic_memory_storage"


@dataclass(frozen=True)
class TweakRequirement:
    label: str
    requires_device: bool = True
    requires_root: bool = False
    capability: str | None = None


@dataclass(frozen=True)
class TweakCommand:
    command: str
    description: str
    requires_root: bool = False


@dataclass(frozen=True)
class TweakDefinition:
    key: str
    name: str
    description: str
    category: TweakCategory
    action_kind: TweakActionKind
    requirements: tuple[TweakRequirement, ...] = field(default_factory=tuple)
    commands: tuple[TweakCommand, ...] = field(default_factory=tuple)
    confirmation_required: bool = False

    @property
    def requires_root(self) -> bool:
        return any(requirement.requires_root for requirement in self.requirements) or any(
            command.requires_root for command in self.commands
        )


@dataclass(frozen=True)
class TweakAvailability:
    enabled: bool
    reason: str = ""


@dataclass(frozen=True)
class TweakExecutionResult:
    tweak: TweakDefinition
    success: bool
    message: str
    output: str = ""
    command_results: tuple[CommandResult, ...] = field(default_factory=tuple)

