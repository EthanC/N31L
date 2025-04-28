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

from core.food import foodish
from core.hooks import hook_error, hook_log

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
def extension_loader(client: GatewayClient) -> None:
    """Required. Called upon loading the extension."""

    logger.debug(f"Attempting to load {plugin.name} extension...")
    logger.trace(plugin)

    try:
        client.add_plugin(plugin)
    except Exception as e:
        logger.opt(exception=e).error(f"Failed to load {plugin.name} extension")


@plugin.include
@arc.with_hook(hook_log)
@arc.slash_command("food", "Fetch a random picture of food.")
async def command_food(
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
                result = await foodish("burger")
            case "Chicken":
                result = await foodish("butter-chicken")
            case "Dessert":
                result = await foodish("dessert")
            case "Pasta":
                result = await foodish("pasta")
            case "Pizza":
                result = await foodish("pizza")
            case "Rice":
                result = await foodish("rice")
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
async def error_handler(ctx: GatewayContext, error: Exception) -> None:
    """Handler for errors originating from this plugin."""

    await hook_error(ctx, error)
