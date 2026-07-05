import json

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QLabel, QPushButton, QScrollArea,
    QSplitter, QFrame, QStackedWidget, QVBoxLayout, QHBoxLayout,
    QFileDialog, QComboBox, QGroupBox
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon

from src.core import PluginManager, PluginBase
from src.theme import ThemeManager, get_theme_manager
from src.paths import config_path, user_plugins_dir, user_icons_dir
from typing import Optional


class MainWindow(QMainWindow):
    def __init__(self, plugin_manager: PluginManager,
                 theme_manager: Optional[ThemeManager] = None,
                 parent=None):
        super().__init__()

        self.plugin_manager = plugin_manager
        self.theme_manager = theme_manager or get_theme_manager()
        self.current_plugin: Optional[PluginBase] = None
        self.setWindowTitle("HEXManager")
        self.resize(900, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)

        self.h_splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(self.h_splitter)

        # ----- Левая панель -----
        self.side_panel = QFrame()
        self.side_panel.setMaximumWidth(300)
        side_layout = QVBoxLayout(self.side_panel)
        side_layout.setContentsMargins(5, 5, 5, 5)

        self.plugins_container = QWidget()
        self.plugins_layout = QVBoxLayout(self.plugins_container)
        self.plugins_layout.setAlignment(Qt.AlignTop)
        self.plugins_layout.setSpacing(5)

        self.scroll_plugins = QScrollArea()
        self.scroll_plugins.setWidgetResizable(True)
        self.scroll_plugins.setWidget(self.plugins_container)
        self.scroll_plugins.setFrameShape(QFrame.NoFrame)
        self.scroll_plugins.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_plugins.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.global_settings_btn = QPushButton("Настройки")
        icon_path = user_icons_dir() / "settings.png"
        if icon_path.exists():
            self.global_settings_btn.setIcon(QIcon(str(icon_path)))
        self.global_settings_btn.setIconSize(QSize(24, 24))
        self.global_settings_btn.setCheckable(True)
        self.global_settings_btn.clicked.connect(self.show_global_settings)

        side_layout.addWidget(self.scroll_plugins)
        side_layout.addWidget(self.global_settings_btn)

        # ----- Правая панель (стек) -----
        self.content_stack = QStackedWidget()

        self.global_settings_widget = GlobalSettingsWidget(self.theme_manager)
        self.content_stack.addWidget(self.global_settings_widget)

        self.h_splitter.addWidget(self.side_panel)
        self.h_splitter.addWidget(self.content_stack)
        self.h_splitter.setSizes([200, 700])

        self.theme_manager.theme_changed.connect(self._on_theme_changed)

    # ------------------------------------------------------------------

    def load_plugins(self) -> None:
        plugins = self.plugin_manager.get_plugins()
        if not plugins:
            label = QLabel("Нет загруженных плагинов")
            label.setAlignment(Qt.AlignCenter)
            self.plugins_layout.addWidget(label)
            return

        for plugin in plugins:
            btn = QPushButton(plugin.icon(), plugin.name())
            btn.setIconSize(plugin.icon().actualSize(QSize(32, 32)))
            btn.setCheckable(True)
            btn.setToolTip(plugin.name())
            btn.clicked.connect(lambda checked, p=plugin: self.switch_to_plugin(p))
            self.plugins_layout.addWidget(btn)

            self.content_stack.addWidget(plugin.plugin_content())

            plugin.apply_theme(self.theme_manager)

        self.global_settings_btn.setChecked(True)
        self.content_stack.setCurrentWidget(self.global_settings_widget)

        for i in range(self.plugins_layout.count()):
            btn = self.plugins_layout.itemAt(i).widget()
            if isinstance(btn, QPushButton):
                btn.setChecked(False)

    def switch_to_plugin(self, plugin: PluginBase) -> None:
        self.current_plugin = plugin
        self.global_settings_btn.setChecked(False)

        widget = plugin.plugin_content()
        index = self.content_stack.indexOf(widget)
        if index >= 0:
            self.content_stack.setCurrentWidget(widget)
        else:
            self.content_stack.addWidget(widget)
            self.content_stack.setCurrentWidget(widget)

        for i in range(self.plugins_layout.count()):
            btn = self.plugins_layout.itemAt(i).widget()
            if isinstance(btn, QPushButton):
                btn.setChecked(btn.text() == plugin.name())

    def show_global_settings(self) -> None:
        self.current_plugin = None
        self.content_stack.setCurrentWidget(self.global_settings_widget)

        for i in range(self.plugins_layout.count()):
            btn = self.plugins_layout.itemAt(i).widget()
            if isinstance(btn, QPushButton):
                btn.setChecked(False)

        self.global_settings_btn.setChecked(True)

    # ------------------------------------------------------------------
    # Смена темы
    # ------------------------------------------------------------------

    def _on_theme_changed(self, theme_name: str) -> None:
        for plugin in self.plugin_manager.get_plugins():
            plugin.apply_theme(self.theme_manager)


