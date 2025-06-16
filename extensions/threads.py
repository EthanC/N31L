import asyncio
from datetime import datetime

import arc
from arc import GatewayClient, GatewayPlugin
from hikari import GuildThreadChannel, GuildThreadCreateEvent
from loguru import logger

from core.config import Config
from core.formatters import expand_server, expand_thread, expand_user, log
from core.utils import elapsed, user_has_role

plugin: GatewayPlugin = GatewayPlugin("threads")


@arc.loader
def extension_loader(client: GatewayClient) -> None:
    """Required. Called upon loading the extension."""

    logger.debug(f"Attempting to load {plugin.name} extension...")
    logger.trace(plugin)

    try:
        client.add_plugin(plugin)
    except Exception as e:
        logger.opt(exception=e).error(f"Failed to load {plugin.name} extension")


@plugin.listen()
async def event_thread_create(event: GuildThreadCreateEvent) -> None:
    """Handler for greeting messages upon thread creation."""

    cfg: Config = plugin.client.get_type_dependency(Config)

    if not event.guild_id == cfg.forums_server:
        logger.debug("Ignored thread creation event, not in the configured server")

        return
    elif not event.thread.parent_id not in cfg.forums_channels:
        logger.debug("Ignored thread creation event, not in a configured forum channel")

        return

    await event.thread.send(cfg.forums_greeting)


@arc.utils.interval_loop(seconds=600)
async def task_archive_threads(client: GatewayClient) -> None:
    """Automatically archive threads in the configured channels."""

    logger.info("Beginning recurring task to archive threads...")

    cfg: Config = client.get_type_dependency(Config)

    lifetime: int = cfg.forums_lifetime
    threads: list[GuildThreadChannel] = list(
        await client.rest.fetch_active_threads(cfg.forums_server)
    )

    for thread in threads:
        title: str = expand_thread(thread, format=False)

        if thread.is_archived:
            logger.debug(f"Skipped thread {title}, already archived")

            continue
        elif thread.parent_id not in cfg.forums_channels:
            logger.debug(f"Skipped thread {title}, not in a configured forum channel")

            continue
        elif elapsed(datetime.now(), thread.created_at) < lifetime:
            logger.debug(f"Skipped thread {title}, maximum lifetime not exceeded")

            continue
        elif await user_has_role(
            thread.owner_id, cfg.forums_immune, thread.guild_id, client
        ):
            logger.debug(
                f"Skipped thread {title}, author {await expand_user(thread.owner_id, format=False, client=client)} is immune"
            )

            continue

        try:
            await client.rest.edit_channel(
                thread.id,
                archived=True,
                reason=f"Maximum lifetime of {lifetime:,}s exceeded.",
            )
        except Exception as e:
            logger.opt(exception=e).error(
                f"Failed to archive thread {title} in {await expand_server(thread.get_guild(), format=False)}"
            )

            continue

        await client.rest.create_message(
            cfg.channels["threads"],
            log(
                "thread",
                f"Archived thread {expand_thread(thread)} with reason: *Maximum lifetime of {lifetime:,}s exceeded.*",
            ),
        )

        logger.success(
            f"Archived thread {title} due to maximum lifetime of {lifetime:,}s exceeded"
        )
        logger.trace("Sleeping 0.5s to avoid ratelimits...")

        await asyncio.sleep(0.5)

    logger.info("Completed recurring task to archive threads")
