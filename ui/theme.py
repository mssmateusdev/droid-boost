from __future__ import annotations

from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication


def apply_dark_theme(app: QApplication) -> None:
    app.setFont(QFont("Segoe UI", 10))
    app.setStyleSheet(
        """
        * {
            color: #F4F7FB;
            font-family: "Segoe UI";
            letter-spacing: 0px;
        }
        QMainWindow, QWidget#AppRoot {
            background: #0B0F14;
        }
        QWidget#Sidebar {
            background: #111821;
            border-right: 1px solid #273344;
        }
        QLabel#AppTitle {
            font-size: 22px;
            font-weight: 700;
            color: #F4F7FB;
        }
        QLabel#AppSubtitle, QLabel#MutedLabel {
            color: #AAB6C5;
        }
        QLabel#SectionTitle {
            font-size: 24px;
            font-weight: 700;
        }
        QLabel#HeroTitle {
            font-size: 13px;
            font-weight: 700;
            color: #AAB6C5;
        }
        QLabel#HeroDeviceName {
            font-size: 24px;
            font-weight: 700;
            color: #F4F7FB;
        }
        QLabel#HeroStatus {
            color: #AAB6C5;
            font-size: 13px;
        }
        QLabel#ConnectionDot {
            border-radius: 6px;
            min-width: 12px;
            max-width: 12px;
            min-height: 12px;
            max-height: 12px;
        }
        QLabel#CardTitle {
            font-size: 14px;
            font-weight: 700;
        }
        QLabel#MetricLabel {
            color: #AAB6C5;
            font-size: 12px;
            font-weight: 600;
        }
        QLabel#MetricValue {
            color: #F4F7FB;
            font-size: 14px;
            font-weight: 600;
        }
        QFrame#MetricTile {
            background: #111923;
            border: 1px solid #223044;
            border-radius: 8px;
        }
        QPushButton {
            background: #1B2531;
            border: 1px solid #273344;
            border-radius: 8px;
            padding: 9px 14px;
            font-weight: 600;
        }
        QPushButton:hover {
            background: #223044;
            border-color: #37516F;
        }
        QPushButton:pressed {
            background: #162030;
        }
        QPushButton:disabled {
            color: #667386;
            background: #121923;
            border-color: #202A37;
        }
        QPushButton#PrimaryButton {
            background: #37B6E6;
            color: #081018;
            border-color: #4CC9F0;
        }
        QPushButton#PrimaryButton:hover {
            background: #4CC9F0;
        }
        QPushButton#NavButton {
            text-align: left;
            padding: 11px 14px;
            border-radius: 8px;
            border: 1px solid transparent;
            background: transparent;
            color: #AAB6C5;
        }
        QPushButton#NavButton:hover {
            background: #172231;
            color: #F4F7FB;
        }
        QPushButton#NavButton[active="true"] {
            background: #1B2B3B;
            color: #F4F7FB;
            border-color: #2F4C65;
        }
        QFrame#Card {
            background: #151D27;
            border: 1px solid #273344;
            border-radius: 8px;
        }
        QFrame#HeroCard {
            background: #151D27;
            border: 1px solid #2F4C65;
            border-radius: 8px;
        }
        QFrame#Banner {
            background: #111923;
            border: 1px solid #273344;
            border-radius: 8px;
        }
        QFrame#StatusPill {
            border-radius: 999px;
            padding: 4px 10px;
        }
        QScrollArea {
            border: 0;
            background: transparent;
        }
        QScrollBar:vertical {
            background: #0B0F14;
            width: 10px;
            margin: 0;
        }
        QScrollBar::handle:vertical {
            background: #273344;
            border-radius: 5px;
            min-height: 28px;
        }
        QScrollBar::add-line:vertical,
        QScrollBar::sub-line:vertical {
            height: 0;
        }
        """
    )
