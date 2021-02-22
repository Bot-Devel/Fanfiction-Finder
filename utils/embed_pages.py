import discord


def get_embed(page=0):

    page_limit = 2

    if page == 0:
        embed = discord.Embed(
            title="Bot Usage Instructions"
        )
        embed.add_field(
            name="AO3 Searching:",
            value="`ao3 [fic name]` or `ao3 [fic name] series` \
            \n **Example:**\n1) `ao3 rogue knight` \n2) `ao3 prince of slytherin series`"
        )

        embed.add_field(
            name="FFN Searching:",
            value="`ffn [fic name]` \
            \n **Example:**\n`ffn cadmean victory` "
        )
        embed.add_field(
            name="Search using Urls:",
            value="**Example:**\nhttps://archiveofourown.org/series/1119027",
            inline=False
        )
        embed.add_field(
            name="Search using code blocks:",
            value="**Example:** \n\`cadmean victory\` will default to ffnet.\n\`rogue knight ao3\` for ao3.\n\`prince of slytherin ao3 series\` for ao3 series."
        )

    elif page == 1:
        embed = discord.Embed(
            title="Bot Configuration",
            description="This section requires Channel ID for the configuration so copy the Channel ID by right clicking on the channel.\nTo use these commands, you need either administrator permissions or Admin or Mods role."
        )
        embed.add_field(
            name="To add new channels:",
            value="`,add CHANNEL_ID`"
        )

        embed.add_field(
            name="To remove channels:",
            value="`,del CHANNEL_ID`"
        )
    else:
        embed = discord.Embed(
            description="No more configuration options found!"
        )

    page_footer = "Page: "+str(page+1)+'/'+str(page_limit)
    embed.set_footer(text=page_footer)

    return embed, page_limit
