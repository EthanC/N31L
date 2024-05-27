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

from core.animals import (
    CATAAS,
    BunniesIO,
    DogCEO,
    NekosLife,
    RandomDog,
    RandomDuk,
    RandomFox,
    SomeRandomAPI,
    TheCatAPI,
    TheDogAPI,
)
from core.hooks import HookError, HookLog
from core.reddit import GetRandomImage

plugin: GatewayPlugin = GatewayPlugin("animals")
animalTypes: list[str] = [
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
    "Shiba",
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
@arc.slash_command("animal", "Fetch a random picture of an animal.")
async def CommandAnimal(
    ctx: GatewayContext,
    type: Option[
        str | None,
        StrParams(
            "Choose an animal type or leave empty for random.", choices=animalTypes
        ),
    ] = None,
) -> None:
    """Handler for the /animal command."""

    result: Embed | None = None
    source: int = 1
    retries: int = 0

    while not result:
        match type:
            case "Axolotl":
                match source:
                    case 1:
                        result = await GetRandomImage("axolotls")
                    case _:
                        logger.warning(
                            f"Recieved unknown source {source} for animal type {type}"
                        )
            case "Bingus":
                match source:
                    case 1:
                        result = await GetRandomImage("sphynx")
                    case _:
                        logger.warning(
                            f"Recieved unknown source {source} for animal type {type}"
                        )
            case "Bird":
                source = random.randint(1, 3)

                match source:
                    case 1:
                        result = await GetRandomImage("Birbs")
                    case 2:
                        result = await SomeRandomAPI("bird")
                    case 3:
                        result = await RandomDuk()
                    case _:
                        logger.warning(
                            f"Recieved unknown source {source} for animal type {type}"
                        )
            case "Bunny":
                source = random.randint(1, 3)

                match source:
                    case 1:
                        result = await GetRandomImage("Bunnies")
                    case 2:
                        result = await GetRandomImage("Rabbits")
                    case 3:
                        result = await BunniesIO()
                    case _:
                        logger.warning(
                            f"Recieved unknown source {source} for animal type {type}"
                        )
            case "Cat":
                source = random.randint(1, 10)

                match source:
                    case 1:
                        result = await GetRandomImage("blurrypicturesofcats")
                    case 2:
                        result = await GetRandomImage("catpics")
                    case 3:
                        result = await GetRandomImage("catpictures")
                    case 4:
                        result = await GetRandomImage("cats")
                    case 5:
                        result = await GetRandomImage("CatsStandingUp")
                    case 6:
                        result = await GetRandomImage("cursedcats")
                    case 7:
                        result = await GetRandomImage("sphynx")
                    case 8:
                        result = await SomeRandomAPI("cat")
                    case 9:
                        result = await TheCatAPI()
                    case 10:
                        result = await CATAAS()
                    case _:
                        logger.warning(
                            f"Recieved unknown source {source} for animal type {type}"
                        )
            case "Capybara":
                source = random.randint(1, 2)

                match source:
                    case 1:
                        result = await GetRandomImage("capybara")
                    case 2:
                        result = await GetRandomImage("Crittersoncapybaras")
                    case _:
                        logger.warning(
                            f"Recieved unknown source {source} for animal type {type}"
                        )
            case "Dog":
                source = random.randint(1, 9)

                match source:
                    case 1:
                        result = await GetRandomImage("blurrypicturesofdogs")
                    case 2:
                        result = await GetRandomImage("dogpictures")
                    case 3:
                        result = await GetRandomImage("lookatmydog")
                    case 4:
                        result = await GetRandomImage("puppies")
                    case 5:
                        result = await GetRandomImage("shiba")
                    case 6:
                        result = await SomeRandomAPI("dog")
                    case 7:
                        result = await TheDogAPI()
                    case 8:
                        result = await DogCEO()
                    case 9:
                        result = await RandomDog()
                    case _:
                        logger.warning(
                            f"Recieved unknown source {source} for animal type {type}"
                        )
            case "Duck":
                match source:
                    case 1:
                        result = await RandomDuk()
                    case _:
                        logger.warning(
                            f"Recieved unknown source {source} for animal type {type}"
                        )
            case "Fox":
                source = random.randint(1, 3)

                match source:
                    case 1:
                        result = await GetRandomImage("foxes")
                    case 2:
                        result = await SomeRandomAPI("fox")
                    case 3:
                        result = await RandomFox()
                    case _:
                        logger.warning(
                            f"Recieved unknown source {source} for animal type {type}"
                        )
            case "Kangaroo":
                match source:
                    case 1:
                        result = await SomeRandomAPI("kangaroo")
                    case _:
                        logger.warning(
                            f"Recieved unknown source {source} for animal type {type}"
                        )
            case "Koala":
                source = random.randint(1, 2)

                match source:
                    case 1:
                        result = await GetRandomImage("koalas")
                    case 2:
                        result = await SomeRandomAPI("koala")
                    case _:
                        logger.warning(
                            f"Recieved unknown source {source} for animal type {type}"
                        )
            case "Lizard":
                source = random.randint(1, 2)

                match source:
                    case 1:
                        result = await GetRandomImage("Lizards")
                    case 2:
                        result = await NekosLife()
                    case _:
                        logger.warning(
                            f"Recieved unknown source {source} for animal type {type}"
                        )
            case "Otter":
                match source:
                    case 1:
                        result = await GetRandomImage("Otterable")
                    case _:
                        logger.warning(
                            f"Recieved unknown source {source} for animal type {type}"
                        )
            case "Panda":
                match source:
                    case 1:
                        result = await SomeRandomAPI("panda")
                    case _:
                        logger.warning(
                            f"Recieved unknown source {source} for animal type {type}"
                        )
            case "Raccoon":
                source = random.randint(1, 3)

                match source:
                    case 1:
                        result = await GetRandomImage("Raccoons")
                    case 2:
                        result = await GetRandomImage("trashpandas")
                    case 3:
                        result = await SomeRandomAPI("raccoon")
                    case _:
                        logger.warning(
                            f"Recieved unknown source {source} for animal type {type}"
                        )
            case "Rat":
                match source:
                    case 1:
                        result = await GetRandomImage("RATS")
                    case _:
                        logger.warning(
                            f"Recieved unknown source {source} for animal type {type}"
                        )
            case "Red Panda":
                source = random.randint(1, 2)

                match source:
                    case 1:
                        result = await GetRandomImage("redpandas")
                    case 2:
                        result = await SomeRandomAPI("red_panda")
                    case _:
                        logger.warning(
                            f"Recieved unknown source {source} for animal type {type}"
                        )
            case "Shiba":
                match source:
                    case 1:
                        result = await GetRandomImage("shiba")
                    case _:
                        logger.warning(
                            f"Recieved unknown source {source} for animal type {type}"
                        )
            case _:
                # type is expected to be null if not provided
                if type:
                    logger.warning(f"Recieved unknown animal type {type}")

                type = random.choice(animalTypes)

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
