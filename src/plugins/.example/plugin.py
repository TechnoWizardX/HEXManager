from src.core import PluginBase
from pathlib import Path
from PySide6.QtWidgets import QLabel, QWidget, QFrame, QVBoxLayout
class ExamplePlugin(PluginBase):
    def __init__(self, plugin_path: Path):
        icon_path = plugin_path / "icons" / "plugin.png"   # создаём Path
        super().__init__(
            plugin_path,
            name="Example Plugin",
            icon_path=str(icon_path)   # передаём строку с абсолютным путём
        )
        self.label = QLabel("This is an example plugin")
        self.lay = QVBoxLayout(self)
        self.lay.addWidget(self.label)