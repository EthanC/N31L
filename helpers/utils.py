import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

import httpx
from hikari import GatewayBot, Member
from httpx import Response
from loguru import logger

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
            logger.opt(exception=e).debug("Failed to parse response as JSON")

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
            for entry in re.findall("\d+", input):
                if minLen is not None:
                    if len(entry) < minLen:
                        continue

                if maxLen is not None:
                    if len(entry) > maxLen:
                        continue

                results.append(int(entry))
        except Exception as e:
            logger.opt(exception=e).debug("Failed to find numbers in string")
            logger.trace(input)

        return results

    async def UserHasRole(
        userId: int, roleId: int, serverId: int, bot: GatewayBot
    ) -> bool:
        """
        Return a boolean value indicating whether or not a server
        member has the specified role.
        """

        user: Member = await bot.rest.fetch_member(serverId, userId)

        for role in user.role_ids:
            if int(role) == roleId:
                logger.debug(
                    f"{Responses.ExpandUser(user.user, False)} has role {roleId} in server {serverId}"
                )

                return True

        logger.debug(
            f"{Responses.ExpandUser(user.user, False)} does not have role {roleId} in server {serverId}"
        )

        return False
