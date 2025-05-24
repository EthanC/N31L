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
    ApplicationContextType,
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
    expand_channel,
    expand_server,
    expand_user,
    json_to_embed,
    response,
)
from core.hooks import hook_error, hook_log
from core.sounds import iw7_n31l_death, t6_fbi_kick

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
def extension_loader(client: GatewayClient) -> None:
    """Required. Called upon loading the extension."""

    logger.debug(f"Attempting to load {plugin.name} extension...")
    logger.trace(plugin)

    try:
        client.add_plugin(plugin)
    except Exception as e:
        logger.opt(exception=e).error(f"Failed to load {plugin.name} extension")


@plugin.include
@arc.with_hook(arc.has_permissions(Permissions.MANAGE_GUILD))
@arc.with_hook(hook_log)
@arc.slash_command(
    "send",
    "Send a message from N31L.",
    autodefer=AutodeferMode.EPHEMERAL,
)
async def command_send(
    ctx: GatewayContext,
    channel_id: Option[str, StrParams("Enter the ID of the channel.")],
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
    reply_message_id: Option[
        str | None,
        StrParams("Enter the Message ID to reply to."),
    ] = None,
) -> None:
    """Handler for the /send command."""

    if (markdown) and (not markdown.filename.endswith(".md")):
        logger.debug("Send Message command ignored, invalid markdown provided")
        logger.trace(f"{markdown=}")

        await ctx.respond(
            flags=MessageFlag.EPHEMERAL,
            embed=response(
                color=Colors.DISCORD_RED,
                description="Provided markdown file is not valid.",
            ),
        )

        return
    elif (embeds) and (not embeds.filename.endswith(".json")):
        logger.debug("Send Message command ignored, invalid embeds JSON provided")
        logger.trace(f"{embeds=}")

        await ctx.respond(
            flags=MessageFlag.EPHEMERAL,
            embed=response(
                color=Colors.DISCORD_RED,
                description="Provided embeds file is not valid JSON. Use the [Embed Builder](https://glitchii.github.io/embedbuilder/).",
            ),
        )

        return

    if markdown:
        # Provided markdown file overrides provided content
        content = (await markdown.read()).decode("UTF-8")

    result: Message = await ctx.client.rest.create_message(
        int(channel_id),
        content,
        attachment=file if file else UNDEFINED,
        embeds=await json_to_embed(embeds) if embeds else UNDEFINED,
        reply=int(reply_message_id) if reply_message_id else UNDEFINED,
    )

    await ctx.respond(
        flags=MessageFlag.EPHEMERAL,
        embed=response(
            color=Colors.DISCORD_GREEN,
            description=f"Sent message {result.make_link(result.guild_id)}.",
        ),
    )


@plugin.include
@arc.with_hook(arc.has_permissions(Permissions.MANAGE_GUILD))
@arc.with_hook(hook_log)
@arc.slash_command(
    "edit",
    "Edit a message sent by N31L.",
    autodefer=AutodeferMode.EPHEMERAL,
)
async def command_edit(
    ctx: GatewayContext,
    channel_id: Option[str, StrParams("Enter the ID of the channel.")],
    message_id: Option[str, StrParams("Enter the ID of the message.")],
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
            embed=response(
                color=Colors.DISCORD_RED,
                description="No message provided.",
            ),
        )

        return
    elif (markdown) and (not markdown.filename.endswith(".md")):
        logger.debug("Send Message command ignored, invalid markdown provided")
        logger.trace(f"{markdown=}")

        await ctx.respond(
            flags=MessageFlag.EPHEMERAL,
            embed=response(
                color=Colors.DISCORD_RED,
                description="Provided markdown file is not valid.",
            ),
        )

        return
    elif (embeds) and (not embeds.filename.endswith(".json")):
        logger.debug("Send Message command ignored, invalid embeds JSON provided")
        logger.trace(f"{embeds=}")

        await ctx.respond(
            flags=MessageFlag.EPHEMERAL,
            embed=response(
                color=Colors.DISCORD_RED,
                description="Provided embeds file is not valid JSON. Use the [Embed Builder](https://glitchii.github.io/embedbuilder/).",
            ),
        )

        return

    bot: GatewayBot = ctx.client.get_type_dependency(GatewayBot)

    if not (n31l := bot.get_me()):
        raise RuntimeError("Bot user is null")

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

    if msg.author.id != n31l.id:
        logger.debug("Edit Message command ignored, message author is not N31L")

        await ctx.respond(
            flags=MessageFlag.EPHEMERAL,
            embed=response(
                color=Colors.DISCORD_RED,
                description=f"Message author is not {n31l.mention}.",
            ),
        )

        return

    await msg.edit(
        content if content else markdown if markdown else UNDEFINED,
        attachment=file if file else UNDEFINED,
        embeds=await json_to_embed(embeds) if embeds else UNDEFINED,
    )

    before: str = "[Empty]"
    after: str = "[Empty]"

    if content:
        after = content
    elif markdown:
        # Provided markdown file overrides provided content
        after = (await markdown.read()).decode("UTF-8")

    if msg.content:
        before = msg.content

    await ctx.respond(
        flags=MessageFlag.EPHEMERAL,
        embed=response(
            color=Colors.DISCORD_GREEN,
            description=f"Edited {msg.author.mention}'s message {msg.make_link(msg.guild_id)}.\n\n**Before:**\n```md\n{before}\n```\n**After:**\n```md\n{after}\n```",
        ),
    )


