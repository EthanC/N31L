from typing import Any

import arc
from arc import GatewayClient, GatewayContext, GatewayPlugin
from hikari import (
    ButtonStyle,
    ComponentInteraction,
    DMMessageCreateEvent,
    Embed,
    GatewayBot,
    GuildMessageCreateEvent,
    InteractionCreateEvent,
    InteractionType,
    LazyIterator,
    Message,
    MessageFlag,
    PartialInteraction,
    ResponseType,
)
from hikari.files import Bytes
from loguru import logger
from urlextract import URLExtract  # type: ignore

from core.config import Config
from core.formatters import (
    Colors,
    expand_channel,
    expand_interaction,
    expand_server,
    expand_user,
    get_server_icon,
    get_user_avatar,
    log,
    response,
)
from core.hooks import hook_error
from core.utils import find_numbers, get, is_valid_user

plugin: GatewayPlugin = GatewayPlugin("logs")


@arc.loader
def extension_loader(client: GatewayClient) -> None:
    """Required. Called upon loading the extension."""

    logger.debug(f"Attempting to load {plugin.name} extension...")
    logger.trace(plugin)

    try:
        client.add_plugin(plugin)
    except Exception as e:
        logger.opt(exception=e).error(f"Failed to load {plugin.name} extension")


@plugin.listen()
async def event_direct_message(event: DMMessageCreateEvent) -> None:
    """Handler for notifying of direct messages."""

    bot: GatewayBot = plugin.client.get_type_dependency(GatewayBot)

    if not (n31l := bot.get_me()):
        raise RuntimeError("Bot user is null")

    if event.author_id == n31l.id:
        logger.debug("Direct Message command ignored, message author is N31L")

        return

    cfg: Config = plugin.client.get_type_dependency(Config)

    fields: list[dict[str, str | bool]] = []

    if attachments := event.message.attachments:
        for attachment in attachments:
            fields.append(
                {
                    "name": "Attachment",
                    "value": f"[`{attachment.filename}`]({attachment.url})",
                }
            )

    if stickers := event.message.stickers:
        for sticker in stickers:
            fields.append(
                {"name": "Sticker", "value": f"[{sticker.name}]({sticker.image_url})"}
            )

    logger.trace(fields)

    await plugin.client.rest.create_message(
        cfg.channels["production"],
        embed=response(
            title="Direct Message",
            color=Colors.N31L_GREEN,
            description=f">>> {event.content}" if event.content else None,
            fields=fields,
            author=await expand_user(event.author, format=False, show_id=False),
            authorIcon=get_user_avatar(event.author),
            footer=str(event.author_id),
            timestamp=event.message.timestamp,
        ),
    )

    logger.success(
        f"Notified of direct message from {await expand_user(event.author, format=False)}"
    )


