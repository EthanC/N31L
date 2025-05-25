import json
import random
import string
from datetime import datetime
from enum import StrEnum
from typing import Any

from arc import (
    GatewayClient,
    GatewayContext,
    SlashCommand,
    SlashSubCommand,
    SlashSubGroup,
)
from hikari import (
    Attachment,
    CommandInteractionOption,
    Embed,
    GatewayGuild,
    Guild,
    GuildChannel,
    GuildThreadChannel,
    PartialChannel,
    PartialGuild,
    PartialInteraction,
    Role,
    Snowflake,
    TextableGuildChannel,
    User,
)
from loguru import logger


class Colors(StrEnum):
    """
    Reusable palette of Discord and Call of Duty brand colors.

    https://discord.com/branding
    """

    DISCORD_RED = "#ED4245"
    DISCORD_GREEN = "#57F287"
    DISCORD_BLURPLE = "#5865F2"
    DISCORD_YELLOW = "#FEE75C"
    N31L_GREEN = "#00FF00"


def expand_command(
    ctx: GatewayContext,
    *,
    mention: bool = False,
    options: bool = True,
    format: bool = True,
) -> str:
    """Build a modular command string for the provided context."""

    if (not hasattr(ctx, "command")) or (not ctx.command):
        logger.debug("Command is null")

        return "Unknown Command"

    if mention:
        if isinstance(ctx.command, (SlashCommand, SlashSubCommand)):
            return ctx.command.make_mention()
        else:
            logger.debug(
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

    logger.debug(f"Expanded command {ctx.command.name} to {result}")

    return result


async def expand_user(
    user: User | Snowflake | None,
    *,
    mention: bool = False,
    format: bool = True,
    show_id: bool = True,
    client: GatewayClient | None = None,
) -> str:
    """Build a modular string for the provided user."""

    if isinstance(user, Snowflake):
        if client:
            user = await client.rest.fetch_user(user)
        else:
            user = None

    if not user:
        logger.debug("User is null")

        return "Unknown User"

    if mention:
        return user.mention

    result: str = ""

    if format:
        result += f"`{user.username}`"
    else:
        result += user.username

    if show_id:
        if format:
            result += f" (`{user.id}`)"
        else:
            result += f" ({user.id})"

    logger.debug(f"Expanded user {user} to {result}")

    return result


async def expand_server(
    server: Guild | PartialGuild | Snowflake | None,
    *,
    format: bool = True,
    show_id: bool = True,
    client: GatewayClient | None = None,
) -> str:
    """Build a modular string for the provided server."""

    if isinstance(server, Snowflake):
        if client:
            server = await client.rest.fetch_guild(server)
        else:
            server = None

    if not server:
        logger.debug("Server is null")

        return "Unknown Server"

    result: str = ""

    if format:
        result += f"`{server.name}`"
    else:
        result += server.name

    if show_id:
        if format:
            result += f" (`{server.id}`)"
        else:
            result += f" ({server.id})"

    logger.debug(f"Expanded server {server} to {result}")

    return result


async def expand_channel(
    channel: GuildChannel
    | PartialChannel
    | TextableGuildChannel
    | GuildThreadChannel
    | Snowflake
    | None,
    *,
    mention: bool = False,
    format: bool = True,
    show_id: bool = True,
    client: GatewayClient | None = None,
) -> str:
    """Build a modular string for the provided channel."""

    if isinstance(channel, Snowflake):
        if client:
            channel = await client.rest.fetch_channel(channel)
        else:
            channel = None

    if not channel:
        logger.debug("Channel is null")

        return "Unknown Channel"

    if isinstance(channel, GuildThreadChannel):
        return expand_thread(channel, mention=mention, format=format, show_id=show_id)

    if mention:
        return channel.mention

    result: str = ""

    if channel.name:
        if format:
            result += f"`#{channel.name}`"
        else:
            result += f"\\#{channel.name}"

    if show_id:
        if format:
            result += f" (`{channel.id}`)"
        else:
            result += f" ({channel.id})"

    logger.debug(f"Expanded channel {channel} to {result}")

    return result


def expand_thread(
    thread: GuildThreadChannel | None,
    *,
    mention: bool = False,
    format: bool = True,
    show_id: bool = True,
) -> str:
    """Build a modular string for the provided thread."""

    if not thread:
        logger.debug("Thread is null")

        return "Unknown Thread"

    if mention:
        return thread.mention

    result: str = ""

    if thread.name:
        if format:
            result += f"`{thread.name}`"
        else:
            result += thread.name

    if show_id:
        if format:
            result += f" (`{thread.id}`)"
        else:
            result += f" ({thread.id})"

    logger.debug(f"Expanded thread {thread} to {result}")

    return result


def expand_role(
    role: Role | None,
    *,
    mention: bool = False,
    format: bool = True,
    show_id: bool = True,
) -> str:
    """Build a modular string for the provided role."""

    if not role:
        logger.debug("Role is null")

        return "Unknown Role"

    if mention:
        return role.mention

    result: str = ""

    if format:
        result += f"`{role.name}`"
    else:
        result += role.name

    if show_id:
        if format:
            result += f" (`{role.id}`)"
        else:
            result += f" ({role.id})"

    logger.debug(f"Expanded role {role} to {result}")

    return result


def expand_interaction(
    interaction: PartialInteraction | None, *, format: bool = True, show_id: bool = True
) -> str:
    """Build a modular string for the provided interaction."""

    if not interaction:
        logger.debug("Interaction is null")

        return "Unknown Interaction"

    result: str = ""

    if show_id:
        if format:
            result += f"`{interaction.id}`"
        else:
            result += f"{interaction.id}"

    if format:
        result += f" `{interaction.type}` (`{type(interaction)}`)"
    else:
        result += f" {interaction.type} ({type(interaction)})"

    logger.debug(f"Expanded interaction {interaction} to {result}")

    # lstrip() to remove leading whitespace if show_id is False
    return result.lstrip()


def get_user_avatar(user: User) -> str | None:
    """Return a URL for the provided Discord user's avatar."""

    if avatar_url := user.make_avatar_url():
        return str(avatar_url)


async def get_server_icon(
    server: PartialGuild
    | Guild
    | GatewayGuild
    | GuildChannel
    | TextableGuildChannel
    | GuildThreadChannel
    | Snowflake
    | None,
    *,
    client: GatewayClient | None = None,
) -> str | None:
    """Return a URL for the provided Discord server's icon."""

    if isinstance(server, GuildChannel):
        server = server.get_guild()
    elif isinstance(server, TextableGuildChannel):
        server = server.get_guild()
    elif isinstance(server, GuildThreadChannel):
        server = server.get_guild()
    elif isinstance(server, Snowflake):
        if client:
            server = await client.rest.fetch_guild(server)
        else:
            server = None

    if not server:
        logger.debug("Guild is null")

        return

    if url := server.make_icon_url():
        return str(url)


def random_string(length: int) -> str:
    """
    Generate a random string consisting of letters and numbers at the
    specified length.
    """

    return "".join(random.choices(string.ascii_letters + string.digits, k=length))


def response(
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
    """
    Build a generic response Embed object.

    All provided string values will be trimmed according to the embed
    limits defined in the Discord API documentation.
    https://discord.com/developers/docs/resources/message#embed-object-embed-limits
    """

    result: Embed = Embed(
        title=trim(title, 256),
        description=trim(description, 4096),
        url=url,
        color=color,
        timestamp=timestamp,
    )

    if author:
        result.set_author(name=trim(author, 256), url=authorUrl, icon=authorIcon)

    if thumbnail:
        result.set_thumbnail(thumbnail)

    if image:
        result.set_image(image)

    if footer:
        result.set_footer(trim(footer, 2048), icon=footerIcon)

    for field in fields:
        name: str | bool | None = field["name"]
        value: str | bool | None = field["value"]

        if not isinstance(name, str):
            logger.warning(
                f"Invalid value provided for field name: {name} ({type(name)})"
            )

            continue
        elif not isinstance(value, str):
            logger.warning(
                f"Invalid value provided for field value: {value} ({type(value)})"
            )

            continue
        if not (name := trim(name, 256)):
            logger.warning(
                f"Invalid value provided for field name: {name} ({type(name)})"
            )

            continue
        elif not (value := trim(value, 1024)):
            logger.warning(
                f"Invalid value provided for field value: {value} ({type(value)})"
            )

            continue

        result.add_field(name, value, inline=bool(field.get("inline", True)))

    return result


def log(emoji: str, message: str, timestamp: datetime | None = None) -> str:
    """Build a reusable log message."""

    if not timestamp:
        timestamp = datetime.now()

    return f"[{time_long(timestamp)}] :{emoji}: {message}"


def time_relative(timestamp: int | float | datetime) -> str:
    """
    Create a relative timestamp using markdown formatting.

    Example: "in 2 minutes" or "6 minutes ago"
    """

    if isinstance(timestamp, float):
        timestamp = int(timestamp)
    elif isinstance(timestamp, datetime):
        timestamp = int(timestamp.timestamp())

    return f"<t:{timestamp}:R>"


def time_long(timestamp: int | float | datetime) -> str:
    """
    Create a long time timestamp using markdown formatting.

    Example: "4:20:00 PM"
    """

    if isinstance(timestamp, float):
        timestamp = int(timestamp)
    elif isinstance(timestamp, datetime):
        timestamp = int(timestamp.timestamp())

    return f"<t:{timestamp}:T>"


def format_options(options: list[CommandInteractionOption]) -> str:
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


def trim(
    input: str | None,
    length: int,
    *,
    prefix: str | None = None,
    suffix: str | None = "...",
) -> str | None:
    """Trim a string using the provided parameters."""

    if not input:
        return

    # Account for length of prefix
    if prefix:
        length -= len(prefix)

    # Account for length of suffix
    if suffix:
        length -= len(suffix)

    if len(input) <= length:
        return input

    result: str = input[:length]

    try:
        result = result.rsplit(" ", 1)[0]
    except Exception as e:
        logger.opt(exception=e).debug("Failed to cleanly trim string")

    if prefix:
        result = prefix + result

    if suffix:
        result += suffix

    return result


async def json_to_embed(data: str | dict[str, Any] | Attachment | None) -> list[Embed]:
    """
    Serialize the provided JSON string, dict, or Attachment object to a list
    of Discord Embed objects.
    """

    entries: list[dict[str, Any]] = []
    results: list[Embed] = []

    if isinstance(data, Attachment):
        data = (await data.read()).decode("UTF-8")

        logger.trace(f"{data=}")

    if isinstance(data, str):
        data = json.loads(data)

        logger.trace(f"{data=}")

    if isinstance(data, dict):
        if value := data.get("embeds"):
            entries = value
        else:
            entries = [data]

    logger.trace(f"{entries=}")

    for entry in entries:
        logger.trace(f"{entry=}")

        embed: Embed = Embed(
            title=entry.get("title"),
            description=entry.get("description"),
            url=entry.get("url"),
            color=entry.get("color"),
            timestamp=None
            if not (ts := entry.get("timestamp"))
            else datetime.fromisoformat(ts),
        )

        if author := entry.get("author"):
            logger.trace(f"{author=}")

            embed.set_author(
                name=author.get("name"),
                url=author.get("url"),
                icon=author.get("icon_url"),
            )

        if thumb := entry.get("thumbnail"):
            logger.trace(f"{thumb=}")

            embed.set_thumbnail(thumb.get("url"))

        if image := entry.get("image"):
            logger.trace(f"{image=}")

            embed.set_image(image.get("url"))

        if footer := entry.get("footer"):
            logger.trace(f"{footer=}")

            embed.set_footer(footer.get("text"), icon=footer.get("icon_url"))

        if fields := entry.get("fields", []):
            logger.trace(f"{fields=}")

            for field in fields:
                logger.trace(f"{field=}")

                embed.add_field(
                    field.get("name"),
                    field.get("value"),
                    inline=field.get("inline"),
                )

        logger.trace(f"{embed=}")

        results.append(embed)

    logger.debug(f"Formed {len(results):,} embed objects from the provided JSON data")

    return results
