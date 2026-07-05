from PySide6.QtWidgets import (
    QMainWindow, QWidget, QLabel, QPushButton,
    QSplitter, QFrame, QStackedWidget, QVBoxLayout, QHBoxLayout,
    QComboBox, QGroupBox, QListWidget, QListWidgetItem, QLineEdit,
    QStatusBar,
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QFontMetrics

from src.core import PluginManager, PluginBase
from src.theme import ThemeManager, get_theme_manager
from src.paths import load_config, save_config, user_plugins_dir, user_icons_dir
from src.gui.widgets import WelcomeWidget
from typing import Optional


class MainWindow(QMainWindow):
    def __init__(self, plugin_manager: PluginManager,
                 theme_manager: Optional[ThemeManager] = None,
                 parent=None):
        super().__init__()

        self.plugin_manager = plugin_manager
        self.theme_manager = theme_manager or get_theme_manager()
        self.current_plugin: Optional[PluginBase] = None
        self._icon_mode = False
        self._icon_mode_threshold = 80
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
        self.side_panel.setMaximumWidth(280)
        side_layout = QVBoxLayout(self.side_panel)
        side_layout.setContentsMargins(4, 4, 4, 4)
        side_layout.setSpacing(4)

        # Поиск плагинов
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск плагинов...")
        self.search_input.textChanged.connect(self._filter_plugins)

        # Список плагинов (QListWidget с drag-drop)
        self.plugin_list = QListWidget()
        self.plugin_list.setDragDropMode(QListWidget.InternalMove)
        self.plugin_list.setDefaultDropAction(Qt.MoveAction)
        self.plugin_list.setIconSize(QSize(32, 32))
        self.plugin_list.setSpacing(2)
        self.plugin_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.plugin_list.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.plugin_list.currentItemChanged.connect(self._on_list_item_changed)

        # Кнопка настроек
        self.global_settings_btn = QPushButton("Настройки")
        icon_path = user_icons_dir() / "settings.png"
        if icon_path.exists():
            self.global_settings_btn.setIcon(QIcon(str(icon_path)))
        self.global_settings_btn.setIconSize(QSize(24, 24))
        self.global_settings_btn.setCheckable(True)
        self.global_settings_btn.clicked.connect(self.show_global_settings)

        side_layout.addWidget(self.search_input)
        side_layout.addWidget(self.plugin_list)
        side_layout.addWidget(self.global_settings_btn)

        # ----- Правая панель (стек) -----
        self.content_stack = QStackedWidget()

        self.welcome_widget = WelcomeWidget()
        self.content_stack.addWidget(self.welcome_widget)

        self.global_settings_widget = GlobalSettingsWidget(self.theme_manager)
        self.content_stack.addWidget(self.global_settings_widget)

        self.h_splitter.addWidget(self.side_panel)
        self.h_splitter.addWidget(self.content_stack)
        self.h_splitter.setSizes([220, 680])

        # Статусбар
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        self.plugins_count_label = QLabel()
        self.current_plugin_label = QLabel()
        self.theme_label = QLabel()
        self.status_bar.addWidget(self.plugins_count_label)
        self.status_bar.addPermanentWidget(self.current_plugin_label)
        self.status_bar.addPermanentWidget(self.theme_label)

        self.theme_manager.theme_changed.connect(self._on_theme_changed)
        self.h_splitter.splitterMoved.connect(self._on_splitter_moved)

        self._restore_state()

    # ------------------------------------------------------------------
    # Загрузка плагинов
    # ------------------------------------------------------------------

    def load_plugins(self) -> None:
        plugins = self.plugin_manager.get_plugins()
        saved_order = self._load_plugin_order()

        if saved_order:
            plugin_map = {p.id(): p for p in plugins}
            ordered = []
            for pid in saved_order:
                if pid in plugin_map:
                    ordered.append(plugin_map.pop(pid))
            ordered.extend(plugin_map.values())
            plugins = ordered

        self.plugin_list.clear()

        if not plugins:
            item = QListWidgetItem("Нет загруженных плагинов")
            item.setFlags(Qt.NoItemFlags)
            self.plugin_list.addItem(item)
            self.content_stack.setCurrentWidget(self.welcome_widget)
            self._update_status_bar()
            return

        for plugin in plugins:
            item = QListWidgetItem(plugin.icon(), plugin.name())
            item.setData(Qt.UserRole, plugin)
            item.setSizeHint(QSize(200, 44))
            self.plugin_list.addItem(item)
            self.content_stack.addWidget(plugin.plugin_content())
            plugin.apply_theme(self.theme_manager)

        self.content_stack.setCurrentWidget(self.welcome_widget)
        self._calc_icon_threshold()
        self._update_sidebar_mode()
        self._update_status_bar()

    # ------------------------------------------------------------------
    # Collapse-режим (иконки без текста)
    # ------------------------------------------------------------------

    def _calc_icon_threshold(self) -> None:
        fm = QFontMetrics(self.plugin_list.font())
        max_w = 0
        for p in self.plugin_manager.get_plugins():
            w = fm.horizontalAdvance(p.name())
            if w > max_w:
                max_w = w
        self._icon_mode_threshold = max(max_w // 2, 50)

    def _update_sidebar_mode(self) -> None:
        width = self.side_panel.width()
        icon_mode = width < self._icon_mode_threshold
        self._apply_icon_mode(icon_mode)

    def _on_splitter_moved(self, pos: int, index: int) -> None:
        self._apply_icon_mode(self.side_panel.width() < self._icon_mode_threshold)

    def _apply_icon_mode(self, icon_mode: bool) -> None:
        if icon_mode == self._icon_mode:
            return
        self._icon_mode = icon_mode

        for i in range(self.plugin_list.count()):
            item = self.plugin_list.item(i)
            plugin = item.data(Qt.UserRole)
            if not plugin:
                continue
            item.setText("" if icon_mode else plugin.name())

        self.search_input.setVisible(not icon_mode)
        self.plugin_list.setIconSize(QSize(36, 36) if icon_mode else QSize(32, 32))

    # ------------------------------------------------------------------
    # Навигация
    # ------------------------------------------------------------------

    def _on_list_item_changed(self, current: Optional[QListWidgetItem],
                              previous: Optional[QListWidgetItem]) -> None:
        self.global_settings_btn.setChecked(current is None)
        if current and current.flags() & Qt.ItemIsSelectable:
            plugin: PluginBase = current.data(Qt.UserRole)
            self.current_plugin = plugin
            widget = plugin.plugin_content()
            idx = self.content_stack.indexOf(widget)
            if idx >= 0:
                self.content_stack.setCurrentWidget(widget)
        self._update_status_bar()

    def show_global_settings(self) -> None:
        self.current_plugin = None
        self.plugin_list.blockSignals(True)
        self.plugin_list.clearSelection()
        self.plugin_list.setCurrentItem(None)
        self.plugin_list.blockSignals(False)
        self.content_stack.setCurrentWidget(self.global_settings_widget)
        self.global_settings_btn.setChecked(True)
        self._update_status_bar()

    # ------------------------------------------------------------------
    # Фильтр плагинов
    # ------------------------------------------------------------------

    def _filter_plugins(self, text: str) -> None:
        text = text.lower()
        for i in range(self.plugin_list.count()):
            item = self.plugin_list.item(i)
            plugin: Optional[PluginBase] = item.data(Qt.UserRole)
            if plugin is None:
                continue
            item.setHidden(text not in plugin.name().lower())

    # ------------------------------------------------------------------
    # Статусбар
    # ------------------------------------------------------------------

    def _update_status_bar(self) -> None:
        count = self.plugin_list.count()
        theme_name = self.theme_manager.display_name(
            self.theme_manager.current_theme_name()
        )
        current_name = self.current_plugin.name() if self.current_plugin else "—"
        self.plugins_count_label.setText(f"Плагинов: {count}  |  ")
        self.current_plugin_label.setText(f"Активен: {current_name}  |  ")
        self.theme_label.setText(f"Тема: {theme_name}")

    # ------------------------------------------------------------------
    # Сохранение / восстановление состояния
    # ------------------------------------------------------------------

    def _restore_state(self) -> None:
        from PySide6.QtCore import QByteArray
        cfg = load_config()
        geom = cfg.get("window_geometry")
        if geom:
            self.restoreGeometry(QByteArray(bytes(geom)))
        state = cfg.get("window_state")
        if state:
            self.restoreState(QByteArray(bytes(state)))
        sizes = cfg.get("splitter_sizes")
        if sizes:
            self.h_splitter.setSizes(sizes)

    def _save_state(self) -> None:
        order = self._get_plugin_order()
        save_config({
            "window_geometry": list(bytes(self.saveGeometry())),
            "window_state": list(bytes(self.saveState())),
            "splitter_sizes": list(self.h_splitter.sizes()),
            "plugin_order": order,
        })

    def _get_plugin_order(self) -> list:
        order = []
        for i in range(self.plugin_list.count()):
            item = self.plugin_list.item(i)
            plugin: Optional[PluginBase] = item.data(Qt.UserRole)
            if plugin:
                order.append(plugin.id())
        return order

    def _load_plugin_order(self) -> list:
        return load_config().get("plugin_order", [])

    def closeEvent(self, event) -> None:
        self._save_state()
        super().closeEvent(event)

    # ------------------------------------------------------------------
    # Смена темы
    # ------------------------------------------------------------------

    def _on_theme_changed(self, theme_name: str) -> None:
        self._update_status_bar()
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
            save_config({"theme": theme_id})

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
