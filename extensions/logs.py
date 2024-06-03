from typing import Any

import arc
from arc import GatewayClient, GatewayContext, GatewayPlugin
from hikari import DMMessageCreateEvent, GatewayBot, GuildMessageCreateEvent
from hikari.files import Bytes
from loguru import logger
from urlextract import URLExtract  # type: ignore

from core.config import Config
from core.formatters import (
    Colors,
    ExpandChannel,
    ExpandServer,
    ExpandUser,
    GetAvatar,
    Log,
    Response,
)
from core.hooks import HookError
from core.utils import GET, FindNumbers, IsValidUser, Trim

plugin: GatewayPlugin = GatewayPlugin("logs")


@arc.loader
def ExtensionLoader(client: GatewayClient) -> None:
    """Required. Called upon loading the extension."""

    logger.debug(f"Attempting to load {plugin.name} extension...")
    logger.trace(plugin)

    try:
        client.add_plugin(plugin)
    except Exception as e:
        logger.opt(exception=e).error(f"Failed to load {plugin.name} extension")


@plugin.listen()
async def EventDirectMessage(event: DMMessageCreateEvent) -> None:
    """Handler for notifying of direct messages."""

    bot: GatewayBot = plugin.client.get_type_dependency(GatewayBot)

    if not (n31l := bot.get_me()):
        raise RuntimeError("Bot user is null")

    if event.author_id == n31l.id:
        logger.debug("Direct Message command ignored, message author is N31L")

        return

    cfg: Config = plugin.client.get_type_dependency(Config)

    fields: list[dict[str, str | bool]] = []

    for attachment in event.message.attachments:
        fields.append(
            {
                "name": "Attachment",
                "value": f"[`{attachment.filename}`]({attachment.url})",
            }
        )

    for sticker in event.message.stickers:
        fields.append(
            {"name": "Sticker", "value": f"[{sticker.name}]({sticker.image_url})"}
        )

    logger.trace(fields)

    await plugin.client.rest.create_message(
        cfg.channels["production"],
        embed=Response(
            title="Direct Message",
            color=Colors.N31LGreen.value,
            description=f">>> {Trim(event.content, 4000)}" if event.content else None,
            fields=fields,
            author=ExpandUser(event.author, format=False, showId=False),
            authorIcon=GetAvatar(event.author),
            footer=str(event.author_id),
            timestamp=event.message.timestamp,
        ),
    )

    logger.success(
        f"Notified of direct message from {ExpandUser(event.author, format=False)}"
    )


@plugin.listen()
async def EventKeyword(event: GuildMessageCreateEvent) -> None:
    """Handler for notifying of keyword mentions."""

    cfg: Config = plugin.client.get_type_dependency(Config)

    if not event.is_human:
        logger.trace("Ignored message creation event, author is not a human")

        return
    elif event.author.is_system:
        logger.trace("Ignored message creation event, author is system")

        return
    elif not event.content:
        logger.trace("Ignored message creation event, content is null")

        return
    elif event.channel_id in cfg.logsIgnoreChannels:
        logger.trace("Ignored message creation event, channel is ignored")

        return

    words: list[str] = [word.lower() for word in event.content.split()]
    found: list[str] = []

    for keyword in cfg.logsKeywords:
        if keyword in words:
            found.append(keyword)

    if len(found) == 0:
        logger.trace("Ignored message creation event, no keywords found")

        return

    content: str = event.content

    for keyword in found:
        content = content.replace(keyword, f"**{keyword}**")

    logger.trace(content)

    fields: list[dict[str, str | bool]] = [
        {"name": "Channel", "value": ExpandChannel(event.get_channel(), showId=False)}
    ]

    for attachment in event.message.attachments:
        fields.append(
            {
                "name": "Attachment",
                "value": f"[`{attachment.filename}`]({attachment.url})",
            }
        )

    logger.trace(fields)

    await plugin.client.rest.create_message(
        cfg.channels["production"],
        embed=Response(
            title=("Keyword" if len(found) == 1 else "Keywords") + " Mention",
            url=event.message.make_link(event.guild_id),
            color=Colors.N31LGreen.value,
            description=f">>> {Trim(content, 4000)}",
            fields=fields,
            author=ExpandUser(event.author, format=False, showId=False),
            authorIcon=GetAvatar(event.author),
            footer=str(event.author_id),
            timestamp=event.message.timestamp,
        ),
    )

    logger.success(
        f"Notified of keyword(s) ({found}) mention by {ExpandUser(event.author, format=False)} in {ExpandServer(event.get_guild(), format=False)} {ExpandChannel(event.get_channel(), format=False)}"
    )


@plugin.listen()
async def EventMention(event: GuildMessageCreateEvent) -> None:
    """Handler for notifying of user mentions."""

    if not event.is_human:
        logger.trace("Ignored message creation event, author is not human")

        return
    elif not event.content:
        logger.trace("Ignored message creation event, content is null")

        return
    elif not event.message.user_mentions_ids:
        logger.trace("Ignored message creation event, no user mentions")

        return

    cfg: Config = plugin.client.get_type_dependency(Config)
    found: list[int] = []

    for userId in cfg.logsMentions:
        if userId in event.message.user_mentions_ids:
            found.append(userId)

    if len(found) == 0:
        logger.trace("Ignored message creation event, no relevant user mentions")

        return

    await plugin.client.rest.create_message(
        cfg.channels["production"],
        embed=Response(
            title=("User" if len(found) == 1 else "Users") + " Mentioned",
            url=event.message.make_link(event.guild_id),
            color=Colors.N31LGreen.value,
            description=f">>> {Trim(event.content, 4000)}",
            author=ExpandUser(event.author, format=False, showId=False),
            authorIcon=GetAvatar(event.author),
            footer=str(event.author_id),
            timestamp=event.message.timestamp,
        ),
    )

    logger.success(
        f"Notified of mention(s) ({found}) by {ExpandUser(event.author, format=False)} in {ExpandServer(event.get_guild(), format=False)} {ExpandChannel(event.get_channel(), format=False)}"
    )


@plugin.listen()
async def EventMirror(event: GuildMessageCreateEvent) -> None:
    """Handler for automatically mirroring Zeppelin log archives."""

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

        data: dict[str, Any] | list[Any] | str | None = await GET(url)

        if not data:
            logger.debug(f"Skipping URL {url}, data is null")

            continue
        elif not isinstance(data, str):
            logger.debug(f"Skipping URL {url}, expected string response")

            continue

        found: list[str] = []

        for line in data.splitlines():
            for find in FindNumbers(line, 17, 19):
                if await IsValidUser(find, plugin.client):
                    found.append(f"`{find}`")

        # Ensure there are no duplicate users
        found: list[str] = list(set(found))

        result: str = f"Mirror of Zeppelin log archive <{url}>"

        if len(found) > 0:
            result += f" ({", ".join(found)})"

        result = Log("mirror", result)
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
async def ErrorHandler(ctx: GatewayContext, error: Exception) -> None:
    """Handler for errors originating from this plugin."""

    await HookError(ctx, error)