@plugin.listen()
async def event_keyword(event: GuildMessageCreateEvent) -> None:
    """Handler for notifying of keyword mentions."""

    cfg: Config = plugin.client.get_type_dependency(Config)

    if not event.is_human:
        logger.trace("Ignored message creation event, author is not a human")

        return
    elif event.author.is_system:
        logger.trace("Ignored message creation event, author is system")

        return
    elif not event.content:
        logger.trace("Ignored message creation event, content is null")

        return
    elif event.channel_id in cfg.logs_ignore_channels:
        logger.trace("Ignored message creation event, channel is ignored")

        return

    words: list[str] = [word.lower() for word in event.content.split()]
    found: list[str] = []

    for keyword in cfg.logs_keywords:
        if keyword in words:
            found.append(keyword)

    if len(found) == 0:
        logger.trace("Ignored message creation event, no keywords found")

        return

    content: str = event.content

    for keyword in found:
        content = content.replace(keyword, f"**{keyword}**")

    logger.trace(content)

    fields: list[dict[str, str | bool]] = [
        {
            "name": "Channel",
            "value": await expand_channel(event.get_channel(), show_id=False),
        }
    ]

    if attachments := event.message.attachments:
        for attachment in attachments:
            fields.append(
                {
                    "name": "Attachment",
                    "value": f"[`{attachment.filename}`]({attachment.url})",
                }
            )

    if stickers := event.message.stickers:
        for sticker in stickers:
            fields.append(
                {"name": "Sticker", "value": f"[{sticker.name}]({sticker.image_url})"}
            )

    logger.trace(fields)

    actions = plugin.client.rest.build_message_action_row()

    actions.add_interactive_button(ButtonStyle.SECONDARY, "before", label="Context")
    actions.add_interactive_button(ButtonStyle.SECONDARY, "after", label="Aftermath")
    actions.add_interactive_button(ButtonStyle.SECONDARY, "dump", label="Dump")

    await plugin.client.rest.create_message(
        cfg.channels["production"],
        embed=response(
            title=("Keyword" if len(found) == 1 else "Keywords") + " Mention",
            url=event.message.make_link(event.guild_id),
            color=Colors.N31L_GREEN,
            description=f">>> {content}",
            fields=fields,
            author=await expand_user(event.author, format=False, show_id=False),
            authorIcon=get_user_avatar(event.author),
            footer=str(event.author_id),
            footerIcon=await get_server_icon(event.get_guild()),
            timestamp=event.message.timestamp,
        ),
        component=actions,
    )

    logger.success(
        f"Notified of keyword(s) ({', '.join(found)}) mention by {await expand_user(event.author, format=False)} in {await expand_server(event.get_guild(), format=False)} {await expand_channel(event.get_channel(), format=False)}"
    )


@plugin.listen()
async def event_mention(event: GuildMessageCreateEvent) -> None:
    """Handler for notifying of user mentions."""

    if not event.is_human:
        logger.trace("Ignored message creation event, author is not human")

        return
    elif not event.content:
        logger.trace("Ignored message creation event, content is null")

        return
    elif not event.message.user_mentions_ids:
        logger.trace("Ignored message creation event, no user mentions")

        return

    cfg: Config = plugin.client.get_type_dependency(Config)
    found: list[int] = []

    for userId in cfg.logs_mentions:
        if userId in event.message.user_mentions_ids:
            found.append(userId)

    if len(found) == 0:
        logger.trace("Ignored message creation event, no relevant user mentions")

        return

    fields: list[dict[str, str | bool]] = [
        {
            "name": "Channel",
            "value": await expand_channel(event.get_channel(), show_id=False),
        }
    ]

    if attachments := event.message.attachments:
        for attachment in attachments:
            fields.append(
                {
                    "name": "Attachment",
                    "value": f"[`{attachment.filename}`]({attachment.url})",
                }
            )

    if stickers := event.message.stickers:
        for sticker in stickers:
            fields.append(
                {"name": "Sticker", "value": f"[{sticker.name}]({sticker.image_url})"}
            )

    logger.trace(fields)

    actions = plugin.client.rest.build_message_action_row()

    actions.add_interactive_button(ButtonStyle.SECONDARY, "before", label="Context")
    actions.add_interactive_button(ButtonStyle.SECONDARY, "after", label="Aftermath")
    actions.add_interactive_button(ButtonStyle.SECONDARY, "dump", label="Dump")

    await plugin.client.rest.create_message(
        cfg.channels["production"],
        embed=response(
            title=("User" if len(found) == 1 else "Users") + " Mentioned",
            url=event.message.make_link(event.guild_id),
            color=Colors.N31L_GREEN,
            description=f">>> {event.content}",
            author=await expand_user(event.author, format=False, show_id=False),
            authorIcon=get_user_avatar(event.author),
            footer=str(event.author_id),
            footerIcon=await get_server_icon(event.get_guild()),
            timestamp=event.message.timestamp,
        ),
        component=actions,
    )

    logger.success(
        f"Notified of mention(s) ({found}) by {await expand_user(event.author, format=False)} in {await expand_server(event.get_guild(), format=False)} {await expand_channel(event.get_channel(), format=False)}"
    )


