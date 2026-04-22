from __future__ import annotations

APP_NAME = "DroidBoost"
DEFAULT_ADB_TIMEOUT_SECONDS = 12
QUICK_ADB_TIMEOUT_SECONDS = 5

CRITICAL_ANDROID_PACKAGES: frozenset[str] = frozenset(
    {
        "android",
        "com.android.packageinstaller",
        "com.android.permissioncontroller",
        "com.android.providers.settings",
        "com.android.providers.telephony",
        "com.android.providers.downloads",
        "com.android.settings",
        "com.google.android.gms",
        "com.google.android.gsf",
        "com.google.android.packageinstaller",
        "com.sec.android.app.launcher",
    }
)

