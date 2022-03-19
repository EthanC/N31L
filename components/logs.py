from typing import Any, Dict, List, Optional

import tanjun
from helpers import Responses, Utility
from hikari.events.message_events import DMMessageCreateEvent, GuildMessageCreateEvent
from hikari.files import Bytes
from loguru import logger
from tanjun import Client, Component

component: Component = Component(name="Logs")


@component.with_listener(DMMessageCreateEvent)
async def EventDirectMessage(
    ctx: DMMessageCreateEvent,
    config: Dict[str, Any] = tanjun.inject(type=Dict[str, Any]),
) -> None:
    """Handler for notifying of direct messages."""

    if not config["logging"]["discord"]["enable"]:
        return
    elif int(ctx.author.id) in config["users"]["owners"]:
        return

    payload: Dict[str, Any] = {
        "username": "N31L",
        "avatar_url": "https://i.imgur.com/cGtkGuI.png",
        "embeds": [
            {
                "title": "Direct Message",
                "description": f">>> {Utility.Trim((content := ctx.message.content), 4000)}"
                if content is not None
                else None,
                "timestamp": ctx.message.timestamp.isoformat(),
                "color": int("00FF00", base=16),
                "footer": {"text": f"{ctx.author.id}"},
                "author": {
                    "name": f"{ctx.author.username}#{ctx.author.discriminator}",
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

    status: bool = await Utility.POST(
        config["logging"]["discord"]["webhookUrl"], payload
    )

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

    if not config["logging"]["discord"]["enable"]:
        return
    elif ctx.author.is_bot:
        return
    elif ctx.author.is_system:
        return
    elif ctx.author.id in config["users"]["owners"]:
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
                "timestamp": ctx.message.timestamp.isoformat(),
                "color": int("00FF00", base=16),
                "footer": {"text": f"{ctx.author.id}"},
                "author": {
                    "name": f"{ctx.author.username}#{ctx.author.discriminator}",
                    "icon_url": str(ctx.author.default_avatar_url)
                    if (avatar := ctx.author.avatar_url) is None
                    else str(avatar),
                },
                "fields": [
                    {
                        "name": "Keyword" if len(found) == 1 else "Keywords",
                        "value": ", ".join(found),
                        "inline": False,
                    },
                    {
                        "name": "Message Link",
                        "value": f"[`#{ctx.get_channel().name}`](https://discord.com/channels/{ctx.guild_id}/{ctx.channel_id}/{ctx.message_id})",
                        "inline": False,
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
            }
        )

    status: bool = await Utility.POST(
        config["logging"]["discord"]["webhookUrl"], payload
    )

    if status is not True:
        return

    logger.success(
        f"Notified of keyword ({found}) mention by {Responses.ExpandUser(ctx.author, False)} in {Responses.ExpandGuild(ctx.get_guild(), False)} {Responses.ExpandChannel(ctx.get_channel(), False)}"
    )


@component.with_listener(GuildMessageCreateEvent)
async def EventMirror(
    ctx: GuildMessageCreateEvent,
    client: Client = tanjun.inject(type=Client),
    config: Dict[str, Any] = tanjun.inject(type=Dict[str, Any]),
) -> None:
    """Handler for automatically mirroring HepBoat log archives."""

    if not ctx.author.is_bot:
        return
    elif int(ctx.author.id) != config["users"]["hepboat"]:
        return
    elif not hasattr(ctx.message, "content"):
        return
    elif ctx.message.content is None:
        return

    content: str = ctx.message.content.lower()
    url: Optional[str] = None

    if "hep.gg/api/archive/" not in content:
        return

    try:
        url = content.split("(<")[1].split(">)")[0]

        if not url.startswith("https://"):
            raise Exception(f"expected startswith https://, got {url}")
        elif not url.endswith(".html"):
            raise Exception(f"expected endswith .html, got {url}")
    except Exception as e:
        logger.debug(f"Failed to validate HepBoat log archive URL, {e}")

        return

    data: Optional[str] = await Utility.GET(url.replace(".html", ".txt"))

    if data is None:
        return

    result: str = Responses.Log("mirror", f"Mirror of HepBoat log archive <{url}>")
    filename: Optional[str] = None
    channelId: Optional[int] = None
    users: List[str] = []

    try:
        filename = url.split("/")[-1].split(".")[0]
    except Exception as e:
        logger.debug(f"Failed to determine HepBoat log archive filename, {e}")

        return

    for line in data.splitlines():
        try:
            if channelId is None:
                channelId = int(line.split("/ ")[1].split("/ ")[0])

            user: str = line.split("/ ")[2].split(")")[0]

            if (user := f"`{user}`") not in users:
                users.append(user)
        except Exception as e:
            logger.debug(
                f"Failed to determine relevant user and channel in HepBoat log archive, {e}"
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

    logger.success(f"Mirrored HepBoat log archive {url}")
