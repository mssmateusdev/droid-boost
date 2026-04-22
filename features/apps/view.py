from __future__ import annotations

from PySide6.QtWidgets import QVBoxLayout, QWidget

from app.ui.components.card import Card
from app.ui.components.page import EmptyState, PageHeader


class AppsPage(QWidget):
    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 26, 28, 28)
        layout.setSpacing(18)
        layout.addWidget(
            PageHeader(
                "Gerenciador de apps",
                "Listagem e acoes de pacote com protecao contra apps criticos.",
            )
        )
        card = Card("Etapa 4")
        card.add_widget(
            EmptyState(
                "Inventario de pacotes",
                "Listagem, busca, classificacao e protecao de pacotes criticos entram aqui.",
            )
        )
        layout.addWidget(card)
        layout.addStretch(1)
