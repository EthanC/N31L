from typing import Any, Dict, List, Optional, Union

from helpers import Responses, Utility
from hikari.embeds import Embed
from loguru import logger

from .reddit import Reddit


class Axolotl:
    """Class containing axolotl image sources."""

    async def AxoltlAPI() -> Optional[Embed]:
        """Fetch a random axoltl image from AxoltlAPI."""

        data: Optional[Dict[str, Any]] = await Utility.GET(
            "https://axoltlapi.herokuapp.com/"
        )

        if data is None:
            return

        try:
            return Responses.Success(color=None, image=data["url"])
        except Exception as e:
            logger.error(f"Failed to fetch from AxolotlAPI, {e}")

    async def RedditAxolotls(credentials: Dict[str, Any]) -> Optional[Embed]:
        """Fetch a random axolotl image from r/axolotls."""

        return await Reddit.GetRandomImage("axolotls", credentials)


class Bird:
    """Class containing bird image sources."""

    async def RandomDuk() -> Optional[Embed]:
        """Fetch a random bird image from RandomDuk."""

        data: Optional[Dict[str, Any]] = await Utility.GET(
            "https://random-d.uk/api/v2/random"
        )

        if data is None:
            return

        try:
            return Responses.Success(color=None, image=data["url"])
        except Exception as e:
            logger.error(f"Failed to fetch from RandomDuk, {e}")

    async def SomeRandomAPI() -> Optional[Embed]:
        """Fetch a random bird image from SomeRandomAPI."""

        data: Optional[Dict[str, Any]] = await Utility.GET(
            "https://some-random-api.ml/animal/birb"
        )

        if data is None:
            return

        try:
            return Responses.Success(color=None, image=data["image"])
        except Exception as e:
            logger.error(f"Failed to fetch from SomeRandomAPI, {e}")

    async def RedditBirbs(credentials: Dict[str, Any]) -> Optional[Embed]:
        """Fetch a random bird image from r/Birbs."""

        return await Reddit.GetRandomImage("Birbs", credentials)

    async def RedditBirdPics(credentials: Dict[str, Any]) -> Optional[Embed]:
        """Fetch a random bird image from r/birdpics."""

        return await Reddit.GetRandomImage("birdpics", credentials)


class Bunny:
    """Class containing bunny image sources."""

    async def BunniesIO() -> Optional[Embed]:
        """Fetch a random bunny image from BunniesIO."""

        data: Optional[Dict[str, Any]] = await Utility.GET(
            "https://api.bunnies.io/v2/loop/random/?media=gif"
        )

        if data is None:
            return

        try:
            return Responses.Success(color=None, image=data["media"]["gif"])
        except Exception as e:
            logger.error(f"Failed to fetch from BunniesIO, {e}")

    async def RedditBunnies(credentials: Dict[str, Any]) -> Optional[Embed]:
        """Fetch a random bird image from r/Bunnies."""

        return await Reddit.GetRandomImage("Bunnies", credentials)

    async def RedditRabbits(credentials: Dict[str, Any]) -> Optional[Embed]:
        """Fetch a random bird image from r/Rabbits."""

        return await Reddit.GetRandomImage("Rabbits", credentials)


