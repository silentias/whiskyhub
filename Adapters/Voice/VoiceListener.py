import json
import queue

import sounddevice as sd
from vosk import KaldiRecognizer, Model

from config import Config


class VoiceListener:
    """Получает звук с микрофона и возвращает распознанный Vosk текст."""

    def __init__(self):
        if not Config.MODEL_PATH.is_dir():
            raise FileNotFoundError(
                f"Папка модели не найдена: {Config.MODEL_PATH}"
            )

        self._audio_queue = queue.Queue()

        print("[LISTENER] Загружаю модель...")
        self._model = Model(str(Config.MODEL_PATH))
        self._recognizer = KaldiRecognizer(
            self._model,
            Config.SAMPLE_RATE,
        )
        print("[LISTENER] Модель готова")

    def _audio_callback(self, indata, frames, time, status) -> None:
        if status:
            print(f"[LISTENER][WARNING] Состояние микрофона: {status}")

        self._audio_queue.put(bytes(indata))

    def get_recognized_text(self) -> str:
        """Слушает микрофон до появления завершённой распознанной фразы."""
        with sd.RawInputStream(
            samplerate=Config.SAMPLE_RATE,
            blocksize=8000,
            dtype="int16",
            channels=1,
            callback=self._audio_callback,
        ):
            while True:
                audio_data = self._audio_queue.get()
                if self._recognizer.AcceptWaveform(audio_data):
                    result = json.loads(self._recognizer.Result())
                    return result.get("text", "").strip()
