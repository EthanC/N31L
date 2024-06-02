import random
import string
from datetime import datetime
from enum import Enum

from hikari import (
    CommandInteractionOption,
    Embed,
    Guild,
    GuildChannel,
    GuildThreadChannel,
    PartialChannel,
    Role,
    Snowflake,
    TextableGuildChannel,
    User,
)
from loguru import logger


class Colors(Enum):
    """
    Reusable palette of Discord and Call of Duty brand colors.

    https://discord.com/branding
    """

    DiscordRed = "#ED4245"
    DiscordGreen = "#57F287"
    DiscordBlurple = "#5865F2"
    DiscordYellow = "#FEE75C"
    N31LGreen = "#00FF00"


def ExpandGuild(guild: Guild | None, format: bool = True) -> str:
    """Build a reusable string for the provided Discord guild."""

    if not guild:
        logger.debug("Failed to expand null guild")

        return "Unknown Server"

    if format:
        return f"`{guild.name}` (`{guild.id}`)"

    return f"{guild.name} ({guild.id})"


def ExpandChannel(
    channel: GuildChannel
    | PartialChannel
    | TextableGuildChannel
    | GuildThreadChannel
    | None,
    format: bool = True,
    showId: bool = True,
) -> str:
    """Build a reusable string for the provided Discord channel."""

    if not channel:
        logger.debug("Failed to expand null channel")

        return "Unknown Channel"

    if isinstance(channel, GuildThreadChannel):
        return ExpandThread(channel, format)

    result: str = ""

    if format:
        result += f"`#{channel.name}`"

        if showId:
            result += f" (`{channel.id}`)"

        return result

    result += f"#{channel.name}"

    if showId:
        result += f" ({channel.id})"

    return result


def ExpandThread(thread: GuildThreadChannel | None, format: bool = True) -> str:
    """Build a reusable string for the provided Discord thread."""

    if not thread:
        logger.debug("Failed to expand null thread")

        return "Unknown Thread"

    if format:
        return f"`{thread.name}` (`{thread.id}`)"

    return f"{thread.name} ({thread.id})"


def ExpandRole(role: Role | None, format: bool = True) -> str:
    """Build a reusable string for the provided Discord role."""

    if not role:
        logger.debug("Failed to expand null role")

        return "Unknown Role"

    if format:
        return f"`{role.name}` (`{role.id}`)"

    return f"{role.name} ({role.id})"


def ExpandUser(user: User | None, format: bool = True, showId: bool = True) -> str:
    """Build a reusable string for the provided Discord user."""

    if not user:
        logger.debug("Failed to expand null user")

        return "Unknown User"

    result: str = ""

    username: str = user.username
    userId: Snowflake = user.id

    if hasattr(user, "discriminator"):
        if (discrim := int(user.discriminator)) != 0:
            username += f"#{discrim}"

    if format:
        result += f"`{username}`"
    else:
        result += username

    if showId:
        if format:
            result += f" (`{userId}`)"
        else:
            result += f" ({userId})"

    logger.debug(f"Expanded user {user} to {result}")

    return result


def GetAvatar(user: User) -> str | None:
    """Return a URL for the provided Discord user's avatar."""

    if user.avatar_url:
        return str(user.avatar_url)
    elif user.default_avatar_url:
        return str(user.default_avatar_url)


def RandomString(length: int) -> str:
    """
    Generate a random string consisting of letters and numbers at the
    specified length.
    """

    return "".join(random.choices(string.ascii_letters + string.digits, k=length))


def Response(
    title: str | None = None,
    url: str | None = None,
    color: str | None = None,
    description: str | None = None,
    fields: list[dict[str, str | bool]] = [],
    author: str | None = None,
    authorUrl: str | None = None,
    authorIcon: str | None = None,
    thumbnail: str | None = None,
    image: str | None = None,
    footer: str | None = None,
    footerIcon: str | None = None,
    timestamp: datetime | None = None,
) -> Embed:
    """Build a generic response Embed object."""

    result: Embed = Embed(
        title=title,
        description=description,
        url=url,
        color=color,
        timestamp=timestamp,
    )

    if author:
        result.set_author(name=author, url=authorUrl, icon=authorIcon)

    if thumbnail:
        result.set_thumbnail(thumbnail)

    if image:
        result.set_image(image)

    if footer:
        result.set_footer(footer, icon=footerIcon)

    for field in fields:
        result.add_field(
            str(field["name"]),
            str(field["value"]),
            inline=bool(field.get("inline", True)),
        )

    return result


def Log(emoji: str, message: str, timestamp: datetime | None = None) -> str:
    """Build a reusable log message."""

    if not timestamp:
        timestamp = datetime.now()

    return f"[{LongTime(timestamp)}] :{emoji}: {message}"


def TimeRelative(timestamp: int | float | datetime) -> str:
    """
    Create a relative timestamp using markdown formatting.

    Example: "in 2 minutes" or "6 minutes ago"
    """

    if isinstance(timestamp, float):
        timestamp = int(timestamp)
    elif isinstance(timestamp, datetime):
        timestamp = int(timestamp.timestamp())

    return f"<t:{timestamp}:R>"


def LongTime(timestamp: int | float | datetime) -> str:
    """
    Create a long time timestamp using markdown formatting.

    Example: "4:20:00 PM"
    """

    if isinstance(timestamp, float):
        timestamp = int(timestamp)
    elif isinstance(timestamp, datetime):
        timestamp = int(timestamp.timestamp())

    return f"<t:{timestamp}:T>"


def FormatOptions(options: list[CommandInteractionOption]) -> str:
    """Return name:value sequence for list of command options."""

    result: str = ""

    logger.trace(options)

    for option in options:
        logger.trace(option)

        try:
            result += f"{option.name}:{option.value} "
        except Exception as e:
            logger.opt(exception=e).warning(
                f"Failed to parse commnad option {option.name} of type {type(option.value)}"
            )

    logger.debug(f"Formatted options {options} to sequence {result}")

    return result.rstrip()
