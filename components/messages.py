from datetime import datetime
from typing import List, Optional

import tanjun
from helpers import Responses, Utility
from hikari import InteractionChannel, Member, Permissions
from hikari.messages import Message
from loguru import logger
from tanjun import Component
from tanjun.abc import SlashContext
from tanjun.commands import SlashCommandGroup

component: Component = Component(name="Messages")

parse: SlashCommandGroup = component.with_slash_command(
    tanjun.slash_command_group("parse", "Slash Commands to parse messages.")
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
@tanjun.with_channel_slash_option("channel", "Channel to fetch the messages from.")
@tanjun.as_slash_command(
    "purge",
    "Mass delete messages in the specified channel.",
    default_permission=False,
)
async def CommandPurge(
    ctx: SlashContext,
    channel: InteractionChannel,
    amount: int,
    member: Optional[Member],
) -> None:
    """Handler for the /purge command."""

    messages: List[int] = []
    users: List[int] = []
    last: datetime = datetime.now()

    try:
        while len(messages) < amount:
            for m in await ctx.rest.fetch_messages(channel.id, before=last).limit(100):
                if m.author.is_system is True:
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
        logger.error(
            f"Failed to fetch messages in {Responses.ExpandGuild(ctx.get_guild(), False)} {Responses.ExpandChannel(channel, False)}, {e}"
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
        logger.error(
            f"Failed to delete messages in {Responses.ExpandGuild(ctx.get_guild(), False)} {Responses.ExpandChannel(channel, False)}, {e}"
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
    "channel", "Choose a channel to parse a message from."
)
@tanjun.as_slash_command(
    "users",
    "Parse a message and return any user ID occurrences.",
    default_permission=False,
)
async def CommandParseUsers(
    ctx: SlashContext, channel: InteractionChannel, message_id: str
) -> None:
    """Handler for the /parse users command."""

    results: List[int] = []

    try:
        target: Message = await ctx.rest.fetch_message(channel.id, int(message_id))

        if target is None:
            raise ValueError("message is null")

        if target.author.is_system is True:
            results.append(target.author.id)

        if (content := target.content) is not None:
            for find in Utility.FindNumbers(content, 17, 18):
                if find in results:
                    continue

                results.append(find)

        for embed in target.embeds:
            if embed.author is not None:
                if (name := embed.author.name) is not None:
                    for find in Utility.FindNumbers(name, 17, 18):
                        if find in results:
                            continue

                        results.append(find)

            if (desc := embed.description) is not None:
                for find in Utility.FindNumbers(desc, 17, 18):
                    if find in results:
                        continue

                    results.append(find)

            if (fields := embed.fields) is not None:
                for field in fields:
                    for find in Utility.FindNumbers(field.name, 17, 18):
                        if find in results:
                            continue

                        results.append(find)

                    for find in Utility.FindNumbers(field.value, 17, 18):
                        if find in results:
                            continue

                        results.append(find)

            if embed.footer is not None:
                if (footer := embed.footer.text) is not None:
                    for find in Utility.FindNumbers(footer, 17, 18):
                        if find in results:
                            continue

                        results.append(find)
    except Exception as e:
        logger.error(
            f"Failed to fetch message {message_id} in {Responses.ExpandGuild(ctx.get_guild(), False)} {Responses.ExpandChannel(channel, False)}, {e}"
        )

        await ctx.respond(
            embed=Responses.Fail(
                description=f"Failed to fetch message in <#{channel.id}>, an unknown error occurred."
            )
        )

        return

    for result in results:
        try:
            logger.debug(
                f"Validated {result} as user {(await ctx.rest.fetch_user(result)).username}"
            )
        except Exception as e:
            results.remove(result)

            logger.debug(f"{result} is not a user ID, removed from results ({e})")

    if len(results) == 0:
        await ctx.respond(
            embed=Responses.Warning(
                description="No user IDs found in the specified message."
            )
        )

        return

    await ctx.respond(
        embed=Responses.Success(description=f"Found {len(results):,} user ID(s).")
    )

    for result in results:
        await ctx.create_followup(str(result))

    logger.success(
        f"Parsed {len(results):,} user IDs from message {message_id} in {Responses.ExpandGuild(ctx.get_guild(), False)} {Responses.ExpandChannel(channel, False)}"
    )
