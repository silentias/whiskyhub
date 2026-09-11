import logging
from logging.handlers import RotatingFileHandler

from config import Config


def configure_logging() -> None:
    """Configure one application-wide rotating file logger."""
    root_logger = logging.getLogger()
    if getattr(root_logger, "_whiskyhub_configured", False):
        return

    Config.LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    handler = RotatingFileHandler(
        Config.LOG_PATH,
        maxBytes=2 * 1024 * 1024,
        backupCount=3,
        encoding="utf-8",
    )
    handler.setFormatter(logging.Formatter(
        "%(asctime)s %(levelname)s %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    ))
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(handler)
    logging.getLogger("werkzeug").setLevel(logging.WARNING)
    root_logger._whiskyhub_configured = True
