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
    theme_manager = get_theme_manager(themes_dir=Path("resources/themes"))
    config_file = Path("HEXManager/data/config.json")
    if config_file.exists():
        import json
        with open(config_file, encoding="utf-8") as f:
            config = json.load(f)
            theme_name = config.get("theme", "dark")
    else:
        theme_name = "dark"

    theme_manager.apply_theme(theme_name, app)

    manager = PluginManager(plugins_dir="resources/plugins")
    manager.discover_plugins()

    window = MainWindow(plugin_manager=manager, theme_manager=theme_manager)
    window.load_plugins()
    window.show()

    sys.exit(app.exec())