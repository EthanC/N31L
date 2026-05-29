"""Module containing the log command handler."""

from typing import Any

import arc
from arc import GatewayClient, GatewayContext, GatewayPlugin
from hikari import (
    ButtonStyle,
    ComponentInteraction,
    DMMessageCreateEvent,
    Embed,
    GatewayBot,
    GuildMessageCreateEvent,
    InteractionCreateEvent,
    InteractionType,
    LazyIterator,
    Message,
    MessageFlag,
    PartialInteraction,
    ResponseType,
)
from hikari.files import Bytes
from loguru import logger
from urlextract import URLExtract

from core.config import Config
from core.formatters import (
    Colors,
    expand_channel,
    expand_interaction,
    expand_server,
    expand_user,
    get_server_icon,
    get_user_avatar,
    log,
    response,
)
from core.hooks import hook_error
from core.utils import find_numbers, get, is_valid_user

plugin: GatewayPlugin = GatewayPlugin("logs")


@arc.loader
def extension_loader(client: GatewayClient) -> None:
    """Load this extension."""
    logger.debug(f"Attempting to load {plugin.name} extension...")
    logger.trace(plugin)

    try:
        client.add_plugin(plugin)
    except Exception as e:
        logger.opt(exception=e).error(f"Failed to load {plugin.name} extension")


@plugin.listen()
async def event_direct_message(event: DMMessageCreateEvent) -> None:
    """Handle notifying of direct messages."""
    bot: GatewayBot = plugin.client.get_type_dependency(GatewayBot)

    if not (n31l := bot.get_me()):
        raise RuntimeError("Bot user is null")

    if event.author_id == n31l.id:
        logger.debug("Direct Message command ignored, message author is N31L")

        return

    cfg: Config = plugin.client.get_type_dependency(Config)

    fields: list[dict[str, str | bool]] = []

    if attachments := event.message.attachments:
        for attachment in attachments:
            fields.append(
                {
                    "name": "Attachment",
                    "value": f"[`{attachment.filename}`]({attachment.url})",
                }
            )

    if stickers := event.message.stickers:
        for sticker in stickers:
            fields.append(
                {"name": "Sticker", "value": f"[{sticker.name}]({sticker.make_url()})"}
            )

    logger.trace(fields)

    await plugin.client.rest.create_message(
        cfg.channels["production"],
        embed=response(
            title="Direct Message",
            color=Colors.N31L_GREEN,
            description=f">>> {event.content}" if event.content else None,
            fields=fields,
            author=await expand_user(event.author, format=False, show_id=False),
            authorIcon=get_user_avatar(event.author),
            footer=str(event.author_id),
            timestamp=event.message.timestamp,
        ),
    )

    logger.success(
        f"Notified of direct message from {await expand_user(event.author, format=False)}"
    )


@plugin.listen()
async def event_mirror(event: GuildMessageCreateEvent) -> None:
    """Handle automatically mirroring Zeppelin log archives."""
    if event.is_human:
        logger.trace("Ignored message creation event, author is not a bot")

        return
    elif not event.content:
        logger.trace("Ignored message creation event, content is null")

        return

    bot: GatewayBot = plugin.client.get_type_dependency(GatewayBot)
    cfg: Config = plugin.client.get_type_dependency(Config)

    if not (n31l := bot.get_me()):
        raise RuntimeError("Bot user is null")

    if event.channel_id != cfg.channels["moderation"]:
        logger.trace("Ignored message creation event, channel is not desired")

        return
    elif event.author_id == n31l.id:
        logger.trace("Ignored message creation event, author is N31L")

        return

    for url in URLExtract().find_urls(event.content.lower(), True):
        if not isinstance(url, str):
            logger.debug(f"Skipping URL {url}, recieved {type(url)} expected string")

            continue

        if not url.startswith("https://api.zeppelin.gg/archives/"):
            continue

        data: dict[str, Any] | list[Any] | str | None = await get(url)

        if not data:
            logger.debug(f"Skipping URL {url}, data is null")

            continue
        elif not isinstance(data, str):
            logger.debug(f"Skipping URL {url}, expected string response")

            continue

        found: list[str] = []

        for line in data.splitlines():
            for find in find_numbers(line, 17, 19):
                if await is_valid_user(find, plugin.client):
                    found.append(f"`{find}`")

        # Ensure there are no duplicate users
        found: list[str] = list(set(found))

        result: str = f"Mirror of Zeppelin log archive <{url}>"

        if len(found) > 0:
            result += f" ({', '.join(found)})"

        result = log("mirror", result)
        filename: str = "archive"

        try:
            filename = url.split("/")[-1]
        except Exception as e:
            logger.opt(exception=e).warning(
                "Failed to determine Zeppelin log archive filename"
            )

        await plugin.client.rest.create_message(
            cfg.channels["moderation"],
            result,
            attachment=Bytes(data, f"{filename}.txt"),
            reply=event.message,
        )

        logger.success(f"Mirrored Zeppelin log archive {url}")


@plugin.set_error_handler
async def error_handler(ctx: GatewayContext, error: Exception) -> None:
    """Handle errors originating from this plugin."""
    await hook_error(ctx, error)
