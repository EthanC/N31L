import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Union

from hikari import Guild, GuildChannel, Role, User
from hikari.api.special_endpoints import ButtonBuilder, LinkButtonBuilder
from hikari.embeds import Embed
from hikari.impl.special_endpoints import ActionRowBuilder
from hikari.messages import ButtonStyle
from loguru import logger


class Buttons:
    """Class containing generic, modular button templates."""

    def Link(container: ActionRowBuilder, label: str, url: str) -> ActionRowBuilder:
        """Build a generic link button."""

        button: LinkButtonBuilder = container.add_button(ButtonStyle, url)

        button.set_label(label)

        button.add_to_container()

        return container

    def Button(
        container: ActionRowBuilder,
        style: ButtonStyle,
        id: str,
        label: Optional[str] = None,
        emoji: Optional[str] = None,
        disabled: bool = False,
    ) -> ActionRowBuilder:
        """Build a generic button."""

        button: ButtonBuilder = container.add_button(style, id)

        if label is not None:
            button.set_label(label)

        if emoji is not None:
            button.set_emoji(emoji)

        if disabled is True:
            button.set_is_disabled(disabled)

        button.add_to_container()

        return container


class Responses:
    """Class containing generic, modular response templates."""

    def ExpandUser(user: User, format: bool = True) -> str:
        """Build a reusable string for the provided identity."""

        if format is True:
            return f"`{user.username}#{user.discriminator}` (`{user.id}`)"

        return f"{user.username}#{user.discriminator} ({user.id})"

    def ExpandRole(role: Role, format: bool = True) -> str:
        """Build a reusable string for the provided role."""

        if format is True:
            return f"`{role.name}` (`{role.id}`)"

        return f"{role.name} ({role.id})"

    def ExpandGuild(guild: Guild, format: bool = True) -> str:
        """Build a reusable string for the provided guild."""

        if format is True:
            return f"`{guild.name}` (`{guild.id}`)"

        return f"{guild.name} ({guild.id})"

    def ExpandChannel(channel: GuildChannel, format: bool = True) -> str:
        """Build a reusable string for the provided channel."""

        if format is True:
            return f"`#{channel.name}` (`{channel.id}`)"

        return f"#{channel.name} ({channel.id})"

    def Log(emoji: str, message: str, timestamp: Optional[datetime] = None) -> str:
        """Build a reusable log message."""

        if timestamp is None:
            timestamp = datetime.now()

        return f"[{Timestamps.ShortTime(timestamp)}] :{emoji}: {message}"

    def Success(
        title: Optional[str] = None,
        url: Optional[str] = None,
        color: str = "3BA55D",
        description: Optional[str] = None,
        fields: List[Dict[str, Union[str, bool]]] = [],
        author: Optional[str] = None,
        authorUrl: Optional[str] = None,
        authorIcon: Optional[str] = None,
        thumbnail: Optional[str] = None,
        image: Optional[str] = None,
        footer: Optional[str] = None,
        footerIcon: Optional[str] = None,
        timestamp: Optional[datetime] = None,
    ) -> Embed:
        """Build a generic successful response Embed object."""

        result: Embed = Embed(
            title=title,
            description=description,
            url=url,
            color=color,
            timestamp=timestamp,
        )

        if author is not None:
            result.set_author(name=author, url=authorUrl, icon=authorIcon)

        if thumbnail is not None:
            result.set_thumbnail(thumbnail)

        if image is not None:
            result.set_image(image)

        if footer is not None:
            result.set_footer(footer, icon=footerIcon)

        for field in fields:
            result.add_field(
                field["name"], field["value"], inline=field.get("inline", True)
            )

        return result

    def Warning(
        title: Optional[str] = None,
        url: Optional[str] = None,
        color: str = "FAA81A",
        description: Optional[str] = None,
        fields: List[Dict[str, Union[str, bool]]] = [],
        author: Optional[str] = None,
        authorUrl: Optional[str] = None,
        authorIcon: Optional[str] = None,
        thumbnail: Optional[str] = None,
        image: Optional[str] = None,
        footer: Optional[str] = None,
        footerIcon: Optional[str] = None,
        timestamp: Optional[datetime] = None,
    ) -> Embed:
        """Build a generic warning response Embed object."""

        result: Embed = Embed(
            title=title,
            description=description,
            url=url,
            color=color,
            timestamp=timestamp,
        )

        if author is not None:
            result.set_author(name=author, url=authorUrl, icon=authorIcon)

        if thumbnail is not None:
            result.set_thumbnail(thumbnail)

        if image is not None:
            result.set_image(image)

        if footer is not None:
            result.set_footer(footer, icon=footerIcon)

        for field in fields:
            result.add_field(
                field["name"], field["value"], inline=field.get("inline", True)
            )

        return result

    def Fail(
        title: Optional[str] = None,
        url: Optional[str] = None,
        color: str = "ED4245",
        description: Optional[str] = None,
        fields: List[Dict[str, Union[str, bool]]] = [],
        author: Optional[str] = None,
        authorUrl: Optional[str] = None,
        authorIcon: Optional[str] = None,
        thumbnail: Optional[str] = None,
        image: Optional[str] = None,
        footer: Optional[str] = None,
        footerIcon: str = "https://i.imgur.com/IwCRM6v.png",
        timestamp: Optional[datetime] = None,
    ) -> Embed:
        """Build a generic failed response Embed object."""

        ref: str = hashlib.md5(
            str(datetime.now().timestamp()).encode("utf-8")
        ).hexdigest()

        logger.debug(f"Generated error reference {ref}")

        result: Embed = Embed(
            title=title,
            description=description,
            url=url,
            color=color,
            timestamp=timestamp,
        )

        if author is not None:
            result.set_author(name=author, url=authorUrl, icon=authorIcon)

        if thumbnail is not None:
            result.set_thumbnail(thumbnail)

        if image is not None:
            result.set_image(image)

        if footer is not None:
            result.set_footer(f"{footer} ({ref})", icon=footerIcon)
        else:
            result.set_footer(ref, icon=footerIcon)

        for field in fields:
            result.add_field(
                field["name"], field["value"], inline=field.get("inline", True)
            )

        return result


