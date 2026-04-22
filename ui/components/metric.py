from __future__ import annotations

from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout, QWidget


class Metric(QFrame):
    def __init__(self, label: str, value: str = "-", parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("MetricTile")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(4)

        self._label = QLabel(label)
        self._label.setObjectName("MetricLabel")
        self._value = QLabel(value)
        self._value.setObjectName("MetricValue")
        self._value.setWordWrap(True)

        layout.addWidget(self._label)
        layout.addWidget(self._value)

    def set_value(self, value: str | None) -> None:
        self._value.setText(value if value not in (None, "") else "-")
