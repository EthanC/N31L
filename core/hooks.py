from arc import GatewayClient, GatewayContext, NotOwnerError, SlashCommand
from loguru import logger

from core.config import Config
from core.formatters import (
    Colors,
    ExpandChannel,
    ExpandUser,
    Log,
    RandomString,
    Response,
)
from extensions.threads import TaskArchiveThreads


async def HookStart(client: GatewayClient) -> None:
    """Handle client startup."""

    TaskArchiveThreads.start(client)


async def HookStop(client: GatewayClient) -> None:
    """Handle client shutdown."""

    TaskArchiveThreads.cancel()


async def HookLog(ctx: GatewayContext) -> None:
    """Handle command pre-execution."""

    cfg: Config = ctx.client.get_type_dependency(Config)

    command: str = ctx.command.name
    user: str = ExpandUser(ctx.user, format=False)
    location: str = "Unknown"

    if isinstance(ctx.command, SlashCommand):
        command = f"/{ctx.command.name}"

    if guild := ctx.get_guild():
        location = f"{guild.name} ({ctx.guild_id})"
    else:
        location = f"{ctx.guild_id}"

    if channel := ctx.get_channel():
        location += f" #{channel.name} ({ctx.channel_id})"
    else:
        location += f" {ctx.channel_id}"

    logger.info(f"Command {command} used by {user} in {location}")

    if isinstance(ctx.command, SlashCommand):
        command = ctx.command.make_mention()
    else:
        command = f"`{ctx.command.name}`"

    await ctx.client.rest.create_message(
        cfg.channels["user"],
        Log(
            "robot",
            f"{ExpandUser(ctx.author)} used command {command} in {ExpandChannel(ctx.get_channel())}",
        ),
    )


async def HookError(ctx: GatewayContext, error: Exception) -> None:
    """Handle uncaught command exceptions."""

    command: str = f"`{ctx.command.name}`"

    if isinstance(ctx.command, SlashCommand):
        command = ctx.command.make_mention()

    if isinstance(error, NotOwnerError):
        await ctx.respond(
            embed=Response(
                color=Colors.DiscordRed.value,
                description=f"You don't have permission to use the {command} command.",
            ),
        )

        return

    code: str = RandomString(16)

    logger.opt(exception=error).error(
        f"An unhandled {type(error).__qualname__} exception occurred in command {command} ({code})"
    )

    await ctx.respond(
        embed=Response(
            title="An unknown error occurred",
            color=Colors.DiscordRed.value,
            description=f"Try to use the {command} command again later.",
            footer=code,
            footerIcon="https://i.imgur.com/IwCRM6v.png",
        ),
    )
