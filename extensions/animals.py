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
    bunnies_io,
    cataas,
    dog_ceo,
    nekos_life,
    random_dog,
    random_duk,
    random_fox,
    some_random_api,
    the_cat_api,
    the_dog_api,
)
from core.hooks import hook_error, hook_log

plugin: GatewayPlugin = GatewayPlugin("animals")
animalTypes: list[str] = [
    "Bird",
    "Bunny",
    "Cat",
    "Dog",
    "Duck",
    "Fox",
    "Lizard",
    "Panda",
    "Red Panda",
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
@arc.with_hook(hook_log)
@arc.slash_command("animal", "Fetch a random picture of an animal.")
async def command_animal(
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
            case "Bird":
                source = random.randint(1, 2)

                match source:
                    case 1:
                        result = await some_random_api("bird")
                    case 2:
                        result = await random_duk()
                    case _:
                        logger.warning(
                            f"Recieved unknown source {source} for animal type {type}"
                        )
            case "Bunny":
                match source:
                    case 1:
                        result = await bunnies_io()
                    case _:
                        logger.warning(
                            f"Recieved unknown source {source} for animal type {type}"
                        )
            case "Cat":
                source = random.randint(1, 3)

                match source:
                    case 1:
                        result = await some_random_api("cat")
                    case 2:
                        result = await the_cat_api()
                    case 3:
                        result = await cataas()
                    case _:
                        logger.warning(
                            f"Recieved unknown source {source} for animal type {type}"
                        )
            case "Dog":
                source = random.randint(1, 4)

                match source:
                    case 1:
                        result = await some_random_api("dog")
                    case 2:
                        result = await the_dog_api()
                    case 3:
                        result = await dog_ceo()
                    case 4:
                        result = await random_dog()
                    case _:
                        logger.warning(
                            f"Recieved unknown source {source} for animal type {type}"
                        )
            case "Duck":
                match source:
                    case 1:
                        result = await random_duk()
                    case _:
                        logger.warning(
                            f"Recieved unknown source {source} for animal type {type}"
                        )
            case "Fox":
                source = random.randint(1, 2)

                match source:
                    case 1:
                        result = await some_random_api("fox")
                    case 2:
                        result = await random_fox()
                    case _:
                        logger.warning(
                            f"Recieved unknown source {source} for animal type {type}"
                        )
            case "Lizard":
                match source:
                    case 1:
                        result = await nekos_life()
                    case _:
                        logger.warning(
                            f"Recieved unknown source {source} for animal type {type}"
                        )
            case "Panda":
                match source:
                    case 1:
                        result = await some_random_api("panda")
                    case _:
                        logger.warning(
                            f"Recieved unknown source {source} for animal type {type}"
                        )
            case "Red Panda":
                match source:
                    case 1:
                        result = await some_random_api("red_panda")
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
async def error_handler(ctx: GatewayContext, error: Exception) -> None:
    """Handler for errors originating from this plugin."""

    await hook_error(ctx, error)
