from typing import Any

from environs import env
from hikari import Embed
from loguru import logger

from core.formatters import response
from core.utils import get


async def bunnies_io() -> Embed | None:
    """Fetch a random bunny image from bunnies_io."""

    data: dict[str, Any] | list[Any] | str | None = await get(
        "https://api.bunnies.io/v2/loop/random/?media=gif"
    )

    if not data:
        logger.debug(f"Failed to fetch bunny from bunnies_io, data is null")

        return
    elif not isinstance(data, dict):
        logger.debug(f"Failed to fetch bunny from bunnies_io, invalid response")

        return

    try:
        return response(image=data["media"]["gif"])
    except Exception as e:
        logger.opt(exception=e).error("Failed to fetch from bunnies_io")


async def cataas() -> Embed | None:
    """Fetch a random cat image from cataas."""

    data: dict[str, Any] | list[Any] | str | None = await get(
        "https://cataas.com/cat?json=true"
    )

    if not data:
        logger.debug(f"Failed to fetch cat from cataas, data is null")

        return
    elif not isinstance(data, dict):
        logger.debug(f"Failed to fetch cat from cataas, invalid response")

        return

    try:
        return response(
            image=data["url"],
            footer=None if not (tags := data.get("tags")) else ", ".join(tags),
        )
    except Exception as e:
        logger.opt(exception=e).error("Failed to fetch from cataas")


async def dog_ceo() -> Embed | None:
    """Fetch a random dog image from dog_ceo."""

    data: dict[str, Any] | list[Any] | str | None = await get(
        "https://dog.ceo/api/breeds/image/random"
    )

    if not data:
        logger.debug(f"Failed to fetch dog from dog_ceo, data is null")

        return
    elif not isinstance(data, dict):
        logger.debug(f"Failed to fetch dog from dog_ceo, invalid response")

        return

    try:
        return response(image=data["message"])
    except Exception as e:
        logger.opt(exception=e).error("Failed to fetch from dog_ceo")


async def nekos_life() -> Embed | None:
    """Fetch a random lizard image from nekos_life."""

    data: dict[str, Any] | list[Any] | str | None = await get(
        "https://nekos.life/api/v2/img/lizard"
    )

    if not data:
        logger.debug(f"Failed to fetch lizard from nekos_life, data is null")

        return
    elif not isinstance(data, dict):
        logger.debug(f"Failed to fetch lizard from nekos_life, invalid response")

        return

    try:
        return response(image=data["url"])
    except Exception as e:
        logger.opt(exception=e).error("Failed to fetch from nekos_life")


async def random_dog() -> Embed | None:
    """Fetch a random dog image from random_dog."""

    data: dict[str, Any] | list[Any] | str | None = await get(
        "https://random.dog/woof.json"
    )

    if not data:
        logger.debug(f"Failed to fetch dog from random_dog, data is null")

        return
    elif not isinstance(data, dict):
        logger.debug(f"Failed to fetch dog from random_dog, invalid response")

        return

    try:
        return response(image=data["url"])
    except Exception as e:
        logger.opt(exception=e).error("Failed to fetch from random_dog")


async def random_duk() -> Embed | None:
    """Fetch a random bird image from random_duk."""

    data: dict[str, Any] | list[Any] | str | None = await get(
        "https://random-d.uk/api/v2/random"
    )

    if not data:
        logger.debug(f"Failed to fetch duck from random_duk, data is null")

        return
    elif not isinstance(data, dict):
        logger.debug(f"Failed to fetch duck from random_duk, invalid response")

        return

    try:
        return response(image=data["url"])
    except Exception as e:
        logger.opt(exception=e).error("Failed to fetch from random_duk")