@plugin.include
@arc.with_hook(arc.has_permissions(Permissions.MANAGE_GUILD))
@arc.with_hook(hook_log)
@arc.message_command(
    "Delete Message",
    autodefer=AutodeferMode.EPHEMERAL,
    invocation_contexts=[ApplicationContextType.GUILD, ApplicationContextType.BOT_DM],
)
async def command_delete(ctx: GatewayContext, msg: Message) -> None:
    """Handler for the Delete Message context menu command."""

    bot: GatewayBot = ctx.client.get_type_dependency(GatewayBot)

    if not (n31l := bot.get_me()):
        raise RuntimeError("Bot user is null")

    if msg.author.id != n31l.id:
        logger.debug("Delete Message command ignored, message author is not N31L")

        await ctx.respond(
            flags=MessageFlag.EPHEMERAL,
            embed=response(
                color=Colors.DISCORD_RED,
                description=f"Message {msg.make_link(msg.guild_id)} author is not {n31l.mention}.",
            ),
        )

        return

    await msg.delete()

    await ctx.respond(
        flags=MessageFlag.EPHEMERAL,
        embed=response(
            color=Colors.DISCORD_GREEN,
            description=f"Deleted message from {msg.author.mention}.",
        ),
    )


@emoji.include
@arc.with_hook(arc.owner_only)
@arc.with_hook(hook_log)
@arc.slash_subcommand(
    "upload", "Upload an emoji in a server.", autodefer=AutodeferMode.EPHEMERAL
)
async def command_emoji_upload(
    ctx: GatewayContext,
    image: Option[Attachment, AttachmentParams("Choose an image for the emoji.")],
    name: Option[
        str | None,
        StrParams(
            "Enter a name for the emoji (image filename is default).", min_length=2
        ),
    ] = None,
    server_id: Option[
        str | None, StrParams("Enter a server ID (current server is default).")
    ] = None,
) -> None:
    """Handler for the /emoji upload command."""

    if not name:
        name = image.filename.rsplit(".")[0]

    if not ctx.guild_id:
        raise RuntimeError("guild_id is null")

    await ctx.client.rest.create_emoji(
        int(server_id) if server_id else ctx.guild_id,
        name,
        image.url,
        reason=f"Emoji uploaded by {await expand_user(ctx.author, format=False)}.",
    )

    await ctx.respond(
        flags=MessageFlag.EPHEMERAL,
        embed=response(
            color=Colors.DISCORD_GREEN,
            description=f"Uploaded emoji `:{name}:`.",
        ),
    )


@emoji.include
@arc.with_hook(arc.owner_only)
@arc.with_hook(hook_log)
@arc.slash_subcommand(
    "delete", "Delete an emoji in a server.", autodefer=AutodeferMode.EPHEMERAL
)
async def command_emoji_delete(
    ctx: GatewayContext,
    emoji_id: Option[str, StrParams("Enter the ID of the emoji.")],
    server_id: Option[
        str | None, StrParams("Enter a server ID (current server is default).")
    ] = None,
) -> None:
    """Handler for the /emoji delete command."""

    if not ctx.guild_id:
        raise RuntimeError("guild_id is null")

    await ctx.client.rest.delete_emoji(
        int(server_id) if server_id else ctx.guild_id,
        int(emoji_id),
        reason=f"Emoji deleted by {await expand_user(ctx.author, format=False)}.",
    )

    await ctx.respond(
        flags=MessageFlag.EPHEMERAL,
        embed=response(
            color=Colors.DISCORD_GREEN,
            description=f"Deleted emoji `:{emoji_id}:`.",
        ),
    )


@emoji.include
@arc.with_hook(arc.owner_only)
@arc.with_hook(hook_log)
@arc.slash_subcommand(
    "rename", "Rename an emoji in a server.", autodefer=AutodeferMode.EPHEMERAL
)
async def command_emoji_rename(
    ctx: GatewayContext,
    emoji_id: Option[str, StrParams("Enter the ID of the emoji.")],
    emoji_name: Option[str, StrParams("Enter a new name for the emoji.")],
    server_id: Option[
        str | None, StrParams("Enter a server ID (current server is default).")
    ] = None,
) -> None:
    """Handler for the /emoji rename command."""

    if not ctx.guild_id:
            raise RuntimeError("guild_id is null")

    await ctx.client.rest.edit_emoji(
        int(server_id) if server_id else ctx.guild_id,
        int(emoji_id),
        name=emoji_name,
        reason=f"Emoji renamed by {await expand_user(ctx.author, format=False)}.",
    )

    await ctx.respond(
        flags=MessageFlag.EPHEMERAL,
        embed=response(
            color=Colors.DISCORD_GREEN,
            description=f"Renamed emoji to `:{emoji_name}:`.",
        ),
    )


