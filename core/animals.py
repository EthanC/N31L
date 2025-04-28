from typing import Any

from environs import env
from hikari import Embed
from loguru import logger

from core.formatters import Response
from core.utils import GET


async def BunniesIO() -> Embed | None:
    """Fetch a random bunny image from BunniesIO."""

    data: dict[str, Any] | list[Any] | str | None = await GET(
        "https://api.bunnies.io/v2/loop/random/?media=gif"
    )

    if not data:
        logger.debug(f"Failed to fetch bunny from BunniesIO, data is null")

        return
    elif not isinstance(data, dict):
        logger.debug(f"Failed to fetch bunny from BunniesIO, invalid response")

        return

    try:
        return Response(image=data["media"]["gif"])
    except Exception as e:
        logger.opt(exception=e).error("Failed to fetch from BunniesIO")


async def CATAAS() -> Embed | None:
    """Fetch a random cat image from CATAAS."""

    data: dict[str, Any] | list[Any] | str | None = await GET(
        "https://cataas.com/cat?json=true"
    )

    if not data:
        logger.debug(f"Failed to fetch cat from CATAAS, data is null")

        return
    elif not isinstance(data, dict):
        logger.debug(f"Failed to fetch cat from CATAAS, invalid response")

        return

    try:
        return Response(
            image=data["url"],
            footer=None if not (tags := data.get("tags")) else ", ".join(tags),
        )
    except Exception as e:
        logger.opt(exception=e).error("Failed to fetch from CATAAS")


async def DogCEO() -> Embed | None:
    """Fetch a random dog image from DogCEO."""

    data: dict[str, Any] | list[Any] | str | None = await GET(
        "https://dog.ceo/api/breeds/image/random"
    )

    if not data:
        logger.debug(f"Failed to fetch dog from DogCEO, data is null")

        return
    elif not isinstance(data, dict):
        logger.debug(f"Failed to fetch dog from DogCEO, invalid response")

        return

    try:
        return Response(image=data["message"])
    except Exception as e:
        logger.opt(exception=e).error("Failed to fetch from DogCEO")


async def NekosLife() -> Embed | None:
    """Fetch a random lizard image from NekosLife."""

    data: dict[str, Any] | list[Any] | str | None = await GET(
        "https://nekos.life/api/v2/img/lizard"
    )

    if not data:
        logger.debug(f"Failed to fetch lizard from NekosLife, data is null")

        return
    elif not isinstance(data, dict):
        logger.debug(f"Failed to fetch lizard from NekosLife, invalid response")

        return

    try:
        return Response(image=data["url"])
    except Exception as e:
        logger.opt(exception=e).error("Failed to fetch from NekosLife")


async def RandomDog() -> Embed | None:
    """Fetch a random dog image from RandomDog."""

    data: dict[str, Any] | list[Any] | str | None = await GET(
        "https://random.dog/woof.json"
    )

    if not data:
        logger.debug(f"Failed to fetch dog from RandomDog, data is null")

        return
    elif not isinstance(data, dict):
        logger.debug(f"Failed to fetch dog from RandomDog, invalid response")

        return

    try:
        return Response(image=data["url"])
    except Exception as e:
        logger.opt(exception=e).error("Failed to fetch from RandomDog")


async def RandomDuk() -> Embed | None:
    """Fetch a random bird image from RandomDuk."""

    data: dict[str, Any] | list[Any] | str | None = await GET(
        "https://random-d.uk/api/v2/random"
    )

    if not data:
        logger.debug(f"Failed to fetch duck from RandomDuk, data is null")

        return
    elif not isinstance(data, dict):
        logger.debug(f"Failed to fetch duck from RandomDuk, invalid response")

        return

    try:
        return Response(image=data["url"])
    except Exception as e:
        logger.opt(exception=e).error("Failed to fetch from RandomDuk")


async def RandomFox() -> Embed | None:
    """Fetch a random fox image from RandomFox."""

    data: dict[str, Any] | list[Any] | str | None = await GET(
        "https://randomfox.ca/floof/"
    )

    if not data:
        logger.debug(f"Failed to fetch fox from RandomFox, data is null")

        return
    elif not isinstance(data, dict):
        logger.debug(f"Failed to fetch fox from RandomFox, invalid response")

        return

    try:
        return Response(image=data["image"])
    except Exception as e:
        logger.opt(exception=e).error("Failed to fetch from RandomFox")


async def SomeRandomAPI(animal: str) -> Embed | None:
    """Fetch a random animal image from SomeRandomAPI."""

    data: dict[str, Any] | list[Any] | str | None = await GET(
        f"https://some-random-api.com/animal/{animal}"
    )

    if not data:
        logger.debug(f"Failed to fetch {animal} from SomeRandomAPI, data is null")

        return
    elif not isinstance(data, dict):
        logger.debug(f"Failed to fetch {animal} from SomeRandomAPI, invalid response")

        return

    try:
        image_url: str = data["image"]

        # April 27th, 2025: SomeRandomAPI CDN has been broken for weeks
        if "cdn.some-random-api.com" not in image_url:
            return Response(image=image_url)
    except Exception as e:
        logger.opt(exception=e).error(f"Failed to fetch {animal} from SomeRandomAPI")


async def TheCatAPI() -> Embed | None:
    """Fetch a random cat image from TheCatAPI."""

    data: dict[str, Any] | list[Any] | str | None = await GET(
        "https://api.thecatapi.com/v1/images/search",
        headers={"x-api-key": env.str("CAT_API_KEY")},
    )

    if not data:
        logger.debug(f"Failed to fetch cat from TheCatAPI, data is null")

        return
    elif not isinstance(data, list):
        logger.debug(f"Failed to fetch cat from TheCatAPI, invalid response")

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

        return Response(
            title=name,
            url=wiki,
            description=info,
            fields=facts,
            image=cat["url"],
            footer=None if not tags else ", ".join(tags),
        )
    except Exception as e:
        logger.opt(exception=e).error("Failed to fetch from TheCatAPI")


async def TheDogAPI() -> Embed | None:
    """Fetch a random dog image from TheDogAPI."""

    data: dict[str, Any] | list[Any] | str | None = await GET(
        "https://api.thedogapi.com/v1/images/search",
        {"x-api-key": env.str("DOG_API_KEY")},
    )

    if not data:
        logger.debug(f"Failed to fetch dog from TheDogAPI, data is null")

        return
    elif not isinstance(data, list):
        logger.debug(f"Failed to fetch dog from TheDogAPI, invalid response")

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

        return Response(title=name, fields=facts, image=dog["url"])
    except Exception as e:
        logger.opt(exception=e).error("Failed to fetch from TheDogAPI")
