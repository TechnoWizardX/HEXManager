import sys

from PySide6.QtWidgets import QApplication

from src.core import PluginManager
from src.theme import get_theme_manager
from src.gui.userinterface import MainWindow
from src.paths import (
    user_themes_dir, user_plugins_dir,
    bundled_plugins_dir, ensure_user_dirs,
    load_config, save_config,
)


def _init_user_data() -> None:
    ensure_user_dirs()
    if not load_config().get("theme"):
        save_config({"theme": "dark"})


if __name__ == "__main__":
    app = QApplication(sys.argv)
    _init_user_data()

    theme_manager = get_theme_manager(themes_dir=user_themes_dir())
    theme_name = load_config().get("theme", "dark")
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
