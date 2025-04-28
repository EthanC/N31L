import asyncpraw
from asyncpraw.reddit import Reddit
from environs import env
from loguru import logger


async def client_create() -> Reddit | None:
    """Create an authenticated Reddit client using the configured credentials."""

    if not (username := env.str("REDDIT_USERNAME")):
        logger.error("Failed to authenticate with Reddit, username is null")

        return
    elif not (password := env.str("REDDIT_PASSWORD")):
        logger.error("Failed to authenticate with Reddit, password is null")

        return
    elif not (client_id := env.str("REDDIT_CLIENT_ID")):
        logger.error("Failed to authenticate with Reddit, client_id is null")

        return
    elif not (client_secret := env.str("REDDIT_CLIENT_SECRET")):
        logger.error("Failed to authenticate with Reddit, client_secret is null")

        return

    client: Reddit = asyncpraw.Reddit(
        username=username,
        password=password,
        client_id=client_id,
        client_secret=client_secret,
        user_agent="https://github.com/EthanC/N31L",
    )

    if client.read_only:
        logger.error("Failed to authenticate with Reddit, client is read-only")

        return

    return client


async def client_destroy(client: Reddit) -> None:
    """Close the provided Reddit requestor."""

    try:
        await client.close()
    except Exception as e:
        logger.opt(exception=e).warning("Failed to close Reddit session")


async def count_modqueue(client: Reddit, community: str) -> int:
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


async def count_unmoderated(client: Reddit, community: str) -> int:
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
