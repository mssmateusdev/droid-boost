from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AppPaths:
    data_dir: Path
    logs_dir: Path
    snapshots_dir: Path
    exports_dir: Path

    @classmethod
    def create(cls) -> "AppPaths":
        base = cls._default_data_dir()
        try:
            return cls._create_from_base(base)
        except OSError:
            return cls._create_from_base(Path.cwd() / ".droidboost")

    @classmethod
    def _create_from_base(cls, base: Path) -> "AppPaths":
        paths = cls(
            data_dir=base,
            logs_dir=base / "logs",
            snapshots_dir=base / "snapshots",
            exports_dir=base / "exports",
        )
        for path in (paths.data_dir, paths.logs_dir, paths.snapshots_dir, paths.exports_dir):
            path.mkdir(parents=True, exist_ok=True)
        return paths

    @staticmethod
    def _default_data_dir() -> Path:
        override = os.getenv("DROIDBOOST_DATA_DIR")
        if override:
            return Path(override)

        local_app_data = os.getenv("LOCALAPPDATA")
        if local_app_data:
            return Path(local_app_data) / "DroidBoost"

        xdg_data_home = os.getenv("XDG_DATA_HOME")
        if xdg_data_home:
            return Path(xdg_data_home) / "DroidBoost"

        return Path.home() / ".droidboost"
