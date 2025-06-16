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
                raise RuntimeError("config values are null")
        except Exception as e:
            logger.opt(exception=e).error("Failed to load configuration")

            return

        self.channels: dict[str, int] = self.values["channels"]

        self.logs_keywords: list[str] = self.values["logs"]["keywords"]
        self.logs_ignore_channels: list[int] = self.values["logs"]["ignoreChannels"]
        self.logs_mentions: list[int] = self.values["logs"]["mentions"]

        self.roles_require: list[int] = self.values["roles"]["require"]
        self.roles_allow: list[int] = self.values["roles"]["allow"]
        self.roles_vip: int = self.values["roles"]["vip"]

        self.forums_server: int = self.values["forums"]["server"]
        self.forums_lifetime: int = self.values["forums"]["lifetime"]
        self.forums_immune: list[int] = self.values["forums"]["immune"]
        self.forums_channels: list[int] = self.values["forums"]["channels"]
        self.forums_greeting: str = self.values["forums"]["greeting"]
