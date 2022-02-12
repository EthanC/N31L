import asyncio
from typing import Any, Dict, Optional

import asyncpraw
from asyncpraw.models.reddit.submission import Submission
from asyncpraw.models.reddit.subreddit import Subreddit
from asyncpraw.reddit import Reddit
from helpers import Responses, Utility
from hikari.embeds import Embed
from loguru import logger


class Reddit:
    """Class containing generic Reddit functions."""

    async def CreateClient(credentials: Dict[str, Any]) -> Optional[Reddit]:
        """Create an authenticated Reddit client using the provided credentials."""

        client: Reddit = asyncpraw.Reddit(
            username=credentials["username"],
            password=credentials["password"],
            client_id=credentials["clientId"],
            client_secret=credentials["clientSecret"],
            user_agent=credentials["userAgent"],
        )

        if client.read_only is True:
            logger.error("Failed to authenticate with Reddit, client is read-only")

            return

        return client

    async def DestroyClient(client: Reddit) -> None:
        """Close the provided Reddit requestor."""

        try:
            await client.close()
        except Exception as e:
            logger.warning(f"Failed to close Reddit session, {e}")

    async def GetSubreddit(client: Reddit, community: str) -> Optional[Subreddit]:
        """Fetch the subreddit object for the specified Reddit community."""

        try:
            return await client.subreddit(community, fetch=True)
        except Exception as e:
            logger.error(f"Failed to fetch Reddit community r/{community}, {e}")

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
            logger.error(
                f"Failed to count moderation queue in Reddit community r/{community.display_name}, {e}"
            )

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
            logger.error(
                f"Failed to count unmoderated queue in Reddit community r/{community.display_name}, {e}"
            )

        logger.success(
            f"Fetched unmoderated queue count ({total:,}) for Reddit community r/{community.display_name}"
        )

        return total

    async def GetRandomImage(
        community: str, credentials: Dict[str, Any]
    ) -> Optional[Embed]:
        """Fetch a random image from the specified Reddit community."""

        client: Optional[Reddit] = await Reddit.CreateClient(credentials)

        if client is None:
            return

        subreddit: Optional[Subreddit] = None
        post: Optional[Submission] = None
        valid: bool = False

        try:
            subreddit = await client.subreddit(community, fetch=True)

            while valid is False:
                post = await subreddit.random()

                if post is None:
                    logger.warning(
                        f"Reddit community r/{community} does not support submission randomization"
                    )

                    await Reddit.DestroyClient(client)

                    return

                await post.load()

                if post.is_reddit_media_domain is False:
                    continue
                elif hasattr(post, "post_hint") is False:
                    continue
                elif post.post_hint != "image":
                    continue
                elif hasattr(post, "over_18") is False:
                    continue
                elif post.over_18 is True:
                    continue

                valid = True

            # Sleep to prevent rate-limiting
            await asyncio.sleep(float(1))
        except Exception as e:
            logger.error(
                f"Failed to fetch random image post from Reddit community r/{community}, {e}"
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
