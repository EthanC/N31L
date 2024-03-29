import asyncio
import sys
from datetime import datetime
from sys import exit
from typing import Any

import hikari
import tanjun
from hikari import (
    Application,
    Attachment,
    DMChannel,
    GatewayBot,
    Guild,
    GuildTextChannel,
    InteractionChannel,
    OwnUser,
    Permissions,
    User,
)
from hikari.embeds import Embed
from hikari.errors import NotFoundError
from hikari.interactions.base_interactions import InteractionMember
from hikari.presences import Activity, ActivityType, Status
from hikari.users import UserImpl
from loguru import logger
from tanjun import Client, Component
from tanjun.abc import SlashContext
from tanjun.commands import SlashCommandGroup

from helpers import Responses, Timestamps
from models import State

component: Component = Component(name="Admin")

send: SlashCommandGroup = component.with_slash_command(
    tanjun.slash_command_group("send", "Send messages from N31L.")
)
set: SlashCommandGroup = component.with_slash_command(
    tanjun.slash_command_group("set", "Manage the state of N31L.")
)
emoji: SlashCommandGroup = component.with_slash_command(
    tanjun.slash_command_group("emoji", "Manage server custom emoji.")
)
stickers: SlashCommandGroup = component.with_slash_command(
    tanjun.slash_command_group("stickers", "Manage server stickers.")
)


@component.with_slash_command()
@tanjun.with_own_permission_check(Permissions.BAN_MEMBERS)
@tanjun.with_str_slash_option("reason", "Enter a reason for unbanning this user.")
@tanjun.with_user_slash_option("user", "Enter a user (userId acceptable).")
@tanjun.as_slash_command("unban", "Unban a user from the current server.")
async def CommandUnban(
    ctx: SlashContext,
    user: InteractionMember | UserImpl,
    reason: str,
    client: Client = tanjun.inject(type=Client),
    config: dict[str, Any] = tanjun.inject(type=dict[str, Any]),
) -> None:
    """Handler for the /unban slash command."""

    server: Guild = await ctx.fetch_guild()

    try:
        await server.unban(
            user,
            reason=f"Unbanned by {Responses.ExpandUser(ctx.author, False)} with reason: {reason}",
        )
    except NotFoundError:
        await ctx.respond(
            Responses.Warning(
                description=f"{Responses.ExpandUser(user)} is not banned in this server."
            )
        )

        return
    except Exception as e:
        logger.opt(exception=e).error(
            f"Failed to unban {Responses.ExpandUser(user)} in {Responses.ExpandGuild(ctx.guild_id)}"
        )

        await ctx.respond(
            Responses.Fail(
                description=f"Failed to unban {Responses.ExpandUser(user)}, an unknown error occurred."
            )
        )

        return

    await client.rest.create_message(
        config["channels"]["moderation"],
        Responses.Log(
            "hammer",
            f"{Responses.ExpandUser(user)} unbanned by {Responses.ExpandUser(ctx.author)} with reason: *{reason}*",
        ),
    )

    await ctx.respond(
        embed=Responses.Success(description=f"Unbanned {Responses.ExpandUser(user)}")
    )


