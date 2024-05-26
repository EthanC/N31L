from datetime import datetime

import arc
from arc import (
    GatewayClient,
    GatewayPlugin,
)
from hikari import GuildThreadChannel
from loguru import logger

from core.config import Config
from core.formatters import ExpandGuild, ExpandThread, Log
from core.utils import Elapsed, UserHasRole

plugin: GatewayPlugin = GatewayPlugin("threads")


@arc.loader
def ExtensionLoader(client: GatewayClient) -> None:
    """Required. Called upon loading the extension."""

    logger.debug(f"Attempting to load {plugin.name} extension...")
    logger.trace(plugin)

    try:
        client.add_plugin(plugin)
    except Exception as e:
        logger.opt(exception=e).error(f"Failed to load {plugin.name} extension")


@arc.utils.interval_loop(seconds=300)
async def TaskArchiveThreads(client: GatewayClient) -> None:
    """Automatically archive threads in the configured channels."""

    logger.info("Beginning recurring task to archive threads...")

    cfg: Config = client.get_type_dependency(Config)

    lifetime: int = cfg.forumsLifetime
    threads: list[GuildThreadChannel] = list(
        await client.rest.fetch_active_threads(cfg.forumsServer)
    )

    for thread in threads:
        title: str = ExpandThread(thread, format=False)

        if thread.is_archived:
            logger.debug(f"Skipped thread {title}, already archived")

            continue
        elif thread.parent_id not in cfg.forumsChannels:
            logger.debug(f"Skipped thread {title}, not in a configured forum channel")

            continue
        elif Elapsed(datetime.now(), thread.created_at) < lifetime:
            logger.debug(f"Skipped thread {title}, maximum lifetime not exceeded")

            continue
        elif await UserHasRole(
            thread.owner_id, cfg.forumsImmune, thread.guild_id, client
        ):
            logger.debug(f"Skipped thread {title}, author is immune")

            continue

        try:
            await client.rest.edit_channel(
                thread.id,
                archived=True,
                reason=f"Maximum lifetime of {lifetime:,}s exceeded.",
            )
        except Exception as e:
            logger.opt(exception=e).error(
                f"Failed to archive thread {title} in {ExpandGuild(thread.get_guild(), format=False)}"
            )

            continue

        await client.rest.create_message(
            cfg.channels["threads"],
            Log(
                "thread",
                f"Archived thread {ExpandThread(thread)} with reason: *Maximum lifetime of {lifetime:,}s exceeded.*",
            ),
        )

        logger.success(
            f"Archived thread {title} due to maximum lifetime of {lifetime:,}s exceeded"
        )

    logger.info("Completed recurring task to archive threads")
