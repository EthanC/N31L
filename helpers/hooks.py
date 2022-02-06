from typing import Any, Dict

import tanjun
from loguru import logger
from tanjun.abc import SlashContext

from .responses import Responses


class Hooks:
    """Logging and error handling hooks."""

    async def PreExecution(ctx: SlashContext) -> None:
        """Slash command pre-execution hook."""

        command: str = "/"

        if (groupB := ctx.command.parent) is not None:
            if (groupA := ctx.command.parent.parent) is not None:
                command += f"{groupA.name} "

            command += f"{groupB.name} "

        command += ctx.command.name

        logger.info(
            f"{Responses.ExpandUser(ctx.author, False)} used {command} in {Responses.ExpandGuild(ctx.get_guild(), False)} {Responses.ExpandChannel(ctx.get_channel(), False)}"
        )

    async def PostExecution(
        ctx: SlashContext, config: Dict[str, Any] = tanjun.inject(type=Dict[str, Any])
    ) -> None:
        """Slash command post-execution hook."""

        command: str = "/"

        if (groupB := ctx.command.parent) is not None:
            if (groupA := ctx.command.parent.parent) is not None:
                command += f"{groupA.name} "

            command += f"{groupB.name} "

        command += ctx.command.name

        await ctx.rest.create_message(
            config["channels"]["user"],
            Responses.Log(
                "robot",
                f"{Responses.ExpandUser(ctx.author)} used `{command}` in {Responses.ExpandChannel(ctx.get_channel())}",
            ),
        )
