from __future__ import annotations

from PySide6.QtWidgets import QLabel, QPlainTextEdit, QVBoxLayout, QWidget

from app.services.app_context import AppContext


class LogsPage(QWidget):
    def __init__(self, context: AppContext) -> None:
        super().__init__()
        self._context = context
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 26, 28, 28)
        layout.setSpacing(14)

        title = QLabel("Logs")
        title.setObjectName("SectionTitle")
        subtitle = QLabel(f"Arquivo atual: {self._context.paths.logs_dir / 'droidboost.log'}")
        subtitle.setObjectName("MutedLabel")
        subtitle.setWordWrap(True)

        viewer = QPlainTextEdit()
        viewer.setReadOnly(True)
        viewer.setPlainText("A central de logs em tempo real sera expandida na Etapa 5.")
        viewer.setStyleSheet(
            """
            QPlainTextEdit {
                background: #151D27;
                border: 1px solid #273344;
                border-radius: 8px;
                padding: 12px;
                color: #AAB6C5;
            }
            """
        )

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(viewer, 1)

