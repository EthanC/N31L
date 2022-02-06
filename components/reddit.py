from typing import Any, Dict, Optional

import tanjun
from asyncpraw.models.reddit.subreddit import Subreddit
from asyncpraw.reddit import Reddit
from helpers import Responses
from loguru import logger
from services import Reddit
from tanjun import Component, SlashCommandGroup
from tanjun.abc import SlashContext

component: Component = Component(name="Reddit")

reddit: SlashCommandGroup = component.with_slash_command(
    tanjun.slash_command_group("reddit", "Slash Commands to manage Reddit communities.")
)


@reddit.with_command
@tanjun.with_str_slash_option(
    "community",
    "Choose a Reddit community to fetch queue counts for.",
    choices={
        "r/CODVanguard": "CODVanguard",
        "r/BlackOpsColdWar": "BlackOpsColdWar",
        "r/CODWarzone": "CODWarzone",
        "r/ModernWarfare": "ModernWarfare",
        "r/BlackOps4": "BlackOps4",
        "r/WWII": "WWII",
        "r/InfiniteWarfare": "InfiniteWarfare",
        "r/CODZombies": "CODZombies",
        "r/CallofDuty": "CallofDuty",
    },
)
@tanjun.as_slash_command(
    "queue",
    "Fetch the moderation and unmoderated queue counts for the specified Reddit community.",
    default_permission=False,
)
async def CommandRedditQueue(
    ctx: SlashContext,
    community: str,
    config: Dict[str, Any] = tanjun.inject(type=Dict[str, Any]),
) -> None:
    """Handler for the /reddit queue command."""

    if int(ctx.channel_id) != (req := config["channels"]["redditModerators"]):
        await ctx.respond(
            embed=Responses.Fail(
                description=f"This command can only be used in <#{req}>."
            )
        )

        return

    client: Optional[Reddit] = await Reddit.CreateClient(
        config["credentials"]["reddit"]
    )

    if client is None:
        await ctx.respond(
            embed=Responses.Fail(description="Failed to authenticate with Reddit.")
        )

        return

    subreddit: Optional[Subreddit] = None

    try:
        subreddit = await client.subreddit(community, fetch=True)
    except Exception as e:
        logger.error(f"Failed to fetch Reddit community r/{community}, {e}")

    if subreddit is None:
        await ctx.respond(
            embed=Responses.Fail(
                description=f"Failed to fetch Reddit community r/{community}."
            )
        )

        await Reddit.DestroyClient(client)

        return

    mod: int = 0
    unmod: int = 0

    try:
        async for _ in subreddit.mod.modqueue(limit=None):
            mod += 1
    except Exception as e:
        logger.error(
            f"Failed to count moderation queue in Reddit community r/{community}, {e}"
        )

    try:
        async for _ in subreddit.mod.unmoderated(limit=None):
            unmod += 1
    except Exception as e:
        logger.error(
            f"Failed to count unmoderated queue in Reddit community r/{community}, {e}"
        )

    await Reddit.DestroyClient(client)

    await ctx.respond(
        embed=Responses.Success(
            color=subreddit.primary_color,
            fields=[
                {
                    "name": "Moderation",
                    "value": f"[{mod:,}](https://www.reddit.com/r/{community}/about/modqueue)",
                    "inline": True,
                },
                {
                    "name": "Unmoderated",
                    "value": f"[{unmod:,}](https://www.reddit.com/r/{community}/about/unmoderated)",
                    "inline": True,
                },
            ],
            author=f"r/{community}",
            authorUrl=f"https://www.reddit.com/r/{community}",
            authorIcon=subreddit.community_icon,
        )
    )
