from __future__ import annotations

from PySide6.QtCore import Qt, QUrl, Signal
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from app.domain.capabilities import DeviceCapabilities
from app.domain.device import DeviceInfo
from app.features.dashboard.presenter import DashboardDisplay, build_dashboard_display
from app.features.dashboard.workers import ADBReconnectThread, DeviceDetectionThread
from app.services.app_context import AppContext
from app.services.device_detection_service import DeviceReport
from app.ui.components.card import Card
from app.ui.components.metric import Metric
from app.ui.components.status_pill import StatusPill


class DashboardPage(QWidget):
    open_logs_requested = Signal()

    def __init__(self, context: AppContext) -> None:
        super().__init__()
        self._context = context
        self._worker: DeviceDetectionThread | None = None
        self._reconnect_worker: ADBReconnectThread | None = None
        self._metrics: dict[str, Metric] = {}
        self._capability_metrics: dict[str, Metric] = {}
        self._build_ui()
        self._set_initial_state()
        self.refresh()

    def refresh(self) -> None:
        if self._worker and self._worker.isRunning():
            return
        self._set_busy(True, "Lendo estado do ADB e do dispositivo...")
        self._worker = DeviceDetectionThread(self._context.device_service)
        self._worker.detected.connect(self._handle_report)
        self._worker.failed.connect(self._handle_error)
        self._worker.finished.connect(lambda: self._set_busy(False))
        self._worker.start()

    def reconnect_adb(self) -> None:
        if self._reconnect_worker and self._reconnect_worker.isRunning():
            return
        self._set_busy(True, "Reiniciando servidor ADB...")
        self._reconnect_worker = ADBReconnectThread(self._context.device_service)
        self._reconnect_worker.completed.connect(self._handle_reconnect_completed)
        self._reconnect_worker.failed.connect(self._handle_reconnect_failed)
        self._reconnect_worker.start()

    def open_logs_folder(self) -> None:
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(self._context.paths.logs_dir)))

    def shutdown_workers(self) -> None:
        for worker in (self._worker, self._reconnect_worker):
            if worker and worker.isRunning():
                worker.wait(5000)

    def _build_ui(self) -> None:
        page_layout = QVBoxLayout(self)
        page_layout.setContentsMargins(0, 0, 0, 0)
        page_layout.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(28, 26, 28, 28)
        content_layout.setSpacing(18)

        content_layout.addLayout(self._build_header())
        content_layout.addWidget(self._build_banner())
        content_layout.addWidget(self._build_hero())
        content_layout.addLayout(self._build_main_grid())
        content_layout.addWidget(self._build_capabilities_card())
        content_layout.addStretch(1)

        scroll.setWidget(content)
        page_layout.addWidget(scroll)

    def _build_header(self) -> QHBoxLayout:
        header = QHBoxLayout()
        header.setSpacing(10)
        title_group = QVBoxLayout()
        title_group.setSpacing(5)

        title = QLabel("Dashboard do dispositivo")
        title.setObjectName("SectionTitle")
        subtitle = QLabel("Diagnostico seguro de ADB, conexao, root e recursos disponiveis.")
        subtitle.setObjectName("MutedLabel")
        subtitle.setWordWrap(True)
        title_group.addWidget(title)
        title_group.addWidget(subtitle)

        self._refresh_button = QPushButton("Atualizar leitura")
        self._refresh_button.setObjectName("PrimaryButton")
        self._refresh_button.clicked.connect(self.refresh)

        self._reconnect_button = QPushButton("Reconectar ADB")
        self._reconnect_button.clicked.connect(self.reconnect_adb)

        self._logs_button = QPushButton("Abrir logs")
        self._logs_button.clicked.connect(self.open_logs_requested.emit)

        self._logs_folder_button = QPushButton("Pasta de logs")
        self._logs_folder_button.clicked.connect(self.open_logs_folder)

        header.addLayout(title_group, 1)
        header.addWidget(self._logs_folder_button, 0, Qt.AlignTop)
        header.addWidget(self._logs_button, 0, Qt.AlignTop)
        header.addWidget(self._reconnect_button, 0, Qt.AlignTop)
        header.addWidget(self._refresh_button, 0, Qt.AlignTop)
        return header

    def _build_banner(self) -> QFrame:
        banner = QFrame()
        banner.setObjectName("Banner")
        layout = QHBoxLayout(banner)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(10)

        self._banner_dot = QLabel()
        self._banner_dot.setObjectName("ConnectionDot")
        self._status_message = QLabel("Aguardando leitura inicial.")
        self._status_message.setObjectName("HeroStatus")
        self._status_message.setWordWrap(True)

        layout.addWidget(self._banner_dot, 0, Qt.AlignTop)
        layout.addWidget(self._status_message, 1)
        return banner

    def _build_hero(self) -> QFrame:
        hero = QFrame()
        hero.setObjectName("HeroCard")
        layout = QHBoxLayout(hero)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(18)

        left = QVBoxLayout()
        left.setSpacing(8)
        eyebrow_row = QHBoxLayout()
        eyebrow_row.setSpacing(8)
        self._connection_dot = QLabel()
        self._connection_dot.setObjectName("ConnectionDot")
        self._connection_label = QLabel("Conexao")
        self._connection_label.setObjectName("HeroTitle")
        eyebrow_row.addWidget(self._connection_dot)
        eyebrow_row.addWidget(self._connection_label)
        eyebrow_row.addStretch(1)

        self._device_name_label = QLabel("Aguardando conexao")
        self._device_name_label.setObjectName("HeroDeviceName")
        self._device_name_label.setWordWrap(True)
        self._connection_description = QLabel("Conecte um dispositivo Android com depuracao USB ativa.")
        self._connection_description.setObjectName("HeroStatus")
        self._connection_description.setWordWrap(True)

        status_row = QHBoxLayout()
        status_row.setSpacing(8)
        self._adb_pill = StatusPill("ADB", "neutral")
        self._device_pill = StatusPill("Device", "neutral")
        self._root_pill = StatusPill("Root", "neutral")
        status_row.addWidget(self._adb_pill)
        status_row.addWidget(self._device_pill)
        status_row.addWidget(self._root_pill)
        status_row.addStretch(1)

        left.addLayout(eyebrow_row)
        left.addWidget(self._device_name_label)
        left.addWidget(self._connection_description)
        left.addLayout(status_row)

        right = QGridLayout()
        right.setHorizontalSpacing(10)
        right.setVerticalSpacing(10)
        self._summary_metrics = {
            "root": Metric("Root", "-"),
            "capabilities": Metric("Capabilities", "-"),
            "android": Metric("Android", "-"),
            "battery": Metric("Bateria", "-"),
        }
        for index, metric in enumerate(self._summary_metrics.values()):
            row, col = divmod(index, 2)
            right.addWidget(metric, row, col)

        layout.addLayout(left, 3)
        layout.addLayout(right, 2)
        return hero

    def _build_main_grid(self) -> QGridLayout:
        grid = QGridLayout()
        grid.setHorizontalSpacing(18)
        grid.setVerticalSpacing(18)
        grid.addWidget(self._build_device_card(), 0, 0)
        grid.addWidget(self._build_runtime_card(), 0, 1)
        grid.addWidget(self._build_adb_card(), 1, 0, 1, 2)
        return grid

    def _build_device_card(self) -> Card:
        card = Card("Identidade do aparelho")
        grid = QGridLayout()
        grid.setHorizontalSpacing(12)
        grid.setVerticalSpacing(12)
        self._add_metric_grid(
            grid,
            (
                ("model", "Modelo"),
                ("manufacturer", "Fabricante"),
                ("android", "Android version"),
                ("api", "API level"),
                ("serial", "Serial"),
                ("abi", "ABI"),
            ),
            columns=2,
        )
        card.add_widget(self._wrap_layout(grid))
        return card

    def _build_runtime_card(self) -> Card:
        card = Card("Recursos do sistema")
        grid = QGridLayout()
        grid.setHorizontalSpacing(12)
        grid.setVerticalSpacing(12)
        self._add_metric_grid(
            grid,
            (
                ("ram", "RAM"),
                ("storage", "Armazenamento"),
                ("battery", "Bateria"),
                ("root_status", "Root status"),
            ),
            columns=2,
        )
        card.add_widget(self._wrap_layout(grid))
        return card

    def _build_adb_card(self) -> Card:
        card = Card("Ambiente ADB")
        grid = QGridLayout()
        grid.setHorizontalSpacing(12)
        grid.setVerticalSpacing(12)
        self._add_metric_grid(
            grid,
            (
                ("adb_path", "Executavel"),
                ("adb_source", "Origem"),
                ("adb_version", "Versao"),
                ("device_status", "Estado do device"),
            ),
            columns=2,
        )
        card.add_widget(self._wrap_layout(grid))
        return card

    def _build_capabilities_card(self) -> Card:
        card = Card("Capabilities do aparelho")
        grid = QGridLayout()
        grid.setHorizontalSpacing(12)
        grid.setVerticalSpacing(12)
        capability_labels = (
            ("can_use_root_commands", "Root commands"),
            ("can_manage_packages", "Gerenciar pacotes"),
            ("can_change_animations", "Alterar animacoes"),
            ("can_clear_cache", "Limpar cache"),
            ("can_run_advanced_profiles", "Perfis avancados"),
            ("can_read_diagnostics", "Diagnosticos"),
        )
        for index, (key, label) in enumerate(capability_labels):
            metric = Metric(label)
            self._capability_metrics[key] = metric
            row, col = divmod(index, 3)
            grid.addWidget(metric, row, col)
        card.add_widget(self._wrap_layout(grid))
        return card

    def _add_metric_grid(
        self,
        grid: QGridLayout,
        items: tuple[tuple[str, str], ...],
        *,
        columns: int,
    ) -> None:
        for index, (key, label) in enumerate(items):
            metric = Metric(label)
            self._metrics[key] = metric
            row, col = divmod(index, columns)
            grid.addWidget(metric, row, col)

    def _set_initial_state(self) -> None:
        self._set_connection_tone("neutral")
        self._adb_pill.set_status("ADB: aguardando", "neutral")
        self._device_pill.set_status("Device: aguardando", "neutral")
        self._root_pill.set_status("Root: aguardando", "neutral")
        for metric in self._metrics.values():
            metric.set_value(None)
        for metric in self._summary_metrics.values():
            metric.set_value(None)
        for metric in self._capability_metrics.values():
            metric.set_value("Bloqueado")

    def _handle_reconnect_completed(self) -> None:
        self._status_message.setText("Servidor ADB reiniciado. Atualizando leitura...")
        self.refresh()

    def _handle_reconnect_failed(self, message: str) -> None:
        self._handle_error(message)
        self._set_busy(False)

    def _handle_report(self, report: DeviceReport) -> None:
        display = build_dashboard_display(report)
        self._update_connection(display)
        self._update_status_pills(display)
        self._update_adb_metrics(report)
        self._update_device_metrics(report.device)
        self._update_summary_metrics(report, display)
        self._update_capabilities(report.capabilities)

    def _handle_error(self, message: str) -> None:
        self._set_connection_tone("danger")
        self._connection_label.setText("Falha na leitura")
        self._device_name_label.setText("Dashboard indisponivel")
        self._connection_description.setText(message)
        self._adb_pill.set_status("ADB: erro", "danger")
        self._device_pill.set_status("Device: indisponivel", "danger")
        self._root_pill.set_status("Root: indisponivel", "neutral")
        self._status_message.setText(f"Falha na deteccao: {message}")

    def _update_connection(self, display: DashboardDisplay) -> None:
        self._set_connection_tone(display.connection_tone)
        self._connection_label.setText(display.connection_title)
        self._device_name_label.setText(display.device_name)
        self._connection_description.setText(display.connection_description)
        self._status_message.setText(display.connection_description)

    def _update_status_pills(self, display: DashboardDisplay) -> None:
        self._adb_pill.set_status(display.adb.text, display.adb.tone)
        self._device_pill.set_status(display.device.text, display.device.tone)
        self._root_pill.set_status(display.root.text, display.root.tone)

    def _update_adb_metrics(self, report: DeviceReport) -> None:
        self._metrics["adb_path"].set_value(report.adb.executable)
        self._metrics["adb_source"].set_value(report.adb.source)
        self._metrics["adb_version"].set_value(report.adb.version)
        self._metrics["device_status"].set_value(report.device.status.value)

    def _update_device_metrics(self, device: DeviceInfo) -> None:
        self._metrics["model"].set_value(device.model)
        self._metrics["manufacturer"].set_value(device.manufacturer)
        self._metrics["android"].set_value(device.android_version)
        self._metrics["api"].set_value(device.api_level)
        self._metrics["serial"].set_value(device.serial)
        self._metrics["abi"].set_value(device.abi)
        self._metrics["ram"].set_value(self._format_ram(device))
        self._metrics["storage"].set_value(self._format_storage(device))
        self._metrics["battery"].set_value(self._format_battery(device))

    def _update_summary_metrics(self, report: DeviceReport, display: DashboardDisplay) -> None:
        self._summary_metrics["root"].set_value(report.root.state.value)
        self._summary_metrics["capabilities"].set_value(display.capabilities_enabled)
        self._summary_metrics["android"].set_value(report.device.android_version)
        self._summary_metrics["battery"].set_value(self._format_battery(report.device))
        self._metrics["root_status"].set_value(report.root.details or report.root.state.value)

    def _update_capabilities(self, capabilities: DeviceCapabilities) -> None:
        for key, metric in self._capability_metrics.items():
            enabled = bool(getattr(capabilities, key))
            metric.set_value("Liberado" if enabled else "Bloqueado")

    def _set_busy(self, busy: bool, message: str | None = None) -> None:
        self._refresh_button.setDisabled(busy)
        self._reconnect_button.setDisabled(busy)
        self._logs_button.setDisabled(busy)
        self._logs_folder_button.setDisabled(busy)
        self._refresh_button.setText("Lendo..." if busy else "Atualizar leitura")
        if message:
            self._status_message.setText(message)
            self._connection_description.setText(message)
            self._set_connection_tone("accent")

    def _set_connection_tone(self, tone: str) -> None:
        colors = {
            "success": "#46D39A",
            "warning": "#F6C350",
            "danger": "#FF6B6B",
            "accent": "#4CC9F0",
            "neutral": "#667386",
        }
        color = colors.get(tone, colors["neutral"])
        style = f"background: {color}; border: 1px solid {color}; border-radius: 6px;"
        self._connection_dot.setStyleSheet(style)
        self._banner_dot.setStyleSheet(style)

    @staticmethod
    def _format_ram(device: DeviceInfo) -> str | None:
        return f"{device.ram_total_gb:.2f} GB" if device.ram_total_gb is not None else None

    @staticmethod
    def _format_storage(device: DeviceInfo) -> str | None:
        if not device.storage:
            return None
        return f"{device.storage.used_gb:.1f} / {device.storage.total_gb:.1f} GB"

    @staticmethod
    def _format_battery(device: DeviceInfo) -> str | None:
        if device.battery_level is None:
            return None
        return f"{device.battery_level}%"

    @staticmethod
    def _wrap_layout(layout: QGridLayout) -> QWidget:
        widget = QWidget()
        widget.setLayout(layout)
        return widget
