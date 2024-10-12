import arc
from arc import (
    AutodeferMode,
    GatewayClient,
    GatewayContext,
    GatewayPlugin,
    Option,
    StrParams,
)
from hikari import Message, MessageFlag, MessageType, Permissions
from loguru import logger

from core.config import Config
from core.formatters import (
    Colors,
    ExpandChannel,
    ExpandCommand,
    ExpandServer,
    ExpandUser,
    GetUserAvatar,
    Response,
    TimeRelative,
)
from core.hooks import HookError, HookLog
from core.utils import FindNumbers, IsValidUser

plugin: GatewayPlugin = GatewayPlugin("messages")


@arc.loader
def ExtensionLoader(client: GatewayClient) -> None:
    """Required. Called upon loading the extension."""

    logger.debug(f"Attempting to load {plugin.name} extension...")
    logger.trace(plugin)

    try:
        client.add_plugin(plugin)
    except Exception as e:
        logger.opt(exception=e).error(f"Failed to load {plugin.name} extension")


@plugin.include
@arc.with_hook(HookLog)
@arc.slash_command(
    "raw",
    "Return the raw markdown content of a provided message.",
    is_dm_enabled=True,
    autodefer=AutodeferMode.EPHEMERAL,
)
async def CommandRawSlash(
    ctx: GatewayContext,
    channelId: Option[
        str, StrParams("Enter the ID of the channel.", name="channel_id")
    ],
    messageId: Option[
        str, StrParams("Enter the ID of the message.", name="message_id")
    ],
) -> None:
    """Handler for the /raw slash command."""

    msg: Message = await ctx.client.rest.fetch_message(int(channelId), int(messageId))

    if not msg:
        logger.debug(
            f"Failed to fetch message {messageId} in channel {await ExpandChannel(channelId, format=False)}"
        )

        await ctx.respond(
            flags=MessageFlag.EPHEMERAL,
            embed=Response(
                color=Colors.DiscordRed.value, description="Failed to fetch message."
            ),
        )

        return

    if not msg.content:
        logger.debug(
            f"Command {ExpandCommand(ctx, format=False)} ignored, message content is null"
        )

        await ctx.respond(
            flags=MessageFlag.EPHEMERAL,
            embed=Response(
                color=Colors.DiscordRed.value,
                description=f"{msg.author.mention}'s message {msg.make_link(msg.guild_id)} has no content.",
            ),
        )

        return

    await ctx.respond(
        flags=MessageFlag.EPHEMERAL,
        embed=Response(
            author=await ExpandUser(msg.author, format=False),
            authorIcon=GetUserAvatar(msg.author),
            color=Colors.DiscordGreen.value,
            description=f"{msg.make_link(msg.guild_id)}\n```md\n{msg.content}\n```",
            timestamp=msg.timestamp,
        ),
    )


@plugin.include
@arc.with_hook(arc.has_permissions(Permissions.MANAGE_MESSAGES))
@arc.with_hook(HookLog)
@arc.message_command("Parse Message", autodefer=AutodeferMode.EPHEMERAL)
async def CommandParse(ctx: GatewayContext, msg: Message) -> None:
    """Handler for the Parse Message context menu command."""

    results: list[int] = []

    # Minimum and maximum length of Discord snowflakes
    # https://discord.com/developers/docs/reference#snowflakes
    sMin: int = 17
    sMax: int = 19

    if msg.type == MessageType.GUILD_MEMBER_JOIN:
        results.append(msg.author.id)

    if content := msg.content:
        for find in FindNumbers(content, sMin, sMax):
            results.append(find)

    for embed in msg.embeds:
        if embed.author:
            if name := embed.author.name:
                for find in FindNumbers(name, sMin, sMax):
                    results.append(find)

        if title := embed.title:
            for find in FindNumbers(title, sMin, sMax):
                results.append(find)

        if desc := embed.description:
            for find in FindNumbers(desc, sMin, sMax):
                results.append(find)

        if fields := embed.fields:
            for field in fields:
                for find in FindNumbers(field.name, sMin, sMax):
                    results.append(find)

                for find in FindNumbers(field.value, sMin, sMax):
                    results.append(find)

        if embed.footer:
            if footer := embed.footer.text:
                for find in FindNumbers(footer, sMin, sMax):
                    results.append(find)

    # Remove duplicates from results
    results = list(set(results))

    for result in results:
        if not await IsValidUser(result, ctx.client):
            results.remove(result)

    if len(results) == 0:
        await ctx.respond(
            flags=MessageFlag.EPHEMERAL,
            embed=Response(
                color=Colors.DiscordYellow.value,
                description=f"No User IDs found in the parsed message {msg.make_link(msg.guild_id)}.",
            ),
        )

        return

    descriptor: str = "User IDs" if len(results) > 1 else "User ID"

    await ctx.respond(
        flags=MessageFlag.EPHEMERAL,
        embed=Response(
            color=Colors.DiscordGreen.value,
            description=f"Found {len(results):,} {descriptor} in the parsed message {msg.make_link(msg.guild_id)}...",
        ),
    )

    for result in results:
        await ctx.respond(str(result), flags=MessageFlag.EPHEMERAL)

    logger.success(
        f"Parsed {len(results):,} {descriptor} ({results}) from message {msg.id} in {await ExpandServer(ctx.get_guild(), format=False)} {await ExpandChannel(await msg.fetch_channel(), format=False)}"
    )


