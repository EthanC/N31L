import json
import logging
import os
from datetime import datetime
from os import environ
from sys import exit
from typing import Any, Dict

import dotenv
import hikari
import tanjun
from hikari.impl.bot import GatewayBot
from hikari.intents import Intents
from hikari.presences import Activity, ActivityType, Status
from loguru import logger
from notifiers.logging import NotificationHandler
from tanjun import Client

from components import Admin, Animals, Food, Logs, Messages, Raid, Reddit, Roles
from helpers import Intercept, MenuHooks, SlashHooks
from models import State


def Initialize() -> None:
    """Initialize N31L and begin primary functionality."""

    logger.info("N31L")
    logger.info("https://github.com/EthanC/N31L")

    if dotenv.load_dotenv():
        logger.success("Loaded environment variables")

    config: Dict[str, Any] = LoadConfig()

    state: State = State(
        botStart=datetime.now(),
        raidOffense=False,
        raidOffAge=None,
        raidOffReason=None,
        raidOffActor=None,
        raidOffCount=None,
        raidDefense=False,
    )

    logging.basicConfig(handlers=[Intercept()], level=0, force=True)

    if logUrl := environ.get("DISCORD_LOG_WEBHOOK"):
        if not (logLevel := environ.get("DISCORD_LOG_LEVEL")):
            logger.critical("Level for Discord webhook logging is not set")

            return

        logger.add(
            NotificationHandler("slack", defaults={"webhook_url": f"{logUrl}/slack"}),
            level=logLevel,
            format="```\n{time:YYYY-MM-DD HH:mm:ss.SSS} | {level:<8} | {name}:{function}:{line} - TEST\n```",
        )

        logger.success(f"Enabled logging to Discord webhook ({logLevel})")
        logger.trace(logUrl)

    if not environ.get("DISCORD_TOKEN"):
        logger.critical("Failed to create bot instance, DISCORD_TOKEN is not set")

        return

    bot: GatewayBot = hikari.GatewayBot(
        environ.get("DISCORD_TOKEN"),
        allow_color=False,
        banner=None,
        intents=(
            Intents.GUILDS
            | Intents.GUILD_MESSAGES
            | Intents.GUILD_MEMBERS
            | Intents.DM_MESSAGES
            | Intents.MESSAGE_CONTENT
        ),
    )

    if not environ.get("DISCORD_SERVER_ID"):
        logger.critical("Failed to register bot commands, DISCORD_SERVER_ID is not set")

        return

    client: Client = tanjun.Client.from_gateway_bot(
        bot, declare_global_commands=int(environ.get("DISCORD_SERVER_ID"))
    )

    client.set_type_dependency(Dict[str, Any], config)
    client.set_type_dependency(State, state)
    client.set_type_dependency(GatewayBot, bot)
    client.set_type_dependency(Client, client)

    client.set_slash_hooks(
        (
            tanjun.SlashHooks()
            .add_pre_execution(SlashHooks.PreExecution)
            .add_post_execution(SlashHooks.PostExecution)
        )
    )
    client.set_menu_hooks(
        tanjun.AnyHooks()
        .add_pre_execution(MenuHooks.PreExecution)
        .add_post_execution(MenuHooks.PostExecution)
    )

    client.add_component(Admin)
    client.add_component(Animals)
    client.add_component(Food)
    client.add_component(Logs)
    client.add_component(Messages)
    client.add_component(Raid)
    client.add_component(Reddit)
    client.add_component(Roles)

    bot.run(
        asyncio_debug=environ.get("DEBUG", False),
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


if __name__ == "__main__":
    try:
        # Replace default asyncio event loop with libuv on UNIX
        # https://github.com/hikari-py/hikari#uvloop
        if os.name != "nt":
            try:
                import uvloop  # type: ignore

                uvloop.install()

                logger.success("Installed libuv event loop")
            except Exception as e:
                logger.debug(f"Defaulted to asyncio event loop, {e}")

        Initialize()
    except KeyboardInterrupt:
        exit()
