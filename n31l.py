import json
import logging
import os
from datetime import datetime
from os import environ
from sys import exit, stdout
from typing import Any

import dotenv
import tanjun
from hikari import GatewayBot, GatewayConnectionError
from hikari.intents import Intents
from hikari.presences import Activity, ActivityType, Status
from loguru import logger
from loguru_discord import DiscordSink
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
        logger.trace(environ)

    config: dict[str, Any] = LoadConfig()
    state: State = State(botStart=datetime.now())

    # Reroute standard logging to Loguru
    logging.basicConfig(handlers=[Intercept()], level=0, force=True)

    if level := environ.get("LOG_LEVEL"):
        logger.remove()
        logger.add(stdout, level=level)

        logger.success(f"Set console logging level to {level}")

    if url := environ.get("LOG_DISCORD_WEBHOOK_URL"):
        logger.add(
            DiscordSink(url, suppress=[GatewayConnectionError]),
            level=environ.get("LOG_DISCORD_WEBHOOK_LEVEL"),
            backtrace=False,
        )

        logger.success("Enabled logging to Discord webhook")
        logger.trace(url)

    if not environ.get("DISCORD_TOKEN"):
        logger.critical("Failed to create bot instance, DISCORD_TOKEN is not set")

        return

    bot: GatewayBot = GatewayBot(
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

    client.set_type_dependency(dict[str, Any], config)
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


def LoadConfig() -> dict[str, Any]:
    """Load the configuration values specified in config.json"""

    try:
        with open("config.json", "r") as file:
            config: dict[str, Any] = json.loads(file.read())
    except Exception as e:
        logger.opt(exception=e).critical("Failed to load configuration")

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
                logger.opt(exception=e).debug("Defaulted to asyncio event loop")

        Initialize()
    except KeyboardInterrupt:
        exit()