@component.with_slash_command()
@tanjun.with_own_permission_check(Permissions.SEND_MESSAGES)
@tanjun.with_user_slash_option("user", "Enter a user to fetch the profile of.")
@tanjun.as_slash_command("profile", "Fetch detailed information about a Discord user.")
async def CommandProfile(ctx: SlashContext, user: InteractionMember | UserImpl) -> None:
    """Handler for the /profile slash command."""

    if hasattr(user, "user"):
        try:
            user.user = await ctx.rest.fetch_user(user.id)
        except Exception as e:
            logger.opt(exception=e).warning(
                f"Failed to fetch user {Responses.ExpandUser(user.id, False)}"
            )

    fields: list[dict[str, Any]] = []
    altAvatar: str | None = None
    accent: str | None = None

    if hasattr(user, "nickname"):
        if nickname := user.nickname:
            fields.append({"name": "Nickname", "value": nickname})

    if hasattr(user, "created_at"):
        if created := user.created_at:
            fields.append({"name": "Created", "value": Timestamps.Relative(created)})

    if hasattr(user, "joined_at"):
        if joined := user.joined_at:
            fields.append({"name": "Joined", "value": Timestamps.Relative(joined)})

    if hasattr(user, "premium_since"):
        if booster := user.premium_since:
            fields.append(
                {
                    "name": "Nitro Booster",
                    "value": f"Since {Timestamps.Relative(booster)}",
                }
            )

    if hasattr(user, "communication_disabled_until"):
        if timeout := user.communication_disabled_until():
            fields.append(
                {"name": "Timed Out", "value": f"Until {Timestamps.Relative(timeout)}"}
            )

    if hasattr(user, "is_pending"):
        if user.is_pending:
            fields.append({"name": "Passed Screening", "value": "No"})

    if hasattr(user, "is_mute"):
        if user.is_mute:
            fields.append({"name": "Muted", "value": "Yes"})

    if hasattr(user, "is_deaf"):
        if user.is_deaf:
            fields.append({"name": "Deafened", "value": "Yes"})

    if hasattr(user, "guild_avatar_url"):
        if url := user.guild_avatar_url:
            altAvatar = url

    if hasattr(user, "accent_color"):
        if color := user.accent_color:
            accent = str(color).replace("#", "")

    result: Embed = Responses.Success(
        color=accent,
        fields=fields,
        author=Responses.ExpandUser(user, False, False),
        authorIcon=altAvatar,
        thumbnail=user.default_avatar_url
        if not (avatar := user.avatar_url)
        else avatar,
        image=None if not hasattr(user, "user") else user.user.banner_url,
        footer=user.id,
        timestamp=None if not created else created.astimezone(),
    )

    await ctx.respond(embed=result)


@component.with_slash_command()
@tanjun.with_owner_check()
@tanjun.with_own_permission_check(Permissions.SEND_MESSAGES)
@tanjun.with_int_slash_option(
    "delay", "Time (in seconds) to wait before initiating reboot.", default=None
)
@tanjun.as_slash_command("reboot", "Restart the active N31L instance.")
async def CommandReboot(
    ctx: SlashContext, delay: int | None, state: State = tanjun.inject(type=State)
) -> None:
    """Handler for the /reboot slash command."""

    started: dict[str, Any] = {
        "name": "Instance Started",
        "value": Timestamps.Relative(state.botStart),
    }

    if delay:
        await ctx.respond(
            embed=Responses.Success(
                description=f"N31L will reboot {Timestamps.Relative((datetime.now().timestamp() + delay))}...",
                fields=[started],
            )
        )

        await asyncio.sleep(float(delay))
    else:
        await ctx.respond(
            embed=Responses.Success(
                description="N31L is rebooting...", fields=[started]
            )
        )

    try:
        logger.critical(
            "N31L is rebooting, this function assumes that a process manager, such as Docker, will automatically restart the process"
        )

        exit(0)
    except Exception as e:
        logger.opt(exception=e).critical("Failed to restart bot instance")

        await ctx.create_followup(
            embed=Responses.Fail(
                description="Failed to reboot, an unknown error occurred."
            )
        )


@component.with_slash_command()
@tanjun.with_own_permission_check(Permissions.SEND_MESSAGES)
@tanjun.as_slash_command(
    "server",
    "Fetch detailed information about the current server.",
    default_to_ephemeral=True,
)
async def CommandServer(ctx: SlashContext) -> None:
    """Handler for the /server slash command."""

    server: Guild = await ctx.fetch_guild()
    creators: dict[int, int] = {136986169563938816: 132693143173857281}

    fields: list[dict[str, Any]] = []

    if hasattr(server, "created_at"):
        if created := server.created_at:
            fields.append({"name": "Created", "value": Timestamps.Relative(created)})

    if creator := creators.get(server.id):
        fields.append({"name": "Creator", "value": f"<@{creator}>"})

    if hasattr(server, "owner_id"):
        if owner := server.owner_id:
            fields.append({"name": "Owner", "value": f"<@{owner}>"})

    await ctx.respond(
        embed=Responses.Success(
            title=server.name,
            url=None
            if not (vanity := server.vanity_url_code)
            else f"https://discord.gg/{vanity}",
            description=server.description,
            fields=fields,
            thumbnail=server.icon_url,
            image=server.banner_url,
            footer=f"{server.id} ({server.shard_id})"
            if hasattr(server, "shard_id")
            else server.id,
            timestamp=server.created_at,
        )
    )


