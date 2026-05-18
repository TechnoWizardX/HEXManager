# main.py (корень проекта)
import sys
from PySide6.QtWidgets import QApplication
from src.core import PluginManager
from src.userinterface import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    manager = PluginManager(plugins_dir="src/plugins")
    manager.discover_plugins()
    window = MainWindow(manager)
    window.load_plugins()
    window.show()
    sys.exit(app.exec())