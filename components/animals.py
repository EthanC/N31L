import asyncio
import random
from typing import List, Optional

import tanjun
from hikari import Permissions
from hikari.embeds import Embed
from tanjun import Component
from tanjun.abc import SlashContext

from helpers import Responses
from services import (
    Axolotl,
    Bird,
    Bunny,
    Capybara,
    Cat,
    Dog,
    Fox,
    Kangaroo,
    Koala,
    Lizard,
    Otter,
    Panda,
    Raccoon,
    Rat,
    RedPanda,
)

component: Component = Component(name="Animals")
animalTypes: List[str] = [
    "Axolotl",
    "Bingus",
    "Bird",
    "Bunny",
    "Cat",
    "Capybara",
    "Dog",
    "Duck",
    "Fox",
    "Kangaroo",
    "Koala",
    "Lizard",
    "Otter",
    "Panda",
    "Raccoon",
    "Rat",
    "Red Panda",
    "Shibe",
]


@component.with_slash_command()
@tanjun.with_own_permission_check(Permissions.SEND_MESSAGES)
@tanjun.with_str_slash_option(
    "type",
    "Choose an animal type or leave empty for random.",
    choices=animalTypes,
    default=None,
)
@tanjun.as_slash_command("animal", "Fetch a random picture of an animal.")
async def CommandAnimal(ctx: SlashContext, type: Optional[str]) -> None:
    """Handler for the /animal command."""

    if type is None:
        type = random.choice(animalTypes)

    result: Optional[Embed] = None
    source: int = 1
    retries: int = 0

    while result is None:
        if type == "Axolotl":
            if source == 1:
                result = await Axolotl.RedditAxolotls()
        elif type == "Bingus":
            if source == 1:
                result = await Cat.RedditSphynx()
        elif type == "Bird":
            source = random.randint(1, 3)

            if source == 1:
                result = await Bird.RandomDuk()
            elif source == 2:
                result = await Bird.SomeRandomAPI()
            elif source == 3:
                result = await Bird.RedditBirbs()
            elif source == 4:
                result = await Bird.RedditBirdPics()
        elif type == "Bunny":
            source = random.randint(1, 3)

            if source == 1:
                result = await Bunny.BunniesIO()
            elif source == 2:
                result = await Bunny.RedditBunnies()
            elif source == 3:
                result = await Bunny.RedditRabbits()
        elif type == "Cat":
            source = random.randint(1, 10)

            if source == 1:
                result = await Cat.TheCatAPI()
            elif source == 2:
                result = await Cat.CATAAS()
            elif source == 3:
                result = await Cat.SomeRandomAPI()
            elif source == 4:
                result = await Cat.RedditBlurryPicturesCats()
            elif source == 5:
                result = await Cat.RedditCatPics()
            elif source == 6:
                result = await Cat.RedditCatPictures()
            elif source == 7:
                result = await Cat.RedditCats()
            elif source == 8:
                result = await Cat.RedditCatsStandingUp()
            elif source == 9:
                result = await Cat.RedditCursedCats()
            elif source == 10:
                result = await Cat.RedditSphynx()
        elif type == "Capybara":
            source = random.randint(1, 2)

            if source == 1:
                result = await Capybara.RedditCapybara()
            elif source == 2:
                result = await Capybara.RedditCrittersoncapybaras()
        elif type == "Dog":
            source = random.randint(1, 9)

            if source == 1:
                result = await Dog.TheDogAPI()
            elif source == 2:
                result = await Dog.DogCEO()
            elif source == 3:
                result = await Dog.RandomDog()
            elif source == 4:
                result = await Dog.ShibeOnline()
            elif source == 5:
                result = await Dog.SomeRandomAPI()
            elif source == 6:
                result = await Dog.RedditBlurryPicturesDogs()
            elif source == 7:
                result = await Dog.RedditDogPictures()
            elif source == 8:
                result = await Dog.RedditLookMyDog()
            elif source == 9:
                result = await Dog.RedditPuppies()
        elif type == "Duck":
            if source == 1:
                result = await Bird.RandomDuk()
        elif type == "Fox":
            source = random.randint(1, 3)

            if source == 1:
                result = await Fox.RandomFox()
            elif source == 2:
                result = await Fox.SomeRandomAPI()
            elif source == 3:
                result = await Fox.RedditFoxes()
        elif type == "Kangaroo":
            if source == 1:
                result = await Kangaroo.SomeRandomAPI()
        elif type == "Koala":
            source = random.randint(1, 2)

            if source == 1:
                result = await Koala.SomeRandomAPI()
            elif source == 2:
                result = await Koala.RedditKoalas()
        elif type == "Lizard":
            source = random.randint(1, 2)

            if source == 1:
                result = await Lizard.NekosLife()
            elif source == 2:
                result = await Lizard.RedditLizards()
        elif type == "Otter":
            if source == 1:
                result = await Otter.RedditOtterable()
        elif type == "Panda":
            source = random.randint(1, 2)

            if source == 1:
                result = await Panda.SomeRandomAPI()
            elif source == 2:
                result = await Panda.RedditPanda()
        elif type == "Raccoon":
            source = random.randint(1, 3)

            if source == 1:
                result = await Raccoon.SomeRandomAPI()
            elif source == 2:
                result = await Raccoon.RedditRaccoons()
            elif source == 3:
                result = await Raccoon.RedditTrashPandas()
        elif type == "Rat":
            if source == 1:
                result = await Rat.RedditRats()
        elif type == "Red Panda":
            source = random.randint(1, 2)

            if source == 1:
                result = await RedPanda.SomeRandomAPI()
            elif source == 2:
                result = await RedPanda.RedditRedPandas()
        elif type == "Shibe":
            source = random.randint(1, 2)

            if source == 1:
                result = await Dog.ShibeOnline()
            elif source == 2:
                result = await Dog.RedditShiba()

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
