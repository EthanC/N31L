import asyncio
import random

import tanjun
from hikari import Permissions
from hikari.embeds import Embed
from tanjun import Component
from tanjun.abc import SlashContext

from helpers import Responses
from services import (
    Burger,
    Chicken,
    Dessert,
    HotDog,
    Pasta,
    Pizza,
    Rice,
    Salad,
    Sandwich,
    Steak,
    Sushi,
    Taco,
)

component: Component = Component(name="Food")
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


@component.with_slash_command()
@tanjun.with_own_permission_check(Permissions.SEND_MESSAGES)
@tanjun.with_str_slash_option(
    "type",
    "Choose a food type or leave empty for random.",
    choices=foodTypes,
    default=None,
)
@tanjun.as_slash_command("food", "Fetch a random picture of food.")
async def CommandFood(ctx: SlashContext, type: str | None) -> None:
    """Handler for the /food command."""

    if not type:
        type = random.choice(foodTypes)

    result: Embed | None = None
    source: int = 1
    retries: int = 0

    while not result:
        if type == "Burger":
            source = random.randint(1, 4)

            if source == 1:
                result = await Burger.Foodish()
            elif source == 2:
                result = await Burger.RedditBobsBurgersCreations()
            elif source == 3:
                result = await Burger.RedditBurgers()
            elif source == 4:
                result = await Burger.RedditCheeseburgers()
        elif type == "Chicken":
            source = random.randint(1, 3)

            if source == 1:
                result = await Chicken.Foodish()
            elif source == 2:
                result = await Chicken.RedditFriedChicken()
            elif source == 3:
                result = await Chicken.RedditWings()
        elif type == "Dessert":
            source = random.randint(1, 9)

            if source == 1:
                result = await Dessert.Foodish()
            elif source == 2:
                result = await Dessert.RedditBaking()
            elif source == 3:
                result = await Dessert.RedditCake()
            elif source == 4:
                result = await Dessert.RedditCakeDecorating()
            elif source == 5:
                result = await Dessert.RedditCheesecake()
            elif source == 6:
                result = await Dessert.RedditCookies()
            elif source == 7:
                result = await Dessert.RedditDessert()
            elif source == 8:
                result = await Dessert.RedditDesserts()
            elif source == 9:
                result = await Dessert.RedditDessertPorn()
            elif source == 10:
                result = await Dessert.RedditIcecreamery()
            elif source == 11:
                result = await Dessert.RedditPie()
        elif type == "Hot Dog":
            source = random.randint(1, 2)

            if source == 1:
                result = await HotDog.RedditHotDog()
            elif source == 2:
                result = await HotDog.RedditHotDogs()
        elif type == "Pasta":
            source = random.randint(1, 2)

            if source == 1:
                result = await Pasta.Foodish()
            elif source == 2:
                result = await Pasta.RedditPasta()
        elif type == "Pizza":
            source = random.randint(1, 4)

            if source == 1:
                result = await Pizza.Foodish()
            elif source == 2:
                result = await Pizza.RedditCatsOnPizza()
            elif source == 3:
                result = await Pizza.RedditPizza()
            elif source == 4:
                result = await Pizza.RedditPizzaCrimes()
        elif type == "Rice":
            source = random.randint(1, 2)

            if source == 1:
                result = await Rice.Foodish()
            elif source == 2:
                result = await Rice.RedditRice()
        elif type == "Salad":
            source = random.randint(1, 2)

            if source == 1:
                result = await Salad.RedditSalad()
            elif source == 2:
                result = await Salad.RedditSalads()
        elif type == "Sandwich":
            source = random.randint(1, 3)

            if source == 1:
                result = await Sandwich.RedditEatSandwiches()
            elif source == 2:
                result = await Sandwich.RedditGrilledCheese()
            elif source == 3:
                result = await Sandwich.RedditSandwich()
        elif type == "Steak":
            source = random.randint(1, 3)

            if source == 1:
                result = await Steak.RedditSteak()
            elif source == 2:
                result = await Steak.RedditSteakCrimes()
            elif source == 3:
                result = await Steak.RedditSteakorTuna()
        elif type == "Sushi":
            source = random.randint(1, 3)

            if source == 1:
                result = await Sushi.RedditSushi()
            elif source == 2:
                result = await Sushi.RedditSushiAbomination()
            elif source == 3:
                result = await Sushi.RedditSushiRoll()
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
