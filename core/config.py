import json
from typing import Any

from loguru import logger


class Config:
    """Class containing N31L configuration values."""

    def __init__(self) -> None:
        """Load configuration values from the config.json file."""

        self.values: dict[str, dict[str, Any]] | None = None

        try:
            with open("config.json", "r") as file:
                self.values = json.loads(file.read())

            if not self.values:
                raise ValueError("config values are null")
        except Exception as e:
            logger.opt(exception=e).error("Failed to load configuration")

            return

        self.channels: dict[str, int] = self.values["channels"]

        self.logsKeywords: list[str] = self.values["logs"]["keywords"]
        self.logsIgnoreChannels: list[int] = self.values["logs"]["ignoreChannels"]
        self.logsMentions: list[int] = self.values["logs"]["mentions"]

        self.forumsServer: int = self.values["forums"]["server"]
        self.forumsLifetime: int = self.values["forums"]["lifetime"]
        self.forumsImmune: list[int] = self.values["forums"]["immune"]
        self.forumsChannels: list[int] = self.values["forums"]["channels"]
