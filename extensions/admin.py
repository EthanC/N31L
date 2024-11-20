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
    UserParams,
)
from hikari import (
    UNDEFINED,
    Attachment,
    Bytes,
    GatewayBot,
    GatewayGuild,
    Member,
    Message,
    MessageFlag,
    Permissions,
    User,
)
from hikari.files import Bytes
from loguru import logger

from core.config import Config
from core.formatters import (
    Colors,
    EmbedsFromJSON,
    ExpandChannel,
    ExpandServer,
    ExpandUser,
    Response,
)
from core.hooks import HookError, HookLog
from core.sounds import IW7N31LDeath, T6FBIKick

plugin: GatewayPlugin = GatewayPlugin("admin")
emoji: SlashGroup[GatewayClient] = plugin.include_slash_group(
    "emoji", "Commands to manage server emoji."
)
sticker: SlashGroup[GatewayClient] = plugin.include_slash_group(
    "sticker", "Commands to manage server stickers."
)
vip: SlashGroup[GatewayClient] = plugin.include_slash_group(
    "vip", "Commands to manage server VIPs."
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
@arc.with_hook(arc.has_permissions(Permissions.MANAGE_GUILD))
@arc.with_hook(HookLog)
@arc.slash_command(
    "send",
    "Send a message from N31L.",
    autodefer=AutodeferMode.EPHEMERAL,
)
async def CommandSend(
    ctx: GatewayContext,
    channelId: Option[
        str, StrParams("Enter the ID of the channel.", name="channel_id")
    ],
    content: Option[str | None, StrParams("Enter the message content.")] = None,
    markdown: Option[
        Attachment | None,
        AttachmentParams(
            "Choose a file containing markdown content (content will be overriden.)"
        ),
    ] = None,
    embeds: Option[
        Attachment | None,
        AttachmentParams(
            "Choose a JSON file containing embed data (glitchii.github.io/embedbuilder)."
        ),
    ] = None,
    file: Option[
        Attachment | None,
        AttachmentParams("Choose a file to attach.", name="attachment"),
    ] = None,
    reply: Option[
        str | None,
        StrParams("Enter the Message ID to reply to.", name="reply_message_id"),
    ] = None,
) -> None:
    """Handler for the /send command."""

    if (not content) and (not markdown) and (not embeds) and (not file):
        logger.debug("Send Message command ignored, no message provided")

        await ctx.respond(
            flags=MessageFlag.EPHEMERAL,
            embed=Response(
                color=Colors.DiscordRed.value,
                description="No message provided.",
            ),
        )

        return
    elif (markdown) and (not markdown.filename.endswith(".md")):
        logger.debug("Send Message command ignored, invalid markdown provided")
        logger.trace(f"{markdown=}")

        await ctx.respond(
            flags=MessageFlag.EPHEMERAL,
            embed=Response(
                color=Colors.DiscordRed.value,
                description="Provided markdown file is not valid.",
            ),
        )

        return
    elif (embeds) and (not embeds.filename.endswith(".json")):
        logger.debug("Send Message command ignored, invalid embeds JSON provided")
        logger.trace(f"{embeds=}")

        await ctx.respond(
            flags=MessageFlag.EPHEMERAL,
            embed=Response(
                color=Colors.DiscordRed.value,
                description="Provided embeds file is not valid JSON. Use the [Embed Builder](https://glitchii.github.io/embedbuilder/).",
            ),
        )

        return

    if markdown:
        # Provided markdown file overrides provided content
        content = (await markdown.read()).decode("UTF-8")

    result: Message = await ctx.client.rest.create_message(
        int(channelId),
        content,
        attachment=file if file else UNDEFINED,
        embeds=await EmbedsFromJSON(embeds) if embeds else UNDEFINED,
        reply=int(reply) if reply else UNDEFINED,
    )

    await ctx.respond(
        flags=MessageFlag.EPHEMERAL,
        embed=Response(
            color=Colors.DiscordGreen.value,
            description=f"Sent message {result.make_link(result.guild_id)}.",
        ),
    )


@plugin.include
@arc.with_hook(arc.has_permissions(Permissions.MANAGE_GUILD))
@arc.with_hook(HookLog)
@arc.slash_command(
    "edit",
    "Edit a message sent by N31L.",
    autodefer=AutodeferMode.EPHEMERAL,
)
async def CommandEdit(
    ctx: GatewayContext,
    channelId: Option[
        str, StrParams("Enter the ID of the channel.", name="channel_id")
    ],
    messageId: Option[
        str, StrParams("Enter the ID of the message.", name="message_id")
    ],
    content: Option[
        str | None, StrParams("Enter text to replace the message content with.")
    ] = None,
    markdown: Option[
        Attachment | None,
        AttachmentParams(
            "Choose a file containing markdown to replace the message content with (content will be overriden.)"
        ),
    ] = None,
    embeds: Option[
        Attachment | None,
        AttachmentParams(
            "Choose a JSON file containing embeds to replace the embeds with (glitchii.github.io/embedbuilder)."
        ),
    ] = None,
    file: Option[
        Attachment | None,
        AttachmentParams("Choose a file to attach to the message.", name="attachment"),
    ] = None,
) -> None:
    """Handler for the /edit command."""

    if (not content) and (not markdown) and (not embeds) and (not file):
        logger.debug("Edit Message command ignored, no message provided")

        await ctx.respond(
            flags=MessageFlag.EPHEMERAL,
            embed=Response(
                color=Colors.DiscordRed.value,
                description="No message provided.",
            ),
        )

        return
    elif (markdown) and (not markdown.filename.endswith(".md")):
        logger.debug("Send Message command ignored, invalid markdown provided")
        logger.trace(f"{markdown=}")

        await ctx.respond(
            flags=MessageFlag.EPHEMERAL,
            embed=Response(
                color=Colors.DiscordRed.value,
                description="Provided markdown file is not valid.",
            ),
        )

        return
    elif (embeds) and (not embeds.filename.endswith(".json")):
        logger.debug("Send Message command ignored, invalid embeds JSON provided")
        logger.trace(f"{embeds=}")

        await ctx.respond(
            flags=MessageFlag.EPHEMERAL,
            embed=Response(
                color=Colors.DiscordRed.value,
                description="Provided embeds file is not valid JSON. Use the [Embed Builder](https://glitchii.github.io/embedbuilder/).",
            ),
        )

        return

    bot: GatewayBot = ctx.client.get_type_dependency(GatewayBot)

    if not (n31l := bot.get_me()):
        raise RuntimeError("Bot user is null")

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

    if msg.author.id != n31l.id:
        logger.debug("Edit Message command ignored, message author is not N31L")

        await ctx.respond(
            flags=MessageFlag.EPHEMERAL,
            embed=Response(
                color=Colors.DiscordRed.value,
                description=f"Message author is not {n31l.mention}.",
            ),
        )

        return

    before: str = "[Empty]"
    after: str = "[Empty]"

    if content:
        after = content
    elif markdown:
        # Provided markdown file overrides provided content
        after = (await markdown.read()).decode("UTF-8")

    if msg.content:
        before = msg.content

    await msg.edit(after, attachment=file, embeds=await EmbedsFromJSON(embeds))

    await ctx.respond(
        flags=MessageFlag.EPHEMERAL,
        embed=Response(
            color=Colors.DiscordGreen.value,
            description=f"Edited {msg.author.mention}'s message {msg.make_link(msg.guild_id)}.\n\n**Before:**\n```md\n{before}\n```\n**After:**\n```md\n{after}\n```",
        ),
    )


@plugin.include
@arc.with_hook(arc.has_permissions(Permissions.MANAGE_GUILD))
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
                description=f"Message {msg.make_link(msg.guild_id)} author is not {n31l.mention}.",
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
        reason=f"Emoji uploaded by {await ExpandUser(ctx.author, format=False)}.",
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
        reason=f"Emoji deleted by {await ExpandUser(ctx.author, format=False)}.",
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
        reason=f"Sticker uploaded by {await ExpandUser(ctx.author, format=False)}.",
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
        reason=f"Sticker deleted by {await ExpandUser(ctx.author, format=False)}.",
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


@vip.include
@arc.with_hook(arc.owner_only)
@arc.with_hook(HookLog)
@arc.slash_subcommand("add", "Add a user to the server VIP list.")
async def CommandVIPAdd(
    ctx: GatewayContext,
    user: Option[User, UserParams("Choose a user to add to the server VIP list.")],
) -> None:
    """Handler for the /vip add command."""

    server: GatewayGuild | None = ctx.get_guild()

    if not server:
        raise RuntimeError(
            f"guild {await ExpandServer(ctx.guild_id, format=False)} is null"
        )

    member: Member | None = server.get_member(user.id)

    if not member:
        raise RuntimeError(
            f"member {await ExpandUser(user, format=False)} in guild {await ExpandServer(ctx.guild_id, format=False)} is null"
        )

    cfg: Config = plugin.client.get_type_dependency(Config)

    await member.add_role(
        cfg.rolesVIP,
        reason=f"Requested by {await ExpandUser(ctx.author, format=False)}",
    )

    await ctx.respond(attachment=Bytes(IW7N31LDeath(), "add.mp3"))


@vip.include
@arc.with_hook(arc.owner_only)
@arc.with_hook(HookLog)
@arc.slash_subcommand("remove", "Remove a user from the server VIP list.")
async def CommandVIPRemove(
    ctx: GatewayContext,
    user: Option[User, UserParams("Choose a user to remove from the server VIP list.")],
) -> None:
    """Handler for the /vip remove command."""

    server: GatewayGuild | None = ctx.get_guild()

    if not server:
        raise RuntimeError(
            f"guild {await ExpandServer(ctx.guild_id, format=False)} is null"
        )

    member: Member | None = server.get_member(user.id)

    if not member:
        raise RuntimeError(
            f"member {await ExpandUser(user, format=False)} in guild {await ExpandServer(ctx.guild_id, format=False)} is null"
        )

    cfg: Config = plugin.client.get_type_dependency(Config)

    await member.remove_role(
        cfg.rolesVIP,
        reason=f"Requested by {await ExpandUser(ctx.author, format=False)}",
    )

    await ctx.respond(attachment=Bytes(T6FBIKick(), "kick.mp3"))
