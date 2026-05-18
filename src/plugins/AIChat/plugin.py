from src.core import PluginBase
from pathlib import Path
from PySide6.QtWidgets import QLabel, QWidget, QFrame, QVBoxLayout
class AIChat(PluginBase):
    def __init__(self, plugin_path: Path):
        icon_path = plugin_path / "icons" / "plugin.png"   # создаём Path
        super().__init__(
            plugin_path,
            name="AI Chat Plugin",
            icon_path=str(icon_path)   # передаём строку с абсолютным путём
        )
        self.label = QLabel("There WIll Be AI Chat")
        self.lay = QVBoxLayout(self)
        self.lay.addWidget(self.label)