from __future__ import annotations

import discord
from discord.ext import commands

from utils.embed_pages import HelpView


class Help(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @commands.command()
    async def help(self, ctx: commands.Context):
        async with ctx.typing():
            view = HelpView()
            view.message = await ctx.send(embed=view.get_first_page(), view=view)

    @help.error
    async def help_error(self, ctx: commands.Context, error: commands.CommandError):
        if isinstance(error, commands.BotMissingPermissions):
            embed = discord.Embed(
                description="The bot is not allowed to send messages in that channel. Ask one of the server admins to use the `,allow` command in that channel to enable it."
            )
            await ctx.author.send(embed=embed)


async def setup(client: commands.Bot):
    await client.add_cog(Help(client))
