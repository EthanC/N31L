from hikari.embeds import Embed
from loguru import logger

from helpers import Responses, Utility

from .reddit import Reddit


class Burger:
    """Class containing burger image sources."""

    async def Foodish() -> Embed | None:
        """Fetch a random burger image from Foodish."""

        data: dict[str, str] | None = await Utility.GET(
            "https://foodish-api.com/api/images/burger"
        )

        if not data:
            return

        try:
            return Responses.Success(color=None, image=data["image"])
        except Exception as e:
            logger.opt(exception=e).error("Failed to fetch burger from Foodish")

    async def RedditBobsBurgersCreations() -> Embed | None:
        """Fetch a random burger image from r/BobsBurgersCreations."""

        return await Reddit.GetRandomImage("BobsBurgersCreations")

    async def RedditBurgers() -> Embed | None:
        """Fetch a random burger image from r/burgers."""

        return await Reddit.GetRandomImage("burgers")

    async def RedditCheeseburgers() -> Embed | None:
        """Fetch a random burger image from r/cheeseburgers."""

        return await Reddit.GetRandomImage("cheeseburgers")


class Chicken:
    """Class containing chicken image sources."""

    async def Foodish() -> Embed | None:
        """Fetch a random chicken image from Foodish."""

        data: dict[str, str] | None = await Utility.GET(
            "https://foodish-api.com/api/images/butter-chicken"
        )

        if not data:
            return

        try:
            return Responses.Success(color=None, image=data["image"])
        except Exception as e:
            logger.opt(exception=e).error("Failed to fetch chicken from Foodish")

    async def RedditFriedChicken() -> Embed | None:
        """Fetch a random chicken image from r/FriedChicken."""

        return await Reddit.GetRandomImage("FriedChicken")

    async def RedditWings() -> Embed | None:
        """Fetch a random chicken image from r/Wings."""

        return await Reddit.GetRandomImage("Wings")


class Dessert:
    """Class containing dessert image sources."""

    async def Foodish() -> Embed | None:
        """Fetch a random dessert image from Foodish."""

        data: dict[str, str] | None = await Utility.GET(
            "https://foodish-api.com/api/images/dessert"
        )

        if not data:
            return

        try:
            return Responses.Success(color=None, image=data["image"])
        except Exception as e:
            logger.opt(exception=e).error("Failed to fetch dessert from Foodish")

    async def RedditBaking() -> Embed | None:
        """Fetch a random dessert image from r/Baking."""

        return await Reddit.GetRandomImage("Baking")

    async def RedditCake() -> Embed | None:
        """Fetch a random dessert image from r/cake."""

        return await Reddit.GetRandomImage("cake")

    async def RedditCakeDecorating() -> Embed | None:
        """Fetch a random dessert image from r/cakedecorating."""

        return await Reddit.GetRandomImage("cakedecorating")

    async def RedditCheesecake() -> Embed | None:
        """Fetch a random dessert image from r/cheesecake."""

        return await Reddit.GetRandomImage("cheesecake")

    async def RedditCookies() -> Embed | None:
        """Fetch a random dessert image from r/Cookies."""

        return await Reddit.GetRandomImage("Cookies")

    async def RedditDessert() -> Embed | None:
        """Fetch a random dessert image from r/dessert."""

        return await Reddit.GetRandomImage("dessert")

    async def RedditDesserts() -> Embed | None:
        """Fetch a random dessert image from r/desserts."""

        return await Reddit.GetRandomImage("desserts")

    async def RedditDessertPorn() -> Embed | None:
        """Fetch a random dessert image from r/DessertPorn."""

        return await Reddit.GetRandomImage("DessertPorn")

    async def RedditIcecreamery() -> Embed | None:
        """Fetch a random dessert image from r/icecreamery."""

        return await Reddit.GetRandomImage("icecreamery")

    async def RedditPie() -> Embed | None:
        """Fetch a random dessert image from r/pie."""

        return await Reddit.GetRandomImage("pie")


class HotDog:
    """Class containing hot dog image sources."""

    async def RedditHotDog() -> Embed | None:
        """Fetch a random hot dog image from r/hot_dog."""

        return await Reddit.GetRandomImage("hot_dog")

    async def RedditHotDogs() -> Embed | None:
        """Fetch a random hot dog image from r/hotdogs."""

        return await Reddit.GetRandomImage("hotdogs")


