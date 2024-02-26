from datetime import datetime
from os import environ
from typing import Any

import tanjun
from hikari import (
    GatewayBot,
    GuildMessageCreateEvent,
    GuildTextChannel,
    GuildThreadChannel,
    InteractionChannel,
    Member,
    MessageType,
    Permissions,
    StickerFormatType,
)
from hikari.messages import Message
from loguru import logger
from tanjun import Component
from tanjun.abc import MenuContext, SlashContext
from tanjun.commands import SlashCommandGroup

from helpers import Responses, Timestamps, Utility

component: Component = Component(name="Messages")

parse: SlashCommandGroup = component.with_slash_command(
    tanjun.slash_command_group("parse", "Slash Commands to parse messages.")
)


@component.with_schedule
@tanjun.as_interval(300)
async def TaskArchiveThreads(
    config: dict[str, Any] = tanjun.inject(type=dict[str, Any]),
    bot: GatewayBot = tanjun.inject(type=GatewayBot),
) -> None:
    """Automatically archive threads in the configured channels."""

    if not config["archiveThreads"]["enable"]:
        return

    logger.info("Beginning recurring task to archive threads...")

    lifetime: int = config["archiveThreads"]["lifetime"]
    threads: list[GuildThreadChannel] = await bot.rest.fetch_active_threads(
        int(environ.get("DISCORD_SERVER_ID"))
    )

    for thread in threads:
        if thread.parent_id not in config["archiveThreads"]["channels"]:
            continue
        elif thread.is_archived:
            continue
        elif Utility.Elapsed(datetime.now(), thread.created_at) < lifetime:
            continue
        elif await Utility.UserHasRole(
            thread.owner_id,
            config["archiveThreads"]["immuneRoles"],
            thread.guild_id,
            bot,
        ):
            continue

        await bot.rest.edit_channel(thread.id, archived=True)

        logger.success(
            f"Archived thread {Responses.ExpandThread(thread, False)} as it exceeded the maximum lifespan"
        )

        await bot.rest.create_message(
            config["channels"]["threads"],
            Responses.Log(
                "thread",
                f"Archived thread {Responses.ExpandThread(thread)} with reason: *Maximum lifespan exceeded*",
            ),
        )


@component.with_listener(GuildMessageCreateEvent)
async def EventShadowban(
    ctx: GuildMessageCreateEvent,
    config: dict[str, Any] = tanjun.inject(type=dict[str, Any]),
) -> None:
    """Silently delete user messages in the configured channels."""

    if not config["shadowban"]["enable"]:
        return
    elif ctx.author.id not in config["shadowban"]["users"]:
        return
    elif ctx.message.channel_id not in config["shadowban"]["channels"]:
        return

    try:
        await ctx.message.delete()
    except Exception as e:
        logger.opt(exception=e).error(
            f"Failed to enforce shadowban for {Responses.ExpandUser(ctx.author, False)} in {Responses.ExpandGuild(ctx.get_guild(), False)} {Responses.ExpandChannel(ctx.get_channel(), False)}"
        )

        return

    logger.success(
        f"Enforced shadowban for {Responses.ExpandUser(ctx.author, False)} in {Responses.ExpandGuild(ctx.get_guild(), False)} {Responses.ExpandChannel(ctx.get_channel(), False)}"
    )


