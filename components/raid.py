from datetime import datetime
from typing import List, Optional, Union

import tanjun
from hikari import InteractionMember, MessageType, Permissions
from hikari.users import UserImpl
from loguru import logger
from tanjun import Component
from tanjun.abc import SlashContext
from tanjun.commands import SlashCommandGroup

from helpers import Responses, Utility

component: Component = Component(name="Raid")

raid: SlashCommandGroup = component.with_slash_command(
    tanjun.slash_command_group(
        "raid", "Slash Commands to protect the server during a raid."
    )
)


@raid.with_command
@tanjun.with_author_permission_check(Permissions.BAN_MEMBERS)
@tanjun.with_own_permission_check(Permissions.SEND_MESSAGES)
@tanjun.with_user_slash_option(
    "oldest_join", "Least recently-joined user to stop collecting IDs at.", default=None
)
@tanjun.with_user_slash_option(
    "newest_join", "Most recently-joined user to start collecting IDs at.", default=None
)
@tanjun.with_int_slash_option(
    "max_joined",
    "Maximum join age (in seconds) to collect (ignored if both newest_join and oldest_join are set).",
    default=None,
    min_value=1,
    max_value=86400,
)
@tanjun.with_int_slash_option(
    "max_created",
    "Maximum account age (in seconds) to collect.",
    default=None,
    min_value=1,
)
@tanjun.with_int_slash_option(
    "amount",
    "Number of user IDs to collect (ignored if both newest_join and oldest_join are set).",
    min_value=2,
    max_value=1000,
)
@tanjun.as_slash_command(
    "collect", "Collect IDs of newly-joined users for use with mass-ban commands."
)
async def CommandRaidCollect(
    ctx: SlashContext,
    amount: Optional[int],
    max_created: Optional[int],
    max_joined: Optional[int],
    newest_join: Optional[Union[InteractionMember, UserImpl]],
    oldest_join: Optional[Union[InteractionMember, UserImpl]],
) -> None:
    """Handler for the /raid collect command."""

    welcomes: Optional[int] = None

    try:
        welcomes = (await ctx.fetch_guild()).system_channel_id

        if welcomes is None:
            raise ValueError("system messages channel is not set")
    except Exception as e:
        logger.error(
            f"Failed to fetch system messages channel in {Responses.ExpandGuild(ctx.get_guild(), False)}, {e}"
        )

        await ctx.respond(
            embed=Responses.Fail(description=f"Failed to collect user IDs, {e}.")
        )

        return

    users: List[int] = []
    start: datetime = datetime.now()
    last: datetime = start
    collect: bool = True
    active: bool = True

    # If both newest_join and oldest_user are set, we can disregard
    # multiple other arguments.
    if (newest_join is not None) and (oldest_join is not None):
        amount = None
        max_joined = None

    # If newest_join is set, we do not begin collecting immediately.
    if newest_join is not None:
        collect = False

    try:
        while active:
            for m in await ctx.rest.fetch_messages(welcomes, before=last).limit(100):
                last = m.created_at

                if m.type != MessageType.GUILD_MEMBER_JOIN:
                    continue

                userId: int = int(m.author.id)

                if max_created is not None:
                    accountAge: int = Utility.Elapsed(start, m.author.created_at)

                    if accountAge > max_created:
                        continue

                if max_joined is not None:
                    joinAge: int = Utility.Elapsed(start, m.created_at)

                    if joinAge > max_joined:
                        active = False

                        break

                if newest_join is not None:
                    if userId == int(newest_join.id):
                        collect = True

                if (userId not in users) and (collect):
                    users.append(userId)

                if oldest_join is not None:
                    if userId == int(oldest_join.id):
                        active = False

                        break

                if amount is not None:
                    if len(users) >= amount:
                        active = False

                        break
    except Exception as e:
        logger.error(
            f"Failed to collect {amount:,} recently-joined users in {Responses.ExpandGuild(ctx.get_guild(), False)}, {e}"
        )

        if len(users) == 0:
            await ctx.respond(
                embed=Responses.Fail(description=f"Failed to collect user IDs, {e}.")
            )

            return

    await ctx.respond(
        embed=Responses.Success(description=f"Collected {len(users):,} users.")
    )

    logger.success(
        f"Collected {len(users):,} users in {Responses.ExpandGuild(ctx.get_guild(), False)}"
    )

    chunk: str = ""

    for user in users:
        # Reply in chunks of less than 1,750 characters in order to
        # avoid message length limits.
        if (len(str(user)) + len(chunk)) >= 1750:
            await ctx.create_followup(chunk)

            chunk = ""

        chunk += f"{user} "

    if chunk != "":
        await ctx.create_followup(chunk)
