from datetime import datetime
from typing import List, Optional

import tanjun
from helpers import Responses
from hikari import InteractionChannel, Member, Permissions
from loguru import logger
from tanjun import Component
from tanjun.abc import SlashContext

component: Component = Component(name="Messages")


@component.with_slash_command()
@tanjun.with_author_permission_check(Permissions.MANAGE_MESSAGES)
@tanjun.with_own_permission_check(Permissions.MANAGE_MESSAGES)
@tanjun.with_own_permission_check(Permissions.SEND_MESSAGES)
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