@component.with_menu_command()
@tanjun.with_own_permission_check(Permissions.SEND_MESSAGES)
@tanjun.as_message_menu("Report Message", default_to_ephemeral=True)
async def CommandReport(
    ctx: MenuContext,
    message: Message,
    config: dict[str, Any] = tanjun.inject(type=dict[str, Any]),
) -> None:
    """Handler for the Report to Moderators message command."""

    if message.author.is_system:
        await ctx.respond(
            embed=Responses.Fail(description="You cannot report system messages.")
        )

        return
    elif message.type == MessageType.GUILD_MEMBER_JOIN:
        await ctx.respond(
            embed=Responses.Fail(description="You cannot report welcome messages.")
        )

        return

    imageUrl: str | None = None
    fields: list[dict[str, Any]] = [
        {"name": "Channel", "value": f"<#{message.channel_id}>"},
        {"name": "Sent", "value": Timestamps.Relative(message.created_at)},
        {"name": "Reported", "value": Timestamps.Relative(ctx.created_at)},
    ]

    if (attachments := message.attachments) is not None:
        for attachment in attachments:
            if imageUrl is None:
                if attachment.media_type.startswith("image/"):
                    imageUrl = attachment.url

                    continue

            fields.append(
                {
                    "name": "Attachment",
                    "value": f"[`{attachment.filename}`]({attachment.url})",
                }
            )

    if (stickers := message.stickers) is not None:
        for sticker in stickers:
            if imageUrl is None:
                if sticker.format_type != StickerFormatType.LOTTIE:
                    imageUrl = sticker.image_url

                    continue

            fields.append(
                {"name": "Sticker", "value": f"[{sticker.name}]({sticker.image_url})"}
            )

    await ctx.rest.create_message(
        config["channels"]["moderators"],
        embed=Responses.Warning(
            title="Message Reported",
            url=f"https://discord.com/channels/{ctx.guild_id}/{message.channel_id}/{message.id}",
            description=None
            if (content := message.content) is None
            else f">>> {content}",
            fields=fields,
            author=Responses.ExpandUser(message.author, False),
            authorIcon=message.author.default_avatar_url
            if (avatar := message.author.avatar_url) is None
            else avatar,
            image=imageUrl,
            footer=f"Reported by {Responses.ExpandUser(ctx.author, False)}",
            footerIcon=ctx.author.default_avatar_url
            if (avatar := ctx.author.avatar_url) is None
            else avatar,
        ),
    )

    await ctx.respond(
        embed=Responses.Success(
            description="Your report to the Moderators has been submitted.",
            footer="Abuse of this feature will result in your removal from the server.",
        )
    )

    logger.success(
        f"{Responses.ExpandUser(ctx.author, False)} reported message ({message.id}) by {Responses.ExpandUser(message.author, False)} in {Responses.ExpandGuild(ctx.get_guild(), False)} {Responses.ExpandChannel(ctx.get_channel(), False)}"
    )


@component.with_slash_command()
@tanjun.with_author_permission_check(Permissions.MANAGE_MESSAGES)
@tanjun.with_own_permission_check(Permissions.MANAGE_MESSAGES)
@tanjun.with_own_permission_check(Permissions.SEND_MESSAGES)
@tanjun.with_own_permission_check(Permissions.READ_MESSAGE_HISTORY)
@tanjun.with_user_slash_option(
    "member", "Target a specific member's messages to delete.", default=None
)
@tanjun.with_int_slash_option(
    "amount", "Number of messages to be deleted.", min_value=2, max_value=100
)
@tanjun.with_channel_slash_option(
    "channel", "Channel to fetch the messages from.", types=[GuildTextChannel]
)
@tanjun.as_slash_command("purge", "Mass delete messages in the specified channel.")
async def CommandPurge(
    ctx: SlashContext,
    channel: InteractionChannel,
    amount: int,
    member: Member | None,
) -> None:
    """Handler for the /purge command."""

    messages: list[int] = []
    users: list[int] = []
    last: datetime = datetime.now()

    try:
        while len(messages) < amount:
            for m in await ctx.rest.fetch_messages(channel.id, before=last).limit(100):
                last = m.timestamp

                if m.author.is_system:
                    continue
                elif (messageId := m.id) in messages:
                    continue

                if member is not None:
                    if m.author.id != member.id:
                        continue

                if (userId := int(m.author.id)) not in users:
                    users.append(userId)

                messages.append(messageId)

                if len(messages) == amount:
                    break
    except Exception as e:
        logger.opt(exception=e).error(
            f"Failed to fetch messages in {Responses.ExpandGuild(ctx.get_guild(), False)} {Responses.ExpandChannel(channel, False)}"
        )

        if len(messages) == 0:
            await ctx.respond(
                embed=Responses.Fail(
                    description=f"Failed to fetch messages in <#{channel.id}>, {e}."
                )
            )

            return

    try:
        await ctx.rest.delete_messages(channel.id, messages)
    except Exception as e:
        logger.opt(exception=e).error(
            f"Failed to delete messages in {Responses.ExpandGuild(ctx.get_guild(), False)} {Responses.ExpandChannel(channel, False)}"
        )

        await ctx.respond(
            embed=Responses.Fail(
                description=f"Failed to delete messages in <#{channel.id}>, {e}."
            )
        )

        return

    uCount: int = len(users)
    uLabel: str = "member"

    mCount: int = len(messages)
    mLabel: str = "message"

    if uCount > 1:
        uLabel = "members"

    if mCount > 1:
        mLabel = "messages"

    await ctx.respond(
        embed=Responses.Success(
            description=f"Deleted {mCount:,} {mLabel} from {uCount:,} {uLabel} in <#{channel.id}>."
        )
    )


