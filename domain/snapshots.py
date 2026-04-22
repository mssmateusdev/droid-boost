from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4


@dataclass(frozen=True)
class SnapshotEntry:
    key: str
    previous_value: str | int | float | bool | None
    restore_command: str | None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class DeviceSnapshot:
    serial: str
    reason: str
    entries: tuple[SnapshotEntry, ...]
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    snapshot_id: str = field(default_factory=lambda: uuid4().hex)
