from discord.ext.commands import command, Cog

from utils.embed_pages import get_embed


class Help(Cog):
    def __init__(self, client):
        self.client = client

    @command()
    async def help(self, ctx):

        embed_pg, page_limit = get_embed(0)
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

        await message.clear_reactions()


def setup(client):
    client.add_cog(Help(client))
