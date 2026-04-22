from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Any

from app.domain.snapshots import DeviceSnapshot, SnapshotEntry


class SnapshotStore:
    def __init__(self, snapshots_dir: Path) -> None:
        self._snapshots_dir = snapshots_dir
        self._snapshots_dir.mkdir(parents=True, exist_ok=True)

    @classmethod
    def from_string(cls, snapshots_dir: str) -> "SnapshotStore":
        return cls(Path(snapshots_dir))

    def save(self, snapshot: DeviceSnapshot) -> Path:
        path = self._snapshots_dir / f"{snapshot.created_at:%Y%m%d_%H%M%S}_{snapshot.snapshot_id}.json"
        payload = asdict(snapshot)
        payload["created_at"] = snapshot.created_at.isoformat()
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return path

    def list_for_profile(self, serial: str, profile_key: str) -> list[DeviceSnapshot]:
        snapshots: list[DeviceSnapshot] = []
        for path in sorted(self._snapshots_dir.glob("*.json"), reverse=True):
            snapshot = self._read_snapshot(path)
            if not snapshot:
                continue
            if snapshot.serial == serial and snapshot.reason == profile_key:
                snapshots.append(snapshot)
        return snapshots

    def latest_for_profile(self, serial: str, profile_key: str) -> DeviceSnapshot | None:
        snapshots = self.list_for_profile(serial, profile_key)
        return snapshots[0] if snapshots else None

    def _read_snapshot(self, path: Path) -> DeviceSnapshot | None:
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return None
        return self._snapshot_from_payload(payload)

    @staticmethod
    def _snapshot_from_payload(payload: dict[str, Any]) -> DeviceSnapshot:
        entries = tuple(
            SnapshotEntry(
                key=str(entry["key"]),
                previous_value=entry.get("previous_value"),
                restore_command=entry.get("restore_command"),
                metadata=dict(entry.get("metadata", {})),
            )
            for entry in payload.get("entries", [])
        )
        return DeviceSnapshot(
            serial=str(payload["serial"]),
            reason=str(payload["reason"]),
            entries=entries,
            created_at=datetime.fromisoformat(payload["created_at"]),
            snapshot_id=str(payload["snapshot_id"]),
        )
