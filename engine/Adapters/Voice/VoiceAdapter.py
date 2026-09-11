import logging
from typing import Callable

from Adapters.Voice.VoiceCommandParser import VoiceCommandParser
from Adapters.Voice.VoiceCommandRouter import VoiceCommandRouter, VoiceRouteType
from Contracts.CommandRequest import CommandRequest
from Adapters.Voice.VoiceListener import VoiceListener

logger = logging.getLogger(__name__)


class VoiceAdapter:
    """Получает речь и выдаёт унифицированные запросы команд."""

    def __init__(
        self,
        listener: VoiceListener,
        assistant_name_provider: Callable[[], str],
        respond_with_voice: bool,
        parser: VoiceCommandParser,
    ):
        self._listener = listener
        self._router = VoiceCommandRouter(assistant_name_provider)
        self._parser = parser
        self._respond_with_voice = respond_with_voice

    def get_command_request(self) -> CommandRequest:
        while True:
            raw_text = self._listener.get_recognized_text()
            if not raw_text:
                continue

            logger.info("Распознано: %s", raw_text)
            route = self._router.route(raw_text)

            if route.route_type is VoiceRouteType.IGNORED:
                continue

            if route.route_type is VoiceRouteType.ACTIVATED:
                logger.info("Помощник активирован. Слушаю команду")
                continue

            request = self._parser.parse(
                route.command_text,
                respond_with_voice=self._respond_with_voice,
            )
            logger.info("Команда преобразована в контракт: %s", request.slug)
            return request

    def complete_session(self, keep_active: bool = False) -> None:
        self._router.complete_session(keep_active)
