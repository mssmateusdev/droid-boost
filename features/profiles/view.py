from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from app.domain.profiles import OptimizationAction, OptimizationProfile
from app.features.profiles.workers import ProfileApplyThread, ProfileRestoreThread
from app.services.app_context import AppContext
from app.services.optimization_profile_service import ProfileExecutionResult
from app.ui.components.card import Card
from app.ui.components.page import PageHeader
from app.ui.components.status_pill import StatusPill


class ProfilesPage(QWidget):
    def __init__(self, context: AppContext) -> None:
        super().__init__()
        self._context = context
        self._profiles = self._context.profile_service.list_profiles()
        self._selected_profile = self._profiles[0]
        self._apply_worker: ProfileApplyThread | None = None
        self._restore_worker: ProfileRestoreThread | None = None
        self._action_widgets: list[QFrame] = []
        self._build_ui()
        self._select_profile(self._selected_profile.key)

    def shutdown_workers(self) -> None:
        for worker in (self._apply_worker, self._restore_worker):
            if worker and worker.isRunning():
                worker.wait(10000)

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 26, 28, 28)
        root.setSpacing(18)
        root.addWidget(
            PageHeader(
                "Perfis de otimizacao",
                "Presets explicitos com preview, snapshot logico e restauracao controlada.",
            )
        )

        body = QHBoxLayout()
        body.setSpacing(18)
        body.addWidget(self._build_profile_list(), 1)
        body.addWidget(self._build_detail_panel(), 3)
        root.addLayout(body, 1)

    def _build_profile_list(self) -> Card:
        card = Card("Presets")
        self._profile_list = QListWidget()
        self._profile_list.setStyleSheet(
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
                padding: 12px;
                margin-bottom: 8px;
                color: #F4F7FB;
            }
            QListWidget::item:selected {
                background: #1B2B3B;
                border-color: #4CC9F0;
            }
            """
        )
        for profile in self._profiles:
            item = QListWidgetItem(profile.title)
            item.setData(Qt.UserRole, profile.key)
            item.setToolTip(profile.description)
            self._profile_list.addItem(item)
        self._profile_list.currentItemChanged.connect(self._handle_profile_changed)
        card.add_widget(self._profile_list)
        return card

    def _build_detail_panel(self) -> QWidget:
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
        self._profile_title = QLabel()
        self._profile_title.setObjectName("HeroDeviceName")
        self._profile_root_pill = StatusPill("Root: nao exige", "neutral")
        title_row.addWidget(self._profile_title, 1)
        title_row.addWidget(self._profile_root_pill)

        self._profile_description = QLabel()
        self._profile_description.setObjectName("HeroStatus")
        self._profile_description.setWordWrap(True)

        button_row = QHBoxLayout()
        button_row.setSpacing(10)
        self._preview_button = QPushButton("Preview")
        self._apply_button = QPushButton("Aplicar perfil")
        self._apply_button.setObjectName("PrimaryButton")
        self._restore_button = QPushButton("Restaurar snapshot")
        self._default_button = QPushButton("Restaurar padrao")
        self._preview_button.clicked.connect(self._show_preview)
        self._apply_button.clicked.connect(self._confirm_apply)
        self._restore_button.clicked.connect(lambda: self._confirm_restore(defaults=False))
        self._default_button.clicked.connect(lambda: self._confirm_restore(defaults=True))
        button_row.addWidget(self._preview_button)
        button_row.addWidget(self._restore_button)
        button_row.addWidget(self._default_button)
        button_row.addStretch(1)
        button_row.addWidget(self._apply_button)

        self._status_label = QLabel("Selecione um perfil para revisar as acoes.")
        self._status_label.setObjectName("MutedLabel")
        self._status_label.setWordWrap(True)

        hero_layout.addLayout(title_row)
        hero_layout.addWidget(self._profile_description)
        hero_layout.addLayout(button_row)
        hero_layout.addWidget(self._status_label)
        layout.addWidget(hero)

        actions_card = Card("Acoes previstas")
        self._actions_container = QWidget()
        self._actions_layout = QVBoxLayout(self._actions_container)
        self._actions_layout.setContentsMargins(0, 0, 0, 0)
        self._actions_layout.setSpacing(10)
        actions_card.add_widget(self._actions_container)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(actions_card)
        layout.addWidget(scroll, 1)
        return panel

    def _handle_profile_changed(
        self,
        current: QListWidgetItem | None,
        previous: QListWidgetItem | None = None,
    ) -> None:
        _ = previous
        if not current:
            return
        self._select_profile(str(current.data(Qt.UserRole)))

    def _select_profile(self, profile_key: str) -> None:
        self._selected_profile = self._context.profile_service.get_profile(profile_key)
        self._profile_title.setText(self._selected_profile.title)
        self._profile_description.setText(self._selected_profile.description)
        root_text = "Root: exige" if self._selected_profile.requires_root else "Root: nao exige"
        root_tone = "warning" if self._selected_profile.requires_root else "neutral"
        self._profile_root_pill.set_status(root_text, root_tone)
        self._status_label.setText("Revise o preview antes de aplicar qualquer alteracao.")
        self._render_actions(self._selected_profile)

        for index in range(self._profile_list.count()):
            item = self._profile_list.item(index)
            if item.data(Qt.UserRole) == profile_key:
                self._profile_list.setCurrentRow(index)
                break

    def _render_actions(self, profile: OptimizationProfile) -> None:
        self._clear_actions()
        for action in profile.actions:
            widget = self._build_action_widget(action)
            self._action_widgets.append(widget)
            self._actions_layout.addWidget(widget)
        self._actions_layout.addStretch(1)

    def _build_action_widget(self, action: OptimizationAction) -> QFrame:
        frame = QFrame()
        frame.setObjectName("MetricTile")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(8)

        title_row = QHBoxLayout()
        title = QLabel(action.title)
        title.setObjectName("CardTitle")
        pill = StatusPill("Root" if action.requires_root else "Sem root", "warning" if action.requires_root else "neutral")
        title_row.addWidget(title, 1)
        title_row.addWidget(pill)

        description = QLabel(action.description)
        description.setObjectName("MutedLabel")
        description.setWordWrap(True)

        command = QPlainTextEdit()
        command.setReadOnly(True)
        command.setMaximumHeight(54)
        command.setPlainText(action.command.shell)
        command.setStyleSheet(
            """
            QPlainTextEdit {
                background: #0B0F14;
                border: 1px solid #273344;
                border-radius: 8px;
                padding: 8px;
                color: #AAB6C5;
            }
            """
        )

        layout.addLayout(title_row)
        layout.addWidget(description)
        layout.addWidget(command)
        return frame

    def _show_preview(self) -> None:
        preview = self._context.profile_service.preview(self._selected_profile.key)
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Preview - {preview.profile.title}")
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        title = QLabel(preview.profile.title)
        title.setObjectName("SectionTitle")
        body = QLabel("Estes comandos serao executados somente depois da sua confirmacao.")
        body.setObjectName("MutedLabel")
        body.setWordWrap(True)
        commands = QPlainTextEdit()
        commands.setReadOnly(True)
        commands.setPlainText("\n".join(preview.commands))
        commands.setMinimumSize(640, 260)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok)
        buttons.accepted.connect(dialog.accept)

        layout.addWidget(title)
        layout.addWidget(body)
        layout.addWidget(commands)
        layout.addWidget(buttons)
        dialog.exec()

    def _confirm_apply(self) -> None:
        profile = self._selected_profile
        commands = "\n".join(self._context.profile_service.preview(profile.key).commands)
        question = (
            f"Aplicar o perfil {profile.title}?\n\n"
            "Um snapshot logico sera criado antes das alteracoes.\n\n"
            f"Comandos:\n{commands}"
        )
        if QMessageBox.question(self, "Confirmar aplicacao", question) != QMessageBox.Yes:
            return
        self._set_busy(True, f"Aplicando {profile.title}...")
        self._apply_worker = ProfileApplyThread(self._context.profile_service, profile.key)
        self._apply_worker.completed.connect(self._handle_execution_result)
        self._apply_worker.failed.connect(self._handle_worker_error)
        self._apply_worker.finished.connect(lambda: self._set_busy(False))
        self._apply_worker.start()

    def _confirm_restore(self, *, defaults: bool) -> None:
        profile = self._selected_profile
        label = "padrao" if defaults else "snapshot mais recente"
        if QMessageBox.question(self, "Confirmar restauracao", f"Restaurar {label} para {profile.title}?") != QMessageBox.Yes:
            return
        self._set_busy(True, f"Restaurando {label}...")
        self._restore_worker = ProfileRestoreThread(
            self._context.profile_service,
            profile.key,
            restore_defaults=defaults,
        )
        self._restore_worker.completed.connect(self._handle_execution_result)
        self._restore_worker.failed.connect(self._handle_worker_error)
        self._restore_worker.finished.connect(lambda: self._set_busy(False))
        self._restore_worker.start()

    def _handle_execution_result(self, result: ProfileExecutionResult) -> None:
        self._status_label.setText(result.message)
        icon = QMessageBox.Information if result.success else QMessageBox.Warning
        detail_lines = [f"{item.action.title}: {item.result.outcome.value}" for item in result.action_results]
        if result.snapshot_path:
            detail_lines.append(f"Snapshot: {result.snapshot_path}")
        message = result.message
        if detail_lines:
            message = f"{message}\n\n" + "\n".join(detail_lines)
        QMessageBox(icon, "DroidBoost", message, QMessageBox.Ok, self).exec()

    def _handle_worker_error(self, message: str) -> None:
        self._status_label.setText(f"Falha: {message}")
        QMessageBox.warning(self, "DroidBoost", message)

    def _set_busy(self, busy: bool, message: str | None = None) -> None:
        for button in (self._preview_button, self._apply_button, self._restore_button, self._default_button):
            button.setDisabled(busy)
        self._profile_list.setDisabled(busy)
        self._apply_button.setText("Aplicando..." if busy else "Aplicar perfil")
        if message:
            self._status_label.setText(message)

    def _clear_actions(self) -> None:
        while self._actions_layout.count():
            item = self._actions_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        self._action_widgets.clear()
