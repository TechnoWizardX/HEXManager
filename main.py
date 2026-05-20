# main.py
import sys
from PySide6.QtWidgets import QApplication
from src.core import PluginManager
from src.theme import get_theme_manager
from src.userinterface import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Инициализируем менеджер тем и сразу применяем тему по умолчанию
    theme_manager = get_theme_manager()
    theme_manager.apply_theme("dark", app)   # "dark" | "light" | "mocha"

    manager = PluginManager(plugins_dir="src/plugins")
    manager.discover_plugins()

    window = MainWindow(manager, theme_manager)
    window.load_plugins()
    window.show()

    sys.exit(app.exec())