import re
from datetime import datetime
from typing import Any

import httpx
from arc import GatewayClient
from hikari import Guild, Member, NotFoundError
from httpx import Response
from loguru import logger

from core.formatters import ExpandServer, ExpandUser


def Elapsed(a: datetime | int | float, b: datetime | int | float) -> int:
    """Determine the elapsed seconds between the provided timestamps."""

    if isinstance(a, datetime):
        a = a.timestamp()

    if isinstance(b, datetime):
        b = b.timestamp()

    return int(a - b)


def Trim(input: str, length: int, end: str | None = "...") -> str:
    """Trim a string using the provided parameters."""

    if len(input) <= length:
        return input

    result: str = input[:length]

    try:
        result = result.rsplit(" ", 1)[0]
    except Exception as e:
        logger.opt(exception=e).debug("Failed to cleanly trim string")

    if end:
        result += end

    return result


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
                    f"{ExpandUser(user.user, format=False)} has role {current} in server {ExpandServer(server, format=False)}"
                )

                return True

        logger.debug(
            f"{ExpandUser(user.user, format=False)} does not have role(s) {roleIds} in server {ExpandServer(server, format=False)}"
        )

    return False


async def GET(
    url: str, headers: dict[str, str] | None = None
) -> dict[str, Any] | list[Any] | str | None:
    """Perform an HTTP GET request and return its response."""

    logger.debug(f"GET {url}")

    try:
        async with httpx.AsyncClient() as http:
            res: Response = await http.get(url, headers=headers, follow_redirects=True)

        res.raise_for_status()

        logger.trace(res.text)
    except Exception as e:
        logger.opt(exception=e).error(f"Failed to GET {url}")

        return

    try:
        return res.json()
    except Exception as e:
        logger.opt(exception=e).debug("Failed to parse response as JSON")

    return res.text
