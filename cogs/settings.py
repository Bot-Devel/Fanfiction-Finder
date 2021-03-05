from discord.ext.commands import command, Cog, \
    has_permissions
import discord


class Settings(Cog):
    def __init__(self, client):
        self.client = client

    @has_permissions(administrator=True)
    @command(aliases=['allow'], pass_context=True)
    async def add_channel(self, ctx):
        """Adds channels to the bot's settings"""

        with open("data/live_channels.txt", "r") as f:
            channels = f.read().splitlines()

        channels = [int(i) for i in channels]
        with open("data/live_channels.txt", "a") as f:

            if ctx.channel.id not in channels:
                f.write(str(ctx.channel.id)+"\n")
                embed = discord.Embed(
                    description="The channel has been added."
                )

            else:
                embed = discord.Embed(
                    description="The channel is already registered!"
                )

        await ctx.channel.send(embed=embed)

    @has_permissions(administrator=True)
    @command(aliases=['disallow'], pass_context=True)
    async def remove_channel(self, ctx):
        """Removes channels from the bot's settings"""

        with open("data/live_channels.txt", "r") as f:
            channels = f.read().splitlines()

        if str(ctx.channel.id) in channels:
            channels.remove(str(ctx.channel.id))

        with open("data/live_channels.txt", "w") as f:
            for channel in channels:
                f.write(str(channel)+"\n")

        embed = discord.Embed(
            description="The channel has been removed \
             from the bot's config."
        )

        await ctx.channel.send(embed=embed)


def setup(client):
    client.add_cog(Settings(client))
