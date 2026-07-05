import sys
import json

from PySide6.QtWidgets import QApplication

from src.core import PluginManager
from src.theme import get_theme_manager
from src.gui.userinterface import MainWindow
from src.paths import (
    config_path, user_themes_dir, user_plugins_dir,
    bundled_themes_dir, bundled_plugins_dir, ensure_user_dirs,
)


def _init_user_data() -> None:
    """Создаёт структуру %APPDATA%/HEXManager/ при первом запуске."""
    ensure_user_dirs()

    if not config_path().exists():
        with open(config_path(), "w", encoding="utf-8") as f:
            json.dump({"theme": "dark"}, f, indent=2)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    _init_user_data()

    theme_manager = get_theme_manager(themes_dir=user_themes_dir())

    with open(config_path(), encoding="utf-8") as f:
        config = json.load(f)
    theme_name = config.get("theme", "dark")
    theme_manager.apply_theme(theme_name, app)

    manager = PluginManager(
        plugins_dir=user_plugins_dir(),
        bundled_dir=bundled_plugins_dir(),
    )
    manager.discover_plugins()

    window = MainWindow(plugin_manager=manager, theme_manager=theme_manager)
    window.load_plugins()
    window.show()

    sys.exit(app.exec())
