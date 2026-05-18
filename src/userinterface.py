# src/userinterface.py
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QLabel, QPushButton, QScrollArea,
    QSplitter, QFrame, QStackedWidget, QVBoxLayout, QHBoxLayout,
    QFileDialog, QMessageBox
)
from PySide6.QtCore import Qt, QSettings, QSize
from PySide6.QtGui import QIcon

from src.core import PluginManager, PluginBase
from typing import Optional

class MainWindow(QMainWindow):
    def __init__(self, plugin_manager: PluginManager):
        super().__init__()
        
        self.plugin_manager = plugin_manager
        self.current_plugin: Optional[PluginBase] = None
        
        self.setWindowTitle("HEXManager")
        self.resize(900, 600)

        # Центральный виджет и горизонтальный сплиттер
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)

        self.h_splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(self.h_splitter)

        # ----- Левая панель (боковое меню) -----
        self.side_panel = QFrame()
        side_layout = QVBoxLayout(self.side_panel)
        side_layout.setContentsMargins(0, 0, 0, 0)

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


        self.global_settings_btn = QPushButton("Общие настройки")
        self.global_settings_btn.setCheckable(True)
        self.global_settings_btn.clicked.connect(self.show_global_settings)

        side_layout.addWidget(self.scroll_plugins)
        side_layout.addWidget(self.global_settings_btn)

        # ----- Правая панель (стек) -----
        self.content_stack = QStackedWidget()

        
        self.global_settings_widget = GlobalSettingsWidget()
        self.content_stack.addWidget(self.global_settings_widget)

        self.h_splitter.addWidget(self.side_panel)
        self.h_splitter.addWidget(self.content_stack)
        self.h_splitter.setSizes([200, 700])

    def load_plugins(self):
        """Загружает плагины и добавляет их кнопки в боковую панель, а виджеты — в стек."""
        plugins = self.plugin_manager.get_plugins()
        if not plugins:
            label = QLabel("Нет загруженных плагинов")
            label.setAlignment(Qt.AlignCenter)
            self.plugins_layout.addWidget(label)
            return

        for plugin in plugins:
            # Кнопка плагина
            btn = QPushButton(plugin.icon(), plugin.name())
            btn.setIconSize(plugin.icon().actualSize(QSize(32, 32)))
            btn.setCheckable(True)
            btn.setToolTip(plugin.name())
            btn.clicked.connect(lambda checked, p=plugin: self.switch_to_plugin(p))
            self.plugins_layout.addWidget(btn)

            # Виджет содержимого плагина добавляем в стек
            self.content_stack.addWidget(plugin.plugin_content())

        self.global_settings_btn.setChecked(True)
        self.content_stack.setCurrentWidget(self.global_settings_widget)

        # Сбрасываем состояние кнопок плагинов
        for i in range(self.plugins_layout.count()):
            btn = self.plugins_layout.itemAt(i).widget()
            if isinstance(btn, QPushButton):
                btn.setChecked(False)

    def switch_to_plugin(self, plugin: PluginBase):
        """Переключает правую панель на виджет выбранного плагина."""
        self.current_plugin = plugin
        # Снимаем выделение с кнопки общих настроек
        self.global_settings_btn.setChecked(False)

        # Показываем виджет плагина в стеке
        widget = plugin.plugin_content()
        index = self.content_stack.indexOf(widget)
        if index >= 0:
            self.content_stack.setCurrentWidget(widget)
        else:
            # На случай, если виджет ещё не добавлен (хотя мы добавили в load_plugins)
            self.content_stack.addWidget(widget)
            self.content_stack.setCurrentWidget(widget)

        # Обновляем состояние кнопок плагинов
        for i in range(self.plugins_layout.count()):
            btn = self.plugins_layout.itemAt(i).widget()
            if isinstance(btn, QPushButton):
                btn.setChecked(btn.text() == plugin.name())

    def show_global_settings(self):
        """Показывает виджет общих настроек в правой панели."""
        self.current_plugin = None
        self.content_stack.setCurrentWidget(self.global_settings_widget)

        # Снимаем выделение со всех кнопок плагинов
        for i in range(self.plugins_layout.count()):
            btn = self.plugins_layout.itemAt(i).widget()
            if isinstance(btn, QPushButton):
                btn.setChecked(False)

        # Убеждаемся, что кнопка общих настроек остаётся нажатой
        self.global_settings_btn.setChecked(True)


class GlobalSettingsWidget(QWidget):
    """Виджет общих настроек приложения (отображается в правой панели)"""
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)

        # Пример настройки: выбор папки с плагинами
        self.plugins_dir_label = QLabel("Папка с плагинами: src/plugins")
        layout.addWidget(self.plugins_dir_label)

        change_dir_btn = QPushButton("Изменить папку плагинов")
        change_dir_btn.clicked.connect(self.change_plugins_dir)
        layout.addWidget(change_dir_btn)

        layout.addStretch()

        # Здесь можно добавить другие глобальные настройки (тема, язык и т.д.)

    def change_plugins_dir(self):
        
        dir_path = QFileDialog.getExistingDirectory(self, "Выберите папку с плагинами")
        if dir_path:
            pass