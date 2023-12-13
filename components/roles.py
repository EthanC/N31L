from typing import Any, Dict, List, Sequence

import tanjun
from hikari.events.message_events import GuildMessageCreateEvent
from hikari.snowflakes import Snowflake
from loguru import logger
from tanjun import Client, Component

from helpers.responses import Responses

component: Component = Component(name="Roles")


@component.with_listener(GuildMessageCreateEvent)
async def EventValidateRoles(
    ctx: GuildMessageCreateEvent,
    client: Client = tanjun.inject(type=Client),
    config: Dict[str, Any] = tanjun.inject(type=Dict[str, Any]),
) -> None:
    """
    Validate that the configured role requirements are met for the
    given member upon message creation.
    """

    if not ctx.is_human:
        return
    elif ctx.message.member is None:
        return

    invalidated: List[int] = []
    equipped: Sequence[Snowflake] = ctx.message.member.role_ids

    if config["roles"]["limit"]:
        matches: List[int] = []

        for role in equipped:
            if role in config["roles"]["allow"]:
                matches.append(role)

        if len(matches) > 1:
            for match in matches[1:]:
                await ctx.message.member.remove_role(
                    match, reason="Member exceeds the limit of allowed roles."
                )

                await client.rest.create_message(
                    config["channels"]["user"],
                    Responses.Log(
                        "shirt",
                        f"Removed role (`{match}`) from {Responses.ExpandUser(ctx.author)} with reason: *Limit exceeded*",
                    ),
                )

                logger.success(
                    f"Invalidated role ({match}) for {Responses.ExpandUser(ctx.author, False)} in {Responses.ExpandGuild(ctx.get_guild(), False)}"
                )

            # Fetch equipped roles again to continue validation
            equipped: Sequence[Snowflake] = ctx.message.member.role_ids

    for role in equipped:
        if role in config["roles"]["require"]:
            return

    for role in equipped:
        if role in config["roles"]["allow"]:
            invalidated.append(role)

    for role in invalidated:
        await ctx.message.member.remove_role(
            role, reason="Member does not meet the requirements to equip this role."
        )

        await client.rest.create_message(
            config["channels"]["user"],
            Responses.Log(
                "shirt",
                f"Removed role (`{role}`) from {Responses.ExpandUser(ctx.author)} with reason: *Requirements not met*",
            ),
        )

        logger.success(
            f"Invalidated role ({role}) for {Responses.ExpandUser(ctx.author, False)} in {Responses.ExpandGuild(ctx.get_guild(), False)}"
        )
