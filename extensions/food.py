import random
from asyncio import sleep

import arc
from arc import (
    GatewayClient,
    GatewayContext,
    GatewayPlugin,
    Option,
    StrParams,
)
from hikari import Embed
from loguru import logger

from core.food import Foodish
from core.hooks import HookError, HookLog

plugin: GatewayPlugin = GatewayPlugin("food")
foodTypes: list[str] = [
    "Burger",
    "Chicken",
    "Dessert",
    "Pasta",
    "Pizza",
    "Rice",
]


@arc.loader
def ExtensionLoader(client: GatewayClient) -> None:
    """Required. Called upon loading the extension."""

    logger.debug(f"Attempting to load {plugin.name} extension...")
    logger.trace(plugin)

    try:
        client.add_plugin(plugin)
    except Exception as e:
        logger.opt(exception=e).error(f"Failed to load {plugin.name} extension")


@plugin.include
@arc.with_hook(HookLog)
@arc.slash_command("food", "Fetch a random picture of food.")
async def CommandFood(
    ctx: GatewayContext,
    type: Option[
        str | None,
        StrParams("Choose a food type or leave empty for random.", choices=foodTypes),
    ] = None,
) -> None:
    """Handler for the /food command."""

    result: Embed | None = None
    retries: int = 0

    while not result:
        match type:
            case "Burger":
                result = await Foodish("burger")
            case "Chicken":
                result = await Foodish("butter-chicken")
            case "Dessert":
                result = await Foodish("dessert")
            case "Pasta":
                result = await Foodish("pasta")
            case "Pizza":
                result = await Foodish("pizza")
            case "Rice":
                result = await Foodish("rice")
            case _:
                # type is expected to be null if not provided
                if type:
                    logger.warning(f"Recieved unknown food type {type}")

                type = random.choice(foodTypes)

                continue

        if not result:
            retries += 1

            if retries >= 3:
                raise RuntimeError("maximum retries exceeded")

            # Sleep to prevent rate-limiting
            await sleep(1)

    await ctx.respond(embed=result)


@plugin.set_error_handler
async def ErrorHandler(ctx: GatewayContext, error: Exception) -> None:
    """Handler for errors originating from this plugin."""

    await HookError(ctx, error)
