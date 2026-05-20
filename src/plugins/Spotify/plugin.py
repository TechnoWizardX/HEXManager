# plugins/example/plugin.py
from src.core import PluginBase
from src.theme import ThemeManager
from pathlib import Path
from PySide6.QtWidgets import QLabel, QVBoxLayout, QFrame


class SpotifyPlugin(PluginBase):
    def __init__(self, plugin_path: Path):
        icon_path = plugin_path / "icons" / "plugin.png"
        super().__init__(
            plugin_path,
            name="Example Plugin",
            icon_path=str(icon_path),
        )
        self.label = QLabel("Spotify")
        self.label.setStyleSheet("font-size: 16px; font-weight: bold;")

        self.accent_demo = QFrame()
        self.accent_demo.setFixedHeight(4)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(16, 16, 16, 16)
        lay.addWidget(self.label)
        lay.addWidget(self.accent_demo)
        lay.addStretch()

    # Опционально: переопределяем apply_theme для ручной перекраски
    def apply_theme(self, theme_manager: ThemeManager) -> None:
        # Сначала применяем базовую логику (theme_overrides из JSON)
        super().apply_theme(theme_manager)

        # Затем вручную обновляем нативные элементы, которые не покрыты QSS
        accent = theme_manager.token("accent", "#4dabf7")
        self.accent_demo.setStyleSheet(f"background-color: {accent}; border-radius: 2px;")