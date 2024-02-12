from os import environ
from typing import Any, Dict, List, Optional

import tanjun
from hikari.events.message_events import (
    DMMessageCreateEvent,
    GuildMessageCreateEvent,
)
from hikari.files import Bytes
from loguru import logger
from tanjun import Client, Component
from urlextract import URLExtract

from helpers import Responses, Utility

component: Component = Component(name="Logs")


@component.with_listener(DMMessageCreateEvent)
async def EventDirectMessage(
    ctx: DMMessageCreateEvent,
    config: Dict[str, Any] = tanjun.inject(type=Dict[str, Any]),
) -> None:
    """Handler for notifying of direct messages."""

    if int(ctx.author.id) == config["users"]["bot"]:
        return
    elif int(ctx.author.id) == config["users"]["owner"]:
        return

    content: Optional[str] = None

    if hasattr(ctx.message, "content"):
        if ctx.message.content is not None:
            content = f">>> {Utility.Trim(ctx.message.content, 4000)}"

    payload: Dict[str, Any] = {
        "username": "N31L",
        "avatar_url": "https://i.imgur.com/cGtkGuI.png",
        "embeds": [
            {
                "title": "Direct Message",
                "description": content,
                "timestamp": ctx.message.timestamp.isoformat(),
                "color": int("00FF00", base=16),
                "footer": {"text": f"{ctx.author.id}"},
                "author": {
                    "name": Responses.ExpandUser(ctx.author, False, False),
                    "icon_url": str(ctx.author.default_avatar_url)
                    if (avatar := ctx.author.avatar_url) is None
                    else str(avatar),
                },
                "fields": [],
            }
        ],
    }

    for attachment in ctx.message.attachments:
        payload["embeds"][0]["fields"].append(
            {
                "name": "Attachment",
                "value": f"[`{attachment.filename}` (`{attachment.media_type}`)]({attachment.url})",
            }
        )

    status: bool = await Utility.POST(environ.get("LOG_DISCORD_WEBHOOK_URL"), payload)

    if status is not True:
        return

    logger.info(
        f"Received direct message from {Responses.ExpandUser(ctx.author, False)}"
    )


@component.with_listener(GuildMessageCreateEvent)
async def EventKeyword(
    ctx: GuildMessageCreateEvent,
    config: Dict[str, Any] = tanjun.inject(type=Dict[str, Any]),
) -> None:
    """Handler for notifying of keyword mentions."""

    if ctx.author.is_bot:
        return
    elif ctx.author.is_system:
        return
    elif ctx.author.id == config["users"]["owner"]:
        return
    elif ctx.message.channel_id in config["logging"]["kwIgnore"]:
        return
    elif ctx.message.content is None:
        return

    words: List[str] = [word.lower() for word in ctx.message.content.split()]
    found: List[str] = []

    for keyword in config["logging"]["keywords"]:
        if keyword not in words:
            continue

        found.append(f"`{keyword}`")

    if len(found) == 0:
        return

    payload: Dict[str, Any] = {
        "username": "N31L",
        "avatar_url": "https://i.imgur.com/cGtkGuI.png",
        "embeds": [
            {
                "title": ("Keyword" if len(found) == 1 else "Keywords") + " Mention",
                "description": f">>> {Utility.Trim(ctx.message.content, 4000)}",
                "url": f"https://discord.com/channels/{ctx.guild_id}/{ctx.channel_id}/{ctx.message_id}",
                "timestamp": ctx.message.timestamp.isoformat(),
                "color": int("00FF00", base=16),
                "footer": {"text": f"{ctx.author.id}"},
                "author": {
                    "name": Responses.ExpandUser(ctx.author, False, False),
                    "icon_url": str(ctx.author.default_avatar_url)
                    if (avatar := ctx.author.avatar_url) is None
                    else str(avatar),
                },
                "fields": [
                    {
                        "name": "Keyword" if len(found) == 1 else "Keywords",
                        "value": ", ".join(found),
                        "inline": True,
                    },
                    {
                        "name": "Channel",
                        "value": "Unknown"
                        if not (chan := ctx.get_channel())
                        else f"`#{chan.name}`",
                        "inline": True,
                    },
                ],
            }
        ],
    }

    for attachment in ctx.message.attachments:
        payload["embeds"][0]["fields"].append(
            {
                "name": "Attachment",
                "value": f"[`{attachment.filename}`]({attachment.url})",
                "inline": True,
            }
        )

    status: bool = await Utility.POST(environ.get("LOG_DISCORD_WEBHOOK_URL"), payload)

    if status is not True:
        return

    logger.success(
        f"Notified of keyword ({found}) mention by {Responses.ExpandUser(ctx.author, False)} in {Responses.ExpandGuild(ctx.get_guild(), False)} {Responses.ExpandChannel(ctx.get_channel(), False)}"
    )


