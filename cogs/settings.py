from __future__ import annotations

import discord
from discord.ext import commands
from loguru import logger


class Settings(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    async def cog_command_error(
        self, ctx: commands.Context[commands.Bot], error: Exception
    ) -> None:
        # Handle all errors that occur within this cog.
        if isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(
                description="You are missing Administrator permission to run this command."
            )
            try:
                # send message in channel
                await ctx.send(embed=embed)
            except Exception:
                logger.error(error)
                # send a DM if send message perms is not enabled
                await ctx.author.send(embed=embed)
        else:
            logger.error(error)

    @commands.command(aliases=["allowAll"])
    @commands.has_permissions(administrator=True)
    async def allow_all(self, ctx: commands.Context[commands.Bot]) -> None:
        """Adds send_message perm for all the channels."""

        # Known at runtime
        assert ctx.guild
        assert isinstance(ctx.author, discord.Member)

        channel_list = ctx.guild.channels

        for channel in channel_list:
            try:
                await channel.set_permissions(
                    ctx.guild.me, send_messages=True, manage_permissions=True
                )
            except Exception as err:
                logger.error(err)

        embed = discord.Embed(
            description="The bot will now start responding to all the channels."
        )
        await ctx.send(embed=embed)

    @commands.command(aliases=["disallowAll"])
    @commands.has_permissions(administrator=True)
    async def disallow_all(self, ctx: commands.Context[commands.Bot]) -> None:
        """Removes send_message perm for all the channels."""

        # Known at runtime
        assert ctx.guild
        assert isinstance(ctx.author, discord.Member)

        embed = discord.Embed(
            description="The bot will now stop responding to all the channels."
        )

        try:
            await ctx.send(embed=embed)
        except Exception as err:
            logger.error(err)
            embed = discord.Embed(
                description="The bot is not allowed to send messages in that channel. Ask one of the server admins to use the `,allow` command in that channel to enable it."
            )
            await ctx.author.send(embed=embed)

        channel_list = ctx.guild.channels
        for channel in channel_list:
            try:
                await channel.set_permissions(
                    ctx.guild.me, send_messages=False, manage_permissions=True
                )
            except Exception as err:
                logger.error(err)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def allow(self, ctx: commands.Context[commands.Bot]) -> None:
        """Adds send_message perm for the current channel."""

        # Known at runtime
        assert ctx.guild
        assert isinstance(ctx.author, discord.Member)
        assert isinstance(ctx.channel, discord.abc.GuildChannel)

        await ctx.channel.set_permissions(
            ctx.guild.me, send_messages=True, manage_permissions=True
        )

        embed = discord.Embed(
            description="The bot will now start responding to this channel."
        )
        await ctx.send(embed=embed)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def disallow(self, ctx: commands.Context[commands.Bot]) -> None:
        """Removes send_message perm for current channel."""

        # Known at runtime
        assert ctx.guild
        assert isinstance(ctx.author, discord.Member)
        assert isinstance(ctx.channel, discord.abc.GuildChannel)

        embed = discord.Embed(
            description="The bot won't respond to this channel anymore."
        )

        try:
            await ctx.send(embed=embed)
        except Exception as err:
            logger.error(err)
            embed = discord.Embed(
                description="The bot is not allowed to send messages in that channel. Ask one of the server admins to use the `,allow` command in that channel to enable it."
            )
            await ctx.author.send(embed=embed)

        await ctx.channel.set_permissions(
            ctx.guild.me, send_messages=False, manage_permissions=True
        )

    @commands.command(aliases=["getChannels"])
    @commands.has_permissions(administrator=True)
    async def get_channels(self, ctx: commands.Context[commands.Bot]) -> None:
        """Gets all the channels in which the bot has send_messages=True"""

        # Known at runtime
        assert ctx.guild
        assert isinstance(ctx.author, discord.Member)

        channel_list = ctx.guild.channels
        channels = []
        for channel in channel_list:
            perms = channel.permissions_for(ctx.guild.me)

            if perms.send_messages:
                channels.append(str(channel.id))

        channels = ", ".join(channels)
        embed = discord.Embed(
            title="The list of channels in which the bot has send_messages=True perms",
            description=channels,
        )
        await ctx.author.send(embed=embed)

    @commands.command(aliases=["refreshPerms"])
    @commands.has_permissions(administrator=True)
    async def refresh_perms(
        self,
        ctx: commands.Context[commands.Bot],
        *,
        channels: commands.Greedy[discord.abc.GuildChannel],
    ) -> None:
        """Gives the manage_perms=True in all the channels"""

        # Known at runtime
        assert ctx.guild
        assert isinstance(ctx.author, discord.Member)

        overwrite = discord.PermissionOverwrite(
            manage_permissions=True, send_messages=True
        )

        for channel in channels:
            try:
                await channel.set_permissions(ctx.guild.me, overwrite=overwrite)
            except Exception as err:
                logger.error(err)

        embed = discord.Embed(
            description="The bot's channel perms were refreshed successfully"
        )
        await ctx.send(embed=embed)

    @commands.command(aliases=["clr-msgs"])
    async def clear_messages(self, ctx: commands.Context[commands.Bot]) -> None:
        """Clears all non-bot messages"""

        # Known at runtime
        assert ctx.guild
        assert isinstance(ctx.author, discord.Member)
        assert isinstance(ctx.channel, discord.abc.GuildChannel)

        def purge_check(m: discord.Message) -> bool:
            return m.author.id != ctx.guild.me.id

        purged_messages = await ctx.channel.purge(limit=None, check=purge_check)

        await ctx.send(
            embed=discord.Embed(
                description=f"Deleted {len(purged_messages)} message(s)"
            ),
            delete_after=3.0,  # Delete the bot's message
        )

    @commands.command(aliases=["sync"])
    @commands.is_owner()
    async def tree_sync(self, ctx: commands.Context[commands.Bot]) -> None:
        """Sync all the Slash Commands"""

        # Known at runtime
        assert ctx.guild
        assert isinstance(ctx.author, discord.Member)
        assert isinstance(ctx.channel, discord.abc.GuildChannel)

        await self.client.tree.sync()
        await ctx.send(embed=discord.Embed(description="Syncing all the slash commands!"))

async def setup(client: commands.Bot):
    await client.add_cog(Settings(client))