@component.with_slash_command()
@tanjun.with_own_permission_check(Permissions.SEND_MESSAGES)
@tanjun.as_slash_command(
    "status", "Get the status of and information about N31L.", default_to_ephemeral=True
)
async def CommandStatus(
    ctx: SlashContext,
    state: State = tanjun.inject(type=State),
    bot: GatewayBot = tanjun.inject(type=GatewayBot),
) -> None:
    """Handler for the /status slash command."""

    stats: list[dict[str, Any]] = []

    # Make a request to Discord to determine the REST latency
    latStart: float = datetime.now().timestamp()
    own: OwnUser = await ctx.rest.fetch_my_user()
    latEnd: float = datetime.now().timestamp()

    app: Application = await ctx.rest.fetch_application()
    guild: Guild = await ctx.fetch_guild()

    stats.append({"name": "Owner", "value": f"<@{app.owner.id}>"})
    stats.append({"name": "Created", "value": Timestamps.Relative(own.created_at)})
    stats.append({"name": "Started", "value": Timestamps.Relative(state.botStart)})

    stats.append(
        {"name": "REST Latency", "value": f"{round((latEnd - latStart) * 1000):,}ms"}
    )
    stats.append(
        {
            "name": "Heartbeat Latency",
            "value": f"{round(bot.heartbeat_latency * 1000):,}ms",
        }
    )
    stats.append({"name": "Guild Shard", "value": f"{guild.shard_id:,}"})

    stats.append(
        {
            "name": "Python",
            "value": f"[`{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}`](https://www.python.org/)",
        }
    )
    stats.append(
        {"name": "Hikari", "value": f"[`{hikari.__version__}`]({hikari.__url__})"}
    )
    stats.append(
        {"name": "GitHub", "value": "[EthanC/N31L](https://github.com/EthanC/N31L)"}
    )

    await ctx.respond(
        embed=Responses.Success(
            color="00FF00",
            description="N31L is a utilitarian bot for the Call of Duty server.\n\nThe commands and functionality of this bot are purpose-built and primarily intended for the Moderators of the server. Because of this, the current bot instance is not available to be invited to other servers.",
            fields=stats,
            author="N31L",
            authorUrl="https://github.com/EthanC/N31L",
            authorIcon="https://i.imgur.com/cGtkGuI.png",
            footer="Developed by lacking",
            footerIcon="https://i.imgur.com/WTQid9f.gif",
        ),
    )


@send.with_command
@tanjun.with_owner_check()
@tanjun.with_attachment_slash_option(
    "attachment", "Upload a file to attach to the message.", default=None
)
@tanjun.with_str_slash_option(
    "content", "Enter the content of the message to send.", default=None
)
@tanjun.with_user_slash_option("user", "Choose a user to send a message to.")
@tanjun.as_slash_command(
    "direct_message",
    "Send a direct message from N31L.",
    default_to_ephemeral=True,
)
async def CommandSendDirectMessage(
    ctx: SlashContext,
    user: User,
    content: str | None,
    attachment: Attachment | None,
) -> None:
    """Handler for the /send direct_message slash command."""

    if (not content) and (not attachment):
        await ctx.respond(
            embed=Responses.Fail(
                description=f"Failed to send direct message to {Responses.ExpandUser(user, False)}, you must supply message content or an attachment."
            )
        )

        return

    try:
        dm: DMChannel = await ctx.rest.create_dm_channel(user.id)

        await ctx.rest.create_message(
            dm.id, content, attachments=[] if not attachment else [attachment]
        )
    except Exception as e:
        logger.opt(exception=e).error(
            f"Failed to send direct message to {Responses.ExpandUser(user, False)}"
        )
        logger.trace(content)

        await ctx.respond(
            embed=Responses.Fail(
                description=f"Failed to send direct message to {Responses.ExpandUser(user)}, {e}"
            )
        )

        return

    await ctx.respond(
        embed=Responses.Success(
            description=f"Direct Message sent to {Responses.ExpandUser(user)}."
        )
    )

    logger.success(
        f"{Responses.ExpandUser(ctx.author, False)} sent a direct message to {Responses.ExpandUser(user, False)}"
    )


