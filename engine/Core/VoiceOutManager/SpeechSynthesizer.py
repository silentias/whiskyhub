import logging
import numpy as np
import sounddevice as sd
from piper import PiperVoice

from config import Config

logger = logging.getLogger(__name__)


class SpeechSynthesizer:
    def __init__(self, model_path):
        logger.info("Загружаю голосовую модель")
        self.voice = PiperVoice.load(str(model_path))
        logger.info("Голосовая модель готова")

    def speak(self, text: str):
        if not text.strip():
            return

        chunks = list(self.voice.synthesize(text))

        if not chunks:
            return

        audio_bytes = b"".join(
            chunk.audio_int16_bytes
            for chunk in chunks
        )

        audio = np.frombuffer(audio_bytes, dtype=np.int16)
        sample_rate = chunks[0].sample_rate

        sd.play(audio, samplerate=sample_rate)
        sd.wait()

speech_synthesizer = SpeechSynthesizer(model_path=Config.PIPER_MODEL_PATH)
