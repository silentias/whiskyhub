from dataclasses import dataclass, field
from typing import Any
from uuid import uuid4


@dataclass(frozen=True, slots=True)
class CommandRequest:
    """Единый запрос команды, не зависящий от способа её получения."""

    slug: str
    arguments: dict[str, Any] = field(default_factory=dict)
    should_respond_with_voice: bool = False
    source: str = "voice"
    raw_text: str = ""
    request_id: str = field(default_factory=lambda: str(uuid4()))
