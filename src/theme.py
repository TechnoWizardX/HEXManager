# src/theme.py
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Optional

from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QApplication

# Папка с темами относительно этого файла: src/themes/
_THEMES_DIR = Path(__file__).parent / "themes"

# Все обязательные токены — используются как fallback
_REQUIRED_TOKENS = {
    "bg_window", "bg_panel", "bg_widget", "bg_hover", "bg_pressed",
    "accent", "accent_hover", "accent_pressed", "accent_text",
    "text_primary", "text_secondary", "text_disabled",
    "border", "border_focus",
    "scrollbar_bg", "scrollbar_handle",
    "radius_sm", "radius_md", "radius_lg",
    "spacing_sm", "spacing_md",
}


class ThemeManager(QObject):
    """
    Централизованный менеджер тем.

    При инициализации автоматически читает все *.json из src/themes/
    и загружает base.qss как шаблон.

    Порядок приоритетов токенов (от низкого к высокому):
        1. Встроенный fallback (нули/пустые строки)
        2. Токены из dark.json (используются как глобальный fallback)
        3. Токены из выбранной темы
        4. theme_overrides из plugin.json (только для конкретного плагина)
    """

    theme_changed = Signal(str)  # передаёт id новой темы

    def __init__(self, themes_dir: str | Path | None = None,
                 default_theme: str = "dark", parent=None):
        super().__init__(parent)

        self._themes_dir = Path(themes_dir) if themes_dir else _THEMES_DIR
        self._qss_template: str = ""
        self._themes: Dict[str, Dict[str, str]] = {}
        self._meta: Dict[str, dict] = {}           # id -> _meta блок из json
        self._current_name: str = default_theme
        self._current_tokens: Dict[str, str] = {}
        self._fallback_tokens: Dict[str, str] = {} # токены dark.json

        self._load_template()
        self._discover_themes()

    # ------------------------------------------------------------------
    # Загрузка файлов
    # ------------------------------------------------------------------

    def _load_template(self) -> None:
        """Читает base.qss. Если файл не найден — кидает RuntimeError."""
        qss_path = self._themes_dir / "base.qss"
        if not qss_path.exists():
            raise RuntimeError(
                f"QSS template not found: {qss_path}\n"
                f"Expected location: src/themes/base.qss"
            )
        self._qss_template = qss_path.read_text(encoding="utf-8")

    def _discover_themes(self) -> None:
        """
        Сканирует themes_dir в поисках *.json (кроме файлов начинающихся с _).
        Каждый файл должен иметь структуру:
            { "_meta": { "id": "...", "display_name": "..." }, "tokens": { ... } }
        """
        if not self._themes_dir.exists():
            raise RuntimeError(f"Themes directory not found: {self._themes_dir}")

        for json_file in sorted(self._themes_dir.glob("*.json")):
            if json_file.stem.startswith("_"):
                continue
            self._load_theme_file(json_file)

        if not self._themes:
            raise RuntimeError(f"No themes found in {self._themes_dir}")

        # dark.json становится глобальным fallback'ом для неполных тем
        if "dark" in self._themes:
            self._fallback_tokens = dict(self._themes["dark"])

        # Если запрошенная тема по умолчанию отсутствует — берём первую
        if self._current_name not in self._themes:
            self._current_name = next(iter(self._themes))

    def _load_theme_file(self, path: Path) -> None:
        """Парсит один JSON-файл темы и регистрирует её."""
        try:
            with open(path, encoding="utf-8") as f:
                data: dict = json.load(f)

            meta: dict = data.get("_meta", {})
            tokens: dict = data.get("tokens", {})

            # id берём из _meta, либо из имени файла
            theme_id: str = meta.get("id", path.stem)

            if not tokens:
                print(f"[ThemeManager] Warning: {path.name} has no 'tokens' block, skipped")
                return

            self._themes[theme_id] = tokens
            self._meta[theme_id] = meta

        except (json.JSONDecodeError, OSError) as e:
            print(f"[ThemeManager] Failed to load {path.name}: {e}")

    # ------------------------------------------------------------------
    # Публичный API
    # ------------------------------------------------------------------

    def apply_theme(self, name: str, app: Optional[QApplication] = None) -> None:
        """Применяет тему к QApplication (или текущему инстансу если app=None)."""
        if name not in self._themes:
            raise ValueError(
                f"Theme '{name}' not found. Available: {self.available_themes()}"
            )

        self._current_name = name
        self._current_tokens = self._resolve_tokens(self._themes[name])

        qss = self._qss_template.format(**self._current_tokens)
        target = app or QApplication.instance()
        if target:
            target.setStyleSheet(qss)

        self.theme_changed.emit(name)

    def reload(self, app: Optional[QApplication] = None) -> None:
        """Перечитывает все файлы с диска и повторно применяет текущую тему.
        Удобно при разработке новой темы — не нужно перезапускать приложение."""
        self._themes.clear()
        self._meta.clear()
        self._load_template()
        self._discover_themes()
        self.apply_theme(self._current_name, app)

    def register_theme(self, name: str, tokens: Dict[str, str],
                       meta: Optional[dict] = None) -> None:
        """Регистрирует тему программно (без JSON-файла).
        Отсутствующие токены берутся из dark.json как fallback."""
        self._themes[name] = tokens
        self._meta[name] = meta or {"id": name, "display_name": name.capitalize()}

    def tokens(self) -> Dict[str, str]:
        """Возвращает копию токенов текущей темы (с применёнными fallback'ами)."""
        return dict(self._current_tokens)

    def token(self, key: str, fallback: str = "") -> str:
        """Возвращает значение одного токена текущей темы."""
        return self._current_tokens.get(key, fallback)

    def stylesheet_for_plugin(
            self, overrides: Optional[Dict[str, str]] = None) -> str:
        """
        Генерирует QSS для виджета плагина с его персональными overrides.
        Если overrides пустые — возвращает пустую строку (плагин
        наследует глобальный стиль приложения и не тратит память).

        overrides берутся из manifest["theme_overrides"] плагина.
        """
        if not overrides:
            return ""

        tokens = dict(self._current_tokens)
        tokens.update(overrides)
        return self._qss_template.format(**tokens)

    def current_theme_name(self) -> str:
        return self._current_name

    def current_theme_meta(self) -> dict:
        """Возвращает _meta блок текущей темы."""
        return dict(self._meta.get(self._current_name, {}))

    def available_themes(self) -> list[str]:
        """Возвращает список id всех загруженных тем."""
        return list(self._themes.keys())

    def display_name(self, theme_id: str) -> str:
        """Возвращает человекочитаемое имя темы из её _meta.display_name."""
        return self._meta.get(theme_id, {}).get("display_name", theme_id.capitalize())

    # ------------------------------------------------------------------
    # Внутреннее
    # ------------------------------------------------------------------

    def _resolve_tokens(self, raw: Dict[str, str]) -> Dict[str, str]:
        """Дополняет токены темы значениями из fallback (dark.json),
        чтобы неполные темы не ломали шаблон."""
        result = dict(self._fallback_tokens)  # начинаем с dark как базы
        result.update(raw)                    # тема перекрывает fallback
        return result


# ---------------------------------------------------------------------------
# Глобальный синглтон
# ---------------------------------------------------------------------------

_instance: Optional[ThemeManager] = None


def get_theme_manager(themes_dir: str | Path | None = None) -> ThemeManager:
    """Возвращает глобальный экземпляр ThemeManager.
    themes_dir учитывается только при первом вызове."""
    global _instance
    if _instance is None:
        _instance = ThemeManager(themes_dir=themes_dir)
    return _instance