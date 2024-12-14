from os import environ

import asyncpraw
from asyncpraw.reddit import Reddit
from loguru import logger


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