class Cat:
    """Class containing cat image sources."""

    async def TheCatAPI(key: str) -> Optional[Embed]:
        """Fetch a random cat image from TheCatAPI."""

        data: Optional[Dict[str, Any]] = await Utility.GET(
            "https://api.thecatapi.com/v1/images/search", headers={"x-api-key": key}
        )

        if data is None:
            return

        try:
            cat: Dict[str, Any] = data[0]

            name: Optional[str] = None
            wiki: Optional[str] = None
            info: Optional[str] = None
            facts: List[Dict[str, Union[str, bool]]] = []
            tags: Optional[List[str]] = None

            if len((breeds := cat["breeds"])) > 0:
                breed: Dict[str, Any] = breeds[0]

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
            logger.error(f"Failed to fetch from TheCatAPI, {e}")

    async def CATAAS() -> Optional[Embed]:
        """Fetch a random cat image from CATAAS."""

        data: Optional[Dict[str, Any]] = await Utility.GET(
            "https://cataas.com/cat?json=true"
        )

        if data is None:
            return

        try:
            return Responses.Success(
                color=None,
                image="https://cataas.com" + data["url"],
                footer=None if (tags := data["tags"]) is None else ", ".join(tags),
            )
        except Exception as e:
            logger.error(f"Failed to fetch from CATAAS, {e}")

    async def RandomCat() -> Optional[Embed]:
        """Fetch a random cat image from RandomCat."""

        data: Optional[Dict[str, Any]] = await Utility.GET(
            "https://aws.random.cat/meow"
        )

        if data is None:
            return

        try:
            return Responses.Success(color=None, image=data["file"])
        except Exception as e:
            logger.error(f"Failed to fetch from RandomCat, {e}")

    async def SomeRandomAPI() -> Optional[Embed]:
        """Fetch a random cat image from SomeRandomAPI."""

        data: Optional[Dict[str, Any]] = await Utility.GET(
            "https://some-random-api.ml/animal/cat"
        )

        if data is None:
            return

        try:
            return Responses.Success(color=None, image=data["image"])
        except Exception as e:
            logger.error(f"Failed to fetch from SomeRandomAPI, {e}")

    async def RedditBlurryPicturesCats(credentials: Dict[str, Any]) -> Optional[Embed]:
        """Fetch a random cat image from r/blurrypicturesofcats."""

        return await Reddit.GetRandomImage("blurrypicturesofcats", credentials)

    async def RedditCatPics(credentials: Dict[str, Any]) -> Optional[Embed]:
        """Fetch a random cat image from r/catpics."""

        return await Reddit.GetRandomImage("catpics", credentials)

    async def RedditCatPictures(credentials: Dict[str, Any]) -> Optional[Embed]:
        """Fetch a random cat image from r/catpictures."""

        return await Reddit.GetRandomImage("catpictures", credentials)

    async def RedditCats(credentials: Dict[str, Any]) -> Optional[Embed]:
        """Fetch a random cat image from r/cats."""

        return await Reddit.GetRandomImage("cats", credentials)

    async def RedditCatsStandingUp(credentials: Dict[str, Any]) -> Optional[Embed]:
        """Fetch a random cat image from r/CatsStandingUp."""

        return await Reddit.GetRandomImage("CatsStandingUp", credentials)

    async def RedditCursedCats(credentials: Dict[str, Any]) -> Optional[Embed]:
        """Fetch a random cat image from r/cursedcats."""

        return await Reddit.GetRandomImage("cursedcats", credentials)

    async def RedditSphynx(credentials: Dict[str, Any]) -> Optional[Embed]:
        """Fetch a random cat image from r/sphynx."""

        return await Reddit.GetRandomImage("sphynx", credentials)


class Capybara:
    """Class containing capybara image sources."""

    async def RedditCapybara(credentials: Dict[str, Any]) -> Optional[Embed]:
        """Fetch a random capybara image from r/capybara."""

        return await Reddit.GetRandomImage("capybara", credentials)

    async def RedditCrittersoncapybaras(credentials: Dict[str, Any]) -> Optional[Embed]:
        """Fetch a random capybara image from r/Crittersoncapybaras."""

        return await Reddit.GetRandomImage("Crittersoncapybaras", credentials)


