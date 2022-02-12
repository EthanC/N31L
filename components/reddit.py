from typing import Any, Dict, List, Optional

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
communities: Dict[str, str] = {
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


@reddit.with_command
@tanjun.with_str_slash_option(
    "community",
    "Choose a Reddit community to fetch queue counts for or leave empty for all.",
    choices=communities,
    default=None,
)
@tanjun.as_slash_command(
    "queue",
    "Fetch the moderation and unmoderated queue counts for the specified Reddit community.",
    default_permission=False,
)
async def CommandRedditQueue(
    ctx: SlashContext,
    community: Optional[str],
    config: Dict[str, Any] = tanjun.inject(type=Dict[str, Any]),
) -> None:
    """Handler for the /reddit queue command."""

    if config.get("debug") is not True:
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
            embed=Responses.Fail(
                description="Failed to authenticate with Reddit, an unknown error occurred."
            )
        )

        return

    if community is None:
        results: List[Dict[str, Any]] = []

        for entry in communities:
            subreddit: Optional[Subreddit] = await Reddit.GetSubreddit(
                client, communities[entry]
            )

            if subreddit is None:
                continue

            mod: int = await Reddit.CountModqueue(client, subreddit)
            unmod: int = await Reddit.CountUnmoderated(client, subreddit)

            results.append(
                {
                    "name": entry,
                    "value": f"Moderation: [{mod:,}](https://reddit.com/{entry}/about/modqueue)\nUnmoderated: [{unmod:,}](https://reddit.com/{entry}/about/unmoderated)",
                }
            )

        await Reddit.DestroyClient(client)

        if len(results) == 0:
            await ctx.respond(
                embed=Responses.Fail(
                    description="Failed to fetch queue counts for all Reddit communities, an unknown error occurred."
                )
            )

            return

        await ctx.respond(
            embed=Responses.Success(
                color="FF4500",
                fields=results,
                author="Reddit",
                authorUrl="https://www.reddit.com/r/Mod/",
                authorIcon="https://i.imgur.com/yZujOa5.png",
            )
        )

        logger.success("Fetched queue counts for all Reddit communities")

        return

    subreddit: Subreddit = await Reddit.GetSubreddit(client, community)

    if subreddit is None:
        await Reddit.DestroyClient(client)

        await ctx.respond(
            embed=Responses.Fail(
                description=f"Failed to fetch Reddit community r/{community}, an unknown error occurred."
            )
        )

        return

    mod: int = await Reddit.CountModqueue(client, subreddit)
    unmod: int = await Reddit.CountUnmoderated(client, subreddit)

    await Reddit.DestroyClient(client)

    await ctx.respond(
        embed=Responses.Success(
            color=subreddit.primary_color,
            fields=[
                {
                    "name": "Moderation",
                    "value": f"[{mod:,}](https://reddit.com/r/{community}/about/modqueue)",
                },
                {
                    "name": "Unmoderated",
                    "value": f"[{unmod:,}](https://reddit.com/r/{community}/about/unmoderated)",
                },
            ],
            author=f"r/{community}",
            authorUrl=f"https://www.reddit.com/r/{community}",
            authorIcon=subreddit.community_icon,
        )
    )

    logger.success(f"Fetched queue counts for Reddit community r/{community}")
