from datetime import datetime
from os import environ
from typing import Any, Dict, List, Optional

import tanjun
from hikari import ChannelType, PartialChannel
from hikari.events.message_events import (
    DMMessageCreateEvent,
    GuildMessageCreateEvent,
    GuildMessageDeleteEvent,
)
from hikari.files import Bytes
from loguru import logger
from tanjun import Client, Component

from helpers import Responses, Utility
from models import State

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
                        "value": f"`#{ctx.get_channel().name}`",
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
                        "value": f"`#{ctx.get_channel().name}`",
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

    if not ctx.author.is_bot:
        return
    elif int(ctx.author.id) != config["users"]["zeppelin"]:
        return
    elif not hasattr(ctx.message, "content"):
        return
    elif ctx.message.content is None:
        return

    content: str = ctx.message.content.lower()
    url: Optional[str] = None

    if "zeppelin.gg/api/archives/" not in content:
        return

    try:
        url = content.split("(<")[1].split(">)")[0]

        if not url.startswith("https://"):
            raise Exception(f"expected startswith https://, got {url}")
    except Exception as e:
        logger.opt(exception=e).debug("Failed to validate Zeppelin log archive URL")

        return

    data: Optional[str] = await Utility.GET(url)

    if data is None:
        return

    result: str = Responses.Log("mirror", f"Mirror of Zeppelin log archive <{url}>")
    filename: Optional[str] = None
    channelId: Optional[int] = None
    users: List[str] = []

    try:
        filename = url.split("/")[-1] + ".txt"
    except Exception as e:
        logger.opt(exception=e).debug(
            f"Failed to determine Zeppelin log archive filename"
        )

        return

    for line in data.splitlines():
        try:
            if channelId is None:
                channelId = int(line.split("/ ")[1].split("/ ")[0])

            user: str = line.split("/ ")[2].split(")")[0]

            if (user := f"`{user}`") not in users:
                users.append(user)
        except Exception as e:
            logger.opt(exception=e).debug(
                f"Failed to determine relevant user and channel in Zeppelin log archive"
            )

    if channelId is not None:
        result += (
            f" in {Responses.ExpandChannel(ctx.get_guild().get_channel(channelId))}"
        )

    if len(users) > 0:
        result += " (" + ", ".join(users) + ")"

    await client.rest.create_message(
        config["channels"]["moderation"],
        result,
        attachment=Bytes(data, f"{filename}.txt"),
    )

    logger.success(f"Mirrored Zeppelin log archive {url}")


@component.with_listener(GuildMessageCreateEvent)
async def EventStoreThreadMessage(
    ctx: GuildMessageCreateEvent,
    config: Dict[str, Any] = tanjun.inject(type=Dict[str, Any]),
    state: State = tanjun.inject(type=State),
) -> None:
    """Temporarily store thread messages for future logging."""

    if not ctx.message:
        return

    channel: PartialChannel = await ctx.message.fetch_channel()

    if not channel:
        return

    # Disregard message deletions in regular channels. Zeppelin is only
    # missing thread message deletions.
    if (channel.type != ChannelType.GUILD_PUBLIC_THREAD) and (
        channel.type != ChannelType.GUILD_PRIVATE_THREAD
    ):
        return

    content: str = ctx.message.content

    for attachment in ctx.message.attachments:
        content += f"\n<{attachment.url}>"

    state.threadMessages.append(
        {
            "id": ctx.message.id,
            "created": int(ctx.message.created_at.timestamp()),
            "content": content,
        }
    )

    logger.debug(
        f"Added {Responses.ExpandUser(ctx.message.author, False)} thread message ({ctx.message.id}) in {Responses.ExpandThread(channel, False)} {Responses.ExpandGuild(ctx.get_guild(), False)} to cache"
    )
    logger.trace(content)
    logger.trace(state.threadMessages)


@component.with_schedule
@tanjun.as_time_schedule(minutes=5)
async def TaskPurgeThreadMessages(
    config: Dict[str, Any] = tanjun.inject(type=Dict[str, Any]),
    state: State = tanjun.inject(type=State),
) -> None:
    """Automatically delete cached thread messages older than the configured lifetime."""

    limit: int = config["logging"]["lifetime"]
    idx: int = 0
    count: int = 0

    for message in state.threadMessages:
        now: int = int(datetime.now().timestamp())
        age: int = now - message["created"]
        mId: int = message["id"]

        if age > limit:
            state.threadMessages.pop(idx)

            logger.debug(
                f"Removed thread message ({mId}) from cache due to age exceeding configured lifetime ({age} > {limit})"
            )
            logger.trace(message["content"])

            count += 1

        idx += 1

    logger.info(
        f"Purged {count:,} cached thread messages per configured lifetime ({limit})"
    )


@component.with_listener(GuildMessageDeleteEvent)
async def EventThreadDelete(
    ctx: GuildMessageDeleteEvent,
    client: Client = tanjun.inject(type=Client),
    config: Dict[str, Any] = tanjun.inject(type=Dict[str, Any]),
    state: State = tanjun.inject(type=State),
) -> None:
    """Handler for logging deleted messages in Threads."""

    if not ctx.old_message:
        return

    channel: PartialChannel = await ctx.old_message.fetch_channel()

    if not channel:
        return

    # Disregard message deletions in regular channels. Zeppelin is only
    # missing thread message deletions.
    if (channel.type != ChannelType.GUILD_PUBLIC_THREAD) and (
        channel.type != ChannelType.GUILD_PRIVATE_THREAD
    ):
        return

    result: str = f"{Responses.ExpandUser(ctx.old_message.author)} thread message deleted in {Responses.ExpandThread(await ctx.old_message.fetch_channel())}"

    idx: int = 0

    for old in state.threadMessages:
        if old["id"] != ctx.old_message.id:
            continue

        result += "\n>>> " + old["content"]

        # Message is deleted, we no longer need to cache it
        state.threadMessages.pop(idx)

        idx += 1

    await client.rest.create_message(
        config["channels"]["moderation"], Responses.Log("wastebasket", result)
    )

    logger.success(
        f"Logged {Responses.ExpandUser(ctx.old_message.author, False)} thread message deletion in {Responses.ExpandGuild(ctx.get_guild(), False)} {Responses.ExpandThread(channel, False)}"
    )
