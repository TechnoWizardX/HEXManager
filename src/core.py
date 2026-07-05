import importlib.util
import sys
from pathlib import Path
from typing import Dict, List, Optional, TYPE_CHECKING
from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QIcon

if TYPE_CHECKING:
    from src.theme import ThemeManager


class PluginBase(QWidget):
    def __init__(self, plugin_path: Path, name: str = "Unnamed",
                 icon_path: str = "icons/plugin.png", parent=None):
        super().__init__(parent)
        self.plugin_path = plugin_path
        self._name = name
        self._icon = QIcon()
        if icon_path and Path(icon_path).exists():
            self._icon = QIcon(str(icon_path))
        self._manifest: dict = {}
        self._id: str = ""

    # ------------------------------------------------------------------
    # Идентификация
    # ------------------------------------------------------------------

    def id(self) -> str:
        return self._id

    def manifest(self) -> dict:
        return self._manifest or {}

    def name(self) -> str:
        return self._name

    def icon(self) -> QIcon:
        return self._icon

    def plugin_content(self) -> QWidget:
        return self

    # ------------------------------------------------------------------
    # Темизация
    # ------------------------------------------------------------------

    def apply_theme(self, theme_manager: "ThemeManager") -> None:
        overrides = self._manifest.get("theme_overrides", {})
        qss = theme_manager.stylesheet_for_plugin(overrides)
        if qss:
            self.setStyleSheet(qss)
        else:
            self.setStyleSheet("")


class PluginManager:
    def __init__(self, plugins_dir: str | Path = "plugins",
                 bundled_dir: Optional[str | Path] = None):
        self.plugins_dir = Path(plugins_dir)
        self.bundled_dir = Path(bundled_dir) if bundled_dir else None
        self.plugins: Dict[str, PluginBase] = {}
        self.plugins_by_name: Dict[str, PluginBase] = {}

    def discover_plugins(self) -> None:
        """Двухслойная загрузка: bundled → user (user переопределяет bundled по id)."""
        if self.bundled_dir and self.bundled_dir.exists():
            self._discover_in_dir(self.bundled_dir)

        if self.plugins_dir.exists():
            self._discover_in_dir(self.plugins_dir)

    def _discover_in_dir(self, dir_path: Path) -> None:
        if not dir_path.exists():
            return

        for plugin_folder in dir_path.iterdir():
            if not plugin_folder.is_dir():
                continue

            manifest_file = plugin_folder / "plugin.json"
            if not manifest_file.exists():
                self._load_legacy_plugin(plugin_folder)
                continue

            try:
                import json
                with open(manifest_file, "r", encoding="utf-8") as f:
                    manifest: dict = json.load(f)

                if "id" not in manifest or "name" not in manifest:
                    print(f"Plugin {plugin_folder.name}: missing 'id' or 'name' in plugin.json")
                    continue

                entry_point = manifest.get("entry_point", "plugin.py")
                plugin_file = plugin_folder / entry_point
                if not plugin_file.exists():
                    print(f"Plugin {manifest['id']}: entry point {entry_point} not found")
                    continue

                spec = importlib.util.spec_from_file_location(
                    f"plugins.{manifest['id']}", plugin_file
                )
                module = importlib.util.module_from_spec(spec)
                sys.modules[spec.name] = module
                spec.loader.exec_module(module)

                plugin_class = None
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if (isinstance(attr, type)
                            and issubclass(attr, PluginBase)
                            and attr is not PluginBase):
                        plugin_class = attr
                        break

                if not plugin_class:
                    print(f"Plugin {manifest['id']}: no class inheriting PluginBase found")
                    continue

                plugin_instance: PluginBase = plugin_class(plugin_path=plugin_folder)
                plugin_instance._manifest = manifest
                plugin_instance._id = manifest["id"]
                plugin_instance._name = manifest.get("display_name", manifest["name"])

                icon_rel = manifest.get("icon", "")
                if icon_rel:
                    icon_abs = plugin_folder / icon_rel
                    if icon_abs.exists():
                        plugin_instance._icon = QIcon(str(icon_abs))

                self.plugins[manifest["id"]] = plugin_instance
                self.plugins_by_name[plugin_instance.name()] = plugin_instance

            except Exception as e:
                print(f"Failed to load plugin {plugin_folder.name}: {e}")

    def _load_legacy_plugin(self, plugin_folder: Path) -> None:
        plugin_file = plugin_folder / "plugin.py"
        if not plugin_file.exists():
            return
        try:
            spec = importlib.util.spec_from_file_location(
                f"plugins.{plugin_folder.name}", plugin_file
            )
            module = importlib.util.module_from_spec(spec)
            sys.modules[spec.name] = module
            spec.loader.exec_module(module)

            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (isinstance(attr, type)
                        and issubclass(attr, PluginBase)
                        and attr is not PluginBase):
                    plugin_instance: PluginBase = attr(plugin_path=plugin_folder)
                    plugin_instance._id = plugin_folder.name
                    self.plugins[plugin_instance._id] = plugin_instance
                    self.plugins_by_name[plugin_instance.name()] = plugin_instance
                    break
        except Exception as e:
            print(f"Failed to load legacy plugin {plugin_folder.name}: {e}")

    def get_plugins(self) -> List[PluginBase]:
        return list(self.plugins.values())
