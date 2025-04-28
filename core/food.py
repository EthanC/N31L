from typing import Any

from hikari import Embed
from loguru import logger

from core.formatters import response
from core.utils import get


async def foodish(food: str) -> Embed | None:
    """Fetch a random food image from foodish."""

    data: dict[str, Any] | list[Any] | str | None = await get(
        f"https://foodish-api.com/api/images/{food}"
    )

    if not data:
        logger.debug(f"Failed to fetch food {food} from foodish, data is null")

        return
    elif not isinstance(data, dict):
        logger.debug(f"Failed to fetch food {food} from foodish, invalid response")

        return

    try:
        return response(image=data["image"])
    except Exception as e:
        logger.opt(exception=e).error(f"Failed to fetch food {food} from foodish")