class Dog:
    """Class containing dog image sources."""

    async def TheDogAPI(key: str) -> Optional[Embed]:
        """Fetch a random dog image from TheDogAPI."""

        data: Optional[Dict[str, Any]] = await Utility.GET(
            "https://api.thedogapi.com/v1/images/search", headers={"x-api-key": key}
        )

        if data is None:
            return

        try:
            dog: Dict[str, Any] = data[0]

            name: Optional[str] = None
            facts: List[Dict[str, Union[str, bool]]] = []

            if len((breeds := dog["breeds"])) > 0:
                breed: Dict[str, Any] = breeds[0]

                name = breed["name"]

                if (temperament := breed["temperament"]) is not None:
                    facts.append({"name": "Temperaments", "value": temperament})

            return Responses.Success(
                title=name, color=None, fields=facts, image=dog["url"]
            )
        except Exception as e:
            logger.error(f"Failed to fetch from TheDogAPI, {e}")

    async def DogCEO() -> Optional[Embed]:
        """Fetch a random dog image from DogCEO."""

        data: Optional[Dict[str, Any]] = await Utility.GET(
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
            logger.error(f"Failed to fetch from DogCEO, {e}")

    async def RandomDog() -> Optional[Embed]:
        """Fetch a random dog image from RandomDog."""

        data: Optional[Dict[str, Any]] = await Utility.GET(
            "https://random.dog/woof.json"
        )

        if data is None:
            return

        try:
            return Responses.Success(color=None, image=data["url"])
        except Exception as e:
            logger.error(f"Failed to fetch from RandomDog, {e}")

    async def ShibeOnline() -> Optional[Embed]:
        """Fetch a random dog image from ShibeOnline."""

        data: Optional[Dict[str, Any]] = await Utility.GET(
            "https://shibe.online/api/shibes"
        )

        if data is None:
            return

        try:
            return Responses.Success(color=None, image=data[0])
        except Exception as e:
            logger.error(f"Failed to fetch from ShibeOnline, {e}")

    async def SomeRandomAPI() -> Optional[Embed]:
        """Fetch a random dog image from SomeRandomAPI."""

        data: Optional[Dict[str, Any]] = await Utility.GET(
            "https://some-random-api.ml/animal/dog"
        )

        if data is None:
            return

        try:
            return Responses.Success(color=None, image=data["image"])
        except Exception as e:
            logger.error(f"Failed to fetch from SomeRandomAPI, {e}")

    async def RedditBlurryPicturesDogs(credentials: Dict[str, Any]) -> Optional[Embed]:
        """Fetch a random dog image from r/blurrypicturesofdogs."""

        return await Reddit.GetRandomImage("blurrypicturesofdogs", credentials)

    async def RedditDogPictures(credentials: Dict[str, Any]) -> Optional[Embed]:
        """Fetch a random dog image from r/dogpictures."""

        return await Reddit.GetRandomImage("dogpictures", credentials)

    async def RedditLookMyDog(credentials: Dict[str, Any]) -> Optional[Embed]:
        """Fetch a random dog image from r/lookatmydog."""

        return await Reddit.GetRandomImage("lookatmydog", credentials)

    async def RedditPuppies(credentials: Dict[str, Any]) -> Optional[Embed]:
        """Fetch a random dog image from r/puppies."""

        return await Reddit.GetRandomImage("puppies", credentials)

    async def RedditShiba(credentials: Dict[str, Any]) -> Optional[Embed]:
        """Fetch a random dog image from r/shiba."""

        return await Reddit.GetRandomImage("shiba", credentials)


class Fox:
    """Class containing fox image sources."""

    async def RandomFox() -> Optional[Embed]:
        """Fetch a random fox image from RandomFox."""

        data: Optional[Dict[str, Any]] = await Utility.GET(
            "https://randomfox.ca/floof/"
        )

        if data is None:
            return

        try:
            return Responses.Success(color=None, image=data["image"])
        except Exception as e:
            logger.error(f"Failed to fetch from RandomFox, {e}")

    async def SomeRandomAPI() -> Optional[Embed]:
        """Fetch a random fox image from SomeRandomAPI."""

        data: Optional[Dict[str, Any]] = await Utility.GET(
            "https://some-random-api.ml/animal/fox"
        )

        if data is None:
            return

        try:
            return Responses.Success(color=None, image=data["image"])
        except Exception as e:
            logger.error(f"Failed to fetch from SomeRandomAPI, {e}")

    async def RedditFoxes(credentials: Dict[str, Any]) -> Optional[Embed]:
        """Fetch a random fox image from r/foxes."""

        return await Reddit.GetRandomImage("foxes", credentials)


class Kangaroo:
    """Class containing kangaroo image sources."""

    async def SomeRandomAPI() -> Optional[Embed]:
        """Fetch a random kangaroo image from SomeRandomAPI."""

        data: Optional[Dict[str, Any]] = await Utility.GET(
            "https://some-random-api.ml/animal/kangaroo"
        )

        if data is None:
            return

        try:
            return Responses.Success(color=None, image=data["image"])
        except Exception as e:
            logger.error(f"Failed to fetch from SomeRandomAPI, {e}")


class Koala:
    """Class containing koala image sources."""

    async def SomeRandomAPI() -> Optional[Embed]:
        """Fetch a random koala image from SomeRandomAPI."""

        data: Optional[Dict[str, Any]] = await Utility.GET(
            "https://some-random-api.ml/animal/koala"
        )

        if data is None:
            return

        try:
            return Responses.Success(color=None, image=data["image"])
        except Exception as e:
            logger.error(f"Failed to fetch from SomeRandomAPI, {e}")

    async def RedditKoalas(credentials: Dict[str, Any]) -> Optional[Embed]:
        """Fetch a random koala image from r/koalas."""

        return await Reddit.GetRandomImage("koalas", credentials)


class Lizard:
    """Class containing lizard image sources."""

    async def NekosLife() -> Optional[Embed]:
        """Fetch a random lizard image from NekosLife."""

        data: Optional[Dict[str, Any]] = await Utility.GET(
            "https://nekos.life/api/v2/img/lizard"
        )

        if data is None:
            return

        try:
            return Responses.Success(color=None, image=data["url"])
        except Exception as e:
            logger.error(f"Failed to fetch from NekosLife, {e}")

    async def RedditLizards(credentials: Dict[str, Any]) -> Optional[Embed]:
        """Fetch a random lizard image from r/Lizards."""

        return await Reddit.GetRandomImage("Lizards", credentials)


class Otter:
    """Class containing otter image sources."""

    async def RedditOtterable(credentials: Dict[str, Any]) -> Optional[Embed]:
        """Fetch a random otter image from r/Otterable."""

        return await Reddit.GetRandomImage("Otterable", credentials)


class Panda:
    """Class containing panda image sources."""

    async def SomeRandomAPI() -> Optional[Embed]:
        """Fetch a random panda image from SomeRandomAPI."""

        data: Optional[Dict[str, Any]] = await Utility.GET(
            "https://some-random-api.ml/animal/panda"
        )

        if data is None:
            return

        try:
            return Responses.Success(color=None, image=data["image"])
        except Exception as e:
            logger.error(f"Failed to fetch from SomeRandomAPI, {e}")

    async def RedditPanda(credentials: Dict[str, Any]) -> Optional[Embed]:
        """Fetch a random panda image from r/panda."""

        return await Reddit.GetRandomImage("panda", credentials)


class Raccoon:
    """Class containing raccoon image sources."""

    async def SomeRandomAPI() -> Optional[Embed]:
        """Fetch a random panda image from SomeRandomAPI."""

        data: Optional[Dict[str, Any]] = await Utility.GET(
            "https://some-random-api.ml/animal/raccoon"
        )

        if data is None:
            return

        try:
            return Responses.Success(color=None, image=data["image"])
        except Exception as e:
            logger.error(f"Failed to fetch from SomeRandomAPI, {e}")

    async def RedditRaccoons(credentials: Dict[str, Any]) -> Optional[Embed]:
        """Fetch a random raccoon image from r/Raccoons."""

        return await Reddit.GetRandomImage("Raccoons", credentials)

    async def RedditTrashPandas(credentials: Dict[str, Any]) -> Optional[Embed]:
        """Fetch a random raccoon image from r/trashpandas."""

        return await Reddit.GetRandomImage("trashpandas", credentials)


class Rat:
    """Class containing rat image sources."""

    async def RedditRats(credentials: Dict[str, Any]) -> Optional[Embed]:
        """Fetch a random rat image from r/RATS."""

        return await Reddit.GetRandomImage("RATS", credentials)


class RedPanda:
    """Class containing red panda image sources."""

    async def SomeRandomAPI() -> Optional[Embed]:
        """Fetch a random panda image from SomeRandomAPI."""

        data: Optional[Dict[str, Any]] = await Utility.GET(
            "https://some-random-api.ml/animal/red_panda"
        )

        if data is None:
            return

        try:
            return Responses.Success(color=None, image=data["image"])
        except Exception as e:
            logger.error(f"Failed to fetch from SomeRandomAPI, {e}")

    async def RedditRedPandas(credentials: Dict[str, Any]) -> Optional[Embed]:
        """Fetch a random red panda image from r/redpandas."""

        return await Reddit.GetRandomImage("redpandas", credentials)