# ---------------------------------------------------------------------------
# Виджет глобальных настроек
# ---------------------------------------------------------------------------

class GlobalSettingsWidget(QWidget):
    def __init__(self, theme_manager: Optional[ThemeManager] = None, parent=None):
        super().__init__(parent)
        self.theme_manager = theme_manager or get_theme_manager()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # --- Блок темы ---
        theme_group = QGroupBox("Оформление")
        theme_layout = QVBoxLayout(theme_group)

        theme_label = QLabel("Тема приложения:")
        self.theme_combo = QComboBox()
        self._populate_themes()
        self.theme_combo.currentTextChanged.connect(self._on_theme_selected)

        theme_layout.addWidget(theme_label)
        theme_layout.addWidget(self.theme_combo)
        layout.addWidget(theme_group)

        # --- Блок плагинов ---
        plugins_group = QGroupBox("Плагины")
        plugins_layout = QVBoxLayout(plugins_group)

        plugins_path_label = QLabel(f"Папка плагинов: {user_plugins_dir()}")
        open_plugins_btn = QPushButton("Открыть папку плагинов")
        open_plugins_btn.clicked.connect(self._open_plugins_folder)

        plugins_layout.addWidget(plugins_path_label)
        plugins_layout.addWidget(open_plugins_btn)
        layout.addWidget(plugins_group)

        layout.addStretch()

        self.theme_manager.theme_changed.connect(self._sync_combo)

    def _populate_themes(self) -> None:
        self.theme_combo.blockSignals(True)
        self.theme_combo.clear()

        for theme_id in self.theme_manager.available_themes():
            display = self.theme_manager.display_name(theme_id)
            self.theme_combo.addItem(display, userData=theme_id)

        current = self.theme_manager.current_theme_name()
        idx = self.theme_combo.findData(current)
        if idx >= 0:
            self.theme_combo.setCurrentIndex(idx)

        self.theme_combo.blockSignals(False)

    def _on_theme_selected(self, _display_name: str) -> None:
        theme_id = self.theme_combo.currentData()
        if theme_id and theme_id != self.theme_manager.current_theme_name():
            self.theme_manager.apply_theme(theme_id)
            self._save_config(theme_id)

    def _save_config(self, theme_id: str) -> None:
        try:
            cfg = {"theme": theme_id}
            with open(config_path(), "w", encoding="utf-8") as f:
                json.dump(cfg, f, indent=2)
        except OSError as e:
            print(f"Failed to save config: {e}")

    def _sync_combo(self, _theme_name: str) -> None:
        current = self.theme_manager.current_theme_name()
        idx = self.theme_combo.findData(current)
        if idx >= 0:
            self.theme_combo.blockSignals(True)
            self.theme_combo.setCurrentIndex(idx)
            self.theme_combo.blockSignals(False)

    def _open_plugins_folder(self) -> None:
        import subprocess
        path = str(user_plugins_dir())
        try:
            subprocess.Popen(["explorer", path])
        except OSError:
            pass
