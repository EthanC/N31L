from arc import GatewayClient, GatewayContext, NotOwnerError, SlashCommand
from loguru import logger

from core.formatters import Colors, ExpandUser, RandomString, Response
from extensions.threads import TaskArchiveThreads


async def HookStart(client: GatewayClient) -> None:
    """Handle client startup."""

    TaskArchiveThreads.start(client)


async def HookStop(client: GatewayClient) -> None:
    """Handle client shutdown."""

    TaskArchiveThreads.cancel()


def HookLog(ctx: GatewayContext) -> None:
    """Handle command pre-execution."""

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
