from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import Qt
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from app.features.apps.view import AppsPage
from app.features.backups.view import BackupsPage
from app.features.dashboard.view import DashboardPage
from app.features.logs.view import LogsPage
from app.features.profiles.view import ProfilesPage
from app.features.settings.view import SettingsPage
from app.features.tweaks.view import TweaksPage
from app.services.app_context import AppContext


@dataclass(frozen=True)
class NavItem:
    title: str
    page: QWidget


class MainWindow(QMainWindow):
    def __init__(self, context: AppContext) -> None:
        super().__init__()
        self._context = context
        self._buttons: list[QPushButton] = []
        self._stack = QStackedWidget()

        self.setWindowTitle("DroidBoost")
        self.resize(1220, 780)
        self.setMinimumSize(980, 640)
        self._build_ui()
        app = QApplication.instance()
        if app:
            app.aboutToQuit.connect(self._shutdown_pages)

    def open_logs(self) -> None:
        self._activate_index(5)

    def _build_ui(self) -> None:
        root = QWidget()
        root.setObjectName("AppRoot")
        root_layout = QHBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        sidebar = self._build_sidebar()
        root_layout.addWidget(sidebar)
        root_layout.addWidget(self._stack, 1)
        self.setCentralWidget(root)

        dashboard = DashboardPage(self._context)
        dashboard.open_logs_requested.connect(self.open_logs)

        items = [
            NavItem("Dashboard", dashboard),
            NavItem("Perfis", ProfilesPage(self._context)),
            NavItem("Tweaks rapidos", TweaksPage(self._context)),
            NavItem("Apps", AppsPage()),
            NavItem("Backups", BackupsPage()),
            NavItem("Logs", LogsPage(self._context)),
            NavItem("Configuracoes", SettingsPage(self._context)),
        ]

        for index, item in enumerate(items):
            self._stack.addWidget(item.page)
            button = QPushButton(item.title)
            button.setObjectName("NavButton")
            button.setCursor(Qt.PointingHandCursor)
            button.clicked.connect(lambda checked=False, item_index=index: self._activate_index(item_index))
            self._buttons.append(button)
            self._nav_layout.addWidget(button)

        self._nav_layout.addStretch(1)
        self._activate_index(0)

    def closeEvent(self, event: QCloseEvent) -> None:
        self._shutdown_pages()
        super().closeEvent(event)

    def _build_sidebar(self) -> QFrame:
        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(232)
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(18, 22, 18, 18)
        layout.setSpacing(12)

        title = QLabel("DroidBoost")
        title.setObjectName("AppTitle")
        subtitle = QLabel("Android ADB optimizer")
        subtitle.setObjectName("AppSubtitle")
        subtitle.setWordWrap(True)

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addSpacing(18)
        self._nav_layout = layout
        return sidebar

    def _activate_index(self, index: int) -> None:
        self._stack.setCurrentIndex(index)
        for button_index, button in enumerate(self._buttons):
            button.setProperty("active", button_index == index)
            button.style().unpolish(button)
            button.style().polish(button)

    def _shutdown_pages(self) -> None:
        for index in range(self._stack.count()):
            page = self._stack.widget(index)
            shutdown = getattr(page, "shutdown_workers", None)
            if callable(shutdown):
                shutdown()
