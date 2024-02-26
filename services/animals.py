from os import environ
from typing import Any

from hikari.embeds import Embed
from loguru import logger

from helpers import Responses, Utility

from .reddit import Reddit


class Axolotl:
    """Class containing axolotl image sources."""

    async def RedditAxolotls() -> Embed | None:
        """Fetch a random axolotl image from r/axolotls."""

        return await Reddit.GetRandomImage("axolotls")


class Bird:
    """Class containing bird image sources."""

    async def RandomDuk() -> Embed | None:
        """Fetch a random bird image from RandomDuk."""

        data: dict[str, Any] | None = await Utility.GET(
            "https://random-d.uk/api/v2/random"
        )

        if data is None:
            return

        try:
            return Responses.Success(color=None, image=data["url"])
        except Exception as e:
            logger.opt(exception=e).error("Failed to fetch from RandomDuk")

    async def SomeRandomAPI() -> Embed | None:
        """Fetch a random bird image from SomeRandomAPI."""

        data: dict[str, Any] | None = await Utility.GET(
            "https://some-random-api.com/animal/bird"
        )

        if data is None:
            return

        try:
            return Responses.Success(color=None, image=data["image"])
        except Exception as e:
            logger.opt(exception=e).error("Failed to fetch from SomeRandomAPI")

    async def RedditBirbs() -> Embed | None:
        """Fetch a random bird image from r/Birbs."""

        return await Reddit.GetRandomImage("Birbs")

    async def RedditBirdPics() -> Embed | None:
        """Fetch a random bird image from r/birdpics."""

        return await Reddit.GetRandomImage("birdpics")


class Bunny:
    """Class containing bunny image sources."""

    async def BunniesIO() -> Embed | None:
        """Fetch a random bunny image from BunniesIO."""

        data: dict[str, Any] | None = await Utility.GET(
            "https://api.bunnies.io/v2/loop/random/?media=gif"
        )

        if data is None:
            return

        try:
            return Responses.Success(color=None, image=data["media"]["gif"])
        except Exception as e:
            logger.opt(exception=e).error("Failed to fetch from BunniesIO")

    async def RedditBunnies() -> Embed | None:
        """Fetch a random bird image from r/Bunnies."""

        return await Reddit.GetRandomImage("Bunnies")

    async def RedditRabbits() -> Embed | None:
        """Fetch a random bird image from r/Rabbits."""

        return await Reddit.GetRandomImage("Rabbits")


class Cat:
    """Class containing cat image sources."""

    async def TheCatAPI() -> Embed | None:
        """Fetch a random cat image from TheCatAPI."""

        data: dict[str, Any] | None = await Utility.GET(
            "https://api.thecatapi.com/v1/images/search",
            headers={"x-api-key": environ.get("CAT_API_KEY")},
        )

        if data is None:
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
                    if name is None:
                        name = altNames
                    else:
                        name = f"{name} ({altNames})"

                if (desc := breed["description"]) is not None:
                    if len(desc) >= 120:
                        info = f"{desc[0:120]}..."
                    else:
                        info = desc

                if (origin := breed["origin"]) is not None:
                    if (country := breed["country_code"]) is not None:
                        origin = f":flag_{country.lower()}: {origin}"

                    facts.append({"name": "Origin", "value": origin})

                if (temperament := breed["temperament"]) is not None:
                    facts.append({"name": "Temperaments", "value": temperament})

            if len((categories := cat.get("categories", []))) > 0:
                tags = []

                for category in categories:
                    tags.append(category["name"])

            return Responses.Success(
                title=name,
                url=wiki,
                color=None,
                description=info,
                fields=facts,
                image=cat["url"],
                footer=None if tags is None else ", ".join(tags),
            )
        except Exception as e:
            logger.opt(exception=e).error("Failed to fetch from TheCatAPI")

    async def CATAAS() -> Embed | None:
        """Fetch a random cat image from CATAAS."""

        data: dict[str, Any] | None = await Utility.GET(
            "https://cataas.com/cat?json=true"
        )

        if data is None:
            return

        try:
            return Responses.Success(
                color=None,
                image="https://cataas.com/cat/" + data["_id"],
                footer=None if (tags := data.get("tags")) is None else ", ".join(tags),
            )
        except Exception as e:
            logger.opt(exception=e).error("Failed to fetch from CATAAS")

    async def SomeRandomAPI() -> Embed | None:
        """Fetch a random cat image from SomeRandomAPI."""

        data: dict[str, Any] | None = await Utility.GET(
            "https://some-random-api.com/animal/cat"
        )

        if data is None:
            return

        try:
            return Responses.Success(color=None, image=data["image"])
        except Exception as e:
            logger.opt(exception=e).error("Failed to fetch from SomeRandomAPI")

    async def RedditBlurryPicturesCats() -> Embed | None:
        """Fetch a random cat image from r/blurrypicturesofcats."""

        return await Reddit.GetRandomImage("blurrypicturesofcats")

    async def RedditCatPics() -> Embed | None:
        """Fetch a random cat image from r/catpics."""

        return await Reddit.GetRandomImage("catpics")

    async def RedditCatPictures() -> Embed | None:
        """Fetch a random cat image from r/catpictures."""

        return await Reddit.GetRandomImage("catpictures")

    async def RedditCats() -> Embed | None:
        """Fetch a random cat image from r/cats."""

        return await Reddit.GetRandomImage("cats")

    async def RedditCatsStandingUp() -> Embed | None:
        """Fetch a random cat image from r/CatsStandingUp."""

        return await Reddit.GetRandomImage("CatsStandingUp")

    async def RedditCursedCats() -> Embed | None:
        """Fetch a random cat image from r/cursedcats."""

        return await Reddit.GetRandomImage("cursedcats")

    async def RedditSphynx() -> Embed | None:
        """Fetch a random cat image from r/sphynx."""

        return await Reddit.GetRandomImage("sphynx")