@send.with_command
@tanjun.with_owner_check()
@tanjun.with_attachment_slash_option(
    "attachment", "Upload a file to attach to the message.", default=None
)
@tanjun.with_str_slash_option(
    "content", "Enter the content of the message to send.", default=None
)
@tanjun.with_channel_slash_option(
    "channel", "Choose a channel to send a message to.", types=[GuildTextChannel]
)
@tanjun.as_slash_command(
    "message",
    "Send a message from N31L.",
    default_to_ephemeral=True,
)
async def CommandSendMessage(
    ctx: SlashContext,
    channel: InteractionChannel,
    content: str | None,
    attachment: Attachment | None,
) -> None:
    """Handler for the /send message slash command."""

    if (not content) and (not attachment):
        await ctx.respond(
            embed=Responses.Fail(
                description=f"Failed to send message to {Responses.ExpandChannel(channel)}, you must supply message content or an attachment."
            )
        )

        return

    try:
        await ctx.rest.create_message(
            channel.id, content, attachments=[] if not attachment else [attachment]
        )
    except Exception as e:
        logger.opt(exception=e).error(
            f"Failed to send message to {Responses.ExpandGuild(ctx.get_guild(), False)} {Responses.ExpandChannel(channel, False)}"
        )
        logger.trace(content)

        await ctx.respond(
            embed=Responses.Fail(
                description=f"Failed to send message to {Responses.ExpandChannel(channel)}, {e}"
            )
        )

        return

    await ctx.respond(
        embed=Responses.Success(
            description=f"Message sent to {Responses.ExpandChannel(channel)}."
        )
    )

    logger.success(
        f"{Responses.ExpandUser(ctx.author, False)} sent a message to {Responses.ExpandChannel(channel, False)}"
    )


@set.with_command
@tanjun.with_owner_check()
@tanjun.with_str_slash_option(
    "url",
    "Enter a Twitch stream URL (used only for Streaming activity type.)",
    default=None,
)
@tanjun.with_str_slash_option("name", "Enter an activity name.")
@tanjun.with_int_slash_option(
    "type",
    "Choose an activity type.",
    choices={
        "Competing in": ActivityType.COMPETING.value,
        "Listening to": ActivityType.LISTENING.value,
        "Playing": ActivityType.PLAYING.value,
        "Streaming": ActivityType.STREAMING.value,
        "Watching": ActivityType.WATCHING.value,
    },
)
@tanjun.as_slash_command("activity", "Set the presence activity for N31L.")
async def CommandSetActivity(
    ctx: SlashContext,
    type: int,
    name: str,
    url: str | None = None,
    bot: GatewayBot = tanjun.inject(type=GatewayBot),
) -> None:
    """Handler for the /set activity slash command."""

    try:
        await bot.update_presence(activity=Activity(name=name, url=url, type=type))
    except Exception as e:
        logger.opt(exception=e).error(
            f"Failed to set presence activity to {ActivityType(type).name} {name}"
        )

        await ctx.respond(
            embed=Responses.Fail(description=f"Failed to set presence activity, {e}")
        )

        return

    await ctx.respond(
        embed=Responses.Success(
            description=f"Set presence activity to `{ActivityType(type).name}` `{name}`."
        )
    )


