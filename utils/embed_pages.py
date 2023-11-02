from __future__ import annotations

from discord import Embed

PAGE0_EMBED = (
    Embed(
        title="Bot Usage Instructions",
        description="**Bugfix for the broken config commands, check Page 4**",
    )
    .add_field(
        name="AO3 Searching:",
        value="`linkao3 [fic name]` or `linkao3 [fic name] series` \
            \n **Example:**\n1) `linkao3 rogue knight` \n2) `linkao3 prince of slytherin series`",
        inline=False,
    )
    .add_field(
        name="Other Fichub supported sites Searching:",
        value="`linkfic [fic name] [site_name]` \
            \n **Example:**\n`linkfic high tide spacebattle`",
        inline=False,
    )
    .add_field(
        name="\u200b", value="**Search using URLs is also allowed**", inline=False
    )
    .add_field(
        name="Search using single-lined code blocks or backquote:",
        value="This will search Fichub first and if it can't find it in Fichub, it will search in ao3. "
        "\n**Example:**\n"
        r"\`cadmean victory\` will default to Fichub.\n\`rogue knight ao3\` for ao3.\n\`prince of slytherin ao3 series\` for ao3 series.",
    )
)

PAGE1_EMBED = (
    Embed(
        title="Bot Configuration",
        description="**Do not give administrator permission to the bot.**\nTo use these commands, you need administrator permission."
        "\nGo to the channel you want to add/remove and use the below commands.",
    )
    .add_field(
        name="To allow the bot to respond to all the channels",
        value="`,allow_all` or `,allowAll`",
        inline=False,
    )
    .add_field(
        name="To disallow the bot from responding to all the channels",
        value="`,disallow_all` or `,disallowAll`",
        inline=False,
    )
    .add_field(
        name="To allow the bot to respond to this channel",
        value="`,allow`",
        inline=False,
    )
    .add_field(
        name="To disallow the bot from responding to this channel",
        value="`,disallow`",
        inline=False,
    )
    .add_field(
        name="To delete all non-bot messages from the channel i.e. all the users except the bot. Useful for archive channels.",
        value="`,clr-msgs`",
        inline=False,
    )
    .add_field(
        name="To delete a bot message if it violates the server rules, the user who requested the bot to find the fanfiction can react with 👎."
        "It's only possible to delete a message if it's done before 30s after the bot has replied.",
        value="\u200b",
        inline=False,
    )
)

PAGE2_EMBED = Embed(
    title="Bot Support",
    description=(
        "Join the Bot's Discord Support Server if you want to report any bugs or want to suggest new features."
        "\n[Discord Support Server](https://discord.gg/bRzzr3EBqH)"
    ),
)

PAGE_LOOKUP = {
    0: PAGE0_EMBED,
    1: PAGE1_EMBED,
    2: PAGE2_EMBED,
}


def get_embed(page: int = 0):
    page_limit = 3
    embed = PAGE_LOOKUP.get(page, Embed(description="No more pages found!"))
    page_footer = f"Page: {page+1}/{page_limit}"
    embed.set_footer(text=page_footer)

    return embed, page_limit
