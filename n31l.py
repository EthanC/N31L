import logging
import os
from sys import exit, stdout

from arc import GatewayClient
from environs import env
from hikari import Activity, ActivityType, GatewayBot, Intents, Permissions, Status
from loguru import logger
from loguru_discord import DiscordSink

from core.config import Config
from core.hooks import HookStart, HookStop
from core.intercept import Intercept

logger.info("N31L")
logger.info("https://github.com/EthanC/N31L")

if env.read_env(recurse=False):
    logger.success("Loaded environment variables")

if level := env.str("LOG_LEVEL"):
    logger.remove()
    logger.add(stdout, level=level)

    logger.success(f"Set console logging level to {level}")

# Reroute standard logging to Loguru
logging.basicConfig(handlers=[Intercept()], level=0, force=True)

logger.add("error.log", level="ERROR", rotation=env.str("LOG_FILE_SIZE", "100 MB"))

if url := env.url("LOG_DISCORD_WEBHOOK_URL"):
    logger.add(
        DiscordSink(url.geturl()),
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

if not (token := env.str("DISCORD_TOKEN")):
    logger.critical("Failed to initialize bot, DISCORD_TOKEN is not set")

    exit(1)

if not (cfg := Config()):
    logger.critical("Failed to initialize bot, config is not initialized")

    exit(1)

isDebug: bool = True if (level and level == "DEBUG" or "TRACE") else False

bot: GatewayBot = GatewayBot(
    token,
    allow_color=False,
    banner=None,
    suppress_optimization_warning=isDebug,
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
    is_dm_enabled=False,
)

client.set_type_dependency(GatewayClient, client)
client.set_type_dependency(GatewayBot, bot)
client.set_type_dependency(Config, cfg)

client.load_extensions_from("extensions")

client.add_startup_hook(HookStart)
client.add_shutdown_hook(HookStop)

try:
    bot.run(
        activity=Activity(name="Call of Duty Server", type=ActivityType.WATCHING),
        check_for_updates=False,
        status=Status.DO_NOT_DISTURB,
    )
except Exception as e:
    logger.opt(exception=e).critical("Fatal error occurred during runtime")