@set.with_command
@tanjun.with_owner_check()
@tanjun.with_attachment_slash_option(
    "image", "Upload an image file or leave empty to use default avatar.", default=None
)
@tanjun.as_slash_command("avatar", "Set the avatar for N31L.")
async def CommandSetAvatar(ctx: SlashContext, image: Attachment | None) -> None:
    """Handler for the /set avatar slash command."""

    url: str | None = None if not image else image.url

    try:
        if image:
            if (not image.width) or (not image.height):
                logger.error(
                    f"Failed to set avatar to {url}, provided attachment is not a valid image ({image.width}x{image.height})"
                )

                await ctx.respond(
                    embed=Responses.Fail(
                        description="Failed to set avatar, provided attachment is not a valid image"
                    )
                )

                return

            await ctx.rest.edit_my_user(avatar=url)
        else:
            await ctx.rest.edit_my_user(avatar=None)
    except Exception as e:
        logger.opt(exception=e).error(f"Failed to set avatar to {url}")

        await ctx.respond(
            embed=Responses.Fail(description=f"Failed to set avatar, {e}")
        )

        return

    await ctx.respond(
        embed=Responses.Success(description=f"Set avatar to `{url}`.", image=url)
    )


@set.with_command
@tanjun.with_owner_check()
@tanjun.with_own_permission_check(Permissions.SEND_MESSAGES)
@tanjun.with_str_slash_option(
    "type",
    "Choose a status type.",
    choices={
        "Do Not Disturb": Status.DO_NOT_DISTURB.value,
        "Idle": Status.IDLE.value,
        "Online": Status.ONLINE.value,
    },
)
@tanjun.as_slash_command("status", "Set the presence status for N31L.")
async def CommandSetStatus(
    ctx: SlashContext, type: str, bot: GatewayBot = tanjun.inject(type=GatewayBot)
) -> None:
    """Handler for the /set status slash command."""

    color: str | None = None

    if type == Status.DO_NOT_DISTURB:
        color = "ED4245"
    elif type == Status.IDLE:
        color = "FAA81A"
    elif type == Status.ONLINE:
        color = "3BA55D"

    try:
        await bot.update_presence(status=type)
    except Exception as e:
        logger.opt(exception=e).error(
            f"Failed to set presence status to {Status(type).name}"
        )

        await ctx.respond(
            embed=Responses.Fail(description=f"Failed to set presence status, {e}")
        )

        return

    await ctx.respond(
        embed=Responses.Success(
            color=color, description=f"Set presence status to `{Status(type).name}`."
        )
    )


@set.with_command
@tanjun.with_owner_check()
@tanjun.with_str_slash_option("username", "Enter a username.")
@tanjun.as_slash_command("username", "Set the username for N31L.")
async def CommandSetUsername(ctx: SlashContext, username: str) -> None:
    """Handler for the /set username slash command."""

    try:
        await ctx.rest.edit_my_user(username=username)
    except Exception as e:
        logger.opt(exception=e).error(f"Failed to set username to {username}")

        await ctx.respond(
            embed=Responses.Fail(description=f"Failed to set username, {e}")
        )

        return

    await ctx.respond(
        embed=Responses.Success(description=f"Set username to `{username}`.")
    )


@emoji.with_command
@tanjun.with_owner_check()
@tanjun.with_own_permission_check(Permissions.CREATE_GUILD_EXPRESSIONS)
@tanjun.with_own_permission_check(Permissions.MANAGE_GUILD_EXPRESSIONS)
@tanjun.with_str_slash_option(
    "name",
    "Enter a name for the emoji (image filename is default).",
    min_length=2,
    default=None,
)
@tanjun.with_attachment_slash_option("image", "Choose an image for the emoji.")
@tanjun.as_slash_command("upload", "Upload a emoji to this server.")
async def CommandEmojiUpload(
    ctx: SlashContext, image: Attachment, name: str | None
) -> None:
    """Handler for the /emoji upload slash command."""

    await ctx.defer(ephemeral=True)

    try:
        if not name:
            name = image.filename.rsplit(".")[0]

        await ctx.rest.create_emoji(
            await ctx.fetch_guild(),
            name,
            image.url,
            reason=f"Uploaded by {Responses.ExpandUser(ctx.author, False)}",
        )
    except Exception as e:
        logger.opt(exception=e).error(f"Failed to upload emoji :{name}:")

        await ctx.respond(
            embed=Responses.Fail(description=f"Failed to upload emoji `:{name}:`.")
        )

        return

    await ctx.respond(
        embed=Responses.Success(description=f"Uploaded emoji `:{name}:`.")
    )


