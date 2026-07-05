from PySide6.QtWidgets import (QWidget, QLabel, QVBoxLayout)
from PySide6.QtCore import Qt


class WelcomeWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        title = QLabel("HEXManager")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 36px; font-weight: bold;")

        subtitle = QLabel("Менеджер плагинов на PySide6")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("font-size: 14px;")

        tip = QLabel("Выберите плагин в боковой панели")
        tip.setAlignment(Qt.AlignCenter)
        tip.setStyleSheet("font-size: 12px; margin-top: 24px;")

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(tip)