class Capybara:
    """Class containing capybara image sources."""

    async def RedditCapybara() -> Embed | None:
        """Fetch a random capybara image from r/capybara."""

        return await Reddit.GetRandomImage("capybara")

    async def RedditCrittersoncapybaras() -> Embed | None:
        """Fetch a random capybara image from r/Crittersoncapybaras."""

        return await Reddit.GetRandomImage("Crittersoncapybaras")


class Dog:
    """Class containing dog image sources."""

    async def TheDogAPI() -> Embed | None:
        """Fetch a random dog image from TheDogAPI."""

        data: dict[str, Any] | None = await Utility.GET(
            "https://api.thedogapi.com/v1/images/search",
            headers={"x-api-key": environ.get("DOG_API_KEY")},
        )

        if data is None:
            return

        try:
            dog: dict[str, Any] = data[0]

            name: str | None = None
            facts: list[dict[str, str | bool]] = []

            if len((breeds := dog["breeds"])) > 0:
                breed: dict[str, Any] = breeds[0]

                name = breed["name"]

                if (temperament := breed["temperament"]) is not None:
                    facts.append({"name": "Temperaments", "value": temperament})

            return Responses.Success(
                title=name, color=None, fields=facts, image=dog["url"]
            )
        except Exception as e:
            logger.opt(exception=e).error("Failed to fetch from TheDogAPI")

    async def DogCEO() -> Embed | None:
        """Fetch a random dog image from DogCEO."""

        data: dict[str, Any] | None = await Utility.GET(
            "https://dog.ceo/api/breeds/image/random"
        )

        if data is None:
            return

        try:
            imageUrl: str = data["message"]
            breed: str = imageUrl

            # Messy solution to determine the breed given the image url
            breed = breed.replace("https://images.dog.ceo/breeds/", "")
            breed = breed.split("/")[0]
            breed = breed.replace("-", " ")
            breed = breed.title()
            return Responses.Success(title=breed, color=None, image=imageUrl)
        except Exception as e:
            logger.opt(exception=e).error("Failed to fetch from DogCEO")

    async def RandomDog() -> Embed | None:
        """Fetch a random dog image from RandomDog."""

        data: dict[str, Any] | None = await Utility.GET(
            "https://random.dog/woof.json"
        )

        if data is None:
            return

        try:
            return Responses.Success(color=None, image=data["url"])
        except Exception as e:
            logger.opt(exception=e).error("Failed to fetch from RandomDog")

    async def ShibeOnline() -> Embed | None:
        """Fetch a random dog image from ShibeOnline."""

        data: dict[str, Any] | None = await Utility.GET(
            "https://shibe.online/api/shibes"
        )

        if data is None:
            return

        try:
            return Responses.Success(color=None, image=data[0])
        except Exception as e:
            logger.opt(exception=e).error("Failed to fetch from ShibeOnline")

    async def SomeRandomAPI() -> Embed | None:
        """Fetch a random dog image from SomeRandomAPI."""

        data: dict[str, Any] | None = await Utility.GET(
            "https://some-random-api.com/animal/dog"
        )

        if data is None:
            return

        try:
            return Responses.Success(color=None, image=data["image"])
        except Exception as e:
            logger.opt(exception=e).error("Failed to fetch from SomeRandomAPI")

    async def RedditBlurryPicturesDogs() -> Embed | None:
        """Fetch a random dog image from r/blurrypicturesofdogs."""

        return await Reddit.GetRandomImage("blurrypicturesofdogs")

    async def RedditDogPictures() -> Embed | None:
        """Fetch a random dog image from r/dogpictures."""

        return await Reddit.GetRandomImage("dogpictures")

    async def RedditLookMyDog() -> Embed | None:
        """Fetch a random dog image from r/lookatmydog."""

        return await Reddit.GetRandomImage("lookatmydog")

    async def RedditPuppies() -> Embed | None:
        """Fetch a random dog image from r/puppies."""

        return await Reddit.GetRandomImage("puppies")

    async def RedditShiba() -> Embed | None:
        """Fetch a random dog image from r/shiba."""

        return await Reddit.GetRandomImage("shiba")