@emoji.with_command
@tanjun.with_owner_check()
@tanjun.with_own_permission_check(Permissions.CREATE_GUILD_EXPRESSIONS)
@tanjun.with_own_permission_check(Permissions.MANAGE_GUILD_EXPRESSIONS)
@tanjun.with_str_slash_option("id", "Enter the ID of the emoji.")
@tanjun.as_slash_command("delete", "Delete a emoji on this server.")
async def CommandEmojiDelete(ctx: SlashContext, id: str) -> None:
    """Handler for the /emoji delete slash command."""

    await ctx.defer(ephemeral=True)

    try:
        await ctx.rest.delete_emoji(
            await ctx.fetch_guild(),
            int(id),
            reason=f"Deleted by {Responses.ExpandUser(ctx.author, False)}",
        )
    except Exception as e:
        logger.opt(exception=e).error(f"Failed to delete emoji {id}")

        await ctx.respond(
            embed=Responses.Fail(description=f"Failed to delete emoji `{id}`.")
        )

        return

    await ctx.respond(embed=Responses.Success(description=f"Deleted emoji `:{id}:`."))


@stickers.with_command
@tanjun.with_owner_check()
@tanjun.with_own_permission_check(Permissions.CREATE_GUILD_EXPRESSIONS)
@tanjun.with_own_permission_check(Permissions.MANAGE_GUILD_EXPRESSIONS)
@tanjun.with_str_slash_option(
    "description", "Enter a description for the sticker.", default=None
)
@tanjun.with_str_slash_option(
    "name",
    "Enter a name for the sticker (image filename is default).",
    min_length=2,
    default=None,
)
@tanjun.with_str_slash_option("related", "Enter a related emoji for the sticker.")
@tanjun.with_attachment_slash_option("image", "Choose an image for the sticker.")
@tanjun.as_slash_command("upload", "Upload a sticker to this server.")
async def CommandStickerUpload(
    ctx: SlashContext,
    image: Attachment,
    related: str,
    name: str | None,
    description: str | None,
) -> None:
    """Handler for the /sticker upload slash command."""

    await ctx.defer(ephemeral=True)

    try:
        if not name:
            name = image.filename.rsplit(".")[0].replace("_", " ")

        await ctx.rest.create_sticker(
            await ctx.fetch_guild(),
            name,
            related,
            image.url,
            description=description,
            reason=f"Uploaded by {Responses.ExpandUser(ctx.author, False)}",
        )
    except Exception as e:
        logger.opt(exception=e).error(f"Failed to upload sticker {name}")

        await ctx.respond(
            embed=Responses.Fail(description=f"Failed to upload sticker `{name}`.")
        )

        return

    await ctx.respond(
        embed=Responses.Success(description=f"Uploaded sticker `{name}`.")
    )


@stickers.with_command
@tanjun.with_owner_check()
@tanjun.with_own_permission_check(Permissions.CREATE_GUILD_EXPRESSIONS)
@tanjun.with_own_permission_check(Permissions.MANAGE_GUILD_EXPRESSIONS)
@tanjun.with_str_slash_option("id", "Enter the ID of the sticker.")
@tanjun.as_slash_command("delete", "Delete a sticker on this server.")
async def CommandStickerDelete(ctx: SlashContext, id: str) -> None:
    """Handler for the /sticker delete slash command."""

    await ctx.defer(ephemeral=True)

    try:
        await ctx.rest.delete_sticker(
            await ctx.fetch_guild(),
            id,
            reason=f"Deleted by {Responses.ExpandUser(ctx.author, False)}",
        )
    except Exception as e:
        logger.opt(exception=e).error(f"Failed to delete sticker {id}")

        await ctx.respond(
            embed=Responses.Fail(description=f"Failed to delete sticker `{id}`.")
        )

        return

    await ctx.respond(embed=Responses.Success(description=f"Deleted sticker `{id}`."))
