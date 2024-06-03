import arc
from arc import (
    AttachmentParams,
    AutodeferMode,
    GatewayClient,
    GatewayContext,
    GatewayPlugin,
    Option,
    SlashGroup,
    StrParams,
)
from hikari import Attachment, GatewayBot, Message, MessageFlag
from loguru import logger

from core.formatters import Colors, ExpandUser, Response
from core.hooks import HookError, HookLog

plugin: GatewayPlugin = GatewayPlugin("admin")
emoji: SlashGroup[GatewayClient] = plugin.include_slash_group(
    "emoji", "Commands to manage server emoji."
)
sticker: SlashGroup[GatewayClient] = plugin.include_slash_group(
    "sticker", "Commands to manage server stickers."
)


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
        raise RuntimeError("Bot user is null")

    if msg.author.id != n31l.id:
        logger.debug("Delete Message command ignored, message author is not N31L")

        await ctx.respond(
            flags=MessageFlag.EPHEMERAL,
            embed=Response(
                color=Colors.DiscordRed.value,
                description=f"Message author is not {n31l.mention}.",
            ),
        )

        return

    await msg.delete()

    await ctx.respond(
        flags=MessageFlag.EPHEMERAL,
        embed=Response(
            color=Colors.DiscordGreen.value,
            description=f"Deleted message from {msg.author.mention}.",
        ),
    )


@emoji.include
@arc.with_hook(arc.owner_only)
@arc.with_hook(HookLog)
@arc.slash_subcommand(
    "upload", "Upload an emoji to this server.", autodefer=AutodeferMode.EPHEMERAL
)
async def CommandEmojiUpload(
    ctx: GatewayContext,
    image: Option[Attachment, AttachmentParams("Choose an image for the emoji.")],
    name: Option[
        str | None,
        StrParams(
            "Enter a name for the emoji (image filename is default).", min_length=2
        ),
    ] = None,
) -> None:
    """Handler for the /emoji upload command."""

    if not name:
        name = image.filename.rsplit(".")[0]

    if not ctx.guild_id:
        raise RuntimeError("guild_id is null")

    await ctx.client.rest.create_emoji(
        ctx.guild_id,
        name,
        image.url,
        reason=f"Emoji uploaded by {ExpandUser(ctx.author, format=False)}.",
    )

    await ctx.respond(
        flags=MessageFlag.EPHEMERAL,
        embed=Response(
            color=Colors.DiscordGreen.value,
            description=f"Uploaded emoji `:{name}:`.",
        ),
    )


@emoji.include
@arc.with_hook(arc.owner_only)
@arc.with_hook(HookLog)
@arc.slash_subcommand(
    "delete", "Delete an emoji on this server.", autodefer=AutodeferMode.EPHEMERAL
)
async def CommandEmojiDelete(
    ctx: GatewayContext,
    emojiId: Option[str, StrParams("Enter the ID of the emoji.", name="id")],
) -> None:
    """Handler for the /emoji delete command."""

    if not ctx.guild_id:
        raise RuntimeError("guild_id is null")

    await ctx.client.rest.delete_emoji(
        ctx.guild_id,
        int(emojiId),
        reason=f"Emoji deleted by {ExpandUser(ctx.author, format=False)}.",
    )

    await ctx.respond(
        flags=MessageFlag.EPHEMERAL,
        embed=Response(
            color=Colors.DiscordGreen.value,
            description=f"Deleted emoji `:{emojiId}:`.",
        ),
    )


@sticker.include
@arc.with_hook(arc.owner_only)
@arc.with_hook(HookLog)
@arc.slash_subcommand(
    "upload", "Upload a sticker to this server.", autodefer=AutodeferMode.EPHEMERAL
)
async def CommandStickerUpload(
    ctx: GatewayContext,
    image: Option[Attachment, AttachmentParams("Choose an image for the sticker.")],
    related: Option[str, StrParams("Enter a related emoji for the sticker.")],
    name: Option[
        str | None,
        StrParams(
            "Enter a name for the sticker (image filename is default).", min_length=2
        ),
    ] = None,
) -> None:
    """Handler for the /sticker upload command."""

    if not name:
        name = image.filename.rsplit(".")[0].replace("_", " ")

    if not ctx.guild_id:
        raise RuntimeError("guild_id is null")

    await ctx.client.rest.create_sticker(
        ctx.guild_id,
        name,
        related,
        image.url,
        reason=f"Sticker uploaded by {ExpandUser(ctx.author, format=False)}.",
    )

    await ctx.respond(
        flags=MessageFlag.EPHEMERAL,
        embed=Response(
            color=Colors.DiscordGreen.value,
            description=f"Uploaded sticker `{name}`.",
        ),
    )


@sticker.include
@arc.with_hook(arc.owner_only)
@arc.with_hook(HookLog)
@arc.slash_subcommand(
    "delete", "Delete a sticker on this server.", autodefer=AutodeferMode.EPHEMERAL
)
async def CommandStickerDelete(
    ctx: GatewayContext,
    stickerId: Option[str, StrParams("Enter the ID of the sticker.", name="id")],
) -> None:
    """Handler for the /emoji delete command."""

    if not ctx.guild_id:
        raise RuntimeError("guild_id is null")

    await ctx.client.rest.delete_sticker(
        ctx.guild_id,
        int(stickerId),
        reason=f"Sticker deleted by {ExpandUser(ctx.author, format=False)}.",
    )

    await ctx.respond(
        flags=MessageFlag.EPHEMERAL,
        embed=Response(
            color=Colors.DiscordGreen.value,
            description=f"Deleted sticker `{stickerId}`.",
        ),
    )


@plugin.set_error_handler
async def ErrorHandler(ctx: GatewayContext, error: Exception) -> None:
    """Handler for errors originating from this plugin."""

    await HookError(ctx, error)
