from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CommandDefinition:
    """Проверенное описание команды, загруженное из YAML."""

    id: int
    slug: str
    voice_phrases: tuple[str, ...] = ()
    voice_patterns: tuple[str, ...] = ()
    action_group: str | None = None
    action_method: str | None = None
    requires_confirmation: bool = False
    confirmation_message: str = ""
