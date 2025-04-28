from arc import (
    GatewayClient,
    GatewayContext,
    InvokerMissingPermissionsError,
    NotOwnerError,
)
from loguru import logger

from core.config import Config
from core.formatters import (
    Colors,
    expand_channel,
    expand_command,
    expand_server,
    expand_user,
    log,
    random_string,
    response,
)
from extensions.threads import task_archive_threads


async def hook_start(client: GatewayClient) -> None:
    """Handle client startup."""

    task_archive_threads.start(client)


async def hook_stop(client: GatewayClient) -> None:
    """Handle client shutdown."""

    task_archive_threads.cancel()


async def hook_log(ctx: GatewayContext) -> None:
    """Handle command pre-execution."""

    cfg: Config = ctx.client.get_type_dependency(Config)

    command: str = expand_command(ctx, format=False)
    user: str = await expand_user(ctx.user, format=False)
    server: str = await expand_server(ctx.get_guild(), format=False)
    channel: str = await expand_channel(ctx.channel, format=False)

    logger.info(f"Command {command} used by {user} in {server} {channel}")

    user = await expand_user(ctx.user)
    channel = await expand_channel(ctx.channel)

    await ctx.client.rest.create_message(
        cfg.channels["user"],
        log("robot", f"{user} used command `{command}` in {channel}"),
    )


async def hook_error(ctx: GatewayContext, error: Exception) -> None:
    """Handle uncaught command exceptions."""

    command: str = expand_command(ctx, mention=True)

    if isinstance(error, (NotOwnerError, InvokerMissingPermissionsError)):
        await ctx.respond(
            embed=response(
                color=Colors.DISCORD_RED,
                description=f"You don't have permission to use the {command} command.",
            ),
        )

        return

    code: str = random_string(16)

    logger.opt(exception=error).error(
        f"An unhandled {type(error).__qualname__} occurred in command {expand_command(ctx, format=False)} [{code}]"
    )

    await ctx.respond(
        embed=response(
            color=Colors.DISCORD_RED,
            description=f"Try to use the {command} command again later.",
            author="Error",
            authorIcon="https://i.imgur.com/IwCRM6v.png",
            footer=code,
        ),
    )
