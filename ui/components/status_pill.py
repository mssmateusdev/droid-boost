from __future__ import annotations

from PySide6.QtWidgets import QLabel


class StatusPill(QLabel):
    COLORS = {
        "success": ("#123326", "#46D39A"),
        "warning": ("#3A2E12", "#F6C350"),
        "danger": ("#3A1B20", "#FF6B6B"),
        "neutral": ("#1B2531", "#AAB6C5"),
        "accent": ("#102B38", "#4CC9F0"),
    }

    def __init__(self, text: str = "Unknown", tone: str = "neutral") -> None:
        super().__init__(text)
        self.setObjectName("StatusPill")
        self.set_tone(tone)

    def set_status(self, text: str, tone: str) -> None:
        self.setText(text)
        self.set_tone(tone)

    def set_tone(self, tone: str) -> None:
        background, color = self.COLORS.get(tone, self.COLORS["neutral"])
        self.setStyleSheet(
            f"""
            QLabel#StatusPill {{
                background: {background};
                color: {color};
                border: 1px solid {color};
                border-radius: 10px;
                padding: 4px 10px;
                font-weight: 700;
                font-size: 12px;
            }}
            """
        )