class Timestamps:
    """Class containing markdown, timestamp formatting templates."""

    def LongDate(timestamp: Union[int, float, datetime]) -> str:
        """
        Create a long date timestamp using markdown formatting.

        Example: "January 21, 2022"
        """

        if type(timestamp) is float:
            timestamp = int(timestamp)
        elif type(timestamp) is datetime:
            timestamp = int(timestamp.timestamp())

        return f"<t:{timestamp}:D>"

    def ExtraLongDateShortTime(timestamp: Union[int, float, datetime]) -> str:
        """
        Create an extra long date and short time timestamp using markdown formatting.

        Example: "Friday, January 21, 2022 at 4:20 PM"
        """

        if type(timestamp) is float:
            timestamp = int(timestamp)
        elif type(timestamp) is datetime:
            timestamp = int(timestamp.timestamp())

        return f"<t:{timestamp}:F>"

    def LongDateShortTime(timestamp: Union[int, float, datetime]) -> str:
        """
        Create a long date and short time timestamp using markdown formatting.

        Example: "January 21, 2022 at 4:20 PM"
        """

        if type(timestamp) is float:
            timestamp = int(timestamp)
        elif type(timestamp) is datetime:
            timestamp = int(timestamp.timestamp())

        return f"<t:{timestamp}:f>"

    def LongTime(timestamp: Union[int, float, datetime]) -> str:
        """
        Create a long time timestamp using markdown formatting.

        Example: "4:20:00 PM"
        """

        if type(timestamp) is float:
            timestamp = int(timestamp)
        elif type(timestamp) is datetime:
            timestamp = int(timestamp.timestamp())

        return f"<t:{timestamp}:T>"

    def Relative(timestamp: Union[int, float, datetime]) -> str:
        """
        Create a relative timestamp using markdown formatting.

        Example: "in 2 minutes" or "6 minutes ago"
        """

        if type(timestamp) is float:
            timestamp = int(timestamp)
        elif type(timestamp) is datetime:
            timestamp = int(timestamp.timestamp())

        return f"<t:{timestamp}:R>"

    def ShortDate(timestamp: Union[int, float, datetime]) -> str:
        """
        Create a short date timestamp using markdown formatting.

        Example: "1/21/2022"
        """

        if type(timestamp) is float:
            timestamp = int(timestamp)
        elif type(timestamp) is datetime:
            timestamp = int(timestamp.timestamp())

        return f"<t:{timestamp}:d>"

    def ShortTime(timestamp: Union[int, float, datetime]) -> str:
        """
        Create a short time timestamp using markdown formatting.

        Example: "4:20 PM"
        """

        if type(timestamp) is float:
            timestamp = int(timestamp)
        elif type(timestamp) is datetime:
            timestamp = int(timestamp.timestamp())

        return f"<t:{timestamp}:t>"
