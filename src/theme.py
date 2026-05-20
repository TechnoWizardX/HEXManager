# src/theme.py
from __future__ import annotations
from typing import Dict, Any, Callable, Optional
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QObject, Signal


# ---------------------------------------------------------------------------
# Токены темы  (все значения — строки, совместимые с QSS)
# ---------------------------------------------------------------------------

THEME_DARK: Dict[str, str] = {
    # фоны
    "bg_window":        "#1a1b1e",
    "bg_panel":         "#25262b",
    "bg_widget":        "#2c2e33",
    "bg_hover":         "#373a40",
    "bg_pressed":       "#1e1f22",

    # акцент
    "accent":           "#4dabf7",
    "accent_hover":     "#74c0fc",
    "accent_pressed":   "#339af0",
    "accent_text":      "#ffffff",

    # текст
    "text_primary":     "#e9ecef",
    "text_secondary":   "#868e96",
    "text_disabled":    "#495057",

    # рамки
    "border":           "#373a40",
    "border_focus":     "#4dabf7",

    # прокрутка
    "scrollbar_bg":     "#25262b",
    "scrollbar_handle": "#373a40",

    # радиусы и отступы (можно менять per-тема)
    "radius_sm":        "4px",
    "radius_md":        "6px",
    "radius_lg":        "10px",
    "spacing_sm":       "4px",
    "spacing_md":       "8px",
}

THEME_LIGHT: Dict[str, str] = {
    "bg_window":        "#f8f9fa",
    "bg_panel":         "#ffffff",
    "bg_widget":        "#f1f3f5",
    "bg_hover":         "#e9ecef",
    "bg_pressed":       "#dee2e6",

    "accent":           "#228be6",
    "accent_hover":     "#1c7ed6",
    "accent_pressed":   "#1971c2",
    "accent_text":      "#ffffff",

    "text_primary":     "#212529",
    "text_secondary":   "#868e96",
    "text_disabled":    "#adb5bd",

    "border":           "#dee2e6",
    "border_focus":     "#228be6",

    "scrollbar_bg":     "#f1f3f5",
    "scrollbar_handle": "#ced4da",

    "radius_sm":        "4px",
    "radius_md":        "6px",
    "radius_lg":        "10px",
    "spacing_sm":       "4px",
    "spacing_md":       "8px",
}

THEME_MOCHA: Dict[str, str] = {
    "bg_window":        "#1e1a18",
    "bg_panel":         "#2a2420",
    "bg_widget":        "#322b27",
    "bg_hover":         "#3d342e",
    "bg_pressed":       "#1a1614",

    "accent":           "#e8956d",
    "accent_hover":     "#f0aa87",
    "accent_pressed":   "#d4744a",
    "accent_text":      "#ffffff",

    "text_primary":     "#ede0d4",
    "text_secondary":   "#a08070",
    "text_disabled":    "#5a4a40",

    "border":           "#3d342e",
    "border_focus":     "#e8956d",

    "scrollbar_bg":     "#2a2420",
    "scrollbar_handle": "#3d342e",

    "radius_sm":        "4px",
    "radius_md":        "6px",
    "radius_lg":        "10px",
    "spacing_sm":       "4px",
    "spacing_md":       "8px",
}

BUILTIN_THEMES: Dict[str, Dict[str, str]] = {
    "dark":  THEME_DARK,
    "light": THEME_LIGHT,
    "mocha": THEME_MOCHA,
}


# ---------------------------------------------------------------------------
# QSS-шаблон  — использует токены через {token_name}
# ---------------------------------------------------------------------------

