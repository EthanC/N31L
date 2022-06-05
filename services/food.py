from typing import Any, Dict, Optional

from helpers import Responses, Utility
from hikari.embeds import Embed
from loguru import logger

from .reddit import Reddit


class Burger:
    """Class containing burger image sources."""

    async def Foodish() -> Optional[Embed]:
        """Fetch a random burger image from Foodish."""

        data: Optional[Dict[str, Any]] = await Utility.GET(
            "https://foodish-api.herokuapp.com/api/images/burger"
        )

        if data is None:
            return

        try:
            return Responses.Success(color=None, image=data["image"])
        except Exception as e:
            logger.error(f"Failed to fetch from Foodish, {e}")

    async def RedditBurgers(credentials: Dict[str, Any]) -> Optional[Embed]:
        """Fetch a random burger image from r/burgers."""

        return await Reddit.GetRandomImage("burgers", credentials)


class Dessert:
    """Class containing dessert image sources."""

    async def Foodish() -> Optional[Embed]:
        """Fetch a random dessert image from Foodish."""

        data: Optional[Dict[str, Any]] = await Utility.GET(
            "https://foodish-api.herokuapp.com/api/images/dessert"
        )

        if data is None:
            return

        try:
            return Responses.Success(color=None, image=data["image"])
        except Exception as e:
            logger.error(f"Failed to fetch from Foodish, {e}")

    async def RedditCake(credentials: Dict[str, Any]) -> Optional[Embed]:
        """Fetch a random dessert image from r/cake."""

        return await Reddit.GetRandomImage("cake", credentials)

    async def RedditCookies(credentials: Dict[str, Any]) -> Optional[Embed]:
        """Fetch a random dessert image from r/Cookies."""

        return await Reddit.GetRandomImage("Cookies", credentials)

    async def RedditCupcakes(credentials: Dict[str, Any]) -> Optional[Embed]:
        """Fetch a random dessert image from r/cupcakes."""

        return await Reddit.GetRandomImage("cupcakes", credentials)

    async def RedditDessert(credentials: Dict[str, Any]) -> Optional[Embed]:
        """Fetch a random dessert image from r/dessert."""

        return await Reddit.GetRandomImage("dessert", credentials)

    async def RedditDessertPorn(credentials: Dict[str, Any]) -> Optional[Embed]:
        """Fetch a random dessert image from r/DessertPorn."""

        return await Reddit.GetRandomImage("DessertPorn", credentials)

    async def RedditIcecreamery(credentials: Dict[str, Any]) -> Optional[Embed]:
        """Fetch a random dessert image from r/icecreamery."""

        return await Reddit.GetRandomImage("icecreamery", credentials)

    async def RedditPie(credentials: Dict[str, Any]) -> Optional[Embed]:
        """Fetch a random dessert image from r/pie."""

        return await Reddit.GetRandomImage("pie", credentials)


class HotDog:
    """Class containing hot dog image sources."""

    async def RedditHotDogs(credentials: Dict[str, Any]) -> Optional[Embed]:
        """Fetch a random hot dog image from r/hotdogs."""

        return await Reddit.GetRandomImage("hotdogs", credentials)


class Pasta:
    """Class containing pasta image sources."""

    async def Foodish() -> Optional[Embed]:
        """Fetch a random pasta image from Foodish."""

        data: Optional[Dict[str, Any]] = await Utility.GET(
            "https://foodish-api.herokuapp.com/api/images/pasta"
        )

        if data is None:
            return

        try:
            return Responses.Success(color=None, image=data["image"])
        except Exception as e:
            logger.error(f"Failed to fetch from Foodish, {e}")

    async def RedditPasta(credentials: Dict[str, Any]) -> Optional[Embed]:
        """Fetch a random pasta image from r/pasta."""

        return await Reddit.GetRandomImage("pasta", credentials)


class Pizza:
    """Class containing pizza image sources."""

    async def Foodish() -> Optional[Embed]:
        """Fetch a random pizza image from Foodish."""

        data: Optional[Dict[str, Any]] = await Utility.GET(
            "https://foodish-api.herokuapp.com/api/images/pizza"
        )

        if data is None:
            return

        try:
            return Responses.Success(color=None, image=data["image"])
        except Exception as e:
            logger.error(f"Failed to fetch from Foodish, {e}")

    async def RedditPizza(credentials: Dict[str, Any]) -> Optional[Embed]:
        """Fetch a random pizza image from r/Pizza."""

        return await Reddit.GetRandomImage("Pizza", credentials)


class Rice:
    """Class containing rice image sources."""

    async def Foodish() -> Optional[Embed]:
        """Fetch a random rice image from Foodish."""

        data: Optional[Dict[str, Any]] = await Utility.GET(
            "https://foodish-api.herokuapp.com/api/images/rice"
        )

        if data is None:
            return

        try:
            return Responses.Success(color=None, image=data["image"])
        except Exception as e:
            logger.error(f"Failed to fetch from Foodish, {e}")


class Salad:
    """Class containing salad image sources."""

    async def RedditSalads(credentials: Dict[str, Any]) -> Optional[Embed]:
        """Fetch a random salad image from r/salads."""

        return await Reddit.GetRandomImage("salads", credentials)


class Sandwich:
    """Class containing sandwich image sources."""

    async def RedditEatSandwiches(credentials: Dict[str, Any]) -> Optional[Embed]:
        """Fetch a random sandwich image from r/eatsandwiches."""

        return await Reddit.GetRandomImage("eatsandwiches", credentials)

    async def RedditGrilledCheese(credentials: Dict[str, Any]) -> Optional[Embed]:
        """Fetch a random sandwich image from r/grilledcheese."""

        return await Reddit.GetRandomImage("grilledcheese", credentials)

    async def RedditSandwiches(credentials: Dict[str, Any]) -> Optional[Embed]:
        """Fetch a random sandwich image from r/sandwiches."""

        return await Reddit.GetRandomImage("sandwiches", credentials)


class Sushi:
    """Class containing sushi image sources."""

    async def RedditSushi(credentials: Dict[str, Any]) -> Optional[Embed]:
        """Fetch a random sushi image from r/sushi."""

        return await Reddit.GetRandomImage("sushi", credentials)


class Taco:
    """Class containing taco image sources."""

    async def RedditTacos(credentials: Dict[str, Any]) -> Optional[Embed]:
        """Fetch a random taco image from r/tacos."""

        return await Reddit.GetRandomImage("tacos", credentials)