class Pasta:
    """Class containing pasta image sources."""

    async def Foodish() -> Embed | None:
        """Fetch a random pasta image from Foodish."""

        data: dict[str, str] | None = await Utility.GET(
            "https://foodish-api.com/api/images/pasta"
        )

        if not data:
            return

        try:
            return Responses.Success(color=None, image=data["image"])
        except Exception as e:
            logger.opt(exception=e).error("Failed to fetch pasta from Foodish")

    async def RedditPasta() -> Embed | None:
        """Fetch a random pasta image from r/pasta."""

        return await Reddit.GetRandomImage("pasta")


class Pizza:
    """Class containing pizza image sources."""

    async def Foodish() -> Embed | None:
        """Fetch a random pizza image from Foodish."""

        data: dict[str, str] | None = await Utility.GET(
            "https://foodish-api.com/api/images/pizza"
        )

        if not data:
            return

        try:
            return Responses.Success(color=None, image=data["image"])
        except Exception as e:
            logger.opt(exception=e).error("Failed to fetch pizza from Foodish")

    async def RedditCatsOnPizza() -> Embed | None:
        """Fetch a random pizza image from r/CatsOnPizza."""

        return await Reddit.GetRandomImage("CatsOnPizza")

    async def RedditPizza() -> Embed | None:
        """Fetch a random pizza image from r/Pizza."""

        return await Reddit.GetRandomImage("Pizza")

    async def RedditPizzaCrimes() -> Embed | None:
        """Fetch a random pizza image from r/PizzaCrimes."""

        return await Reddit.GetRandomImage("PizzaCrimes")


class Rice:
    """Class containing rice image sources."""

    async def Foodish() -> Embed | None:
        """Fetch a random rice image from Foodish."""

        data: dict[str, str] | None = await Utility.GET(
            "https://foodish-api.com/api/images/rice"
        )

        if not data:
            return

        try:
            return Responses.Success(color=None, image=data["image"])
        except Exception as e:
            logger.opt(exception=e).error("Failed to fetch rice from Foodish")

    async def RedditRice() -> Embed | None:
        """Fetch a random rice image from r/RICE."""

        return await Reddit.GetRandomImage("RICE")


class Salad:
    """Class containing salad image sources."""

    async def RedditSalad() -> Embed | None:
        """Fetch a random salad image from r/salad."""

        return await Reddit.GetRandomImage("salad")

    async def RedditSalads() -> Embed | None:
        """Fetch a random salad image from r/salads."""

        return await Reddit.GetRandomImage("salads")


class Steak:
    """Class containing steak image sources."""

    async def RedditSteak() -> Embed | None:
        """Fetch a random steak image from r/steak."""

        return await Reddit.GetRandomImage("steak")

    async def RedditSteakCrimes() -> Embed | None:
        """Fetch a random steak image from r/steakcrimes."""

        return await Reddit.GetRandomImage("steakcrimes")

    async def RedditSteakorTuna() -> Embed | None:
        """Fetch a random steak image from r/SteakorTuna."""

        return await Reddit.GetRandomImage("SteakorTuna")


class Sandwich:
    """Class containing sandwich image sources."""

    async def RedditEatSandwiches() -> Embed | None:
        """Fetch a random sandwich image from r/eatsandwiches."""

        return await Reddit.GetRandomImage("eatsandwiches")

    async def RedditGrilledCheese() -> Embed | None:
        """Fetch a random sandwich image from r/grilledcheese."""

        return await Reddit.GetRandomImage("grilledcheese")

    async def RedditSandwich() -> Embed | None:
        """Fetch a random sandwich image from r/Sandwich."""

        return await Reddit.GetRandomImage("Sandwich")


class Sushi:
    """Class containing sushi image sources."""

    async def RedditSushi() -> Embed | None:
        """Fetch a random sushi image from r/sushi."""

        return await Reddit.GetRandomImage("sushi")

    async def RedditSushiAbomination() -> Embed | None:
        """Fetch a random sushi image from r/SushiAbomination."""

        return await Reddit.GetRandomImage("SushiAbomination")

    async def RedditSushiRoll() -> Embed | None:
        """Fetch a random sushi image from r/SushiRoll."""

        return await Reddit.GetRandomImage("SushiRoll")


class Taco:
    """Class containing taco image sources."""

    async def RedditTacos() -> Embed | None:
        """Fetch a random taco image from r/tacos."""

        return await Reddit.GetRandomImage("tacos")
