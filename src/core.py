import importlib.util
import sys
from pathlib import Path
from typing import Dict, List
from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QIcon

# Базовый класс плагина (должен быть определён до PluginManager)
class PluginBase(QWidget):
    def __init__(self, plugin_path: Path, name: str = "Unnamed", icon_path: str = "icons/plugin.png", parent = None):
        
        super().__init__(parent)
        self.plugin_path = plugin_path
        self._name = name
        self._icon = QIcon()
        if icon_path and Path(icon_path).exists():
            self._icon = QIcon(str(icon_path))
        
    def name(self) -> str:
        """Ru: Возвращает название плагина \n
        En: Returns the plugin name"""
        return self._name
    
    def icon(self) -> QIcon:
        """Ru: Возвращает иконку плагина \n
        En: Returns the plugin icon"""
        
        return self._icon
    
    def plugin_content(self) -> QWidget:
        """Ru: Возвращает содержимое плагина \n
        En: Returns the plugin widget"""
        return self
    
    def apply_theme(self):
        pass


class PluginManager:
    """Ru: Менеджер плагинов
       En: Plugin manager"""
    
    def __init__(self, plugins_dir: str = "plugins"):
        # Преобразуем строку в Path
        self.plugins_dir = Path(plugins_dir)
        self.plugins: Dict[str, PluginBase] = {}  # инициализируем словарь
    
    def discover_plugins(self):
        """
        Ru: Поиск и загрузка плагинов \n
        En: Search and load plugins
        """
        if not self.plugins_dir.exists():
            self.plugins_dir.mkdir(parents=True)
            return
        
        for plugin_folder in self.plugins_dir.iterdir():
            if not plugin_folder.is_dir():
                continue
            plugin_file = plugin_folder / "plugin.py"
            if not plugin_file.exists():
                continue
            
            try:
            # Загружаем модуль динамически
                spec = importlib.util.spec_from_file_location(
                    f"plugins.{plugin_folder.name}", plugin_file
                )
                module = importlib.util.module_from_spec(spec)
                sys.modules[spec.name] = module
                spec.loader.exec_module(module)
                
                # Ищем класс, унаследованный от PluginBase
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if (isinstance(attr, type) and 
                        issubclass(attr, PluginBase) and 
                        attr is not PluginBase):
                        # Создаём экземпляр плагина
                        plugin_instance = attr(plugin_path=plugin_folder)
                        self.plugins[plugin_instance.name()] = plugin_instance
                        break  # предполагаем, что в plugin.py один класс-плагин
            except Exception as e:
                print(f"Failed to load plugin {plugin_folder.name}: {e}")
                continue
    
    def get_plugins(self) -> List[PluginBase]:
        """Ru: Возвращает список плагинов \n
        En: Returns a list of plugins"""
        return list(self.plugins.values())
    
    def get_plugin_by_name(self, name: str) -> PluginBase:
        """Ru: Возвращает плагин по имени \n
        En: Returns a plugin by name"""
        return self.plugins.get(name)