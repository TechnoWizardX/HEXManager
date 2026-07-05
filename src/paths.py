import sys
import os
import json
from pathlib import Path


def is_frozen() -> bool:
    return getattr(sys, 'frozen', False)


def _bundle_dir() -> Path:
    """Корень bundled-ресурсов: sys._MEIPASS (frozen) или корень проекта (dev)."""
    if is_frozen():
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parent.parent


def resources_dir() -> Path:
    """resources/ — содержит themes/, plugins/, icons/."""
    return _bundle_dir() / "resources"


def user_data_dir() -> Path:
    """%APPDATA%/HEXManager (Win) или ~/.local/share/HEXManager (Linux/Mac)."""
    if os.name == 'nt':
        base = Path(os.environ.get('APPDATA', Path.home() / 'AppData' / 'Roaming'))
    else:
        base = Path(os.environ.get('XDG_DATA_HOME', Path.home() / '.local' / 'share'))
    return base / "HEXManager"


def config_path() -> Path:
    return user_data_dir() / "config.json"


def user_plugins_dir() -> Path:
    return user_data_dir() / "plugins"


def user_themes_dir() -> Path:
    return user_data_dir() / "themes"


def user_icons_dir() -> Path:
    return user_data_dir() / "icons"


def bundled_themes_dir() -> Path:
    return resources_dir() / "themes"


def bundled_plugins_dir() -> Path:
    return resources_dir() / "plugins"


def bundled_icons_dir() -> Path:
    return resources_dir() / "icons"


def ensure_user_dirs() -> None:
    for d in [user_data_dir(), user_plugins_dir(), user_themes_dir(), user_icons_dir()]:
        d.mkdir(parents=True, exist_ok=True)


def load_config() -> dict:
    try:
        with open(config_path(), encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"theme": "dark"}


def save_config(data: dict) -> None:
    try:
        existing = load_config()
        existing.update(data)
        with open(config_path(), "w", encoding="utf-8") as f:
            json.dump(existing, f, indent=2)
    except OSError as e:
        print(f"Failed to save config: {e}")