@component.with_listener(GuildMessageCreateEvent)
async def EventMention(
    ctx: GuildMessageCreateEvent,
    config: Dict[str, Any] = tanjun.inject(type=Dict[str, Any]),
) -> None:
    """Handler for notifying of mentions."""

    if ctx.author.is_bot:
        return
    elif ctx.author.is_system:
        return
    elif ctx.author.id == config["users"]["owner"]:
        return
    elif ctx.message.content is None:
        return

    found: List[str] = []

    for id in config["logging"]["mentions"]:
        if id not in ctx.message.user_mentions_ids:
            continue

        found.append(f"<@{id}>")

    if len(found) == 0:
        return

    payload: Dict[str, Any] = {
        "username": "N31L",
        "avatar_url": "https://i.imgur.com/cGtkGuI.png",
        "embeds": [
            {
                "title": "Mention",
                "description": f">>> {Utility.Trim(ctx.message.content, 4000)}",
                "url": f"https://discord.com/channels/{ctx.guild_id}/{ctx.channel_id}/{ctx.message_id}",
                "timestamp": ctx.message.timestamp.isoformat(),
                "color": int("00FF00", base=16),
                "footer": {"text": f"{ctx.author.id}"},
                "author": {
                    "name": Responses.ExpandUser(ctx.author, False, False),
                    "icon_url": str(ctx.author.default_avatar_url)
                    if (avatar := ctx.author.avatar_url) is None
                    else str(avatar),
                },
                "fields": [
                    {
                        "name": "User" if len(found) == 1 else "Users",
                        "value": ", ".join(found),
                        "inline": True,
                    },
                    {
                        "name": "Channel",
                        "value": "Unknown"
                        if not (chan := ctx.get_channel())
                        else f"`#{chan.name}`",
                        "inline": True,
                    },
                ],
            }
        ],
    }

    for attachment in ctx.message.attachments:
        payload["embeds"][0]["fields"].append(
            {
                "name": "Attachment",
                "value": f"[`{attachment.filename}`]({attachment.url})",
                "inline": True,
            }
        )

    status: bool = await Utility.POST(environ.get("LOG_DISCORD_WEBHOOK_URL"), payload)

    if status is not True:
        return

    logger.success(
        f"Notified of mention ({found}) by {Responses.ExpandUser(ctx.author, False)} in {Responses.ExpandGuild(ctx.get_guild(), False)} {Responses.ExpandChannel(ctx.get_channel(), False)}"
    )


@component.with_listener(GuildMessageCreateEvent)
async def EventMirror(
    ctx: GuildMessageCreateEvent,
    client: Client = tanjun.inject(type=Client),
    config: Dict[str, Any] = tanjun.inject(type=Dict[str, Any]),
) -> None:
    """Handler for automatically mirroring Zeppelin log archives."""

    if int(ctx.channel_id) != config["channels"]["moderation"]:
        return
    elif not ctx.author.is_bot:
        return
    elif int(ctx.author.id) == config["users"]["bot"]:
        return
    elif not hasattr(ctx.message, "content"):
        return
    elif ctx.message.content is None:
        return

    content: str = ctx.message.content.lower()
    urls: List[str] = []
    extractor: URLExtract = URLExtract()

    urls = extractor.find_urls(content, True)

    logger.trace(content)
    logger.trace(urls)

    for url in urls:
        if not url.startswith("https://api.zeppelin.gg/archives/"):
            continue

        data: Optional[str] = await Utility.GET(url)

        if data is None:
            return
        
        found: list[str] = []

        for line in data.splitlines():
            for find in Utility.FindNumbers(line, 17, 19):
                if await Utility.IsValidUser(find, client):
                    found.append(f"`{find}`")
        
        # Ensure there are no duplicate users
        found: list[str] = list(set(found))

        result: str = f"Mirror of Zeppelin log archive <{url}>"

        if len(found) > 0:
            result += f" ({", ".join(found)})"

        result = Responses.Log("mirror", result)
        filename: str = "archive"

        try:
            filename = url.split("/")[-1]
        except Exception as e:
            logger.opt(exception=e).warning(
                "Failed to determine Zeppelin log archive filename"
            )

        await client.rest.create_message(
            config["channels"]["moderation"],
            result,
            attachment=Bytes(data, f"{filename}.txt"),
            reply=ctx.message,
        )

        logger.success(f"Mirrored Zeppelin log archive {url}")
