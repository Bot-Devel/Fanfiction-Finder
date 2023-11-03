from __future__ import annotations

import discord
from discord.ext import commands
from loguru import logger

from utils.embed_pages import HelpView


class Help(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @commands.hybrid_command(name="help")
    async def help(self, ctx: commands.Context):
        """Help menu for the bot"""
    
        async with ctx.typing():
            view = HelpView()
            view.message = await ctx.send(embed=view.get_first_page(), view=view)

    @help.error
    async def help_error(self, ctx: commands.Context, error: commands.CommandError):
        """Error handler for the help command."""
        if isinstance(error, commands.BotMissingPermissions):
            embed = discord.Embed(
                description="The bot is not allowed to send messages in that channel. Ask one of the server admins to use the `,allow` command in that channel to enable it."
            )
            await ctx.author.send(embed=embed)
        else:
            logger.error(error)


async def setup(client: commands.Bot):
    await client.add_cog(Help(client))