@sticker.include
@arc.with_hook(arc.owner_only)
@arc.with_hook(hook_log)
@arc.slash_subcommand(
    "upload", "Upload a sticker in a server.", autodefer=AutodeferMode.EPHEMERAL
)
async def command_sticker_upload(
    ctx: GatewayContext,
    image: Option[Attachment, AttachmentParams("Choose an image for the sticker.")],
    related: Option[str, StrParams("Enter a related emoji for the sticker.")],
    name: Option[
        str | None,
        StrParams(
            "Enter a name for the sticker (image filename is default).", min_length=2
        ),
    ] = None,
    server_id: Option[
        str | None, StrParams("Enter a server ID (current server is default).")
    ] = None,
) -> None:
    """Handler for the /sticker upload command."""

    if not name:
        name = image.filename.rsplit(".")[0].replace("_", " ")

    if not ctx.guild_id:
        raise RuntimeError("guild_id is null")

    await ctx.client.rest.create_sticker(
        int(server_id) if server_id else ctx.guild_id,
        name,
        related,
        image.url,
        reason=f"Sticker uploaded by {await expand_user(ctx.author, format=False)}.",
    )

    await ctx.respond(
        flags=MessageFlag.EPHEMERAL,
        embed=response(
            color=Colors.DISCORD_GREEN,
            description=f"Uploaded sticker `{name}`.",
        ),
    )


@sticker.include
@arc.with_hook(arc.owner_only)
@arc.with_hook(hook_log)
@arc.slash_subcommand(
    "delete", "Delete a sticker in a server.", autodefer=AutodeferMode.EPHEMERAL
)
async def command_sticker_delete(
    ctx: GatewayContext,
    sticker_id: Option[str, StrParams("Enter the ID of the sticker.")],
    server_id: Option[
        str | None, StrParams("Enter a server ID (current server is default).")
    ] = None,
) -> None:
    """Handler for the /emoji delete command."""

    if not ctx.guild_id:
        raise RuntimeError("guild_id is null")

    await ctx.client.rest.delete_sticker(
        int(server_id) if server_id else ctx.guild_id,
        int(sticker_id),
        reason=f"Sticker deleted by {await expand_user(ctx.author, format=False)}.",
    )

    await ctx.respond(
        flags=MessageFlag.EPHEMERAL,
        embed=response(
            color=Colors.DISCORD_GREEN,
            description=f"Deleted sticker `{sticker_id}`.",
        ),
    )


@plugin.set_error_handler
async def ErrorHandler(ctx: GatewayContext, error: Exception) -> None:
    """Handler for errors originating from this plugin."""

    await hook_error(ctx, error)


@vip.include
@arc.with_hook(arc.owner_only)
@arc.with_hook(hook_log)
@arc.slash_subcommand("add", "Add a user to the server VIP list.")
async def command_vip_add(
    ctx: GatewayContext,
    user: Option[User, UserParams("Choose a user to add to the server VIP list.")],
) -> None:
    """Handler for the /vip add command."""

    server: GatewayGuild | None = ctx.get_guild()

    if not server:
        raise RuntimeError(
            f"guild {await expand_server(ctx.guild_id, format=False)} is null"
        )

    member: Member | None = server.get_member(user.id)

    if not member:
        raise RuntimeError(
            f"member {await expand_user(user, format=False)} in guild {await expand_server(ctx.guild_id, format=False)} is null"
        )

    cfg: Config = plugin.client.get_type_dependency(Config)

    await member.add_role(
        cfg.roles_vip,
        reason=f"Requested by {await expand_user(ctx.author, format=False)}",
    )

    await ctx.respond(attachment=Bytes(iw7_n31l_death(), "add.mp3"))


@vip.include
@arc.with_hook(arc.owner_only)
@arc.with_hook(hook_log)
@arc.slash_subcommand("remove", "Remove a user from the server VIP list.")
async def command_vip_remove(
    ctx: GatewayContext,
    user: Option[User, UserParams("Choose a user to remove from the server VIP list.")],
) -> None:
    """Handler for the /vip remove command."""

    server: GatewayGuild | None = ctx.get_guild()

    if not server:
        raise RuntimeError(
            f"guild {await expand_server(ctx.guild_id, format=False)} is null"
        )

    member: Member | None = server.get_member(user.id)

    if not member:
        raise RuntimeError(
            f"member {await expand_user(user, format=False)} in guild {await expand_server(ctx.guild_id, format=False)} is null"
        )

    cfg: Config = plugin.client.get_type_dependency(Config)

    await member.remove_role(
        cfg.roles_vip,
        reason=f"Requested by {await expand_user(ctx.author, format=False)}",
    )

    await ctx.respond(attachment=Bytes(t6_fbi_kick(), "kick.mp3"))
