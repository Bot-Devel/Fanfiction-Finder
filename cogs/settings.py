import os
from dotenv import load_dotenv

from discord.ext.commands import command, Cog
from discord import Embed, PermissionOverwrite

load_dotenv()
BOT_ID = int(os.getenv('BOT_ID'))


class Settings(Cog):
    def __init__(self, client):
        self.client = client

    @command(pass_context=True, aliases=['allowAll'])
    async def allow_all(self, ctx):
        """Adds send_message perm for all the channels."""

        if not ctx.author.guild_permissions.administrator:
            try:
                return await ctx.send(
                    embed=Embed(
                        description="You are missing Administrator permission to run this command."))
            except Exception:  # send a DM if send message perms is not enabled
                return await ctx.author.send(
                    embed=Embed(
                        description="You are missing Administrator permission to run this command."))

        bot_user = ctx.guild.get_member(BOT_ID)
        channel_list = ctx.guild.channels
        for channel in channel_list:
            try:
                await channel.set_permissions(
                    bot_user,
                    send_messages=True, manage_permissions=True)
            except Exception:
                pass

        embed = Embed(
            description="The bot will now start responding to all the channels."
        )
        await ctx.channel.send(embed=embed)

    @command(pass_context=True, aliases=['disallowAll'])
    async def disallow_all(self, ctx):
        """Removes send_message perm for all the channels."""

        if not ctx.author.guild_permissions.administrator:
            try:
                return await ctx.send(  # send message in channel
                    embed=Embed(
                        description="You are missing Administrator permission to run this command."))
            except Exception:  # send a DM if send message perms is not enabled
                return await ctx.author.send(
                    embed=Embed(
                        description="You are missing Administrator permission to run this command."))

        embed = Embed(
            description="The bot will now stop responding to all the channels."
        )

        try:
            await ctx.channel.send(embed=embed)
        except Exception:
            embed = Embed(
                description="The bot is not allowed to send messages in that channel. Ask one of the server admins to use the `,allow` command in that channel to enable it."
            )
            await ctx.author.send(embed=embed)

        bot_user = ctx.guild.get_member(BOT_ID)
        channel_list = ctx.guild.channels
        for channel in channel_list:
            try:
                await channel.set_permissions(
                    bot_user,
                    send_messages=False, manage_permissions=True)
            except Exception:
                pass

    @command(pass_context=True)
    async def allow(self, ctx):
        """Adds send_message perm for the current channel."""

        if not ctx.author.guild_permissions.administrator:
            try:
                return await ctx.send(
                    embed=Embed(
                        description="You are missing Administrator permission to run this command."))
            except Exception:  # send a DM if send message perms is not enabled
                return await ctx.author.send(
                    embed=Embed(
                        description="You are missing Administrator permission to run this command."))

        bot_user = ctx.guild.get_member(BOT_ID)
        await ctx.channel.set_permissions(
            bot_user,
            send_messages=True, manage_permissions=True)

        embed = Embed(
            description="The bot will now start responding to this channel."
        )
        await ctx.channel.send(embed=embed)

    @command(pass_context=True)
    async def disallow(self, ctx):
        """Removes send_message perm for current channel."""

        if not ctx.author.guild_permissions.administrator:
            try:
                return await ctx.send(
                    embed=Embed(
                        description="You are missing Administrator permission to run this command."))
            except Exception:  # send a DM if send message perms is not enabled
                return await ctx.author.send(
                    embed=Embed(
                        description="You are missing Administrator permission to run this command."))

        embed = Embed(
            description="The bot won't respond to this channel anymore."
        )

        try:
            await ctx.channel.send(embed=embed)
        except Exception:
            embed = Embed(
                description="The bot is not allowed to send messages in that channel. Ask one of the server admins to use the `,allow` command in that channel to enable it."
            )
            await ctx.author.send(embed=embed)

        bot_user = ctx.guild.get_member(BOT_ID)
        await ctx.channel.set_permissions(
            bot_user,
            send_messages=False, manage_permissions=True)

    @command(pass_context=True, aliases=['getChannels'])
    async def get_channels(self, ctx):
        """Gets all the channels in which the bot has send_messages=True"""

        if not ctx.author.guild_permissions.administrator:
            try:
                return await ctx.send(
                    embed=Embed(
                        description="You are missing Administrator permission to run this command."))
            except Exception:  # send a DM if send message perms is not enabled
                return await ctx.author.send(
                    embed=Embed(
                        description="You are missing Administrator permission to run this command."))

        bot_user = ctx.guild.get_member(BOT_ID)
        channel_list = ctx.guild.channels
        channels = []
        for channel in channel_list:

            perms = bot_user.permissions_in(channel)

            if perms.send_messages:
                channels.append(str(channel.id))
            else:
                pass

        channels = ", ".join(channels)
        embed = Embed(
            title="The list of channels in which the bot has send_messages=True perms",
            description=channels
        )
        await ctx.author.send(embed=embed)

    @command(pass_context=True, aliases=['refreshPerms'])
    async def refresh_perms(self, ctx, *, channels=0):
        """Gives the manage_perms=True in all the channels"""

        if not ctx.author.guild_permissions.administrator:
            try:
                return await ctx.send(
                    embed=Embed(
                        description="You are missing Administrator permission to run this command."))
            except Exception:  # send a DM if send message perms is not enabled
                return await ctx.author.send(
                    embed=Embed(
                        description="You are missing Administrator permission to run this command."))

        overwrite = PermissionOverwrite()
        overwrite.manage_permissions = True

        bot_user = ctx.guild.get_member(BOT_ID)
        channel_list = ctx.guild.channels
        channels = [x.strip() for x in channels.split(',')]

        for channel in channel_list:
            if str(channel.id) in channels:
                overwrite.send_messages = True
            else:
                overwrite.send_messages = False

            try:
                await channel.set_permissions(
                    bot_user, overwrite=overwrite)
            except Exception:
                pass

        embed = Embed(
            description="The bot's channel perms were refreshed successfully"
        )
        await ctx.channel.send(embed=embed)

    @command(pass_context=True, aliases=['clr-msgs'])
    async def clear_messages(self, ctx):
        """Clears all non-bot messages"""

        if not ctx.author.guild_permissions.administrator:
            try:
                return await ctx.send(
                    embed=Embed(
                        description="You are missing Administrator permission to run this command."))
            except Exception:  # send a DM if send message perms is not enabled
                return await ctx.author.send(
                    embed=Embed(
                        description="You are missing Administrator permission to run this command."))

        message_history = await ctx.channel.history(
            limit=None).flatten()

        deleted_msgs = 0
        for message in message_history:
            if int(message.author.id) != BOT_ID:
                deleted_msgs += 1
                await message.delete()

        msg = await ctx.channel.send(
            embed=Embed(
                description='Deleted {} message(s)'.format(deleted_msgs-1)))

        await msg.delete(delay=3)  # Delete the bot's message


def setup(client):
    client.add_cog(Settings(client))
