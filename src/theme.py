from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Optional

from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QApplication

from src.paths import bundled_themes_dir

_THEMES_DIR = bundled_themes_dir()

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
    theme_changed = Signal(str)

    def __init__(self, themes_dir: str | Path | None = None,
                 default_theme: str = "dark", parent=None):
        super().__init__(parent)

        self._themes_dir = Path(themes_dir) if themes_dir else _THEMES_DIR
        self._qss_template: str = ""
        self._themes: Dict[str, Dict[str, str]] = {}
        self._meta: Dict[str, dict] = {}
        self._current_name: str = default_theme
        self._current_tokens: Dict[str, str] = {}
        self._fallback_tokens: Dict[str, str] = {}

        self._load_template()
        self._discover_themes()

    # ------------------------------------------------------------------
    # Загрузка файлов
    # ------------------------------------------------------------------

    def _load_template(self) -> None:
        """Ищет base.qss сначала в user themes, затем в bundled."""
        qss_path = self._themes_dir / "base.qss"
        if not qss_path.exists():
            qss_path = bundled_themes_dir() / "base.qss"
        if not qss_path.exists():
            raise RuntimeError(
                f"QSS template not found in {self._themes_dir} or {bundled_themes_dir()}"
            )
        self._qss_template = qss_path.read_text(encoding="utf-8")

    def _discover_themes(self) -> None:
        """
        Двухслойная загрузка:
          1. bundled themes (базовый слой)
          2. user themes  (переопределяет/дополняет bundled)
        """
        # 1. Bundled themes
        bundled = bundled_themes_dir()
        if bundled.exists() and bundled.resolve() != self._themes_dir.resolve():
            self._load_theme_dir(bundled)

        # 2. User themes
        if self._themes_dir.exists():
            self._load_theme_dir(self._themes_dir)

        if not self._themes:
            raise RuntimeError(
                f"No themes found in bundled ({bundled}) or user ({self._themes_dir})"
            )

        if "dark" in self._themes:
            self._fallback_tokens = dict(self._themes["dark"])

        if self._current_name not in self._themes:
            self._current_name = next(iter(self._themes))

    def _load_theme_dir(self, dir_path: Path) -> None:
        """Загружает все *.json из указанной директории (кроме _префиксных)."""
        if not dir_path.exists():
            return

        for json_file in sorted(dir_path.glob("*.json")):
            if json_file.stem.startswith("_"):
                continue
            self._load_theme_file(json_file)

    def _load_theme_file(self, path: Path) -> None:
        try:
            with open(path, encoding="utf-8") as f:
                data: dict = json.load(f)

            meta: dict = data.get("_meta", {})
            tokens: dict = data.get("tokens", {})

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
        self._themes.clear()
        self._meta.clear()
        self._load_template()
        self._discover_themes()
        self.apply_theme(self._current_name, app)

    def register_theme(self, name: str, tokens: Dict[str, str],
                       meta: Optional[dict] = None) -> None:
        self._themes[name] = tokens
        self._meta[name] = meta or {"id": name, "display_name": name.capitalize()}

    def tokens(self) -> Dict[str, str]:
        return dict(self._current_tokens)

    def token(self, key: str, fallback: str = "") -> str:
        return self._current_tokens.get(key, fallback)

    def stylesheet_for_plugin(
            self, overrides: Optional[Dict[str, str]] = None) -> str:
        if not overrides:
            return ""

        tokens = dict(self._current_tokens)
        tokens.update(overrides)
        return self._qss_template.format(**tokens)

    def current_theme_name(self) -> str:
        return self._current_name

    def current_theme_meta(self) -> dict:
        return dict(self._meta.get(self._current_name, {}))

    def available_themes(self) -> list[str]:
        return list(self._themes.keys())

    def display_name(self, theme_id: str) -> str:
        return self._meta.get(theme_id, {}).get("display_name", theme_id.capitalize())

    # ------------------------------------------------------------------
    # Внутреннее
    # ------------------------------------------------------------------

    def _resolve_tokens(self, raw: Dict[str, str]) -> Dict[str, str]:
        result = dict(self._fallback_tokens)
        result.update(raw)
        return result


# ---------------------------------------------------------------------------
# Глобальный синглтон
# ---------------------------------------------------------------------------

_instance: Optional[ThemeManager] = None


def get_theme_manager(themes_dir: str | Path | None = None) -> ThemeManager:
    global _instance
    if _instance is None:
        _instance = ThemeManager(themes_dir=themes_dir)
    return _instance
