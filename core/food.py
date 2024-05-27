from typing import Any

from hikari import Embed
from loguru import logger

from core.formatters import Response
from core.utils import GET


async def Foodish(food: str) -> Embed | None:
    """Fetch a random food image from Foodish."""

    data: dict[str, Any] | list[Any] | str | None = await GET(
        f"https://foodish-api.com/api/images/{food}"
    )

    if not data:
        logger.debug(f"Failed to fetch food {food} from Foodish, data is null")

        return
    elif not isinstance(data, dict):
        logger.debug(f"Failed to fetch food {food} from Foodish, invalid response")

        return

    try:
        return Response(image=data["image"])
    except Exception as e:
        logger.opt(exception=e).error(f"Failed to fetch food {food} from Foodish")
