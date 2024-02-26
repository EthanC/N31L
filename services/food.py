from hikari.embeds import Embed

from .reddit import Reddit


class Burger:
    """Class containing burger image sources."""

    async def RedditBurgers() -> Embed | None:
        """Fetch a random burger image from r/burgers."""

        return await Reddit.GetRandomImage("burgers")


class Dessert:
    """Class containing dessert image sources."""

    async def RedditCake() -> Embed | None:
        """Fetch a random dessert image from r/cake."""

        return await Reddit.GetRandomImage("cake")

    async def RedditCookies() -> Embed | None:
        """Fetch a random dessert image from r/Cookies."""

        return await Reddit.GetRandomImage("Cookies")

    async def RedditCupcakes() -> Embed | None:
        """Fetch a random dessert image from r/cupcakes."""

        return await Reddit.GetRandomImage("cupcakes")

    async def RedditDessert() -> Embed | None:
        """Fetch a random dessert image from r/dessert."""

        return await Reddit.GetRandomImage("dessert")

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

    async def RedditHotDogs() -> Embed | None:
        """Fetch a random hot dog image from r/hotdogs."""

        return await Reddit.GetRandomImage("hotdogs")


class Pasta:
    """Class containing pasta image sources."""

    async def RedditPasta() -> Embed | None:
        """Fetch a random pasta image from r/pasta."""

        return await Reddit.GetRandomImage("pasta")


class Pizza:
    """Class containing pizza image sources."""

    async def RedditPizza() -> Embed | None:
        """Fetch a random pizza image from r/Pizza."""

        return await Reddit.GetRandomImage("Pizza")


class Salad:
    """Class containing salad image sources."""

    async def RedditSalads() -> Embed | None:
        """Fetch a random salad image from r/salads."""

        return await Reddit.GetRandomImage("salads")


class Sandwich:
    """Class containing sandwich image sources."""

    async def RedditEatSandwiches() -> Embed | None:
        """Fetch a random sandwich image from r/eatsandwiches."""

        return await Reddit.GetRandomImage("eatsandwiches")

    async def RedditGrilledCheese() -> Embed | None:
        """Fetch a random sandwich image from r/grilledcheese."""

        return await Reddit.GetRandomImage("grilledcheese")

    async def RedditSandwiches() -> Embed | None:
        """Fetch a random sandwich image from r/sandwiches."""

        return await Reddit.GetRandomImage("sandwiches")


class Sushi:
    """Class containing sushi image sources."""

    async def RedditSushi() -> Embed | None:
        """Fetch a random sushi image from r/sushi."""

        return await Reddit.GetRandomImage("sushi")


class Taco:
    """Class containing taco image sources."""

    async def RedditTacos() -> Embed | None:
        """Fetch a random taco image from r/tacos."""

        return await Reddit.GetRandomImage("tacos")
