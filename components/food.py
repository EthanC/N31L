import asyncio
import random
from typing import Any, Dict, List, Optional

import tanjun
from helpers import Responses
from hikari import Permissions
from hikari.embeds import Embed
from services import (
    Burger,
    Dessert,
    HotDog,
    Pasta,
    Pizza,
    Rice,
    Salad,
    Sandwich,
    Sushi,
    Taco,
)
from services.food import Pasta
from tanjun import Component
from tanjun.abc import SlashContext

component: Component = Component(name="Food")
foodTypes: List[str] = [
    "Burger",
    "Dessert",
    "Hot Dog",
    "Pasta",
    "Pizza",
    "Rice",
    "Salad",
    "Sandwich",
    "Sushi",
    "Taco",
]


@component.with_slash_command()
@tanjun.with_own_permission_check(Permissions.SEND_MESSAGES)
@tanjun.with_str_slash_option(
    "type",
    "Choose a food type or leave empty for random.",
    choices=foodTypes,
    default=None,
)
@tanjun.as_slash_command("food", "Fetch a random picture of food.")
async def CommandFood(
    ctx: SlashContext,
    type: Optional[str],
    config: Dict[str, Any] = tanjun.inject(type=Dict[str, Any]),
) -> None:
    """Handler for the /food command."""

    if type is None:
        type = random.choice(foodTypes)

    redditLogin: Dict[str, str] = config["credentials"]["reddit"]

    result: Optional[Embed] = None
    source: int = 1
    retries: int = 0

    while result is None:
        if type == "Burger":
            source = random.randint(1, 2)

            if source == 1:
                result = await Burger.Foodish()
            elif source == 2:
                result = await Burger.RedditBurgers(redditLogin)
        elif type == "Dessert":
            source = random.randint(1, 8)

            if source == 1:
                result = await Dessert.Foodish()
            elif source == 2:
                result = await Dessert.RedditCake(redditLogin)
            elif source == 3:
                result = await Dessert.RedditCookies(redditLogin)
            elif source == 4:
                result = await Dessert.RedditCupcakes(redditLogin)
            elif source == 5:
                result = await Dessert.RedditDessert(redditLogin)
            elif source == 6:
                result = await Dessert.RedditDessertPorn(redditLogin)
            elif source == 7:
                result = await Dessert.RedditIcecreamery(redditLogin)
            elif source == 8:
                result = await Dessert.RedditPie(redditLogin)
        elif type == "Hot Dog":
            result = await HotDog.RedditHotDogs(redditLogin)
        elif type == "Pasta":
            source = random.randint(1, 2)

            if source == 1:
                result = await Pasta.Foodish()
            elif source == 2:
                result = await Pasta.RedditPasta(redditLogin)
        elif type == "Pizza":
            source = random.randint(1, 2)

            if source == 1:
                result = await Pizza.Foodish()
            elif source == 2:
                result = await Pizza.RedditPizza(redditLogin)
        elif type == "Rice":
            result = await Rice.Foodish()
        elif type == "Salad":
            result = await Salad.RedditSalads(redditLogin)
        elif type == "Sandwich":
            source = random.randint(1, 3)

            if source == 1:
                result = await Sandwich.RedditEatSandwiches(redditLogin)
            if source == 2:
                result = await Sandwich.RedditGrilledCheese(redditLogin)
            elif source == 3:
                result = await Sandwich.RedditSandwiches(redditLogin)
        elif type == "Sushi":
            result = await Sushi.RedditSushi(redditLogin)
        elif type == "Taco":
            result = await Taco.RedditTacos(redditLogin)

        retries += 1

        if retries >= 3:
            await ctx.respond(
                embed=Responses.Fail(
                    description=f"Failed to fetch {type}, an unknown error occurred."
                )
            )

            return

        # Sleep to prevent rate-limiting
        await asyncio.sleep(float(1))

    await ctx.respond(embed=result)
