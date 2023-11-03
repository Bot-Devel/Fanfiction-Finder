from __future__ import annotations

import discord


PAGE0 = (
    discord.Embed(
        title='Bot Usage Instructions',
        description='**Bugfix for the broken config commands, check Page 4**',
    )
    .add_field(
        name='AO3 Searching:',
        value=(
            '`linkao3 [fic name]` or `linkao3 [fic name] series` \
            \n **Example:**\n1) `linkao3 rogue knight` \n2) `linkao3 prince of slytherin series`'
        ),
        inline=False,
    )
    .add_field(
        name='Other Fichub supported sites Searching:',
        value=(
            '`linkfic [fic name] [site_name]`'
            '\n **Example:**\n`linkfic high tide spacebattle`'
        ),
        inline=False,
    )
    .add_field(
        name='\u200b', value='**Search using URLs is also allowed**', inline=False
    )
    .add_field(
        name='Search using single-lined code blocks or backquote:',
        value=(
            "This will search Fichub first and if it can't find it in Fichub, it will search in ao3. "
            '\n**Example:**\n'
            r'\`cadmean victory\` will default to Fichub.\n\`rogue knight ao3\` for ao3.\n\`prince of slytherin ao3 series\` for ao3 series.'
        ),
    )
)

PAGE1 = (
    discord.Embed(
        title='Bot Configuration',
        description=(
            '**Do not give administrator permission to the bot.**\nTo use these commands, you need administrator permission.'
            '\nGo to the channel you want to add/remove and use the below commands.'
        ),
    )
    .add_field(
        name='To allow the bot to respond to all the channels',
        value='`,allow_all` or `,allowAll`',
        inline=False,
    )
    .add_field(
        name='To disallow the bot from responding to all the channels',
        value='`,disallow_all` or `,disallowAll`',
        inline=False,
    )
    .add_field(
        name='To allow the bot to respond to this channel',
        value='`,allow`',
        inline=False,
    )
    .add_field(
        name='To disallow the bot from responding to this channel',
        value='`,disallow`',
        inline=False,
    )
    .add_field(
        name='To delete all non-bot messages from the channel i.e. all the users except the bot. Useful for archive channels.',
        value='`,clr-msgs`',
        inline=False,
    )
    .add_field(
        name=(
            'To delete a bot message if it violates the server rules, the user who requested the bot to find the fanfiction can react with 👎.'
            "It's only possible to delete a message if it's done before 30s after the bot has replied."
        ),
        value='\u200b',
        inline=False,
    )
)

PAGE2 = discord.Embed(
    title='Bot Support',
    description=(
        "Join the Bot's Discord Support Server if you want to report any bugs or want to suggest new features."
        '\n[Discord Support Server](https://discord.gg/bRzzr3EBqH)'
    ),
)

HELP_PAGE_LOOKUP = [PAGE0, PAGE1, PAGE2]


class HelpView(discord.ui.View):
    message: discord.Message

    def __init__(self, *, timeout: float | None = 30):
        super().__init__(timeout=timeout)
        self.pages = HELP_PAGE_LOOKUP
        self.page_index = 0

    async def on_timeout(self) -> None:
        """Deletes all buttons when the view times out."""

        self.clear_items()
        await self.message.edit(view=self)
        self.stop()

    def format_page(self) -> discord.Embed:
        """Makes the embed 'page' that the user will see.

        This is a distinct method to separate formatting logic if the pages aren't already embeds.
        """

        embed = self.pages[self.page_index]
        embed.set_footer(text=f'Page: {self.page_index + 1}/{len(self.pages)}')
        return embed

    def disable_page_buttons(self) -> None:
        """Enables and disables page-turning buttons based on current position."""

        self.turn_to_previous.disabled = self.turn_to_first.disabled = (
            self.page_index == 0
        )
        self.turn_to_next.disabled = self.turn_to_last.disabled = self.page_index == (
            len(self.pages) - 1
        )

    def get_first_page(self) -> discord.Embed:
        """Get the embed of the first page."""

        return self.pages[0]

    async def update_page(self, interaction: discord.Interaction) -> None:
        """Update and display the view for the given page."""

        embed_page = self.pages[self.page_index]
        self.disable_page_buttons()
        await interaction.response.edit_message(embed=embed_page, view=self)

    @discord.ui.button(label='\N{MUCH LESS-THAN}')
    async def turn_to_first(
        self, interaction: discord.Interaction, _: discord.ui.Button
    ):
        """Skips to the first page of the view."""

        self.page_index = 0
        await self.update_page(interaction)

    @discord.ui.button(label='<')
    async def turn_to_previous(
        self, interaction: discord.Interaction, _: discord.ui.Button
    ) -> None:
        """Turns to the previous page of the view."""

        self.page_index -= 1
        await self.update_page(interaction)

    @discord.ui.button(label='>')
    async def turn_to_next(
        self, interaction: discord.Interaction, _: discord.ui.Button
    ) -> None:
        """Turns to the next page of the view."""

        self.page_index += 1
        await self.update_page(interaction)

    @discord.ui.button(label='\N{MUCH GREATER-THAN}')
    async def turn_to_last(
        self, interaction: discord.Interaction, _: discord.ui.Button
    ) -> None:
        """Skips to the last page of the view."""

        self.page_index = len(self.pages) - 1
        await self.update_page(interaction)
