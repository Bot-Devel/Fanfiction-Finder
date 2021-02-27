from discord.ext.commands import command, Cog, \
    has_permissions
import discord


class Settings(Cog):
    def __init__(self, client):
        self.client = client

    @has_permissions(administrator=True)
    @command(aliases=['add'], pass_context=True)
    async def add_channel(self, ctx, message):
        """Adds channels to the bot's settings"""

        with open("data/live_channels.txt", "r") as f:
            channels = f.read().splitlines()

        error = 0
        channels = [int(i) for i in channels]
        try:  # check if the message is a channel ID

            message = int(message)

        except ValueError:
            error = 1
            embed = discord.Embed(
                description="That is not a valid channel ID."
            )

        if error == 0:  # If no errors found, add the channel
            with open("data/live_channels.txt", "a") as f:

                if message not in channels:
                    f.write(str(message)+"\n")
                    embed = discord.Embed(
                        description="The channel has been added."
                    )

                else:
                    embed = discord.Embed(
                        description="The channel is already registered!"
                    )

        await ctx.channel.send(embed=embed)

    @has_permissions(administrator=True)
    @command(aliases=['del', 'remove'], pass_context=True)
    async def remove_channel(self, ctx, message):
        """Removes channels from the bot's settings"""

        with open("data/live_channels.txt", "r") as f:
            channels = f.read().splitlines()

        if message in channels:
            channels.remove(message)

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
