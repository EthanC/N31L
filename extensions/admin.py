"""Module containing the admin command handler."""

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

plugin: GatewayPlugin = GatewayPlugin("admin")


@arc.loader
def extension_loader(client: GatewayClient) -> None:
    """Load this extension."""
    logger.debug(f"Attempting to load {plugin.name} extension...")
    logger.trace(plugin)

    try:
        client.add_plugin(plugin)
    except Exception as e:
        logger.opt(exception=e).error(f"Failed to load {plugin.name} extension")


@plugin.include  # ty:ignore[invalid-argument-type]
@arc.with_hook(arc.has_permissions(Permissions.MANAGE_GUILD))
@arc.with_hook(hook_log)
@arc.slash_command(
    "send", "Send a message from N31L.", autodefer=AutodeferMode.EPHEMERAL
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
        str | None, StrParams("Enter the Message ID to reply to.")
    ] = None,
) -> None:
    """Handle the /send command."""
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


@plugin.include  # ty:ignore[invalid-argument-type]
@arc.with_hook(arc.has_permissions(Permissions.MANAGE_GUILD))
@arc.with_hook(hook_log)
@arc.slash_command(
    "edit", "Edit a message sent by N31L.", autodefer=AutodeferMode.EPHEMERAL
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
    """Handle the /edit command."""
    if (not content) and (not markdown) and (not embeds) and (not file):
        logger.debug("Edit Message command ignored, no message provided")

        await ctx.respond(
            flags=MessageFlag.EPHEMERAL,
            embed=response(
                color=Colors.DISCORD_RED, description="No message provided."
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


@plugin.include  # ty:ignore[invalid-argument-type]
@arc.with_hook(arc.has_permissions(Permissions.MANAGE_GUILD))
@arc.with_hook(hook_log)
@arc.message_command(
    "Delete Message",
    autodefer=AutodeferMode.EPHEMERAL,
    invocation_contexts=[ApplicationContextType.GUILD, ApplicationContextType.BOT_DM],
)
async def command_delete(ctx: GatewayContext, msg: Message) -> None:
    """Handle the Delete Message context menu command."""
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


@plugin.set_error_handler
async def ErrorHandler(ctx: GatewayContext, error: Exception) -> None:
    """Handle errors originating from this plugin."""
    await hook_error(ctx, error)
