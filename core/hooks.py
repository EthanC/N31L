from arc import (
    GatewayClient,
    GatewayContext,
    NotOwnerError,
)
from loguru import logger

from core.config import Config
from core.formatters import (
    Colors,
    ExpandChannel,
    ExpandCommand,
    ExpandServer,
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

    command: str = ExpandCommand(ctx, format=False)
    user: str = ExpandUser(ctx.user, format=False)
    server: str = ExpandServer(ctx.get_guild(), format=False)
    channel: str = ExpandChannel(ctx.get_channel(), format=False)

    logger.info(f"Command {command} used by {user} in {server} {channel}")

    user: str = ExpandUser(ctx.user)
    channel: str = ExpandChannel(ctx.get_channel())

    await ctx.client.rest.create_message(
        cfg.channels["user"],
        Log("robot", f"{user} used command `{command}` in {channel}"),
    )


async def HookError(ctx: GatewayContext, error: Exception) -> None:
    """Handle uncaught command exceptions."""

    command: str = ExpandCommand(ctx, mention=True)

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
        f"An unhandled {type(error).__qualname__} occurred in command {ExpandCommand(ctx, format=False)} [{code}]"
    )

    await ctx.respond(
        embed=Response(
            color=Colors.DiscordRed.value,
            description=f"Try to use the {command} command again later.",
            author="Error",
            authorIcon="https://i.imgur.com/IwCRM6v.png",
            footer=code,
        ),
    )