@plugin.include
@arc.with_hook(HookLog)
@arc.message_command("Raw Message", autodefer=AutodeferMode.EPHEMERAL)
async def CommandRaw(ctx: GatewayContext, msg: Message) -> None:
    """Handler for the Raw Message context menu command."""

    if not msg.content:
        logger.debug("Raw Message command ignored, message content is null")

        await ctx.respond(
            flags=MessageFlag.EPHEMERAL,
            embed=Response(
                color=Colors.DiscordRed.value,
                description=f"{msg.author.mention}'s message {msg.make_link(msg.guild_id)} has no content.",
            ),
        )

        return

    await ctx.respond(
        flags=MessageFlag.EPHEMERAL,
        embed=Response(
            author=await ExpandUser(msg.author, format=False),
            authorIcon=GetUserAvatar(msg.author),
            color=Colors.DiscordGreen.value,
            description=f"{msg.make_link(msg.guild_id)}\n```md\n{msg.content}\n```",
            timestamp=msg.timestamp,
        ),
    )


@plugin.include
@arc.with_hook(HookLog)
@arc.message_command("Report Message", autodefer=AutodeferMode.EPHEMERAL)
async def CommandReport(ctx: GatewayContext, msg: Message) -> None:
    """Handler for the Report Message context menu command."""

    cfg: Config = ctx.client.get_type_dependency(Config)

    if msg.author.is_system:
        logger.debug("Report Message command ignored, reported system message")

        await ctx.respond(
            flags=MessageFlag.EPHEMERAL,
            embed=Response(
                color=Colors.DiscordRed.value,
                description=f"You cannot report a system message {msg.make_link(msg.guild_id)}.",
            ),
        )

        return
    elif msg.type == MessageType.GUILD_MEMBER_JOIN:
        logger.debug("Report Message command ignored, reported welcome message")

        await ctx.respond(
            flags=MessageFlag.EPHEMERAL,
            embed=Response(
                color=Colors.DiscordRed.value,
                description=f"You cannot report a welcome message {msg.make_link(msg.guild_id)}.",
            ),
        )

        return
    elif msg.author.id == ctx.author.id:
        logger.debug("Report Message command ignored, reported own message")

        await ctx.respond(
            flags=MessageFlag.EPHEMERAL,
            embed=Response(
                color=Colors.DiscordRed.value,
                description=f"You cannot report your own message {msg.make_link(msg.guild_id)}.",
            ),
        )

        return

    fields: list[dict[str, str | bool]] = [
        {"name": "Sent", "value": TimeRelative(msg.created_at)},
        {"name": "Reported", "value": TimeRelative(ctx.interaction.created_at)},
    ]

    for attachment in msg.attachments:
        fields.append(
            {
                "name": "Attachment",
                "value": f"[`{attachment.filename}`]({attachment.url})",
            }
        )

    for embed in msg.embeds:
        if embed.image:
            fields.append({"name": "Embed", "value": f"[Image]({embed.image.url})"})

        if embed.thumbnail:
            fields.append(
                {"name": "Embed", "value": f"[Thumbnail]({embed.thumbnail.url})"}
            )

    for sticker in msg.stickers:
        fields.append(
            {"name": "Sticker", "value": f"[{sticker.name}]({sticker.image_url})"}
        )

    await ctx.client.rest.create_message(
        cfg.channels["moderators"],
        embed=Response(
            title="Reported Message",
            url=msg.make_link(msg.guild_id),
            color=Colors.DiscordYellow.value,
            description=None if not (content := msg.content) else f">>> {content}",
            fields=fields,
            author=await ExpandUser(msg.author, format=False),
            authorIcon=GetUserAvatar(msg.author),
            footer=f"Reported by {await ExpandUser(ctx.author, format=False)}",
            footerIcon=GetUserAvatar(ctx.author),
        ),
    )

    await ctx.respond(
        flags=MessageFlag.EPHEMERAL,
        embed=Response(
            color=Colors.DiscordGreen.value,
            description=f"Reported message {msg.make_link(msg.guild_id)} to the Moderators.",
            footer="Abuse of this feature will result in your removal from the server.",
        ),
    )


@plugin.set_error_handler
async def ErrorHandler(ctx: GatewayContext, error: Exception) -> None:
    """Handler for errors originating from the messages plugin."""

    await HookError(ctx, error)
