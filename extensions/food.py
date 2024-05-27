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
from core.reddit import GetRandomImage

plugin: GatewayPlugin = GatewayPlugin("food")
foodTypes: list[str] = [
    "Burger",
    "Chicken",
    "Dessert",
    "Hot Dog",
    "Pasta",
    "Pizza",
    "Rice",
    "Salad",
    "Sandwich",
    "Steak",
    "Sushi",
    "Taco",
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
    source: int = 1
    retries: int = 0

    while not result:
        match type:
            case "Burger":
                source = random.randint(1, 4)

                match source:
                    case 1:
                        result = await GetRandomImage("BobsBurgersCreations")
                    case 2:
                        result = await GetRandomImage("burgers")
                    case 3:
                        result = await GetRandomImage("cheeseburgers")
                    case 4:
                        result = await Foodish("burger")
                    case _:
                        logger.warning(
                            f"Recieved unknown source {source} for food type {type}"
                        )
            case "Chicken":
                source = random.randint(1, 3)

                match source:
                    case 1:
                        result = await GetRandomImage("FriedChicken")
                    case 2:
                        result = await GetRandomImage("Wings")
                    case 3:
                        result = await Foodish("butter-chicken")
                    case _:
                        logger.warning(
                            f"Recieved unknown source {source} for food type {type}"
                        )
            case "Dessert":
                source = random.randint(1, 11)

                match source:
                    case 1:
                        result = await GetRandomImage("Baking")
                    case 2:
                        result = await GetRandomImage("cake")
                    case 3:
                        result = await GetRandomImage("cakedecorating")
                    case 4:
                        result = await GetRandomImage("cheesecake")
                    case 5:
                        result = await GetRandomImage("Cookies")
                    case 6:
                        result = await GetRandomImage("dessert")
                    case 7:
                        result = await GetRandomImage("desserts")
                    case 8:
                        result = await GetRandomImage("DessertPorn")
                    case 9:
                        result = await GetRandomImage("icecreamery")
                    case 10:
                        result = await GetRandomImage("pie")
                    case 11:
                        result = await Foodish("dessert")
                    case _:
                        logger.warning(
                            f"Recieved unknown source {source} for food type {type}"
                        )
            case "Hot Dog":
                source = random.randint(1, 2)

                match source:
                    case 1:
                        result = await GetRandomImage("hot_dog")
                    case 2:
                        result = await GetRandomImage("hotdogs")
                    case _:
                        logger.warning(
                            f"Recieved unknown source {source} for food type {type}"
                        )
            case "Pasta":
                source = random.randint(1, 2)

                match source:
                    case 1:
                        result = await GetRandomImage("pasta")
                    case 2:
                        result = await Foodish("pasta")
                    case _:
                        logger.warning(
                            f"Recieved unknown source {source} for food type {type}"
                        )
            case "Pizza":
                source = random.randint(1, 4)

                match source:
                    case 1:
                        result = await GetRandomImage("CatsOnPizza")
                    case 2:
                        result = await GetRandomImage("Pizza")
                    case 3:
                        result = await GetRandomImage("PizzaCrimes")
                    case 4:
                        result = await Foodish("pizza")
                    case _:
                        logger.warning(
                            f"Recieved unknown source {source} for food type {type}"
                        )
            case "Rice":
                source = random.randint(1, 2)

                match source:
                    case 1:
                        result = await GetRandomImage("RICE")
                    case 2:
                        result = await Foodish("rice")
                    case _:
                        logger.warning(
                            f"Recieved unknown source {source} for food type {type}"
                        )
            case "Salad":
                source = random.randint(1, 2)

                match source:
                    case 1:
                        result = await GetRandomImage("salad")
                    case 2:
                        result = await GetRandomImage("salads")
                    case _:
                        logger.warning(
                            f"Recieved unknown source {source} for food type {type}"
                        )
            case "Sandwich":
                source = random.randint(1, 3)

                match source:
                    case 1:
                        result = await GetRandomImage("eatsandwiches")
                    case 2:
                        result = await GetRandomImage("grilledcheese")
                    case 3:
                        result = await GetRandomImage("Sandwich")
                    case _:
                        logger.warning(
                            f"Recieved unknown source {source} for food type {type}"
                        )
            case "Steak":
                source = random.randint(1, 3)

                match source:
                    case 1:
                        result = await GetRandomImage("steak")
                    case 2:
                        result = await GetRandomImage("steakcrimes")
                    case 3:
                        result = await GetRandomImage("SteakorTuna")
                    case _:
                        logger.warning(
                            f"Recieved unknown source {source} for food type {type}"
                        )
            case "Sushi":
                source = random.randint(1, 3)

                match source:
                    case 1:
                        result = await GetRandomImage("sushi")
                    case 2:
                        result = await GetRandomImage("SushiAbomination")
                    case 3:
                        result = await GetRandomImage("SushiRoll")
                    case _:
                        logger.warning(
                            f"Recieved unknown source {source} for food type {type}"
                        )
            case "Taco":
                match source:
                    case 1:
                        result = await GetRandomImage("tacos")
                    case _:
                        logger.warning(
                            f"Recieved unknown source {source} for food type {type}"
                        )
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
