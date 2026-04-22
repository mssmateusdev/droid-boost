from __future__ import annotations

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from app.services.app_context import AppContext
from app.ui.components.card import Card
from app.ui.components.page import EmptyState, PageHeader


class SettingsPage(QWidget):
    def __init__(self, context: AppContext) -> None:
        super().__init__()
        self._context = context
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 26, 28, 28)
        layout.setSpacing(18)
        layout.addWidget(
            PageHeader(
                "Configuracoes",
                "Preferencias da interface, ADB, logs e confirmacoes sensiveis.",
            )
        )
        card = Card("Ambiente")
        adb = QLabel(f"ADB atual: {self._context.adb_executor.adb_path}")
        adb.setObjectName("MutedLabel")
        adb.setWordWrap(True)
        card.add_widget(adb)
        card.add_widget(
            EmptyState(
                "Configuracoes planejadas",
                "Caminho do ADB, tema, confirmacoes e pastas de exportacao entram na Etapa 6.",
            )
        )
        layout.addWidget(card)
        layout.addStretch(1)