@parse.with_command
@tanjun.with_author_permission_check(Permissions.MANAGE_MESSAGES)
@tanjun.with_own_permission_check(Permissions.SEND_MESSAGES)
@tanjun.with_own_permission_check(Permissions.READ_MESSAGE_HISTORY)
@tanjun.with_str_slash_option("message_id", "Enter the ID of the message to parse.")
@tanjun.with_channel_slash_option(
    "channel", "Choose a channel to parse a message from.", types=[GuildTextChannel]
)
@tanjun.as_slash_command("users", "Parse a message and return any user ID occurrences.")
async def CommandParseUsers(
    ctx: SlashContext, channel: InteractionChannel, message_id: str
) -> None:
    """Handler for the /parse users command."""

    results: list[int] = []

    # Minimum and maximum length of Discord snowflakes
    # https://discord.com/developers/docs/reference#snowflakes
    sMin: int = 17
    sMax: int = 19

    try:
        target: Message = await ctx.rest.fetch_message(channel.id, int(message_id))

        if target is None:
            raise ValueError("target message is null")

        if target.type == MessageType.GUILD_MEMBER_JOIN:
            results.append(target.author.id)

        if (content := target.content) is not None:
            for find in Utility.FindNumbers(content, sMin, sMax):
                if find in results:
                    continue

                results.append(find)

        for embed in target.embeds:
            if embed.author is not None:
                if (name := embed.author.name) is not None:
                    for find in Utility.FindNumbers(name, sMin, sMax):
                        if find in results:
                            continue

                        results.append(find)

            if (title := embed.title) is not None:
                for find in Utility.FindNumbers(title, sMin, sMax):
                    if find in results:
                        continue

                    results.append(find)

            if (desc := embed.description) is not None:
                for find in Utility.FindNumbers(desc, sMin, sMax):
                    if find in results:
                        continue

                    results.append(find)

            if (fields := embed.fields) is not None:
                for field in fields:
                    for find in Utility.FindNumbers(field.name, sMin, sMax):
                        if find in results:
                            continue

                        results.append(find)

                    for find in Utility.FindNumbers(field.value, sMin, sMax):
                        if find in results:
                            continue

                        results.append(find)

            if embed.footer is not None:
                if (footer := embed.footer.text) is not None:
                    for find in Utility.FindNumbers(footer, sMin, sMax):
                        if find in results:
                            continue

                        results.append(find)
    except Exception as e:
        logger.opt(exception=e).error(
            f"Failed to parse message {message_id} in {Responses.ExpandGuild(ctx.get_guild(), False)} {Responses.ExpandChannel(channel, False)}"
        )

        await ctx.respond(
            embed=Responses.Fail(
                description=f"Failed to fetch parse in <#{channel.id}>, {e}"
            )
        )

        return

    for result in results:
        if not await Utility.IsValidUser(result, ctx.client):
            results.remove(result)

    if len(results) == 0:
        await ctx.respond(
            embed=Responses.Warning(
                description="No user IDs found in the provided message."
            )
        )

        return

    await ctx.respond(
        embed=Responses.Success(description=f"Found {len(results):,} user ID(s)...")
    )

    for result in results:
        await ctx.create_followup(str(result))

    logger.success(
        f"Parsed {len(results):,} user IDs from message {message_id} in {Responses.ExpandGuild(ctx.get_guild(), False)} {Responses.ExpandChannel(channel, False)}"
    )
