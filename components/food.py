import asyncio
import random
from typing import List, Optional

import tanjun
from hikari import Permissions
from hikari.embeds import Embed
from tanjun import Component
from tanjun.abc import SlashContext

from helpers import Responses
from services import Burger, Dessert, HotDog, Pasta, Pizza, Salad, Sandwich, Sushi, Taco

component: Component = Component(name="Food")
foodTypes: List[str] = [
    "Burger",
    "Dessert",
    "Hot Dog",
    "Pasta",
    "Pizza",
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
async def CommandFood(ctx: SlashContext, type: Optional[str]) -> None:
    """Handler for the /food command."""

    if type is None:
        type = random.choice(foodTypes)

    result: Optional[Embed] = None
    source: int = 1
    retries: int = 0

    while result is None:
        if type == "Burger":
            result = await Burger.RedditBurgers()
        elif type == "Dessert":
            source = random.randint(1, 7)

            if source == 1:
                result = await Dessert.RedditCake()
            elif source == 2:
                result = await Dessert.RedditCookies()
            elif source == 3:
                result = await Dessert.RedditCupcakes()
            elif source == 4:
                result = await Dessert.RedditDessert()
            elif source == 5:
                result = await Dessert.RedditDessertPorn()
            elif source == 6:
                result = await Dessert.RedditIcecreamery()
            elif source == 7:
                result = await Dessert.RedditPie()
        elif type == "Hot Dog":
            result = await HotDog.RedditHotDogs()
        elif type == "Pasta":
            result = await Pasta.RedditPasta()
        elif type == "Pizza":
            result = await Pizza.RedditPizza()
        elif type == "Salad":
            result = await Salad.RedditSalads()
        elif type == "Sandwich":
            source = random.randint(1, 3)

            if source == 1:
                result = await Sandwich.RedditEatSandwiches()
            if source == 2:
                result = await Sandwich.RedditGrilledCheese()
            elif source == 3:
                result = await Sandwich.RedditSandwiches()
        elif type == "Sushi":
            result = await Sushi.RedditSushi()
        elif type == "Taco":
            result = await Taco.RedditTacos()

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