async def random_fox() -> Embed | None:
    """Fetch a random fox image from random_fox."""

    data: dict[str, Any] | list[Any] | str | None = await get(
        "https://randomfox.ca/floof/"
    )

    if not data:
        logger.debug(f"Failed to fetch fox from random_fox, data is null")

        return
    elif not isinstance(data, dict):
        logger.debug(f"Failed to fetch fox from random_fox, invalid response")

        return

    try:
        return response(image=data["image"])
    except Exception as e:
        logger.opt(exception=e).error("Failed to fetch from random_fox")


async def some_random_api(animal: str) -> Embed | None:
    """Fetch a random animal image from some_random_api."""

    data: dict[str, Any] | list[Any] | str | None = await get(
        f"https://some-random-api.com/animal/{animal}"
    )

    if not data:
        logger.debug(f"Failed to fetch {animal} from some_random_api, data is null")

        return
    elif not isinstance(data, dict):
        logger.debug(f"Failed to fetch {animal} from some_random_api, invalid response")

        return

    try:
        image_url: str = data["image"]

        # April 27th, 2025: some_random_api CDN has been broken for weeks
        if "cdn.some-random-api.com" not in image_url:
            return response(image=image_url)
    except Exception as e:
        logger.opt(exception=e).error(f"Failed to fetch {animal} from some_random_api")


async def the_cat_api() -> Embed | None:
    """Fetch a random cat image from the_cat_api."""

    data: dict[str, Any] | list[Any] | str | None = await get(
        "https://api.thecatapi.com/v1/images/search",
        headers={"x-api-key": env.str("CAT_API_KEY")},
    )

    if not data:
        logger.debug(f"Failed to fetch cat from the_cat_api, data is null")

        return
    elif not isinstance(data, list):
        logger.debug(f"Failed to fetch cat from the_cat_api, invalid response")

        return

    try:
        cat: dict[str, Any] = data[0]

        name: str | None = None
        wiki: str | None = None
        info: str | None = None
        facts: list[dict[str, str | bool]] = []
        tags: list[str] | None = None

        if len((breeds := cat["breeds"])) > 0:
            breed: dict[str, Any] = breeds[0]

            name = breed["name"]
            wiki = breed["wikipedia_url"]

            if len((altNames := breed.get("alt_names", []))) > 0:
                if not name:
                    name = altNames
                else:
                    name = f"{name} ({altNames})"

            if desc := breed["description"]:
                info = desc

            if origin := breed["origin"]:
                if country := breed["country_code"]:
                    origin = f":flag_{country.lower()}: {origin}"

                facts.append({"name": "Origin", "value": origin})

            if temperament := breed["temperament"]:
                facts.append({"name": "Temperaments", "value": temperament})

        if len((categories := cat.get("categories", []))) > 0:
            tags = []

            for category in categories:
                tags.append(category["name"])

        return response(
            title=name,
            url=wiki,
            description=info,
            fields=facts,
            image=cat["url"],
            footer=None if not tags else ", ".join(tags),
        )
    except Exception as e:
        logger.opt(exception=e).error("Failed to fetch from the_cat_api")


async def the_dog_api() -> Embed | None:
    """Fetch a random dog image from the_dog_api."""

    data: dict[str, Any] | list[Any] | str | None = await get(
        "https://api.thedogapi.com/v1/images/search",
        {"x-api-key": env.str("DOG_API_KEY")},
    )

    if not data:
        logger.debug(f"Failed to fetch dog from the_dog_api, data is null")

        return
    elif not isinstance(data, list):
        logger.debug(f"Failed to fetch dog from the_dog_api, invalid response")

        return

    try:
        dog: dict[str, Any] = data[0]

        name: str | None = None
        facts: list[dict[str, str | bool]] = []

        if len((breeds := dog["breeds"])) > 0:
            breed: dict[str, Any] = breeds[0]

            name = breed["name"]

            if temperament := breed["temperament"]:
                facts.append({"name": "Temperaments", "value": temperament})

        return response(title=name, fields=facts, image=dog["url"])
    except Exception as e:
        logger.opt(exception=e).error("Failed to fetch from the_dog_api")
