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
from core.formatters import response
from core.hooks import hook_error, hook_log
from core.reddit import client_create, client_destroy, count_modqueue, count_unmoderated

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
def extension_loader(client: GatewayClient) -> None:
    """Required. Called upon loading the extension."""

    logger.debug(f"Attempting to load {plugin.name} extension...")
    logger.trace(plugin)

    try:
        client.add_plugin(plugin)
    except Exception as e:
        logger.opt(exception=e).error(f"Failed to load {plugin.name} extension")


@group.include
@arc.with_hook(hook_log)
@arc.slash_subcommand(
    "queue",
    "Fetch the moderation and unmoderated queue counts for the specified Reddit community.",
)
async def command_reddit_queue(
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

    client: Reddit | None = await client_create()

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
        mod: int = await count_modqueue(client, request)
        unmod: int = await count_unmoderated(client, request)

        results.append(
            {
                "name": f"r/{request}",
                "value": f"Moderation: [{mod:,}](https://reddit.com/{request}/about/modqueue)\nUnmoderated: [{unmod:,}](https://reddit.com/{request}/about/unmoderated)",
            }
        )

    await client_destroy(client)

    await ctx.respond(
        embed=response(
            color="FF4500",
            fields=results,
            author="Reddit",
            authorUrl="https://www.reddit.com/r/Mod/",
            authorIcon="https://i.imgur.com/yZujOa5.png",
        )
    )


@plugin.set_error_handler
async def error_handler(ctx: GatewayContext, error: Exception) -> None:
    """Handler for errors originating from this plugin."""

    await hook_error(ctx, error)
