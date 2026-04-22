from __future__ import annotations

import os
import platform
import shutil
from collections.abc import Iterable
from pathlib import Path

from app.core.enums import ADBAvailability
from app.domain.adb import ADBInstallation


class ADBDiscoveryService:
    """Finds the best ADB executable without involving the UI layer."""

    def discover(self, configured_path: str | None = None) -> ADBInstallation:
        for source, candidate in self._candidate_paths(configured_path):
            resolved = self._resolve_candidate(candidate)
            if resolved:
                return ADBInstallation(
                    availability=ADBAvailability.AVAILABLE,
                    executable=resolved,
                    source=source,
                    message=f"ADB found via {source}.",
                )

        return ADBInstallation(
            availability=ADBAvailability.MISSING,
            executable=None,
            source="not_found",
            message="ADB executable was not found in configuration, bundled files, or PATH.",
        )

    def _candidate_paths(self, configured_path: str | None) -> Iterable[tuple[str, str]]:
        if configured_path:
            yield "configured_path", configured_path

        env_path = os.getenv("DROIDBOOST_ADB_PATH")
        if env_path:
            yield "DROIDBOOST_ADB_PATH", env_path

        app_dir = Path(__file__).resolve().parents[1]
        if platform.system().lower() == "windows":
            yield "bundled_app_root", str(app_dir / "adb.exe")
            yield "bundled_platform_tools", str(app_dir / "assets" / "platform-tools" / "adb.exe")
        else:
            yield "bundled_platform_tools", str(app_dir / "assets" / "platform-tools" / "adb")

        yield "PATH", "adb"

    @staticmethod
    def _resolve_candidate(candidate: str) -> str | None:
        candidate = candidate.strip()
        if not candidate:
            return None

        found = shutil.which(candidate)
        if found:
            return found

        path = Path(candidate)
        if path.exists() and path.is_file():
            return str(path)
        return None

