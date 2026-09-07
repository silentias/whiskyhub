from pathlib import Path

class Config:
    DEFAULT_ASSISTANT_NAME = "Робот"

    SETTINGS_PATH = (
        Path(__file__).parent
        / "Core"
        / "Storage"
        / "Data"
        / "config.json"
    )

    DATABASE_PATH = (
        Path(__file__).parent
        / "Core"
        / "Storage"
        / "Data"
        / "assistant.db"
    )
    MODEL_PATH = (
        Path(__file__).parent
        / "models"
        / "vosk-model-small-ru-0.22"
        / "vosk-model-small-ru-0.22"
    )
    PIPER_MODEL_PATH = (
        Path(__file__).parent
        / "models"
        / "piper-tts"
        / "ru_RU-irina-medium.onnx"
    )
    SAMPLE_RATE = 16000
