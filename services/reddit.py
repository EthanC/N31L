import asyncio
from typing import Any, Dict, Optional

import asyncpraw
from asyncpraw.models.reddit.submission import Submission
from asyncpraw.models.reddit.subreddit import Subreddit
from asyncpraw.reddit import Reddit
from helpers import Responses
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
            return

        return client

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

                    return

                await post.load()

                if post.is_reddit_media_domain is False:
                    valid = False
                elif (hasattr(post, "post_hint")) and (post.post_hint == "image"):
                    valid = True

            # Sleep to prevent rate-limiting
            asyncio.sleep(float(3))
        except Exception as e:
            logger.error(
                f"Failed to fetch random image post from Reddit community r/{community}, {e}"
            )

        try:
            await client.close()
        except Exception as e:
            logger.warning(f"Failed to close Reddit session, {e}")

        if post is None:
            return

        return Responses.Success(
            title=post.title, url=f"https://reddit.com{post.permalink}", image=post.url
        )
