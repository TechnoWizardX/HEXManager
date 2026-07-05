# main.py
import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication
from src.core import PluginManager
from src.theme import get_theme_manager
from src.gui.userinterface import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # ThemeManager сам найдёт src/themes/*.json и base.qss
    theme_manager = get_theme_manager(themes_dir=Path("src/themes"))
    theme = Path("src/data/config.json")
    if theme.exists():
        import json
        with open(theme, encoding="utf-8") as f:
            config = json.load(f)
            theme_name = config.get("theme", "dark")
            theme_manager.apply_theme(theme_name, app)

    else:
        theme_manager.apply_theme("dark", app)
      # тема по умолчанию

    manager = PluginManager(plugins_dir="src/plugins")
    manager.discover_plugins()

    window = MainWindow(plugin_manager=manager, theme_manager=theme_manager, data_path="data")
    window.load_plugins()
    window.show()

    sys.exit(app.exec())