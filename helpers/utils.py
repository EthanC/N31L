import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

import httpx
from hikari import GatewayBot, Member, NotFoundError
from httpx import Response
from loguru import logger
from tanjun import Client

from .responses import Responses


class Utility:
    """Utilitarian functions designed for N31L."""

    async def GET(
        url: str, headers: Optional[Dict[str, str]] = None
    ) -> Optional[Union[str, Dict[str, Any]]]:
        """Perform an HTTP GET request and return its response."""

        logger.debug(f"GET {url}")

        try:
            async with httpx.AsyncClient() as http:
                res: Response = await http.get(
                    url, headers=headers, follow_redirects=True
                )

            res.raise_for_status()

            logger.trace(res.text)
        except Exception as e:
            logger.opt(exception=e).error(f"Failed to GET {url}")

            return

        try:
            return res.json()
        except Exception as e:
            logger.opt(exception=e).trace("Failed to parse response as JSON")

        return res.text

    async def POST(url: str, payload: Dict[str, Any]) -> bool:
        """Perform an HTTP POST request and return its status."""

        logger.debug(f"POST {url}")

        try:
            async with httpx.AsyncClient() as http:
                res: Response = await http.post(
                    url,
                    json=payload,
                    headers={"content-type": "application/json"},
                )

                res.raise_for_status()
        except Exception as e:
            logger.opt(exception=e).error(f"Failed to POST {url}")

            return False

        return True

    def Elapsed(a: Union[datetime, int, float], b: Union[datetime, int, float]) -> int:
        """Determine the elapsed seconds between the provided datetime objects."""

        if type(a) is datetime:
            a = a.timestamp()

        if type(b) is datetime:
            b = b.timestamp()

        return int(a - b)

    def Trim(input: str, length: int, end: Optional[str] = "...") -> str:
        """Trim a string using the provided parameters."""

        if len(input) <= length:
            return input

        result: str = input[:length]

        try:
            result = result.rsplit(" ", 1)[0]
        except Exception as e:
            logger.opt(exception=e).debug("Failed to cleanly trim string")
            logger.trace(result)

        if end is not None:
            result += end

        return result

    def FindNumbers(
        input: str, minLen: Optional[int] = None, maxLen: Optional[int] = None
    ) -> List[int]:
        """Return all number sequences found in the given string."""

        results: List[int] = []

        try:
            for entry in re.findall("\\d+", input):
                if minLen is not None:
                    if len(entry) < minLen:
                        continue

                if maxLen is not None:
                    if len(entry) > maxLen:
                        continue

                logger.debug(f"Found number {entry} in string {input}")

                results.append(int(entry))
        except Exception as e:
            logger.opt(exception=e).debug("Failed to find numbers in string")
            logger.trace(input)

        return results

    async def UserHasRole(
        userId: int, roleIds: Union[int, List[int]], serverId: int, bot: GatewayBot
    ) -> bool:
        """
        Return a boolean value indicating whether or not a server
        member has a specified role.

        If an array of role IDs is provided, return True upon first
        successful match.
        """

        user: Optional[Member] = None

        # Accept both a singular int or array of integers.
        if isinstance(roleIds, int):
            roleIds = [roleIds]

        try:
            user = await bot.rest.fetch_member(serverId, userId)
        except NotFoundError as e:
            logger.debug(f"Failed to locate member {userId} in server {serverId}, {e}")
        except Exception as e:
            logger.error(f"Failed to locate member {userId} in server {serverId}, {e}")

        if user:
            for role in user.role_ids:
                if (current := int(role)) in roleIds:
                    logger.debug(
                        f"{Responses.ExpandUser(user.user, False)} has role {current} in server {serverId}"
                    )

                    return True

            logger.debug(
                f"{Responses.ExpandUser(user.user, False)} does not have role {current} in server {serverId}"
            )

        return False
    
    async def IsValidUser(userId: int, client: Client) -> bool:
        """
        Determine if the provided integer is a valid
        Discord user ID.
        """

        try:
            logger.debug(f"Validated {userId} as user {(await client.rest.fetch_user(userId)).username}")
        except Exception as e:
            logger.opt(exception=e).debug(f"Invalidated potential user ID {userId}")

            return

        return True
