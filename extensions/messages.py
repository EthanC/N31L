import arc
from arc import (
    AutodeferMode,
    GatewayClient,
    GatewayContext,
    GatewayPlugin,
)
from hikari import GatewayBot, Message, MessageFlag, MessageType, Permissions
from loguru import logger

from core.config import Config
from core.formatters import (
    Colors,
    ExpandChannel,
    ExpandServer,
    ExpandUser,
    GetAvatar,
    Response,
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
@arc.with_hook(arc.owner_only)
@arc.with_hook(HookLog)
@arc.message_command(
    "Delete Message", is_dm_enabled=True, autodefer=AutodeferMode.EPHEMERAL
)
async def CommandDelete(ctx: GatewayContext, msg: Message) -> None:
    """Handler for the Delete Message context menu command."""

    bot: GatewayBot = ctx.client.get_type_dependency(GatewayBot)

    if not (n31l := bot.get_me()):
        raise ValueError("Bot user is null")

    if msg.author.id != n31l.id:
        logger.debug("Delete Message command ignored, message author is not N31L")

        await ctx.respond(
            embed=Response(
                color=Colors.DiscordRed.value,
                description=f"Message author is not {n31l.mention}.",
            ),
            flags=MessageFlag.EPHEMERAL,
        )

        return

    await msg.delete()

    await ctx.respond(
        embed=Response(
            color=Colors.DiscordGreen.value,
            description=f"Deleted message from {msg.author.mention}.",
        ),
        flags=MessageFlag.EPHEMERAL,
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
            embed=Response(
                color=Colors.DiscordYellow.value,
                description=f"No User IDs found in the parsed [message]({msg.make_link(msg.guild_id)}).",
            ),
            flags=MessageFlag.EPHEMERAL,
        )

        return

    descriptor: str = "User IDs" if len(results) > 1 else "User ID"

    await ctx.respond(
        embed=Response(
            color=Colors.DiscordGreen.value,
            description=f"Found {len(results):,} {descriptor} in the parsed [message]({msg.make_link(msg.guild_id)})...",
        ),
        flags=MessageFlag.EPHEMERAL,
    )

    for result in results:
        await ctx.respond(str(result), flags=MessageFlag.EPHEMERAL)

    logger.success(
        f"Parsed {len(results):,} {descriptor} ({results}) from message {msg.id} in {ExpandServer(ctx.get_guild(), format=False)} {ExpandChannel(await msg.fetch_channel(), format=False)}"
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
            embed=Response(
                color=Colors.DiscordRed.value,
                description="You cannot report system messages.",
            ),
            flags=MessageFlag.EPHEMERAL,
        )

        return
    elif msg.type == MessageType.GUILD_MEMBER_JOIN:
        logger.debug("Report Message command ignored, reported welcome message")

        await ctx.respond(
            embed=Response(
                color=Colors.DiscordRed.value,
                description="You cannot report welcome messages.",
            ),
            flags=MessageFlag.EPHEMERAL,
        )

        return
    elif msg.author.id == ctx.author.id:
        logger.debug("Report Message command ignored, reported own message")

        await ctx.respond(
            embed=Response(
                color=Colors.DiscordRed.value,
                description=f"You cannot report your own [message]({msg.make_link(msg.guild_id)}).",
            ),
            flags=MessageFlag.EPHEMERAL,
        )

        return

    await ctx.client.rest.create_message(
        cfg.channels["moderators"],
        embed=Response(
            title="Reported Message",
            url=msg.make_link(msg.guild_id),
            color=Colors.DiscordYellow.value,
            description=None if not (content := msg.content) else f">>> {content}",
            author=ExpandUser(msg.author, format=False),
            authorIcon=GetAvatar(msg.author),
            footer=f"Reported by {ExpandUser(ctx.author, format=False)}",
            footerIcon=GetAvatar(ctx.author),
        ),
    )

    await ctx.respond(
        embed=Response(
            color=Colors.DiscordGreen.value,
            description=f"Reported [message]({msg.make_link(msg.guild_id)}) to the Moderators.",
            footer="Abuse of this feature will result in your removal from the server.",
        ),
        flags=MessageFlag.EPHEMERAL,
    )


@plugin.set_error_handler
async def ErrorHandler(ctx: GatewayContext, error: Exception) -> None:
    """Handler for errors originating from the messages plugin."""

    await HookError(ctx, error)
