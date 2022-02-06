import logging
from logging import Handler, LogRecord
from types import FrameType
from typing import Any

from loguru import logger


class LogIntercept(Handler):
    """Handler to intercept logging messages and redirect to Loguru."""

    def emit(self: Any, record: LogRecord):
        """Log emitter."""

        level: str = record.levelno
        frame: FrameType = logging.currentframe()
        depth: int = 2

        try:
            level = logger.level(record.levelname).name
        except Exception:
            pass

        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )
