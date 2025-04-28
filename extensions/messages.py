import arc
from arc import (
    AutodeferMode,
    GatewayClient,
    GatewayContext,
    GatewayPlugin,
    Option,
    StrParams,
)
from hikari import (
    ApplicationContextType,
    Message,
    MessageFlag,
    MessageType,
    Permissions,
)
from loguru import logger

from core.config import Config
from core.formatters import (
    Colors,
    expand_channel,
    expand_command,
    expand_server,
    expand_user,
    get_user_avatar,
    response,
    time_relative,
)
from core.hooks import hook_error, hook_log
from core.utils import find_numbers, is_valid_user

plugin: GatewayPlugin = GatewayPlugin("messages")


@arc.loader
def extension_loader(client: GatewayClient) -> None:
    """Required. Called upon loading the extension."""

    logger.debug(f"Attempting to load {plugin.name} extension...")
    logger.trace(plugin)

    try:
        client.add_plugin(plugin)
    except Exception as e:
        logger.opt(exception=e).error(f"Failed to load {plugin.name} extension")


@plugin.include
@arc.with_hook(hook_log)
@arc.slash_command(
    "raw",
    "Return the raw markdown content of a provided message.",
    autodefer=AutodeferMode.EPHEMERAL,
    invocation_contexts=[ApplicationContextType.GUILD, ApplicationContextType.BOT_DM],
)
async def command_raw_slash(
    ctx: GatewayContext,
    channel_id: Option[str, StrParams("Enter the ID of the channel.")],
    message_id: Option[str, StrParams("Enter the ID of the message.")],
) -> None:
    """Handler for the /raw slash command."""

    msg: Message = await ctx.client.rest.fetch_message(int(channel_id), int(message_id))

    if not msg:
        logger.debug(
            f"Failed to fetch message {message_id} in channel {await expand_channel(channel_id, format=False)}"
        )

        await ctx.respond(
            flags=MessageFlag.EPHEMERAL,
            embed=response(
                color=Colors.DISCORD_RED, description="Failed to fetch message."
            ),
        )

        return

    if not msg.content:
        logger.debug(
            f"Command {expand_command(ctx, format=False)} ignored, message content is null"
        )

        await ctx.respond(
            flags=MessageFlag.EPHEMERAL,
            embed=response(
                color=Colors.DISCORD_RED,
                description=f"{msg.author.mention}'s message {msg.make_link(msg.guild_id)} has no content.",
            ),
        )

        return

    await ctx.respond(
        flags=MessageFlag.EPHEMERAL,
        embed=response(
            author=await expand_user(msg.author, format=False),
            authorIcon=get_user_avatar(msg.author),
            color=Colors.DISCORD_GREEN,
            description=f"{msg.make_link(msg.guild_id)}\n```md\n{msg.content}\n```",
            timestamp=msg.timestamp,
        ),
    )


@plugin.include
@arc.with_hook(arc.has_permissions(Permissions.MANAGE_MESSAGES))
@arc.with_hook(hook_log)
@arc.message_command("Parse Message", autodefer=AutodeferMode.EPHEMERAL)
async def command_parse(ctx: GatewayContext, msg: Message) -> None:
    """Handler for the Parse Message context menu command."""

    results: list[int] = []

    # Minimum and maximum length of Discord snowflakes
    # https://discord.com/developers/docs/reference#snowflakes
    sMin: int = 17
    sMax: int = 19

    if msg.type == MessageType.GUILD_MEMBER_JOIN:
        results.append(msg.author.id)

    if content := msg.content:
        for find in find_numbers(content, sMin, sMax):
            results.append(find)

    for embed in msg.embeds:
        if embed.author:
            if name := embed.author.name:
                for find in find_numbers(name, sMin, sMax):
                    results.append(find)

        if title := embed.title:
            for find in find_numbers(title, sMin, sMax):
                results.append(find)

        if desc := embed.description:
            for find in find_numbers(desc, sMin, sMax):
                results.append(find)

        if fields := embed.fields:
            for field in fields:
                for find in find_numbers(field.name, sMin, sMax):
                    results.append(find)

                for find in find_numbers(field.value, sMin, sMax):
                    results.append(find)

        if embed.footer:
            if footer := embed.footer.text:
                for find in find_numbers(footer, sMin, sMax):
                    results.append(find)

    # Remove duplicates from results
    results = list(set(results))

    for result in results:
        if not await is_valid_user(result, ctx.client):
            results.remove(result)

    if len(results) == 0:
        await ctx.respond(
            flags=MessageFlag.EPHEMERAL,
            embed=response(
                color=Colors.DISCORD_YELLOW,
                description=f"No User IDs found in the parsed message {msg.make_link(msg.guild_id)}.",
            ),
        )

        return

    descriptor: str = "User IDs" if len(results) > 1 else "User ID"

    await ctx.respond(
        flags=MessageFlag.EPHEMERAL,
        embed=response(
            color=Colors.DISCORD_GREEN,
            description=f"Found {len(results):,} {descriptor} in the parsed message {msg.make_link(msg.guild_id)}...",
        ),
    )

    for result in results:
        await ctx.respond(str(result), flags=MessageFlag.EPHEMERAL)

    logger.success(
        f"Parsed {len(results):,} {descriptor} ({results}) from message {msg.id} in {await expand_server(ctx.get_guild(), format=False)} {await expand_channel(await msg.fetch_channel(), format=False)}"
    )


@plugin.include
@arc.with_hook(hook_log)
@arc.message_command("Raw Message", autodefer=AutodeferMode.EPHEMERAL)
async def command_raw(ctx: GatewayContext, msg: Message) -> None:
    """Handler for the Raw Message context menu command."""

    if not msg.content:
        logger.debug("Raw Message command ignored, message content is null")

        await ctx.respond(
            flags=MessageFlag.EPHEMERAL,
            embed=response(
                color=Colors.DISCORD_RED,
                description=f"{msg.author.mention}'s message {msg.make_link(msg.guild_id)} has no content.",
            ),
        )

        return

    await ctx.respond(
        flags=MessageFlag.EPHEMERAL,
        embed=response(
            author=await expand_user(msg.author, format=False),
            authorIcon=get_user_avatar(msg.author),
            color=Colors.DISCORD_GREEN,
            description=f"{msg.make_link(msg.guild_id)}\n```md\n{msg.content}\n```",
            timestamp=msg.timestamp,
        ),
    )


@plugin.include
@arc.with_hook(hook_log)
@arc.message_command("Report Message", autodefer=AutodeferMode.EPHEMERAL)
async def command_report(ctx: GatewayContext, msg: Message) -> None:
    """Handler for the Report Message context menu command."""

    cfg: Config = ctx.client.get_type_dependency(Config)

    if msg.author.is_system:
        logger.debug("Report Message command ignored, reported system message")

        await ctx.respond(
            flags=MessageFlag.EPHEMERAL,
            embed=response(
                color=Colors.DISCORD_RED,
                description=f"You cannot report a system message {msg.make_link(msg.guild_id)}.",
            ),
        )

        return
    elif msg.type == MessageType.GUILD_MEMBER_JOIN:
        logger.debug("Report Message command ignored, reported welcome message")

        await ctx.respond(
            flags=MessageFlag.EPHEMERAL,
            embed=response(
                color=Colors.DISCORD_RED,
                description=f"You cannot report a welcome message {msg.make_link(msg.guild_id)}.",
            ),
        )

        return
    elif msg.author.id == ctx.author.id:
        logger.debug("Report Message command ignored, reported own message")

        await ctx.respond(
            flags=MessageFlag.EPHEMERAL,
            embed=response(
                color=Colors.DISCORD_RED,
                description=f"You cannot report your own message {msg.make_link(msg.guild_id)}.",
            ),
        )

        return

    fields: list[dict[str, str | bool]] = [
        {"name": "Channel", "value": (await msg.fetch_channel()).mention},
        {"name": "Sent", "value": time_relative(msg.created_at)},
        {"name": "Reported", "value": time_relative(ctx.interaction.created_at)},
    ]

    for attachment in msg.attachments:
        fields.append(
            {
                "name": "Attachment",
                "value": f"[`{attachment.filename}`]({attachment.url})",
            }
        )

    # Empty string for easy appends, will be made None later if still empty
    embed_content: str | None = ""

    for embed in msg.embeds:
        if embed.description:
            embed_content += f"{embed.description}\n\n"

        if embed_content:
            # Remove trailing newlines
            embed_content = embed_content.strip()

        if embed.image:
            fields.append({"name": "Embed", "value": f"[Image]({embed.image.url})"})

        if embed.thumbnail:
            fields.append(
                {"name": "Embed", "value": f"[Thumbnail]({embed.thumbnail.url})"}
            )

    if embed_content == "":
        embed_content = None

    for sticker in msg.stickers:
        fields.append(
            {"name": "Sticker", "value": f"[{sticker.name}]({sticker.image_url})"}
        )

    await ctx.client.rest.create_message(
        cfg.channels["moderators"],
        embed=response(
            title="Reported Message",
            url=msg.make_link(msg.guild_id),
            color=Colors.DISCORD_YELLOW,
            description="[Empty]"
            if not (content := msg.content or embed_content)
            else f">>> {content}",
            fields=fields,
            author=await expand_user(msg.author, format=False),
            authorIcon=get_user_avatar(msg.author),
            footer=f"Reported by {await expand_user(ctx.author, format=False)}",
            footerIcon=get_user_avatar(ctx.author),
        ),
    )

    await ctx.respond(
        flags=MessageFlag.EPHEMERAL,
        embed=response(
            color=Colors.DISCORD_GREEN,
            description=f"Reported message {msg.make_link(msg.guild_id)} to the Moderators.",
            footer="Abuse of this feature will result in your removal from the server.",
        ),
    )


@plugin.set_error_handler
async def error_handler(ctx: GatewayContext, error: Exception) -> None:
    """Handler for errors originating from the messages plugin."""

    await hook_error(ctx, error)
