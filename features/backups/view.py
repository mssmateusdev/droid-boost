from __future__ import annotations

from PySide6.QtWidgets import QVBoxLayout, QWidget

from app.ui.components.card import Card
from app.ui.components.page import EmptyState, PageHeader


class BackupsPage(QWidget):
    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 26, 28, 28)
        layout.setSpacing(18)
        layout.addWidget(
            PageHeader(
                "Backups e snapshots",
                "Historico local para restaurar ajustes que o DroidBoost alterou.",
            )
        )
        card = Card("Etapa 2")
        card.add_widget(
            EmptyState(
                "Snapshots logicos",
                "Restauracao de alteracoes gerenciadas pelo app sera baseada nesses registros.",
            )
        )
        layout.addWidget(card)
        layout.addStretch(1)
