import asyncio
from os import environ
from typing import Optional

import asyncpraw
from asyncpraw.models.reddit.submission import Submission
from asyncpraw.models.reddit.subreddit import Subreddit
from asyncpraw.reddit import Reddit
from hikari.embeds import Embed
from loguru import logger

from helpers import Responses, Utility


class Reddit:
    """Class containing generic Reddit functions."""

    async def CreateClient() -> Optional[Reddit]:
        """Create an authenticated Reddit client using the configured credentials."""

        client: Reddit = asyncpraw.Reddit(
            username=environ.get("REDDIT_USERNAME"),
            password=environ.get("REDDIT_PASSWORD"),
            client_id=environ.get("REDDIT_CLIENT_ID"),
            client_secret=environ.get("REDDIT_CLIENT_SECRET"),
            user_agent="https://github.com/EthanC/N31L",
        )

        if client.read_only:
            logger.error("Failed to authenticate with Reddit, client is read-only")

            return

        return client

    async def DestroyClient(client: Reddit) -> None:
        """Close the provided Reddit requestor."""

        try:
            await client.close()
        except Exception as e:
            logger.opt(exception=e).warning("Failed to close Reddit session")

    async def GetSubreddit(client: Reddit, community: str) -> Optional[Subreddit]:
        """Fetch the subreddit object for the specified Reddit community."""

        try:
            return await client.subreddit(community, fetch=True)
        except Exception as e:
            logger.opt(exception=e).error(
                f"Failed to fetch Reddit community r/{community}"
            )

    async def CountModqueue(client: Reddit, community: Subreddit) -> int:
        """
        Return the number of items in the moderation queue for the
        specified Reddit community.
        """

        total: int = 0

        try:
            async for _ in community.mod.modqueue(limit=None):
                total += 1
        except Exception as e:
            logger.opt(exception=e).error(
                f"Failed to count moderation queue in Reddit community r/{community.display_name}"
            )

            return total

        logger.success(
            f"Fetched moderation queue count ({total:,}) for Reddit community r/{community.display_name}"
        )

        return total

    async def CountUnmoderated(client: Reddit, community: Subreddit) -> int:
        """
        Return the number of items in the unmoderated queue for the
        specified Reddit community.
        """

        total: int = 0

        try:
            async for _ in community.mod.unmoderated(limit=None):
                total += 1
        except Exception as e:
            logger.opt(exception=e).error(
                f"Failed to count unmoderated queue in Reddit community r/{community.display_name}"
            )

            return total

        logger.success(
            f"Fetched unmoderated queue count ({total:,}) for Reddit community r/{community.display_name}"
        )

        return total

    async def GetRandomImage(community: str) -> Optional[Embed]:
        """Fetch a random image from the specified Reddit community."""

        client: Optional[Reddit] = await Reddit.CreateClient()

        if client is None:
            return

        subreddit: Optional[Subreddit] = None
        post: Optional[Submission] = None
        valid: bool = False
        attempts: int = 0

        try:
            subreddit = await client.subreddit(community, fetch=True)

            while not valid:
                if attempts >= 5:
                    logger.debug(
                        f"Abandonning search for random image in Reddit community r/{community}, too many attempts"
                    )

                    await Reddit.DestroyClient(client)

                    return

                post = await subreddit.random()

                attempts += 1

                if post is None:
                    logger.warning(
                        f"Reddit community r/{community} does not support submission randomization"
                    )

                    await Reddit.DestroyClient(client)

                    return

                await post.load()

                if not post.is_reddit_media_domain:
                    continue
                elif not hasattr(post, "post_hint"):
                    continue
                elif post.post_hint != "image":
                    continue
                elif not hasattr(post, "over_18"):
                    continue
                elif post.over_18:
                    continue

                valid = True

            # Sleep to prevent rate-limiting
            await asyncio.sleep(float(1))
        except Exception as e:
            logger.opt(exception=e).error(
                f"Failed to fetch random image post from Reddit community r/{community}"
            )

        await Reddit.DestroyClient(client)

        if post is None:
            return

        return Responses.Success(
            title=Utility.Trim(post.title, 25),
            url=f"https://reddit.com{post.permalink}",
            color=None,
            image=post.url,
        )
