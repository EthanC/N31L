import asyncio
from datetime import datetime
from typing import Any, Dict, List, Optional

import tanjun
from helpers import Responses, Timestamps, Utility
from hikari import (
    DMChannel,
    MessageType,
    PermissionOverwrite,
    PermissionOverwriteType,
    Permissions,
)
from hikari.channels import GuildChannel
from hikari.errors import ForbiddenError
from hikari.events.member_events import MemberCreateEvent
from loguru import logger
from models import State
from tanjun import Client, Component
from tanjun.abc import SlashContext
from tanjun.commands import SlashCommandGroup

component: Component = Component(name="Raid")

raid: SlashCommandGroup = component.with_slash_command(
    tanjun.slash_command_group(
        "raid", "Slash Commands to protect the server during a raid."
    )
)
offense: SlashCommandGroup = raid.with_command(
    tanjun.slash_command_group("offense", "Slash Commands to combat a raid.")
)
defense: SlashCommandGroup = raid.with_command(
    tanjun.slash_command_group("defense", "Slash Commands to defend against a raid.")
)


@raid.with_command
@tanjun.with_author_permission_check(Permissions.BAN_MEMBERS)
@tanjun.with_own_permission_check(Permissions.SEND_MESSAGES)
@tanjun.with_int_slash_option(
    "max_age", "Maximum account age (in seconds) to collect.", default=None, min_value=1
)
@tanjun.with_int_slash_option(
    "amount", "Number of user IDs to collect.", min_value=2, max_value=1000
)
@tanjun.as_slash_command(
    "collect",
    "Collect IDs of newly-joined users for use with mass-ban commands.",
    default_permission=False,
)
async def CommandRaidCollect(
    ctx: SlashContext, amount: int, max_age: Optional[int]
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
    last: datetime = datetime.now()

    try:
        while len(users) < amount:
            for m in await ctx.rest.fetch_messages(welcomes, before=last).limit(100):
                last = m.created_at

                if m.type != MessageType.GUILD_MEMBER_JOIN:
                    continue
                elif (userId := m.author.id) in users:
                    continue

                if max_age is not None:
                    accountAge: int = Utility.Elapsed(
                        datetime.utcnow(), m.author.created_at
                    )

                    if accountAge > max_age:
                        continue

                users.append(userId)

                if len(users) == amount:
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


@offense.with_command
@tanjun.with_author_permission_check(Permissions.BAN_MEMBERS)
@tanjun.with_own_permission_check(Permissions.BAN_MEMBERS)
@tanjun.with_own_permission_check(Permissions.SEND_MESSAGES)
@tanjun.with_int_slash_option(
    "duration",
    "Duration (in seconds) that offensive raid protection should be active.",
    min_value=1,
    max_value=3600,
)
@tanjun.with_str_slash_option("reason", "Reason provided to a banned user.")
@tanjun.with_int_slash_option(
    "max_age", "Maximum account age (in seconds) to ban.", min_value=1
)
@tanjun.as_slash_command(
    "enable",
    "Evaluate users upon join and ban if account age is less than provided threshold.",
    default_permission=False,
)
async def CommandRaidOffenseEnable(
    ctx: SlashContext,
    max_age: int,
    reason: str,
    duration: int,
    state: State = tanjun.inject(type=State),
) -> None:
    """Handler for the /raid offense enable command."""

    if state.raidOffense is True:
        await ctx.respond(
            embed=Responses.Fail(
                description=f"Offensive raid protection is already active, {state.raidOffCount:,} users banned so far."
            )
        )

        return

    await ctx.respond(
        embed=Responses.Success(
            description=f"Enabled offensive raid protection, automatically disabled {Timestamps.Relative((datetime.now().timestamp() + duration))}."
        )
    )

    state.raidOffense = True
    state.raidOffAge = max_age
    state.raidOffReason = reason
    state.raidOffActor = ctx.member.user
    state.raidOffCount = 0

    logger.success(
        f"Offensive raid protection enabled for {duration:,}s by {Responses.ExpandUser(ctx.author, False)}"
    )

    await asyncio.sleep(float(duration))

    await CommandRaidOffenseDisable(ctx, True, state)


@offense.with_command
@tanjun.with_author_permission_check(Permissions.BAN_MEMBERS)
@tanjun.with_own_permission_check(Permissions.BAN_MEMBERS)
@tanjun.with_own_permission_check(Permissions.SEND_MESSAGES)
@tanjun.as_slash_command(
    "disable",
    "Disable offensive raid protection, if enabled.",
    default_permission=False,
)
async def CommandRaidOffenseDisable(
    ctx: SlashContext, auto: bool = False, state: State = tanjun.inject(type=State)
) -> None:
    """Handler for the /raid offense disable command."""

    if state.raidOffense is False:
        await ctx.respond(
            embed=Responses.Fail(description="Offensive raid protection is not active.")
        )

        return

    response: str = (
        f"Disabled offensive raid protection, {state.raidOffCount:,} users banned."
    )

    if auto is True:
        await ctx.create_followup(embed=Responses.Success(description=response))
    else:
        await ctx.respond(embed=Responses.Success(description=response))

    state.raidOffense = False
    state.raidOffAge = None
    state.raidOffReason = None
    state.raidOffActor = None
    state.raidOffCount = None

    logger.success(
        f"Offensive raid protection disabled by {Responses.ExpandUser(ctx.author, False)}"
    )


@defense.with_command
@tanjun.with_author_permission_check(Permissions.BAN_MEMBERS)
@tanjun.with_own_permission_check(Permissions.MANAGE_CHANNELS)
@tanjun.with_own_permission_check(Permissions.SEND_MESSAGES)
@tanjun.with_int_slash_option(
    "duration",
    "Duration (in seconds) that defensive protection should be active.",
    min_value=1,
    max_value=3600,
)
@tanjun.as_slash_command(
    "enable",
    "Deny the Send Messages permission for @everyone in all channels.",
    default_permission=False,
)
async def CommandRaidDefenseEnable(
    ctx: SlashContext,
    duration: int,
    config: Dict[str, Any] = tanjun.inject(type=Dict[str, Any]),
    state: State = tanjun.inject(type=State),
) -> None:
    """Handler for the /raid defense enable command."""

    if state.raidDefense is True:
        await ctx.respond(
            embed=Responses.Fail(
                description="Defensive raid protection is already active."
            )
        )

        return

    for entry in config["channels"]["raidDefense"]:
        try:
            chan: GuildChannel = await ctx.rest.fetch_channel(entry)
            current: PermissionOverwrite = chan.permission_overwrites[int(ctx.guild_id)]

            await ctx.rest.edit_permission_overwrites(
                entry,
                ctx.guild_id,
                target_type=PermissionOverwriteType.ROLE,
                allow=(current.allow & ~Permissions.SEND_MESSAGES),
                deny=(current.deny | Permissions.SEND_MESSAGES),
                reason=f"{Responses.ExpandUser(ctx.author, False)} enabled defensive raid protection.",
            )
        except Exception as e:
            logger.error(
                f"Failed to deny Send Messages permission for everyone in {Responses.ExpandGuild(ctx.get_guild(), False)} {Responses.ExpandChannel(ctx.get_channel(), False)}, {e}"
            )

    await ctx.respond(
        embed=Responses.Success(
            description=f"Enabled defensive raid protection, automatically disabled {Timestamps.Relative((datetime.now().timestamp() + duration))}."
        )
    )

    state.raidDefense = True

    logger.success(
        f"Defensive raid protection enabled for {duration:,}s by {Responses.ExpandUser(ctx.author, False)}"
    )

    await asyncio.sleep(float(duration))

    await CommandRaidDefenseDisable(ctx, True, config, state)


@defense.with_command
@tanjun.with_author_permission_check(Permissions.BAN_MEMBERS)
@tanjun.with_own_permission_check(Permissions.MANAGE_CHANNELS)
@tanjun.with_own_permission_check(Permissions.SEND_MESSAGES)
@tanjun.as_slash_command(
    "disable",
    "Disable defensive raid protection, if enabled.",
    default_permission=False,
)
async def CommandRaidDefenseDisable(
    ctx: SlashContext,
    auto: bool = False,
    config: Dict[str, Any] = tanjun.inject(type=Dict[str, Any]),
    state: State = tanjun.inject(type=State),
) -> None:
    """Handler for the /raid defense disable command."""

    if state.raidDefense is False:
        await ctx.respond(
            embed=Responses.Fail(description="Defensive raid protection is not active.")
        )

        return

    for entry in config["channels"]["raidDefense"]:
        try:
            chan: GuildChannel = await ctx.rest.fetch_channel(entry)
            current: PermissionOverwrite = chan.permission_overwrites[int(ctx.guild_id)]

            await ctx.rest.edit_permission_overwrites(
                entry,
                ctx.guild_id,
                target_type=PermissionOverwriteType.ROLE,
                allow=(current.allow | Permissions.SEND_MESSAGES),
                deny=(current.deny & ~Permissions.SEND_MESSAGES),
                reason=f"{Responses.ExpandUser(ctx.author, False)} disabled defensive raid protection.",
            )
        except Exception as e:
            logger.error(
                f"Failed to allow Send Messages permission for everyone in {Responses.ExpandGuild(ctx.get_guild(), False)} {Responses.ExpandChannel(ctx.get_channel(), False)}, {e}"
            )

    response: str = "Disabled defensive raid protection."

    if auto is True:
        await ctx.create_followup(embed=Responses.Success(description=response))
    else:
        await ctx.respond(embed=Responses.Success(description=response))

    state.raidDefense = False

    logger.success(
        f"Defensive raid protection disabled by {Responses.ExpandUser(ctx.author, False)}"
    )


@component.with_listener(MemberCreateEvent)
async def EventRaidOffense(
    ctx: MemberCreateEvent,
    config: Dict[str, Any] = tanjun.inject(type=Dict[str, Any]),
    state: State = tanjun.inject(type=State),
    client: Client = tanjun.inject(type=Client),
) -> None:
    """Handler for offensive raid protection."""

    if state.raidOffense is False:
        return

    accountAge: int = Utility.Elapsed(datetime.utcnow(), ctx.member.created_at)

    if accountAge > state.raidOffAge:
        return

    template: str = "You have been **banned** from the **Call of Duty** server for the following reason(s):\n> {}\n\nTo appeal this decision, join the following server and carefully read the \#how-to-appeal channel.\nhttps://discord.gg/PHGxw9w"

    try:
        dm: DMChannel = await client.rest.create_dm_channel(ctx.member.id)

        await dm.send(template.format(state.raidOffReason))
    except ForbiddenError:
        pass
    except Exception as e:
        logger.error(
            f"Failed to notify {Responses.ExpandUser(ctx.user, False)} of offensive raid protection action, {e}"
        )

    try:
        await ctx.member.ban(
            reason=f"Automatic by {Responses.ExpandUser(state.raidOffActor, False)} ({accountAge:,}s<{state.raidOffAge:,}s): {state.raidOffReason}"
        )
    except Exception as e:
        logger.error(
            f"Failed to ban {Responses.ExpandUser(ctx.user, False)} from {Responses.ExpandGuild(ctx.get_guild(), False)}, {e}"
        )

        return

    try:
        await client.rest.create_message(
            config["channels"]["moderation"],
            Responses.Log(
                "rotating_light",
                f"{Responses.ExpandUser(ctx.user)} was banned by {Responses.ExpandUser(state.raidOffActor)} with reason: *{state.raidOffReason}*",
            ),
        )
    except Exception as e:
        logger.error(f"Failed to log offensive raid protection action, {e}")

    state.raidOffCount += 1

    logger.success(
        f"Banned {Responses.ExpandUser(ctx.user, False)} in {Responses.ExpandGuild(ctx.get_guild(), False)} due to offensive raid protection"
    )
