from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class CommandResult:
    """Единый результат обработки команды для любого входного адаптера."""

    success: bool
    status: str
    message: str = ""
    data: dict[str, Any] | None = None
    keep_session_active: bool = False
