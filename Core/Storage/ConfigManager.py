import json
from pathlib import Path
from typing import Any

from config import Config


class ConfigManager:
    """Создаёт, читает и изменяет локальные настройки приложения."""

    DEFAULT_SETTINGS = {
        "voice_enabled": True,
    }

    def __init__(self, config_path: str | Path = Config.SETTINGS_PATH):
        self.config_path = Path(config_path)
        self.create_if_not_exists()

    def create_if_not_exists(self) -> None:
        self.config_path.parent.mkdir(parents=True, exist_ok=True)

        if not self.config_path.exists():
            self._write(self.DEFAULT_SETTINGS.copy())
            return

        settings = self._read()
        missing_settings = {
            key: value
            for key, value in self.DEFAULT_SETTINGS.items()
            if key not in settings
        }

        if missing_settings:
            settings.update(missing_settings)
            self._write(settings)

    def get_setting(self, key: str, default: Any = None) -> Any:
        return self._read().get(key, default)

    def get_all_settings(self) -> dict[str, Any]:
        return self._read().copy()

    def add_setting(self, key: str, value: Any) -> bool:
        settings = self._read()
        if key in settings:
            return False

        settings[key] = value
        self._write(settings)
        return True

    def set_setting(self, key: str, value: Any) -> None:
        settings = self._read()
        settings[key] = value
        self._write(settings)

    def _read(self) -> dict[str, Any]:
        try:
            with self.config_path.open("r", encoding="utf-8") as config_file:
                settings = json.load(config_file)
        except json.JSONDecodeError as error:
            raise ValueError(
                f"Некорректный JSON в файле {self.config_path}"
            ) from error

        if not isinstance(settings, dict):
            raise ValueError("Корнем config.json должен быть JSON-объект")

        return settings

    def _write(self, settings: dict[str, Any]) -> None:
        temporary_path = self.config_path.with_suffix(".json.tmp")

        with temporary_path.open("w", encoding="utf-8") as config_file:
            json.dump(
                settings,
                config_file,
                ensure_ascii=False,
                indent=2,
            )
            config_file.write("\n")

        temporary_path.replace(self.config_path)
