import arc
from arc import (
    GatewayClient,
    GatewayContext,
    GatewayPlugin,
    Option,
    SlashGroup,
    StrParams,
)
from asyncpraw.reddit import Reddit
from loguru import logger

from core.config import Config
from core.formatters import Response
from core.hooks import HookError, HookLog
from core.reddit import CountModqueue, CountUnmoderated, CreateClient, DestroyClient

plugin: GatewayPlugin = GatewayPlugin("reddit")
group: SlashGroup[GatewayClient] = plugin.include_slash_group(
    "reddit", "Commands to manage Reddit communities."
)
communities: dict[str, str] = {
    "r/BlackOps6": "BlackOps6",
    "r/ModernWarfareIII": "ModernWarfareIII",
    "r/ModernWarfareII": "ModernWarfareII",
    "r/CODVanguard": "CODVanguard",
    "r/BlackOpsColdWar": "BlackOpsColdWar",
    "r/CODWarzone": "CODWarzone",
    "r/ModernWarfare": "ModernWarfare",
    "r/BlackOps4": "BlackOps4",
    "r/WWII": "WWII",
    "r/InfiniteWarfare": "InfiniteWarfare",
    "r/CODZombies": "CODZombies",
    "r/CallofDuty": "CallofDuty",
}


@arc.loader
def ExtensionLoader(client: GatewayClient) -> None:
    """Required. Called upon loading the extension."""

    logger.debug(f"Attempting to load {plugin.name} extension...")
    logger.trace(plugin)

    try:
        client.add_plugin(plugin)
    except Exception as e:
        logger.opt(exception=e).error(f"Failed to load {plugin.name} extension")


@group.include
@arc.with_hook(HookLog)
@arc.slash_subcommand(
    "queue",
    "Fetch the moderation and unmoderated queue counts for the specified Reddit community.",
)
async def CommandRedditQueue(
    ctx: GatewayContext,
    community: Option[
        str | None,
        StrParams(
            "Choose a Reddit community to fetch queue counts for or leave empty for all.",
            choices=communities,
        ),
    ] = None,
) -> None:
    """Handler for the /reddit queue command."""

    cfg: Config = ctx.client.get_type_dependency(Config)

    if ctx.channel_id != cfg.channels["reddit"]:
        raise RuntimeError("Disallowed outside of designated Reddit channel")

    client: Reddit | None = await CreateClient()

    if not client:
        raise RuntimeError("Reddit client is null")

    requested: list[str] | None = None
    results: list[dict[str, str | bool]] = []

    # Request all communities if none is specified
    if not community:
        requested = list(communities.values())
    else:
        requested = [community]

    for request in requested:
        mod: int = await CountModqueue(client, request)
        unmod: int = await CountUnmoderated(client, request)

        results.append(
            {
                "name": f"r/{request}",
                "value": f"Moderation: [{mod:,}](https://reddit.com/{request}/about/modqueue)\nUnmoderated: [{unmod:,}](https://reddit.com/{request}/about/unmoderated)",
            }
        )

    await DestroyClient(client)

    await ctx.respond(
        embed=Response(
            color="FF4500",
            fields=results,
            author="Reddit",
            authorUrl="https://www.reddit.com/r/Mod/",
            authorIcon="https://i.imgur.com/yZujOa5.png",
        )
    )


@plugin.set_error_handler
async def ErrorHandler(ctx: GatewayContext, error: Exception) -> None:
    """Handler for errors originating from this plugin."""

    await HookError(ctx, error)
