# HEXMANAGER

**Менеджер плагинов на PySide6 (Qt for Python)**

## Структура проекта

```
HEXManager/
├── main.py                     # Точка входа
├── requirements                # pyside6
├── src/
│   ├── core.py                 # PluginBase + PluginManager
│   ├── theme.py                # ThemeManager (QSS + JSON-токены)
│   └── gui/
│       ├── userinterface.py    # MainWindow + GlobalSettingsWidget
│       └── widgets.py          # WelcomeWidget
├── resources/
│   ├── plugins/                # Плагины
│   │   ├── AIChat/
│   │   ├── Browser/
│   │   └── Spotify/
│   ├── themes/                 # Темы
│   │   ├── base.qss
│   │   ├── dark.json
│   │   ├── light.json
│   │   └── mocha.json
│   └── icons/
└── HEXManager/data/
    └── config.json
```

## Быстрый старт

```bash
git clone https://github.com/TechnoWizardX/HEXManager
cd HEXManager
pip install -r requirements
python main.py
```

## Написание плагина

1. Скопируй любую папку из `resources/plugins/`
2. Отредактируй `plugin.json`:
```json
{
  "id": "my_plugin",
  "name": "MyPlugin",
  "display_name": "Мой плагин",
  "entry_point": "plugin.py",
  "version": "1.0.0",
  "author": "Ты",
  "icon": "icons/plugin.png",
  "theme_overrides": {}
}
```
3. В `plugin.py` создай наследник `PluginBase`:
```python
from src.core import PluginBase
from pathlib import Path
from PySide6.QtWidgets import QLabel, QVBoxLayout

class MyPlugin(PluginBase):
    def __init__(self, plugin_path: Path):
        super().__init__(plugin_path, name="Мой плагин")
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Привет!"))
```

### Поля plugin.json

| Поле | Описание |
|------|----------|
| `id` | Уникальный идентификатор (обязательно) |
| `name` | Имя (обязательно) |
| `display_name` | Отображаемое имя |
| `entry_point` | Точка входа (обычно `plugin.py`) |
| `icon` | Путь к иконке относительно папки плагина |
| `theme_overrides` | Переопределение цветов темы |

## Темы

Находятся в `resources/themes/`. Каждая тема — JSON с токенами:

```json
{
  "_meta": { "id": "mytheme", "display_name": "Моя тема" },
  "tokens": {
    "bg_window": "#...",
    "accent": "#..."
  }
}
```

QSS-шаблон: `resources/themes/base.qss`. Токены подставляются через `{имя}`.