class Fox:
    """Class containing fox image sources."""

    async def RandomFox() -> Embed | None:
        """Fetch a random fox image from RandomFox."""

        data: dict[str, Any] | None = await Utility.GET(
            "https://randomfox.ca/floof/"
        )

        if data is None:
            return

        try:
            return Responses.Success(color=None, image=data["image"])
        except Exception as e:
            logger.opt(exception=e).error("Failed to fetch from RandomFox")

    async def SomeRandomAPI() -> Embed | None:
        """Fetch a random fox image from SomeRandomAPI."""

        data: dict[str, Any] | None = await Utility.GET(
            "https://some-random-api.com/animal/fox"
        )

        if data is None:
            return

        try:
            return Responses.Success(color=None, image=data["image"])
        except Exception as e:
            logger.opt(exception=e).error("Failed to fetch from SomeRandomAPI")

    async def RedditFoxes() -> Embed | None:
        """Fetch a random fox image from r/foxes."""

        return await Reddit.GetRandomImage("foxes")


class Kangaroo:
    """Class containing kangaroo image sources."""

    async def SomeRandomAPI() -> Embed | None:
        """Fetch a random kangaroo image from SomeRandomAPI."""

        data: dict[str, Any] | None = await Utility.GET(
            "https://some-random-api.com/animal/kangaroo"
        )

        if data is None:
            return

        try:
            return Responses.Success(color=None, image=data["image"])
        except Exception as e:
            logger.opt(exception=e).error("Failed to fetch from SomeRandomAPI")


class Koala:
    """Class containing koala image sources."""

    async def SomeRandomAPI() -> Embed | None:
        """Fetch a random koala image from SomeRandomAPI."""

        data: dict[str, Any] | None = await Utility.GET(
            "https://some-random-api.com/animal/koala"
        )

        if data is None:
            return

        try:
            return Responses.Success(color=None, image=data["image"])
        except Exception as e:
            logger.opt(exception=e).error("Failed to fetch from SomeRandomAPI")

    async def RedditKoalas() -> Embed | None:
        """Fetch a random koala image from r/koalas."""

        return await Reddit.GetRandomImage("koalas")


class Lizard:
    """Class containing lizard image sources."""

    async def NekosLife() -> Embed | None:
        """Fetch a random lizard image from NekosLife."""

        data: dict[str, Any] | None = await Utility.GET(
            "https://nekos.life/api/v2/img/lizard"
        )

        if data is None:
            return

        try:
            return Responses.Success(color=None, image=data["url"])
        except Exception as e:
            logger.opt(exception=e).error("Failed to fetch from NekosLife")

    async def RedditLizards() -> Embed | None:
        """Fetch a random lizard image from r/Lizards."""

        return await Reddit.GetRandomImage("Lizards")


class Otter:
    """Class containing otter image sources."""

    async def RedditOtterable() -> Embed | None:
        """Fetch a random otter image from r/Otterable."""

        return await Reddit.GetRandomImage("Otterable")


class Panda:
    """Class containing panda image sources."""

    async def SomeRandomAPI() -> Embed | None:
        """Fetch a random panda image from SomeRandomAPI."""

        data: dict[str, Any] | None = await Utility.GET(
            "https://some-random-api.com/animal/panda"
        )

        if data is None:
            return

        try:
            return Responses.Success(color=None, image=data["image"])
        except Exception as e:
            logger.opt(exception=e).error("Failed to fetch from SomeRandomAPI")


class Raccoon:
    """Class containing raccoon image sources."""

    async def SomeRandomAPI() -> Embed | None:
        """Fetch a random panda image from SomeRandomAPI."""

        data: dict[str, Any] | None = await Utility.GET(
            "https://some-random-api.com/animal/raccoon"
        )

        if data is None:
            return

        try:
            return Responses.Success(color=None, image=data["image"])
        except Exception as e:
            logger.opt(exception=e).error("Failed to fetch from SomeRandomAPI")

    async def RedditRaccoons() -> Embed | None:
        """Fetch a random raccoon image from r/Raccoons."""

        return await Reddit.GetRandomImage("Raccoons")

    async def RedditTrashPandas() -> Embed | None:
        """Fetch a random raccoon image from r/trashpandas."""

        return await Reddit.GetRandomImage("trashpandas")


class Rat:
    """Class containing rat image sources."""

    async def RedditRats() -> Embed | None:
        """Fetch a random rat image from r/RATS."""

        return await Reddit.GetRandomImage("RATS")


class RedPanda:
    """Class containing red panda image sources."""

    async def SomeRandomAPI() -> Embed | None:
        """Fetch a random panda image from SomeRandomAPI."""

        data: dict[str, Any] | None = await Utility.GET(
            "https://some-random-api.com/animal/red_panda"
        )

        if data is None:
            return

        try:
            return Responses.Success(color=None, image=data["image"])
        except Exception as e:
            logger.opt(exception=e).error("Failed to fetch from SomeRandomAPI")

    async def RedditRedPandas() -> Embed | None:
        """Fetch a random red panda image from r/redpandas."""

        return await Reddit.GetRandomImage("redpandas")
