from asyncio import sleep
from os import environ

import asyncpraw
from asyncpraw.models import Subreddit
from asyncpraw.models.reddit.submission import Submission
from asyncpraw.reddit import Reddit
from hikari import Embed
from loguru import logger

from core.formatters import Response


async def CreateClient() -> Reddit | None:
    """Create an authenticated Reddit client using the configured credentials."""

    if not (username := environ.get("REDDIT_USERNAME")):
        logger.error("Failed to authenticate with Reddit, username is null")

        return
    elif not (password := environ.get("REDDIT_PASSWORD")):
        logger.error("Failed to authenticate with Reddit, password is null")

        return
    elif not (clientId := environ.get("REDDIT_CLIENT_ID")):
        logger.error("Failed to authenticate with Reddit, clientId is null")

        return
    elif not (clientSecret := environ.get("REDDIT_CLIENT_SECRET")):
        logger.error("Failed to authenticate with Reddit, clientSecret is null")

        return

    client: Reddit = asyncpraw.Reddit(
        username=username,
        password=password,
        client_id=clientId,
        client_secret=clientSecret,
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


async def GetRandomImage(community: str) -> Embed | None:
    """Fetch a random image from the specified Reddit community."""

    client: Reddit | None = await CreateClient()

    if not client:
        logger.debug(
            f"Failed to fetch random image from r/{community}, Reddit client is null"
        )

        return

    subreddit: Subreddit | None = None
    post: Submission | None = None
    valid: bool = False
    attempts: int = 0

    try:
        subreddit = await client.subreddit(community, fetch=True)  # type: ignore

        while not valid:
            if attempts >= 5:
                logger.debug(
                    f"Abandonning search for random image in Reddit community r/{community}, too many attempts"
                )

                await DestroyClient(client)

                return

            post = await subreddit.random()  # type: ignore

            attempts += 1

            if not post:
                logger.warning(
                    f"Reddit community r/{community} does not support submission randomization"
                )

                await DestroyClient(client)

                return

            await post.load()  # type: ignore

            if not post.is_reddit_media_domain:  # type: ignore
                logger.debug("Skipping Reddit post, not native media domain")

                continue
            elif not hasattr(post, "post_hint"):  # type: ignore
                logger.debug("Skipping Reddit post, no post_hint attribute")

                continue
            elif post.post_hint != "image":  # type: ignore
                logger.debug("Skipping Reddit post, post_hint is not image")

                continue
            elif not hasattr(post, "over_18"):  # type: ignore
                logger.debug("Skipping Reddit post, cannot verify safety")

                continue
            elif post.over_18:  # type: ignore
                logger.debug("Skipping Reddit post, is unsafe content")

                continue

            valid = True

        # Sleep to prevent rate-limiting
        await sleep(1)
    except Exception as e:
        logger.opt(exception=e).error(
            f"Failed to fetch random image post from Reddit community r/{community}"
        )

    await DestroyClient(client)

    if not post:
        return

    return Response(
        title=post.title,  # type: ignore
        url=f"https://reddit.com{post.permalink}",  # type: ignore
        image=post.url,  # type: ignore
    )


async def CountModqueue(client: Reddit, community: str) -> int:
    """
    Return the number of items in the moderation queue for the
    specified Reddit community.
    """

    total: int = 0

    subreddit = await client.subreddit(community, fetch=True)  # type: ignore

    if not subreddit:
        logger.error(
            f"Failed to fetch modqueue count for Reddit community r/{community}, subreddit is null"
        )

        return total

    try:
        async for _ in subreddit.mod.modqueue(limit=None):  # type: ignore
            total += 1
    except Exception as e:
        logger.opt(exception=e).error(
            f"Failed to count moderation queue in Reddit community r/{community}"
        )

        return total

    logger.success(
        f"Fetched moderation queue count ({total:,}) for Reddit community r/{community}"
    )

    return total


async def CountUnmoderated(client: Reddit, community: str) -> int:
    """
    Return the number of items in the unmoderated queue for the
    specified Reddit community.
    """

    total: int = 0

    subreddit = await client.subreddit(community, fetch=True)  # type: ignore

    if not subreddit:
        logger.error(
            f"Failed to fetch unmoderated count for Reddit community r/{community}, subreddit is null"
        )

        return total

    try:
        async for _ in subreddit.mod.unmoderated(limit=None):  # type: ignore
            total += 1
    except Exception as e:
        logger.opt(exception=e).error(
            f"Failed to count unmoderated queue in Reddit community r/{community}"
        )

        return total

    logger.success(
        f"Fetched unmoderated queue count ({total:,}) for Reddit community r/{community}"
    )

    return total