QSS_TEMPLATE = """
/* === Главное окно / фон === */
QMainWindow, QDialog {{
    background-color: {bg_window};
}}

QWidget {{
    background-color: transparent;
    color: {text_primary};
    font-size: 13px;
}}

/* === Панели === */
QFrame, QScrollArea {{
    background-color: {bg_panel};
    border: none;
}}

/* === Кнопки === */
QPushButton {{
    background-color: {bg_widget};
    color: {text_primary};
    border: 1px solid {border};
    border-radius: {radius_md};
    padding: {spacing_md} 14px;
    text-align: left;
}}
QPushButton:hover {{
    background-color: {bg_hover};
    border-color: {border_focus};
}}
QPushButton:pressed {{
    background-color: {bg_pressed};
}}
QPushButton:checked {{
    background-color: {accent};
    color: {accent_text};
    border-color: {accent};
}}
QPushButton:disabled {{
    color: {text_disabled};
    border-color: {border};
}}

/* === Метки === */
QLabel {{
    background-color: transparent;
    color: {text_primary};
}}

/* === Поля ввода === */
QLineEdit, QTextEdit, QPlainTextEdit {{
    background-color: {bg_widget};
    color: {text_primary};
    border: 1px solid {border};
    border-radius: {radius_md};
    padding: {spacing_sm} {spacing_md};
    selection-background-color: {accent};
    selection-color: {accent_text};
}}
QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
    border-color: {border_focus};
}}

/* === Комбобокс === */
QComboBox {{
    background-color: {bg_widget};
    color: {text_primary};
    border: 1px solid {border};
    border-radius: {radius_md};
    padding: {spacing_sm} {spacing_md};
}}
QComboBox:hover {{ border-color: {border_focus}; }}
QComboBox QAbstractItemView {{
    background-color: {bg_widget};
    color: {text_primary};
    border: 1px solid {border};
    selection-background-color: {accent};
    selection-color: {accent_text};
}}

/* === Чекбокс / Радио === */
QCheckBox, QRadioButton {{
    color: {text_primary};
    background-color: transparent;
    spacing: 6px;
}}
QCheckBox::indicator, QRadioButton::indicator {{
    width: 16px;
    height: 16px;
    border: 1px solid {border};
    border-radius: {radius_sm};
    background-color: {bg_widget};
}}
QCheckBox::indicator:checked, QRadioButton::indicator:checked {{
    background-color: {accent};
    border-color: {accent};
}}

/* === Скроллбар === */
QScrollBar:vertical {{
    background: {scrollbar_bg};
    width: 8px;
    border-radius: 4px;
}}
QScrollBar::handle:vertical {{
    background: {scrollbar_handle};
    border-radius: 4px;
    min-height: 24px;
}}
QScrollBar::handle:vertical:hover {{ background: {text_secondary}; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0px; }}

QScrollBar:horizontal {{
    background: {scrollbar_bg};
    height: 8px;
    border-radius: 4px;
}}
QScrollBar::handle:horizontal {{
    background: {scrollbar_handle};
    border-radius: 4px;
    min-width: 24px;
}}
QScrollBar::handle:horizontal:hover {{ background: {text_secondary}; }}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ width: 0px; }}

/* === Сплиттер === */
QSplitter::handle {{
    background-color: {border};
}}
QSplitter::handle:horizontal {{ width: 1px; }}
QSplitter::handle:vertical  {{ height: 1px; }}

/* === Стэк / контентная область === */
QStackedWidget {{
    background-color: {bg_window};
}}

/* === Тулбар / статусбар === */
QStatusBar {{
    background-color: {bg_panel};
    color: {text_secondary};
}}

/* === Таблицы === */
QTableWidget, QTableView {{
    background-color: {bg_widget};
    color: {text_primary};
    gridline-color: {border};
    border: 1px solid {border};
    border-radius: {radius_md};
}}
QHeaderView::section {{
    background-color: {bg_panel};
    color: {text_secondary};
    border: none;
    border-bottom: 1px solid {border};
    padding: {spacing_sm} {spacing_md};
}}
QTableWidget::item:selected, QTableView::item:selected {{
    background-color: {accent};
    color: {accent_text};
}}

/* === Список === */
QListWidget, QListView {{
    background-color: {bg_widget};
    color: {text_primary};
    border: 1px solid {border};
    border-radius: {radius_md};
}}
QListWidget::item:hover, QListView::item:hover {{
    background-color: {bg_hover};
}}
QListWidget::item:selected, QListView::item:selected {{
    background-color: {accent};
    color: {accent_text};
}}

/* === TabWidget === */
QTabWidget::pane {{
    border: 1px solid {border};
    border-radius: {radius_md};
    background-color: {bg_widget};
}}
QTabBar::tab {{
    background-color: {bg_panel};
    color: {text_secondary};
    border: 1px solid {border};
    border-bottom: none;
    border-radius: {radius_sm};
    padding: {spacing_sm} 16px;
    margin-right: 2px;
}}
QTabBar::tab:selected {{
    background-color: {bg_widget};
    color: {text_primary};
    border-bottom: 2px solid {accent};
}}
QTabBar::tab:hover:!selected {{
    background-color: {bg_hover};
}}

/* === GroupBox === */
QGroupBox {{
    border: 1px solid {border};
    border-radius: {radius_md};
    margin-top: 12px;
    color: {text_secondary};
    font-size: 12px;
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 4px;
}}

/* === Прогресс-бар === */
QProgressBar {{
    background-color: {bg_widget};
    border: 1px solid {border};
    border-radius: {radius_sm};
    text-align: center;
    color: {text_primary};
    height: 8px;
}}
QProgressBar::chunk {{
    background-color: {accent};
    border-radius: {radius_sm};
}}

/* === Слайдер === */
QSlider::groove:horizontal {{
    background: {bg_widget};
    height: 4px;
    border-radius: 2px;
}}
QSlider::handle:horizontal {{
    background: {accent};
    width: 14px;
    height: 14px;
    margin: -5px 0;
    border-radius: 7px;
}}
QSlider::sub-page:horizontal {{
    background: {accent};
    border-radius: 2px;
}}

/* === Спинбокс === */
QSpinBox, QDoubleSpinBox {{
    background-color: {bg_widget};
    color: {text_primary};
    border: 1px solid {border};
    border-radius: {radius_md};
    padding: {spacing_sm} {spacing_md};
}}
QSpinBox:focus, QDoubleSpinBox:focus {{
    border-color: {border_focus};
}}

/* === Тултип === */
QToolTip {{
    background-color: {bg_widget};
    color: {text_primary};
    border: 1px solid {border};
    border-radius: {radius_sm};
    padding: {spacing_sm} {spacing_md};
}}
"""


