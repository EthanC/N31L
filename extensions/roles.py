from typing import Sequence

import arc
from arc import GatewayClient, GatewayContext, GatewayPlugin
from hikari import GuildMessageCreateEvent, Snowflake
from loguru import logger

from core.config import Config
from core.formatters import ExpandServer, ExpandUser, Log
from core.hooks import HookError

plugin: GatewayPlugin = GatewayPlugin("roles")


@arc.loader
def ExtensionLoader(client: GatewayClient) -> None:
    """Required. Called upon loading the extension."""

    logger.debug(f"Attempting to load {plugin.name} extension...")
    logger.trace(plugin)

    try:
        client.add_plugin(plugin)
    except Exception as e:
        logger.opt(exception=e).error(f"Failed to load {plugin.name} extension")


@plugin.listen()
async def EventValidateRoles(event: GuildMessageCreateEvent) -> None:
    """Handler for validating role requirements are met for members."""

    if not event.is_human:
        logger.trace("Ignoring message creation event, author is not human")

        return
    elif not event.message.member:
        logger.trace("Ignoring message creation event, author is not a server member")

        return

    cfg: Config = plugin.client.get_type_dependency(Config)
    equipped: Sequence[Snowflake] = event.message.member.role_ids
    matches: list[int] = []
    invalidated: list[int] = []

    logger.trace(equipped)

    for role in equipped:
        if role in cfg.rolesAllow:
            matches.append(role)

    logger.trace(matches)

    if len(matches) > 1:
        for match in matches[1:]:
            logger.trace(match)

            await event.message.member.remove_role(
                match, reason="Member exceeds the limit (1) of allowed roles."
            )

            await plugin.client.rest.create_message(
                cfg.channels["user"],
                Log(
                    "shirt",
                    f"Removed role (`{match}`) from {await ExpandUser(event.author)} with reason: *Member exceeds limit (1) of allowed roles.*",
                ),
            )

            logger.success(
                f"Invalidated role {match} for {await ExpandUser(event.author, format=False)} in {await ExpandServer(event.get_guild(), format=False)}"
            )

    # Refetch equipped roles before continuing validation
    if member := event.get_member():
        equipped = member.role_ids

        logger.trace(equipped)

    for role in equipped:
        logger.trace(role)

        if role in cfg.rolesRequire:
            logger.trace("Exiting role validation, user has a required role")

            return

    for role in equipped:
        logger.trace(role)

        if role in cfg.rolesAllow:
            invalidated.append(role)

    logger.trace(invalidated)

    for role in invalidated:
        logger.trace(role)

        await event.message.member.remove_role(
            role, reason="Member does not meet the requirements to equip this role."
        )

        await plugin.client.rest.create_message(
            cfg.channels["user"],
            Log(
                "shirt",
                f"Removed role (`{role}`) from {await ExpandUser(event.author)} with reason: *Requirements not met.*",
            ),
        )

        logger.success(
            f"Invalidated role ({role}) for {await ExpandUser(event.author, format=False)} in {await ExpandServer(event.get_guild(), format=False)}"
        )


@plugin.set_error_handler
async def ErrorHandler(ctx: GatewayContext, error: Exception) -> None:
    """Handler for errors originating from this plugin."""

    await HookError(ctx, error)
