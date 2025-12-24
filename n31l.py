"""Primary entry point for the N31L Discord bot."""

import logging
import os
from os import environ
from sys import exit, stdout

from arc import GatewayClient
from environs import env
from hikari import (
    Activity,
    ActivityType,
    ApplicationContextType,
    GatewayBot,
    Intents,
    Permissions,
    Status,
)
from loguru import logger
from loguru_discord import DiscordSink
from loguru_discord.intercept import Intercept

from core.config import Config
from core.hooks import hook_start, hook_stop

logger.info("N31L")
logger.info("https://github.com/EthanC/N31L")

if env.read_env(recurse=False):
    logger.success("Loaded environment variables")

if environ.get("LOG_LEVEL"):
    level: str = env.str("LOG_LEVEL")

    logger.remove()
    logger.add(stdout, level=level)

    logger.success(f"Set console logging level to {level}")

Intercept.setup()

if environ.get("LOG_DISCORD_WEBHOOK_URL"):
    logger.add(
        DiscordSink(env.url("LOG_DISCORD_WEBHOOK_URL").geturl()),
        level=env.str("LOG_DISCORD_WEBHOOK_LEVEL"),
        backtrace=False,
    )

    logger.success("Enabled logging to Discord webhook")

# Replace default asyncio event loop with libuv on UNIX
# https://github.com/hikari-py/hikari#uvloop
if os.name != "nt":
    try:
        import uvloop  # type: ignore

        uvloop.install()

        logger.success("Installed libuv event loop")
    except Exception as e:
        logger.opt(exception=e).debug("Defaulted to asyncio event loop")

if not environ.get("DISCORD_TOKEN"):
    logger.critical("Failed to initialize bot, DISCORD_TOKEN is not set")

    exit(1)

if not (cfg := Config()):
    logger.critical("Failed to initialize bot, config is not initialized")

    exit(1)

is_debug: bool = (
    True
    if (
        environ.get("LOG_DISCORD_WEBHOOK_LEVEL")
        and env.str("LOG_DISCORD_WEBHOOK_LEVEL") == "DEBUG"
        or "TRACE"
    )
    else False
)

bot: GatewayBot = GatewayBot(
    env.str("DISCORD_TOKEN"),
    allow_color=False,
    banner=None,
    suppress_optimization_warning=is_debug,
    intents=(
        Intents.GUILDS
        | Intents.GUILD_MESSAGES
        | Intents.GUILD_MEMBERS
        | Intents.DM_MESSAGES
        | Intents.MESSAGE_CONTENT
    ),
)
client: GatewayClient = GatewayClient(
    bot,
    default_permissions=(
        Permissions.SEND_MESSAGES | Permissions.USE_APPLICATION_COMMANDS
    ),
    invocation_contexts=[ApplicationContextType.GUILD],
)

client.set_type_dependency(GatewayClient, client)
client.set_type_dependency(GatewayBot, bot)
client.set_type_dependency(Config, cfg)

client.load_extensions_from("extensions")

client.add_startup_hook(hook_start)
client.add_shutdown_hook(hook_stop)

try:
    bot.run(
        activity=Activity(name="Call of Duty Server", type=ActivityType.WATCHING),
        check_for_updates=False,
        status=Status.DO_NOT_DISTURB,
    )
except Exception as e:
    logger.opt(exception=e).critical("Fatal error occurred during runtime")
