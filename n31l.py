import json
import logging
import os
from datetime import datetime
from sys import exit, stderr
from typing import Any, Dict

import hikari
import tanjun
from hikari.impl.bot import GatewayBot
from hikari.intents import Intents
from hikari.presences import Activity, ActivityType, Status
from loguru import logger
from notifiers.logging import NotificationHandler
from tanjun import Client

from components import Admin, Animals, Logs, Messages, Raid, Reddit, Roles
from helpers import Hooks, LogIntercept
from models import State


def Initialize() -> None:
    """Initialize N31L and begin primary functionality."""

    logger.info("N31L")
    logger.info("https://github.com/EthanC/N31L")

    config: Dict[str, Any] = LoadConfig()
    debug: bool = config.get("debug", False)
    state: State = State(
        botStart=datetime.now(),
        raidOffense=False,
        raidOffAge=None,
        raidOffReason=None,
        raidOffActor=None,
        raidOffCount=None,
        raidDefense=False,
    )

    SetupLogging(config)

    bot: GatewayBot = hikari.GatewayBot(
        config["credentials"]["discord"]["token"],
        allow_color=False,
        banner=None,
        intents=Intents.ALL,
    )
    client: Client = tanjun.Client.from_gateway_bot(
        bot, declare_global_commands=config["channels"]["guild"]
    )

    client.set_type_dependency(Dict[str, Any], config)
    client.set_type_dependency(State, state)
    client.set_type_dependency(GatewayBot, bot)
    client.set_type_dependency(Client, client)

    client.set_slash_hooks(
        (
            tanjun.SlashHooks()
            .add_pre_execution(Hooks.PreExecution)
            .add_post_execution(Hooks.PostExecution)
        )
    )

    client.add_component(Admin)
    client.add_component(Animals)
    client.add_component(Logs)
    client.add_component(Messages)
    client.add_component(Raid)
    client.add_component(Reddit)
    client.add_component(Roles)

    bot.run(
        asyncio_debug=debug,
        activity=Activity(name="Call of Duty server", type=ActivityType.WATCHING),
        status=Status.DO_NOT_DISTURB,
    )


def LoadConfig() -> Dict[str, Any]:
    """Load the configuration values specified in config.json"""

    try:
        with open("config.json", "r") as file:
            config: Dict[str, Any] = json.loads(file.read())
    except Exception as e:
        logger.critical(f"Failed to load configuration, {e}")

        exit(1)

    logger.success("Loaded configuration")

    return config


def SetupLogging(config: Dict[str, Any]) -> None:
    """Setup the logger using the configured values."""

    settings: Dict[str, Any] = config["logging"]

    logging.basicConfig(handlers=[LogIntercept()], level=0)

    if (level := settings["severity"].upper()) != "DEBUG":
        try:
            logger.remove()
            logger.add(stderr, level=level)

            logger.success(f"Set logger severity to {level}")
        except Exception as e:
            # Fallback to default logger settings
            logger.add(stderr, level="DEBUG")

            logger.error(f"Failed to set logger severity to {level}, {e}")

    if settings["files"]["enable"] is True:
        if (size := settings["files"]["debug"]) > 0:
            logger.add("n31l_debug.log", level="DEBUG", rotation=f"{size} MB")

        if (size := settings["files"]["info"]) > 0:
            logger.add("n31l_info.log", level="INFO", rotation=f"{size} MB")

        if (size := settings["files"]["warning"]) > 0:
            logger.add("n31l_warning.log", level="WARNING", rotation=f"{size} MB")

        logger.success("Enabled local file logging")

    if settings["discord"]["enable"] is True:
        level: str = settings["discord"]["severity"].upper()
        url: str = settings["discord"]["webhookUrl"]

        try:
            # Notifiers library does not natively support Discord at
            # this time. However, Discord will accept payloads which
            # are compatible with Slack by appending to the url.
            # https://github.com/liiight/notifiers/issues/400
            handler: NotificationHandler = NotificationHandler(
                "slack", defaults={"webhook_url": f"{url}/slack"}
            )

            logger.add(
                handler,
                level=level,
                format="```\n{time:YYYY-MM-DD HH:mm:ss.SSS} | {level:<8} | {name}:{function}:{line} - {message}\n```",
            )

            logger.success(f"Enabled logging to Discord with severity {level}")
        except Exception as e:
            logger.error(f"Failed to enable logging to Discord, {e}")


if __name__ == "__main__":
    try:
        # Replace default asyncio event loop with libuv on UNIX
        # https://github.com/hikari-py/hikari#uvloop
        if os.name != "nt":
            try:
                import uvloop  # type: ignore

                uvloop.install()
            except Exception as e:
                logger.debug(f"Defaulting to asyncio event loop, {e}")

        Initialize()
    except KeyboardInterrupt:
        exit()
