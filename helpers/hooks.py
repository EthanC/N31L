from typing import Any, Dict

import tanjun
from loguru import logger
from tanjun.abc import MenuContext, SlashContext

from .responses import Responses


class MenuHooks:
    """Logging and error handling hooks for menu commands."""

    async def PreExecution(ctx: MenuContext) -> None:
        """Menu command pre-execution hook."""

        logger.info(
            f"{Responses.ExpandUser(ctx.author, False)} used {ctx.command.name} in {Responses.ExpandGuild(ctx.get_guild(), False)} {Responses.ExpandChannel(ctx.get_channel(), False)}"
        )

    async def PostExecution(
        ctx: MenuContext, config: dict[str, Any] = tanjun.inject(type=dict[str, Any])
    ) -> None:
        """Menu command pre-execution hook."""

        await ctx.rest.create_message(
            config["channels"]["user"],
            Responses.Log(
                "robot",
                f"{Responses.ExpandUser(ctx.author)} used `{ctx.command.name}` in {Responses.ExpandChannel(ctx.get_channel())}",
            ),
        )


class SlashHooks:
    """Logging and error handling hooks for slash commands."""

    async def PreExecution(ctx: SlashContext) -> None:
        """Slash command pre-execution hook."""

        command: str = "/"

        if groupB := ctx.command.parent:
            if groupA := ctx.command.parent.parent:
                command += f"{groupA.name} "

            command += f"{groupB.name} "

        command += ctx.command.name

        logger.info(
            f"{Responses.ExpandUser(ctx.author, False)} used {command} in {Responses.ExpandGuild(ctx.get_guild(), False)} {Responses.ExpandChannel(ctx.get_channel(), False)}"
        )

    async def PostExecution(
        ctx: SlashContext, config: dict[str, Any] = tanjun.inject(type=dict[str, Any])
    ) -> None:
        """Slash command post-execution hook."""

        command: str = "/"

        if groupB := ctx.command.parent:
            if groupA := ctx.command.parent.parent:
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
