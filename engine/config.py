import sys
from pathlib import Path


def _documents_directory() -> Path:
    """Return the current user's Documents directory."""
    if sys.platform == "win32":
        try:
            import os
            import winreg

            key_path = r"Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders"
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path) as key:
                value, _ = winreg.QueryValueEx(key, "Personal")
            return Path(os.path.expandvars(value))
        except (OSError, TypeError):
            pass

    return Path.home() / "Documents"


ENGINE_ROOT = Path(getattr(sys, "_MEIPASS", Path(__file__).parent))
USER_DATA_ROOT = _documents_directory() / "WhiskyHub"

class Config:
    DEFAULT_ASSISTANT_NAME = "Виски"

    SETTINGS_PATH = (
        USER_DATA_ROOT
        / "config.json"
    )

    SETTINGS_TEMPLATE_PATH = (
        ENGINE_ROOT
        / "Core"
        / "Storage"
        / "Data"
        / "config.json"
    )

    DATABASE_PATH = (
        USER_DATA_ROOT
        / "assistant.db"
    )
    MODEL_PATH = (
        ENGINE_ROOT
        / "models"
        / "vosk-model-small-ru-0.22"
        / "vosk-model-small-ru-0.22"
    )
    PIPER_MODEL_PATH = (
        ENGINE_ROOT
        / "models"
        / "piper-tts"
        / "ru_RU-irina-medium.onnx"
    )
    COMMANDS_PATH = USER_DATA_ROOT / "commands.yaml"
    COMMANDS_TEMPLATE_PATH = ENGINE_ROOT / "Dispatcher" / "Data" / "commands.yaml"
    SAMPLE_RATE = 16000
