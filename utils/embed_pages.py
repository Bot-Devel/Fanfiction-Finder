from discord import Embed


def get_embed(author_id, page=0):
    page_limit = 4

    if page == 0:
        embed = Embed(
            title="Bot Usage Instructions",
            description="**Bugfix for the broken config commands, check Page 4**"
        )
        embed.add_field(
            name="AO3 Searching:",
            value="`linkao3 [fic name]` or `linkao3 [fic name] series` \
            \n **Example:**\n1) `linkao3 rogue knight` \n2) `linkao3 prince of slytherin series`",
            inline=False
        )

        embed.add_field(
            name="FFN Searching:",
            value="`linkffn [fic name]` \
            \n **Example:**\n`linkffn cadmean victory`",
            inline=False
        )
        embed.add_field(
            name="\u200b",
            value="**Search using URLs is also allowed**",
            inline=False
        )
        embed.add_field(
            name="Search using single-lined code blocks or backquote:",
            value="This will search ffn first and if it can't find it in ffn, it will search in ao3. " +
            "Use this when you are not sure if the fanfiction is from ffn or ao3.\n**Example:**\n \
            \`cadmean victory\` will default to ffnet.\n\`rogue knight ao3\` for ao3.\n\`prince of slytherin ao3 series\` for ao3 series."
        )

    elif page == 1:
        embed = Embed(
            title="Bot Configuration",
            description="**Do not give administrator permission to the bot.**\nTo use these commands, you need administrator permission. \
            \nGo to the channel you want to add/remove and use the below commands."
        )
        embed.add_field(
            name="To allow the bot to respond to all the channels",
            value="`,allow_all` or `,allowAll`", inline=False
        )
        embed.add_field(
            name="To disallow the bot from responding to all the channels",
            value="`,disallow_all` or `,disallowAll`", inline=False
        )
        embed.add_field(
            name="To allow the bot to respond to this channel",
            value="`,allow`", inline=False
        )

        embed.add_field(
            name="To disallow the bot from responding to this channel",
            value="`,disallow`", inline=False
        )

        embed.add_field(
            name="To delete all non-bot messages from the channel i.e. all the users except the bot. Useful for archive channels.",
            value="`,clr-msgs`", inline=False
        )

        embed.add_field(
            name="To delete a bot message if it violates the server rules, the user who requested the bot to find the fanfiction can reply to the offending bot message by clicking on `Reply` and replying with `del`.",
            value="**Note:** Help menu messages can also be deleted using this command.", inline=False
        )

    elif page == 2:
        embed = Embed(
            title="Bot Support",
            description="Join the Bot's Discord Support Server if you want to report any bugs or want to suggest new features." +
            "\n[Discord Support Server](https://discord.gg/bRzzr3EBqH)"
        )

    elif page == 3:
        embed = Embed(
            title="Bugfix for the broken config commands - 22nd May, 2021",
            description="Few weeks back, the config commands i.e. `,allow`, `,disallow` etc were broken due to a Discord API change.\nTo fix the bug, the bot needs to have `manage_permissions=True` in all the channel settings.\nTwo temporary commands have been added: `,getChannels` & `,refreshPerms` to make the fix easier.\n Use `,getChannels` first, the bot will DM you a comma separated list of channels in which the bot has `send_messages=True` perms.\n Then give the bot admin perm, and use the `,refreshPerms channel_ids`, where channel_ids is the comma separated list of channels.\nEg: `,refreshPerms 752196383066554535, 852196383066554538, 751199383066554538`\nAfter you receive the success message, remove the admin perms from the bot.\n\n**It is not necessary to apply this fix unless you need to use the config commands since this bug doesn't stop the bot from functioning.**",
        )

    else:
        embed = Embed(
            description="No more pages found!"
        )

    page_footer = f"Page: {str(page+1)}/{str(page_limit)} | User ID: {str(author_id)}"
    embed.set_footer(text=page_footer)

    return embed, page_limit