@plugin.listen()
async def event_context(event: InteractionCreateEvent) -> None:
    """Handler for the Context and Aftermath button commands."""

    interaction: PartialInteraction = event.interaction
    display_name: str = expand_interaction(interaction, format=False)

    if not interaction.type == InteractionType.MESSAGE_COMPONENT:
        logger.trace(f"Ignored {display_name}, expected MESSAGE_COMPONENT")

        return
    elif not isinstance(interaction, ComponentInteraction):
        logger.trace(f"Ignored {display_name}, expected ComponentInteraction")

        return
    elif not hasattr(interaction, "custom_id"):
        logger.trace(f"Ignored {display_name}, expected custom_id")

        return
    elif not (btnId := interaction.custom_id):
        logger.trace(f"Ignored {display_name}, custom_id is null")

        return
    elif (btnId != "before") and (btnId != "after"):
        logger.trace(f"Ignored {display_name}, expected custom_id before or after")

        return

    await interaction.create_initial_response(
        ResponseType.DEFERRED_MESSAGE_CREATE, flags=MessageFlag.EPHEMERAL
    )

    target: str = str(interaction.message.embeds[0].url)
    target_id: int = int(target.split("/")[-1])
    target_channel: int = int(target.split("/")[-2])

    context: LazyIterator[Message] | None = None

    if btnId == "before":
        context = event.app.rest.fetch_messages(target_channel, before=target_id)
    elif btnId == "after":
        context = event.app.rest.fetch_messages(target_channel, after=target_id)

    if not context:
        raise RuntimeError("context is null")

    # Discord limitation is 10 embeds
    # https://discord.com/developers/docs/resources/message#create-message-jsonform-params
    context = context.limit(10)

    # Reverse iterator to maintain chronological order
    if btnId == "before":
        context = context.reversed()

    logger.trace(context)

    results: list[Embed] = []

    try:
        for message in await context:
            logger.trace(message)

            fields: list[dict[str, str | bool]] = []

            if attachments := message.attachments:
                for attachment in attachments:
                    fields.append(
                        {
                            "name": "Attachment",
                            "value": f"[`{attachment.filename}`]({attachment.url})",
                        }
                    )

            if stickers := message.stickers:
                for sticker in stickers:
                    fields.append(
                        {
                            "name": "Sticker",
                            "value": f"[{sticker.name}]({sticker.image_url})",
                        }
                    )

            results.append(
                response(
                    color=Colors.DISCORD_BLURPLE,
                    description=f">>> {message.content}" if message.content else None,
                    fields=fields,
                    author=await expand_user(message.author, format=False),
                    authorIcon=get_user_avatar(message.author),
                    footer=str(message.id),
                    footerIcon=await get_server_icon(
                        message.guild_id, client=plugin.client
                    ),
                    timestamp=message.created_at
                    if not message.edited_timestamp
                    else message.edited_timestamp,
                )
            )
    except Exception as e:
        logger.opt(exception=e).error("Failed to fetch message(s) in context")

    if len(results) < 1:
        results.append(
            response(
                description=f"No context found {btnId} message.",
                color=Colors.DISCORD_YELLOW,
            )
        )

    logger.trace(results)

    await interaction.edit_initial_response(embeds=results)

    logger.success(
        f"Fetched context requested by {await expand_user(interaction.user, format=False)} in {await expand_server(interaction.get_guild(), format=False)} {await expand_channel(interaction.channel, format=False)}"
    )


