import json
import logging
import queue

import sounddevice as sd
from vosk import KaldiRecognizer, Model

from config import Config
from App.RunTime import RunTime

logger = logging.getLogger(__name__)


class VoiceListener:
    """Получает звук с микрофона и возвращает распознанный Vosk текст."""

    def __init__(self, runtime: RunTime | None = None):
        if not Config.MODEL_PATH.is_dir():
            raise FileNotFoundError(
                f"Папка модели не найдена: {Config.MODEL_PATH}"
            )

        self._audio_queue = queue.Queue()
        self._runtime = runtime or RunTime()
        self._stream = None

        logger.info("Загружаю модель распознавания")
        self._model = Model(str(Config.MODEL_PATH))
        self._recognizer = KaldiRecognizer(
            self._model,
            Config.SAMPLE_RATE,
        )
        logger.info("Модель распознавания готова")

    def _audio_callback(self, indata, frames, time, status) -> None:
        if status:
            logger.warning("Состояние микрофона: %s", status)

        if self._runtime.microphone_enabled.is_set():
            self._audio_queue.put(bytes(indata))

    def get_recognized_text(self) -> str:
        """Слушает микрофон до появления завершённой распознанной фразы."""
        while True:
            self._runtime.microphone_enabled.wait()
            self._clear_audio_queue()
            self._start_stream()

            while self._runtime.microphone_enabled.is_set():
                try:
                    audio_data = self._audio_queue.get(timeout=0.1)
                except queue.Empty:
                    continue

                if self._recognizer.AcceptWaveform(audio_data):
                    result = json.loads(self._recognizer.Result())
                    return result.get("text", "").strip()

            self._stop_stream()
            self._recognizer.Reset()

    def _start_stream(self) -> None:
        if self._stream is not None:
            if self._stream.active:
                return

            self._stream.close()
            self._stream = None

        self._stream = sd.RawInputStream(
            samplerate=Config.SAMPLE_RATE,
            blocksize=8000,
            dtype="int16",
            channels=1,
            callback=self._audio_callback,
        )
        self._stream.start()

    def _stop_stream(self) -> None:
        if self._stream is None:
            return

        try:
            if self._stream.active:
                self._stream.stop()
            self._stream.close()
        except Exception as error:
            logger.warning("Ошибка при закрытии аудиопотока: %s", error)
        finally:
            self._stream = None

    def _clear_audio_queue(self) -> None:
        while True:
            try:
                self._audio_queue.get_nowait()
            except queue.Empty:
                return

    def close(self) -> None:
        self._stop_stream()

    def recover(self) -> None:
        """Reset audio resources after a recoverable listening error."""
        self._stop_stream()
        self._clear_audio_queue()
        self._recognizer.Reset()
