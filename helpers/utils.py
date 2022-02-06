import json
from datetime import datetime
from typing import Any, Dict, Optional, Union

import httpx
from httpx import Response
from loguru import logger


class Utility:
    """Utilitarian functions designed for N31L."""

    async def GET(
        url: str, headers: Optional[Dict[str, str]] = None
    ) -> Optional[Union[str, Dict[str, Any]]]:
        """Perform an HTTP GET request and return its response."""

        logger.debug(f"GET {url}")

        try:
            async with httpx.AsyncClient() as http:
                res: Response = await http.get(url, headers=headers)

            res.raise_for_status()

            logger.trace(res.text)
        except Exception as e:
            logger.error(f"Failed to GET {url}, {e}")

            return

        try:
            return res.json()
        except:
            pass

        return res.text

    async def POST(url: str, payload: Dict[str, Any]) -> bool:
        """Perform an HTTP POST request and return its status."""

        logger.debug(f"POST {url}")

        try:
            async with httpx.AsyncClient() as http:
                res: Response = await http.post(
                    url,
                    data=json.dumps(payload),
                    headers={"content-type": "application/json"},
                )

                res.raise_for_status()
        except Exception as e:
            logger.error(f"Failed to POST {url}, {e}")

            return False

        return True

    def Elapsed(a: Union[datetime, int, float], b: Union[datetime, int, float]) -> int:
        """Determine the elapsed seconds between the provided datetime objects."""

        if type(a) is datetime:
            a = a.timestamp()

        if type(b) is datetime:
            b = b.timestamp()

        return int(a - b)