@plugin.listen()
async def event_dump(event: InteractionCreateEvent) -> None:
    """Handler for the Dump button command."""

    interaction: PartialInteraction = event.interaction
    display_name: str = expand_interaction(interaction, format=False)

    if not interaction.type == InteractionType.MESSAGE_COMPONENT:
        logger.trace(f"Ignored {display_name}, expected MESSAGE_COMPONENT")

        return
    elif not isinstance(interaction, ComponentInteraction):
        logger.trace(f"Ignored {display_name}, expected ComponentInteraction")

        return
    elif not hasattr(interaction, "custom_id"):
        logger.trace(f"Ignored {display_name}, expected custom_id")

        return
    elif not (btnId := interaction.custom_id):
        logger.trace(f"Ignored {display_name}, custom_id is null")

        return
    elif btnId != "dump":
        logger.trace(f"Ignored {display_name}, expected custom_id dump")

        return

    await interaction.create_initial_response(
        ResponseType.DEFERRED_MESSAGE_CREATE, flags=MessageFlag.EPHEMERAL
    )

    target: str = str(interaction.message.embeds[0].url)
    target_id: int = int(target.split("/")[-1])
    target_channel: int = int(target.split("/")[-2])

    context: list[Message] = []
    before: LazyIterator[Message] = event.app.rest.fetch_messages(
        target_channel, before=target_id
    ).limit(100)
    after: LazyIterator[Message] = event.app.rest.fetch_messages(
        target_channel, after=target_id
    ).limit(100)

    try:
        # Reverse iterator to maintain chronological order
        for message in await before.reversed():
            context.append(message)
    except Exception as e:
        logger.opt(exception=e).error("Failed to fetch message(s) in context")

    try:
        for message in await after:
            context.append(message)
    except Exception as e:
        logger.opt(exception=e).error("Failed to fetch message(s) in context")

    logger.trace(context)

    result: str = ""

    for message in context:
        logger.trace(message)

        result += f"{await expand_user(message.author, format=False)}"
        result += f" at {message.timestamp}"

        if content := message.content:
            result += f"\n{content}"

        if attachments := message.attachments:
            for attachment in attachments:
                result += f"\n{attachment.url}"

        if stickers := message.stickers:
            for sticker in stickers:
                result += f"\n{sticker.image_url}"

        if embeds := message.embeds:
            for embed in embeds:
                result += f"\n{embed}"

        result += "\n\n"

    logger.trace(result)

    if result == "":
        await interaction.edit_initial_response(
            embed=response(
                description="No context found for message.",
                color=Colors.DISCORD_YELLOW,
            )
        )

        return

    await interaction.edit_initial_response(
        attachment=Bytes(result, f"dump_{target_id}.txt")
    )


@plugin.listen()
async def event_mirror(event: GuildMessageCreateEvent) -> None:
    """Handler for automatically mirroring Zeppelin log archives."""

    if event.is_human:
        logger.trace("Ignored message creation event, author is not a bot")

        return
    elif not event.content:
        logger.trace("Ignored message creation event, content is null")

        return

    bot: GatewayBot = plugin.client.get_type_dependency(GatewayBot)
    cfg: Config = plugin.client.get_type_dependency(Config)

    if not (n31l := bot.get_me()):
        raise RuntimeError("Bot user is null")

    if event.channel_id != cfg.channels["moderation"]:
        logger.trace("Ignored message creation event, channel is not desired")

        return
    elif event.author_id == n31l.id:
        logger.trace("Ignored message creation event, author is N31L")

        return

    for url in URLExtract().find_urls(event.content.lower(), True):
        if not isinstance(url, str):
            logger.debug(f"Skipping URL {url}, recieved {type(url)} expected string")

            continue

        if not url.startswith("https://api.zeppelin.gg/archives/"):
            continue

        data: dict[str, Any] | list[Any] | str | None = await get(url)

        if not data:
            logger.debug(f"Skipping URL {url}, data is null")

            continue
        elif not isinstance(data, str):
            logger.debug(f"Skipping URL {url}, expected string response")

            continue

        found: list[str] = []

        for line in data.splitlines():
            for find in find_numbers(line, 17, 19):
                if await is_valid_user(find, plugin.client):
                    found.append(f"`{find}`")

        # Ensure there are no duplicate users
        found: list[str] = list(set(found))

        result: str = f"Mirror of Zeppelin log archive <{url}>"

        if len(found) > 0:
            result += f" ({', '.join(found)})"

        result = log("mirror", result)
        filename: str = "archive"

        try:
            filename = url.split("/")[-1]
        except Exception as e:
            logger.opt(exception=e).warning(
                "Failed to determine Zeppelin log archive filename"
            )

        await plugin.client.rest.create_message(
            cfg.channels["moderation"],
            result,
            attachment=Bytes(data, f"{filename}.txt"),
            reply=event.message,
        )

        logger.success(f"Mirrored Zeppelin log archive {url}")


@plugin.set_error_handler
async def error_handler(ctx: GatewayContext, error: Exception) -> None:
    """Handler for errors originating from this plugin."""

    await hook_error(ctx, error)
