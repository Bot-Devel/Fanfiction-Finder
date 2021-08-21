from discord.ext.commands import command, Cog
import discord
import re

from utils.embed_pages import get_embed


class Help(Cog):
    def __init__(self, client):
        self.client = client

    @command()
    async def help(self, ctx):

        try:
            embed_pg, page_limit = get_embed(ctx.author.id, 0)
            message = await ctx.send(embed=embed_pg)
            await message.add_reaction('⏮')
            await message.add_reaction('◀')
            await message.add_reaction('▶')
            await message.add_reaction('⏭')

            def check(reaction, user):
                return user == ctx.author

            page = 0
            reaction = None
            while True:
                if str(reaction) == '⏮':
                    page = 0
                    embed_pg, page_limit = get_embed(page)
                    await message.edit(embed=embed_pg)
                elif str(reaction) == '◀':
                    if page > 0:
                        page -= 1
                        embed_pg, page_limit = get_embed(page)
                        await message.edit(embed=embed_pg)
                elif str(reaction) == '▶':
                    if page < page_limit:
                        page += 1
                        embed_pg, page_limit = get_embed(page)
                        await message.edit(embed=embed_pg)
                elif str(reaction) == '⏭':
                    page = page_limit-1
                    embed_pg, page_limit = get_embed(page)
                    await message.edit(embed=embed_pg)

                reaction, user = await self.client.wait_for('reaction_add', timeout=30.0, check=check)
                await message.remove_reaction(reaction, user)
        except Exception as error:

            if re.search("Missing Permissions", str(error), re.IGNORECASE):
                embed = discord.Embed(
                    description="The bot is not allowed to send messages in that channel. Ask one of the server admins to use the `,allow` command in that channel to enable it."
                )
                await ctx.author.send(embed=embed)
            elif re.search("TimeoutError", str(error), re.IGNORECASE):
                pass  # ignore Timeout errors

        finally:
            try:
                await message.clear_reactions()
            except UnboundLocalError:
                pass  # ignore this


def setup(client):
    client.add_cog(Help(client))
