from discord.ext.commands import command, Cog
import discord


class Settings(Cog):
    def __init__(self, client):
        self.client = client

    @command(pass_context=True)
    async def allow_all(self, ctx):
        """Adds send_message perm for all the channels."""

        if not ctx.author.guild_permissions.administrator:
            try:
                return await ctx.send(
                    embed=discord.Embed(
                        description="You are missing Administrator permission to run this command."))
            except Exception:  # send a DM if send message perms is not enabled
                return await ctx.author.send(
                    embed=discord.Embed(
                        description="You are missing Administrator permission to run this command."))

        bot_user = ctx.guild.get_member(779772534040166450)
        channel_list = ctx.guild.channels
        for channel in channel_list:
            try:
                await channel.set_permissions(bot_user, send_messages=True)
            except Exception:
                pass

        embed = discord.Embed(
            description="The bot will now start responding to all the channels."
        )
        await ctx.channel.send(embed=embed)

    @command(pass_context=True)
    async def disallow_all(self, ctx):
        """Removes send_message perm for all the channels."""

        if not ctx.author.guild_permissions.administrator:
            try:
                return await ctx.send(
                    embed=discord.Embed(
                        description="You are missing Administrator permission to run this command."))
            except Exception:  # send a DM if send message perms is not enabled
                return await ctx.author.send(
                    embed=discord.Embed(
                        description="You are missing Administrator permission to run this command."))

        embed = discord.Embed(
            description="The bot will now stop responding to all the channels."
        )

        try:
            await ctx.channel.send(embed=embed)
        except Exception:
            embed = discord.Embed(
                description="The bot is not allowed to send messages in that channel. Ask one of the server admins to use the `,allow` command in that channel to enable it."
            )
            await ctx.author.send(embed=embed)

        bot_user = ctx.guild.get_member(779772534040166450)
        channel_list = ctx.guild.channels
        for channel in channel_list:
            try:
                await channel.set_permissions(bot_user, send_messages=False)
            except Exception:
                pass

    @command(pass_context=True)
    async def allow(self, ctx):
        """Adds send_message perm for the current channel."""

        if not ctx.author.guild_permissions.administrator:
            try:
                return await ctx.send(
                    embed=discord.Embed(
                        description="You are missing Administrator permission to run this command."))
            except Exception:  # send a DM if send message perms is not enabled
                return await ctx.author.send(
                    embed=discord.Embed(
                        description="You are missing Administrator permission to run this command."))

        bot_user = ctx.guild.get_member(779772534040166450)
        await ctx.channel.set_permissions(
            bot_user,
            send_messages=True)

        embed = discord.Embed(
            description="The bot will now start responding to this channel."
        )
        await ctx.channel.send(embed=embed)

    @command(pass_context=True)
    async def disallow(self, ctx):
        """Removes send_message perm for current channel."""

        if not ctx.author.guild_permissions.administrator:
            try:
                return await ctx.send(
                    embed=discord.Embed(
                        description="You are missing Administrator permission to run this command."))
            except Exception:  # send a DM if send message perms is not enabled
                return await ctx.author.send(
                    embed=discord.Embed(
                        description="You are missing Administrator permission to run this command."))

        embed = discord.Embed(
            description="The bot won't respond to this channel anymore."
        )

        try:
            await ctx.channel.send(embed=embed)
        except Exception:
            embed = discord.Embed(
                description="The bot is not allowed to send messages in that channel. Ask one of the server admins to use the `,allow` command in that channel to enable it."
            )
            await ctx.author.send(embed=embed)

        bot_user = ctx.guild.get_member(779772534040166450)
        await ctx.channel.set_permissions(
            bot_user,
            send_messages=False)


def setup(client):
    client.add_cog(Settings(client))
