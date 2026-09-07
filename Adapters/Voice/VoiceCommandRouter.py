from dataclasses import dataclass
from enum import Enum
from typing import Callable


class VoiceRouteType(Enum):
    IGNORED = "ignored"
    ACTIVATED = "activated"
    COMMAND = "command"


@dataclass(frozen=True, slots=True)
class VoiceRouteResult:
    route_type: VoiceRouteType
    command_text: str = ""


class VoiceCommandRouter:
    """Определяет, относится ли распознанная фраза к ассистенту."""

    def __init__(self, assistant_name_provider: Callable[[], str]):
        self._assistant_name_provider = assistant_name_provider
        self._is_listening_for_command = False

    def route(self, raw_text: str) -> VoiceRouteResult:
        text = self._normalize(raw_text)
        if not text:
            return VoiceRouteResult(VoiceRouteType.IGNORED)

        if self._is_listening_for_command:
            return VoiceRouteResult(VoiceRouteType.COMMAND, text)

        assistant_name = self._normalize(self._assistant_name_provider())
        if not assistant_name:
            return VoiceRouteResult(VoiceRouteType.IGNORED)

        if text == assistant_name:
            self._is_listening_for_command = True
            return VoiceRouteResult(VoiceRouteType.ACTIVATED)

        prefix = f"{assistant_name} "
        if text.startswith(prefix):
            self._is_listening_for_command = True
            return VoiceRouteResult(VoiceRouteType.COMMAND, text[len(prefix):].strip())

        return VoiceRouteResult(VoiceRouteType.IGNORED)

    def complete_session(self, keep_active: bool = False) -> None:
        """Завершает командную сессию либо оставляет её активной."""
        self._is_listening_for_command = keep_active

    @staticmethod
    def _normalize(text: str) -> str:
        return " ".join(text.lower().strip().split())
