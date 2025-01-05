from __future__ import annotations


import re
import asyncio
import traceback
from loguru import logger

import discord
from discord.ext import commands

from config import TOKEN, OWNER_ID, FICHUB_SITES
from utils.metadata import ao3_metadata, fichub_metadata


URL_VALIDATE = r"(?:(?:https?|ftp)://)(?:\S+(?::\S*)?@)?(?:(?:[1-9]\d?|1\d\d|2[01]\d|22[0-3])(?:\.(?:1?\d{1,2}|2[0-4]\d|25[0-5])){2}(?:\.(?:[1-9]\d?|1\d\d|2[0-4]\d|25[0-4]))|(?:(?:[a-z\u00a1-\uffff0-9]+-?)*[a-z\u00a1-\uffff0-9]+)(?:\.(?:[a-z\u00a1-\uffff0-9]+-?)*[a-z\u00a1-\uffff0-9]+)*(?:\.(?:[a-z\u00a1-\uffff]{2,})))(?::\d{2,5})?(?:/[^\s]*)?"


class FicFinder(commands.Bot):
    def __init__(self) -> None:
        # Use the minimal number of intents necessary to conserve memory.
        super().__init__(
            command_prefix=",",
            help_command=None,
            intents=discord.Intents(guilds=True, messages=True, reactions=True, message_content=True),
        )

        # Make sure all commands can only be invoked within guilds.
        self.add_check(commands.guild_only().predicate)

    async def setup_hook(self) -> None:
        """Load extensions after the bot is logged in, but before it connects to the Discord Gateway."""

        await self.load_extension("cogs.settings")
        await self.load_extension("cogs.help")
        await self.load_extension("cogs.link")

    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent) -> None:
        channel = self.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        
        # Check if the message was sent by the bot
        if message.author == self.user:
            if payload.emoji.name == "👎":
                await message.delete()
            else:
                await message.remove_reaction(payload.emoji, payload.member)
            
    async def on_message(self, message: discord.Message) -> None:
        """Command to search and find the fanfiction by scraping google"""
        # TODO: Re-evaluate logging for messages containing "-log".

        # To run client.commands & client.event simultaneously
        await super().on_message(message)

        try:
            query = message.content.lower()
            msg = list(message.content.lower())

            if message.guild is None:
                logger.info("Not allowed to reply to DMs.")
                return  # Do not reply to DMs

            # Known since we must be in a guild.
            assert isinstance(message.channel, discord.abc.GuildChannel)

            # if in code blocks
            if re.search(r"`(.*?)`", query) is not None:
                logger.info("The backquote search was used. Searching Fichub")
                str_found = re.findall(r"`(.*?)`", query, re.MULTILINE)
                str_found = str_found[:1]  # to limit the search query to 1 only

                for i in str_found:
                    logger.info("Sleeping for 1s to avoid ratelimit")
                    await asyncio.sleep(1)

                    i = i.replace("-log", "")
                    await message.channel.typing()
                    embed_pg = fichub_metadata(i)

                    # if not found in FFN, search in AO3
                    if embed_pg is None or embed_pg.description.startswith(
                        "Fanfiction not found"
                    ):
                        logger.info("Fanfiction not found on FFN. Trying to search AO3")

                        msg = i.replace("ao3", "")
                        msg = msg.replace("-log", "")

                        embed_pg = ao3_metadata(msg)

                    logger.info(
                        f"Sending embed to Channel-> {message.channel.guild}:{message.channel.name}"
                    )
                    try:
                        await message.reply(
                            embed=embed_pg, mention_author=False
                        )
                    except Exception as err:
                        logger.error(err)
                        await message.channel.send(embed=embed_pg)

            elif (
                url_found := re.search(URL_VALIDATE, query, re.MULTILINE)
            ) is not None:
                logger.info("URL was passed. Verifying if URL is supported")
                # to limit the url to 1 only
                supported_url = (url_found.string,)

                for url in supported_url:
                    logger.info("Sleeping for 2s to avoid ratelimit")
                    await asyncio.sleep(2)

                    if re.search(r"archiveofourown.org\b", url) is not None:
                        # ignore /users/ endpoint
                        if not re.search(r"/users/", url):
                            await message.channel.typing()
                            logger.info(
                                "archiveofourown.org URL was passed. Searching ao3"
                            )

                            embed_pg = ao3_metadata(url)

                            logger.info(
                                f"Sending embed to Channel-> {message.channel.guild}:{message.channel.name}"
                            )

                            try:
                                await message.reply(
                                    embed=embed_pg, mention_author=False
                                )
                            except Exception as err:
                                logger.error(err)
                                await message.channel.send(embed=embed_pg)

                    elif not re.search(r"fanfiction.net/u/", url):
                        # Check if the URL is in the FICHUB_SITES list
                        if any(site.strip() in url.strip() for site in FICHUB_SITES):
                            await message.channel.typing()
                            logger.info("URL was passed. Searching Fichub")
                            embed_pg = fichub_metadata(url)

                            logger.info(
                                f"Sending embed to Channel-> {message.channel.guild}:{message.channel.name}"
                            )
                            try:
                                await message.reply(
                                    embed=embed_pg, mention_author=False
                                )
                            except Exception as err:
                                logger.error(err)
                                await message.channel.send(embed=embed_pg)

        except Exception:
            logger.error(traceback.format_exc())

if __name__ == "__main__":
    client = FicFinder()
    client.run(TOKEN)