# ---------------------------------------------------------------------------
# ThemeManager
# ---------------------------------------------------------------------------

class ThemeManager(QObject):
    """
    Централизованный менеджер тем.

    Использование:
        tm = ThemeManager()
        tm.register_theme("custom", {...токены...})   # опционально
        tm.apply_theme("dark")                        # применяет на QApplication

    Плагины могут переопределять отдельные токены через plugin.json:
        "theme_overrides": { "accent": "#ff6b6b", "radius_md": "12px" }

    При этом переопределения применяются только к виджету плагина
    через метод theme_stylesheet_for_plugin().
    """

    theme_changed = Signal(str)   # имя новой темы

    def __init__(self, default_theme: str = "dark", parent=None):
        super().__init__(parent)
        self._themes: Dict[str, Dict[str, str]] = dict(BUILTIN_THEMES)
        self._current_name: str = default_theme
        self._current_tokens: Dict[str, str] = {}
        self._plugin_callbacks: list[Callable[[str], None]] = []

    # ------------------------------------------------------------------
    # Регистрация кастомных тем
    # ------------------------------------------------------------------

    def register_theme(self, name: str, tokens: Dict[str, str]) -> None:
        """
        Регистрирует новую тему или перезаписывает существующую.
        tokens — полный или частичный словарь токенов.
        Отсутствующие токены берутся из THEME_DARK как fallback.
        """
        merged = dict(THEME_DARK)
        merged.update(tokens)
        self._themes[name] = merged

    # ------------------------------------------------------------------
    # Применение темы
    # ------------------------------------------------------------------

    def apply_theme(self, name: str, app: Optional[QApplication] = None) -> None:
        """Применяет тему к QApplication (или текущему инстансу если app=None)."""
        if name not in self._themes:
            raise ValueError(f"Theme '{name}' is not registered. Available: {list(self._themes)}")

        self._current_name = name
        self._current_tokens = dict(self._themes[name])

        qss = QSS_TEMPLATE.format(**self._current_tokens)

        target = app or QApplication.instance()
        if target:
            target.setStyleSheet(qss)

        self.theme_changed.emit(name)

    # ------------------------------------------------------------------
    # Токены для плагинов
    # ------------------------------------------------------------------

    def tokens(self) -> Dict[str, str]:
        """Возвращает копию токенов текущей темы."""
        return dict(self._current_tokens)

    def token(self, key: str, fallback: str = "") -> str:
        return self._current_tokens.get(key, fallback)

    def stylesheet_for_plugin(self, overrides: Optional[Dict[str, str]] = None) -> str:
        """
        Генерирует QSS для отдельного виджета плагина с применёнными
        переопределениями.  overrides берутся из manifest["theme_overrides"].

        Применять:  plugin_widget.setStyleSheet(tm.stylesheet_for_plugin(overrides))
        """
        if not overrides:
            return ""   # плагин наследует стиль приложения — ничего не нужно

        tokens = dict(self._current_tokens)
        tokens.update(overrides)
        return QSS_TEMPLATE.format(**tokens)

    # ------------------------------------------------------------------
    # Вспомогательное
    # ------------------------------------------------------------------

    def current_theme_name(self) -> str:
        return self._current_name

    def available_themes(self) -> list[str]:
        return list(self._themes.keys())


# ---------------------------------------------------------------------------
# Глобальный синглтон (удобно импортировать везде)
# ---------------------------------------------------------------------------

_instance: Optional[ThemeManager] = None

def get_theme_manager() -> ThemeManager:
    global _instance
    if _instance is None:
        _instance = ThemeManager()
    return _instance