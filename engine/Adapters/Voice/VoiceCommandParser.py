from Contracts.CommandRequest import CommandRequest
from Dispatcher.CommandCatalog import CommandCatalog


class VoiceCommandParser:
    """Преобразует текст голосовой команды в общий контракт."""

    def __init__(self, command_catalog: CommandCatalog):
        self._command_catalog = command_catalog

    def parse(self, command_text: str, respond_with_voice: bool) -> CommandRequest:
        normalized_text = " ".join(command_text.lower().strip().split())
        match = self._command_catalog.match_voice_text(normalized_text)
        if match is None:
            slug = "unknown_command"
            arguments = {"text": normalized_text}
        else:
            command, arguments = match
            slug = command.slug

        return CommandRequest(
            slug=slug,
            arguments=arguments,
            should_respond_with_voice=respond_with_voice,
            source="voice",
            raw_text=normalized_text,
        )
