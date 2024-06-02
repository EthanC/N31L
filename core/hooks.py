from arc import (
    GatewayClient,
    GatewayContext,
    NotOwnerError,
    SlashCommand,
    SlashSubCommand,
    SlashSubGroup,
)
from loguru import logger

from core.config import Config
from core.formatters import (
    Colors,
    ExpandChannel,
    ExpandGuild,
    ExpandUser,
    FormatOptions,
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
    location: str = f"{ExpandGuild(ctx.get_guild(), False)} {ExpandChannel(ctx.get_channel(), False)}"

    if isinstance(ctx.command, SlashSubCommand):
        if isinstance(ctx.command.parent, SlashSubGroup):
            command = f"/{ctx.command.parent.parent.name} {ctx.command.parent.name} {ctx.command.name}"
        else:
            command = f"/{ctx.command.parent.name} {ctx.command.name}"
    elif isinstance(ctx.command, SlashCommand):
        command = f"/{ctx.command.name}"

    if hasattr(ctx, "_options") and ctx._options:  # type: ignore
        command += f" {FormatOptions(ctx._options)}"  # type: ignore

    logger.info(f"Command {command} used by {user} in {location}")

    await ctx.client.rest.create_message(
        cfg.channels["user"],
        Log(
            "robot",
            f"{ExpandUser(ctx.author)} used command `{command}` in {ExpandChannel(ctx.get_channel())}",
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
