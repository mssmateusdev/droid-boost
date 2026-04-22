from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.domain.tweaks import TweakAvailability, TweakDefinition, TweakExecutionResult
from app.features.tweaks.workers import TweakCatalogThread, TweakExecuteThread
from app.services.app_context import AppContext
from app.services.tweak_service import TweakCatalog
from app.ui.components.card import Card
from app.ui.components.page import PageHeader
from app.ui.components.status_pill import StatusPill


class TweaksPage(QWidget):
    def __init__(self, context: AppContext) -> None:
        super().__init__()
        self._context = context
        self._catalog_worker: TweakCatalogThread | None = None
        self._execute_worker: TweakExecuteThread | None = None
        self._catalog: TweakCatalog | None = None
        self._selected_tweak: TweakDefinition | None = None
        self._availability_by_key: dict[str, TweakAvailability] = {}
        self._build_ui()
        self.refresh_catalog()

    def shutdown_workers(self) -> None:
        for worker in (self._catalog_worker, self._execute_worker):
            if worker and worker.isRunning():
                worker.wait(10000)

    def refresh_catalog(self) -> None:
        if self._catalog_worker and self._catalog_worker.isRunning():
            return
        self._set_busy(True, "Lendo compatibilidade dos tweaks...")
        self._catalog_worker = TweakCatalogThread(self._context.tweak_service)
        self._catalog_worker.completed.connect(self._handle_catalog)
        self._catalog_worker.failed.connect(self._handle_error)
        self._catalog_worker.finished.connect(lambda: self._set_busy(False))
        self._catalog_worker.start()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 26, 28, 28)
        root.setSpacing(18)

        header = QHBoxLayout()
        header.addWidget(
            PageHeader(
                "Tweaks rapidos",
                "Acoes pequenas, explicitas e validadas contra o estado atual do aparelho.",
            ),
            1,
        )
        self._refresh_button = QPushButton("Atualizar compatibilidade")
        self._refresh_button.setObjectName("PrimaryButton")
        self._refresh_button.clicked.connect(self.refresh_catalog)
        header.addWidget(self._refresh_button, 0, Qt.AlignTop)
        root.addLayout(header)

        body = QHBoxLayout()
        body.setSpacing(18)
        body.addWidget(self._build_list_card(), 1)
        body.addWidget(self._build_details(), 2)
        root.addLayout(body, 1)

    def _build_list_card(self) -> Card:
        card = Card("Tweaks disponiveis")
        self._tweak_list = QListWidget()
        self._tweak_list.setStyleSheet(
            """
            QListWidget {
                background: transparent;
                border: 0;
                outline: 0;
            }
            QListWidget::item {
                background: #111923;
                border: 1px solid #223044;
                border-radius: 8px;
                padding: 11px;
                margin-bottom: 8px;
                color: #F4F7FB;
            }
            QListWidget::item:selected {
                background: #1B2B3B;
                border-color: #4CC9F0;
            }
            """
        )
        self._tweak_list.currentItemChanged.connect(self._handle_selection_changed)
        card.add_widget(self._tweak_list)
        return card

    def _build_details(self) -> QWidget:
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)

        hero = QFrame()
        hero.setObjectName("HeroCard")
        hero_layout = QVBoxLayout(hero)
        hero_layout.setContentsMargins(18, 16, 18, 16)
        hero_layout.setSpacing(10)

        title_row = QHBoxLayout()
        self._title = QLabel("Selecione um tweak")
        self._title.setObjectName("HeroDeviceName")
        self._category_pill = StatusPill("Categoria", "neutral")
        self._state_pill = StatusPill("Aguardando", "neutral")
        title_row.addWidget(self._title, 1)
        title_row.addWidget(self._category_pill)
        title_row.addWidget(self._state_pill)

        self._description = QLabel("Atualize a compatibilidade e escolha uma acao.")
        self._description.setObjectName("HeroStatus")
        self._description.setWordWrap(True)
        self._requirements = QLabel("-")
        self._requirements.setObjectName("MutedLabel")
        self._requirements.setWordWrap(True)

        self._commands = QPlainTextEdit()
        self._commands.setReadOnly(True)
        self._commands.setMaximumHeight(110)
        self._commands.setStyleSheet(self._plain_text_style())

        button_row = QHBoxLayout()
        self._execute_button = QPushButton("Executar tweak")
        self._execute_button.setObjectName("PrimaryButton")
        self._execute_button.clicked.connect(self._confirm_execute)
        button_row.addStretch(1)
        button_row.addWidget(self._execute_button)

        hero_layout.addLayout(title_row)
        hero_layout.addWidget(self._description)
        hero_layout.addWidget(QLabel("Requisitos"))
        hero_layout.addWidget(self._requirements)
        hero_layout.addWidget(QLabel("Comandos / acao"))
        hero_layout.addWidget(self._commands)
        hero_layout.addLayout(button_row)
        layout.addWidget(hero)

        result_card = Card("Resultado")
        self._status_label = QLabel("Nenhum tweak executado ainda.")
        self._status_label.setObjectName("MutedLabel")
        self._status_label.setWordWrap(True)
        self._result_output = QPlainTextEdit()
        self._result_output.setReadOnly(True)
        self._result_output.setStyleSheet(self._plain_text_style())
        result_card.add_widget(self._status_label)
        result_card.add_widget(self._result_output)
        layout.addWidget(result_card, 1)
        return panel

    def _handle_catalog(self, catalog: TweakCatalog) -> None:
        self._catalog = catalog
        self._availability_by_key = {
            status.tweak.key: status.availability
            for status in catalog.statuses
        }
        self._render_tweaks(catalog)
        if self._tweak_list.count() and self._tweak_list.currentRow() < 0:
            self._tweak_list.setCurrentRow(0)
        self._status_label.setText("Compatibilidade atualizada.")

    def _render_tweaks(self, catalog: TweakCatalog) -> None:
        current_key = self._selected_tweak.key if self._selected_tweak else None
        self._tweak_list.clear()
        for status in catalog.statuses:
            state = "OK" if status.availability.enabled else "BLOQUEADO"
            item = QListWidgetItem(f"{state}  |  {status.tweak.category.value.upper()}  |  {status.tweak.name}")
            item.setData(Qt.UserRole, status.tweak.key)
            item.setToolTip(status.availability.reason or status.tweak.description)
            self._tweak_list.addItem(item)
            if current_key == status.tweak.key:
                self._tweak_list.setCurrentItem(item)

    def _handle_selection_changed(
        self,
        current: QListWidgetItem | None,
        previous: QListWidgetItem | None = None,
    ) -> None:
        _ = previous
        if not current:
            return
        key = str(current.data(Qt.UserRole))
        self._selected_tweak = self._context.tweak_service.get_tweak(key)
        self._render_selected()

    def _render_selected(self) -> None:
        if not self._selected_tweak:
            return
        tweak = self._selected_tweak
        availability = self._availability_by_key.get(tweak.key, TweakAvailability(False, "Atualize compatibilidade."))
        self._title.setText(tweak.name)
        self._description.setText(tweak.description)
        self._category_pill.set_status(tweak.category.value, "accent")
        self._state_pill.set_status("Liberado" if availability.enabled else "Bloqueado", "success" if availability.enabled else "warning")
        requirements = "\n".join(f"- {requirement.label}" for requirement in tweak.requirements) or "- Sem requisitos especiais"
        if not availability.enabled and availability.reason:
            requirements = f"{requirements}\n\nBloqueio: {availability.reason}"
        self._requirements.setText(requirements)
        command_lines = [command.command for command in tweak.commands]
        if not command_lines:
            command_lines = [f"Acao interna: {tweak.action_kind.value}"]
        self._commands.setPlainText("\n".join(command_lines))
        self._execute_button.setDisabled(not availability.enabled)

    def _confirm_execute(self) -> None:
        if not self._selected_tweak:
            return
        tweak = self._selected_tweak
        if tweak.confirmation_required:
            command_text = self._commands.toPlainText()
            message = f"Executar {tweak.name}?\n\n{tweak.description}\n\n{command_text}"
            if QMessageBox.question(self, "Confirmar tweak", message) != QMessageBox.Yes:
                return
        self._set_busy(True, f"Executando {tweak.name}...")
        self._execute_worker = TweakExecuteThread(self._context.tweak_service, tweak.key)
        self._execute_worker.completed.connect(self._handle_execution)
        self._execute_worker.failed.connect(self._handle_error)
        self._execute_worker.finished.connect(lambda: self._set_busy(False))
        self._execute_worker.start()

    def _handle_execution(self, result: TweakExecutionResult) -> None:
        tone = "OK" if result.success else "Falha"
        self._status_label.setText(f"{tone}: {result.message}")
        output = result.output
        if result.command_results:
            lines = [
                f"{item.label}: {item.outcome.value}\n{item.combined_output}".strip()
                for item in result.command_results
            ]
            output = "\n\n".join(line for line in lines if line)
        self._result_output.setPlainText(output or result.message)
        self.refresh_catalog()

    def _handle_error(self, message: str) -> None:
        self._status_label.setText(f"Falha: {message}")
        self._result_output.setPlainText(message)

    def _set_busy(self, busy: bool, message: str | None = None) -> None:
        self._refresh_button.setDisabled(busy)
        self._execute_button.setDisabled(busy or not self._selected_tweak or not self._selected_tweak_available())
        self._tweak_list.setDisabled(busy)
        self._execute_button.setText("Executando..." if busy else "Executar tweak")
        if message:
            self._status_label.setText(message)

    def _selected_tweak_available(self) -> bool:
        if not self._selected_tweak:
            return False
        return self._availability_by_key.get(
            self._selected_tweak.key,
            TweakAvailability(False),
        ).enabled

    @staticmethod
    def _plain_text_style() -> str:
        return """
        QPlainTextEdit {
            background: #0B0F14;
            border: 1px solid #273344;
            border-radius: 8px;
            padding: 8px;
            color: #AAB6C5;
        }
        """
