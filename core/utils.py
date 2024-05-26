import re
from datetime import datetime

from arc import GatewayClient
from hikari import Guild, Member, NotFoundError
from loguru import logger

from core.formatters import ExpandGuild, ExpandUser


def Elapsed(a: datetime | int | float, b: datetime | int | float) -> int:
    """Determine the elapsed seconds between the provided timestamps."""

    if isinstance(a, datetime):
        a = a.timestamp()

    if isinstance(b, datetime):
        b = b.timestamp()

    return int(a - b)


def FindNumbers(
    input: str, minLen: int | None = None, maxLen: int | None = None
) -> list[int]:
    """Return all number sequences found in the given string."""

    results: list[int] = []

    try:
        for entry in re.findall("\\d+", input):
            if minLen:
                if len(entry) < minLen:
                    continue

            if maxLen:
                if len(entry) > maxLen:
                    continue

            logger.debug(f"Found number {entry} in string {input}")

            results.append(int(entry))
    except Exception as e:
        logger.opt(exception=e).debug("Failed to find numbers in string")
        logger.trace(input)

    return results


async def IsValidUser(userId: int, client: GatewayClient) -> bool:
    """
    Determine if the provided integer is a valid
    Discord user ID.
    """

    try:
        logger.debug(
            f"Validated {userId} as user {(await client.rest.fetch_user(userId)).username}"
        )
    except Exception as e:
        logger.opt(exception=e).debug(f"Invalidated potential user ID {userId}")

        return False

    return True


async def UserHasRole(
    userId: int,
    roleIds: int | list[int],
    serverId: int,
    client: GatewayClient,
) -> bool:
    """
    Return a boolean value indicating whether or not a server
    member has a specified role.

    If an array of role IDs is provided, return True upon first
    successful match.
    """

    user: Member | None = None
    server: Guild = await client.rest.fetch_guild(serverId)

    # Accept both a singular int or array of integers.
    if isinstance(roleIds, int):
        roleIds = [roleIds]

    try:
        user = await client.rest.fetch_member(serverId, userId)
    except NotFoundError as e:
        logger.opt(exception=e).debug(
            f"Failed to locate member {userId} in server {serverId}"
        )
    except Exception as e:
        logger.opt(exception=e).error(
            f"Failed to locate member {userId} in server {serverId}"
        )

    if user:
        for role in user.role_ids:
            if (current := int(role)) in roleIds:
                logger.debug(
                    f"{ExpandUser(user.user, format=False)} has role {current} in server {ExpandGuild(server, format=False)}"
                )

                return True

        logger.debug(
            f"{ExpandUser(user.user, format=False)} does not have role(s) {roleIds} in server {ExpandGuild(server, format=False)}"
        )

    return False
