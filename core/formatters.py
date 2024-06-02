import random
import string
from datetime import datetime
from enum import Enum

from arc import (
    GatewayContext,
    SlashCommand,
    SlashSubCommand,
    SlashSubGroup,
)
from hikari import (
    CommandInteractionOption,
    Embed,
    Guild,
    GuildChannel,
    GuildThreadChannel,
    PartialChannel,
    Role,
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


def ExpandCommand(
    ctx: GatewayContext,
    *,
    mention: bool = False,
    options: bool = True,
    format: bool = True,
) -> str:
    """Build a modular command string for the provided context."""

    if (not hasattr(ctx, "command")) or (not ctx.command):
        logger.debug("Failed to expand null command")

        return "Unknown Command"

    if mention:
        if isinstance(ctx.command, (SlashCommand, SlashSubCommand)):
            return ctx.command.make_mention()
        else:
            logger.warning(
                f"Attempted to mention command of invalid type {type(ctx.command)}"
            )

    result: str = ctx.command.name

    if isinstance(ctx.command, SlashSubCommand):
        if isinstance(ctx.command.parent, SlashSubGroup):
            result = f"/{ctx.command.parent.parent.name} {ctx.command.parent.name} {ctx.command.name}"
        else:
            result = f"/{ctx.command.parent.name} {ctx.command.name}"
    elif isinstance(ctx.command, SlashCommand):
        result = f"/{ctx.command.name}"

    if options:
        if (hasattr(ctx, "_options")) and (ctx._options):  # type: ignore
            for option in ctx._options:  # type: ignore
                result += f" {option.name}:{option.value}"

    if format:
        result = f"`{result}`"

    logger.debug(f"Expanded command {ctx.command} to {result}")

    return result


def ExpandUser(
    user: User | None,
    *,
    mention: bool = False,
    format: bool = True,
    showId: bool = True,
) -> str:
    """Build a reusable string for the provided Discord user."""

    if not user:
        logger.debug("Failed to expand null user")

        return "Unknown User"

    if mention:
        return user.mention

    result: str = ""

    if format:
        result += f"`{user.username}`"
    else:
        result += user.username

    if showId:
        if format:
            result += f" (`{user.id}`)"
        else:
            result += f" ({user.id})"

    logger.debug(f"Expanded user {user} to {result}")

    return result


def ExpandServer(
    server: Guild | None, *, format: bool = True, showId: bool = True
) -> str:
    """Build a modular string for the provided server."""

    if not server:
        logger.debug("Failed to expand null server")

        return "Unknown Server"

    result: str = ""

    if format:
        result += f"`{server.name}`"
    else:
        result += server.name

    if showId:
        if format:
            result += f" (`{server.id}`)"
        else:
            result += f" ({server.id})"

    logger.debug(f"Expanded server {server} to {result}")

    return result


def ExpandChannel(
    channel: GuildChannel
    | PartialChannel
    | TextableGuildChannel
    | GuildThreadChannel
    | None,
    *,
    mention: bool = False,
    format: bool = True,
    showId: bool = True,
) -> str:
    """Build a reusable string for the provided Discord channel."""

    if not channel:
        logger.debug("Failed to expand null channel")

        return "Unknown Channel"

    if isinstance(channel, GuildThreadChannel):
        return ExpandThread(channel, mention=mention, format=format, showId=showId)

    if mention:
        return channel.mention

    result: str = ""

    if channel.name:
        if format:
            result += f"`{channel.name}`"
        else:
            result += channel.name

    if showId:
        if format:
            result += f" (`{channel.id}`)"
        else:
            result += f" ({channel.id})"

    logger.debug(f"Expanded channel {channel} to {result}")

    return result


def ExpandThread(
    thread: GuildThreadChannel | None,
    *,
    mention: bool = False,
    format: bool = True,
    showId: bool = True,
) -> str:
    """Build a reusable string for the provided Discord thread."""

    if not thread:
        logger.debug("Failed to expand null thread")

        return "Unknown Thread"

    if mention:
        return thread.mention

    result: str = ""

    if thread.name:
        if format:
            result += f"`{thread.name}`"
        else:
            result += thread.name

    if showId:
        if format:
            result += f" (`{thread.id}`)"
        else:
            result += f" ({thread.id})"

    logger.debug(f"Expanded thread {thread} to {result}")

    return result


def ExpandRole(
    role: Role | None,
    *,
    mention: bool = False,
    format: bool = True,
    showId: bool = True,
) -> str:
    """Build a reusable string for the provided Discord role."""

    if not role:
        logger.debug("Failed to expand null role")

        return "Unknown Role"

    if mention:
        return role.mention

    result: str = ""

    if format:
        result += f"`{role.name}`"
    else:
        result += role.name

    if showId:
        if format:
            result += f" (`{role.id}`)"
        else:
            result += f" ({role.id})"

    logger.debug(f"Expanded role {role} to {result}")

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
