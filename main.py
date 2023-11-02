from __future__ import annotations

import os
import re
import asyncio
import traceback
from loguru import logger

import discord
from discord.ext import commands
from dotenv import load_dotenv

from utils.metadata import ao3_metadata, fichub_metadata

# to use repl+uptime monitor
# from utils.bot_uptime import start_server


load_dotenv()
TOKEN = os.environ["DISCORD_TOKEN"]
OWNER_ID = os.environ["OWNER_ID"]
FICHUB_SITES = os.environ["FICHUB_SITES"].split(",")
URL_VALIDATE = r"(?:(?:https?|ftp)://)(?:\S+(?::\S*)?@)?(?:(?:[1-9]\d?|1\d\d|2[01]\d|22[0-3])(?:\.(?:1?\d{1,2}|2[0-4]\d|25[0-5])){2}(?:\.(?:[1-9]\d?|1\d\d|2[0-4]\d|25[0-4]))|(?:(?:[a-z\u00a1-\uffff0-9]+-?)*[a-z\u00a1-\uffff0-9]+)(?:\.(?:[a-z\u00a1-\uffff0-9]+-?)*[a-z\u00a1-\uffff0-9]+)*(?:\.(?:[a-z\u00a1-\uffff]{2,})))(?::\d{2,5})?(?:/[^\s]*)?"


class FicFinder(commands.Bot):
    def __init__(self) -> None:
        # Use the minimal number of intents necessary to conserve memory.
        super().__init__(
            command_prefix=",",
            help_command=None,
            intents=discord.Intents(guilds=True, messages=True, message_content=True),
        )

    async def setup_hook(self) -> None:
        """Load extensions after the bot is logged in, but before it connects to the Discord Gateway."""

        await self.load_extension("cogs.settings")
        await self.load_extension("cogs.help")

    async def on_message(self, message: discord.Message):
        """Command to search and find the fanfiction by scraping google"""

        try:
            # To run client.commands & client.event simultaneously
            await self.process_commands(message)

            query = message.content.lower()
            msg = list(message.content.lower())

            if message.guild is None:
                logger.info("Not allowed to reply to DMs.")
                return  # Do not reply to DMs

            elif re.search(r"^linkao3\b", query) is not None:
                logger.info("linkao3 command was used. Searching ao3")
                await message.channel.typing()
                logger.info("Sleeping for 1s to avoid ratelimit")
                await asyncio.sleep(1)

                msg = (
                    query.replace("linkao3", "")
                    .replace("linkffn", "")
                    .replace("linkfic", "")
                )

                embed_pg = ao3_metadata(msg)

                if embed_pg is None:  # if not found in AO3, search in Fichub
                    logger.info("Fanfiction not found in AO3, trying to search Fichub")
                    embed_pg = fichub_metadata(msg)

                logger.info(
                    f"Sending embed to Channel-> {message.channel.guild}:{message.channel.name}"
                )
                try:
                    sent_msg = await message.reply(embed=embed_pg, mention_author=False)
                except Exception as err:
                    logger.error(err)
                    sent_msg = await message.channel.send(embed=embed_pg)

            elif re.search(r"^linkfic\b", query) is not None:
                logger.info("linkfic command was used. Searching Fichub")
                await message.channel.typing()
                logger.info("Sleeping for 1s to avoid ratelimit")
                await asyncio.sleep(1)

                msg = (
                    query.replace("linkffn", "")
                    .replace("linkfic", "")
                    .replace("linkao3", "")
                )

                embed_pg = fichub_metadata(msg)

                if embed_pg is None:  # if not found in FFN, search in AO3
                    logger.info("Fanfiction not found in Fichub, trying to search AO3")
                    embed_pg = ao3_metadata(msg)

                logger.info(
                    f"Sending embed to Channel-> {message.channel.guild}:{message.channel.name}"
                )
                try:
                    sent_msg = await message.reply(embed=embed_pg, mention_author=False)
                except Exception as err:
                    logger.error(err)
                    sent_msg = await message.channel.send(embed=embed_pg)

            # if in code blocks
            elif re.search(r"`(.*?)`", query) is not None:
                logger.info("The backquote search was used. Searching Fichub")
                str_found = re.findall(r"`(.*?)`", query.lower(), re.MULTILINE)
                str_found = str_found[:1]  # to limit the search query to 1 only

                for i in str_found:
                    await message.channel.typing()
                    logger.info("Sleeping for 1s to avoid ratelimit")
                    await asyncio.sleep(1)

                    i = i.replace("-log", "")
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
                        sent_msg = await message.reply(
                            embed=embed_pg, mention_author=False
                        )
                    except Exception as err:
                        logger.error(err)
                        sent_msg = await message.channel.send(embed=embed_pg)

            elif re.search(URL_VALIDATE, query) is not None:
                logger.info("URL was passed. Verifying if URL is supported")
                url_found = re.findall(URL_VALIDATE, query.lower(), re.MULTILINE)

                # to limit the url to 1 only
                supported_url = url_found[:1]

                for url in supported_url:
                    await message.channel.typing()
                    logger.info("Sleeping for 2s to avoid ratelimit")
                    await asyncio.sleep(2)

                    if re.search(r"archiveofourown.org\b", url) is not None:
                        # ignore /users/ endpoint
                        if not re.search(r"/users/", url):
                            logger.info(
                                "archiveofourown.org URL was passed. Searching ao3"
                            )

                            embed_pg = ao3_metadata(url)

                            logger.info(
                                f"Sending embed to Channel-> {message.channel.guild}:{message.channel.name}"
                            )

                            try:
                                sent_msg = await message.reply(
                                    embed=embed_pg, mention_author=False
                                )
                            except Exception as err:
                                logger.error(err)
                                sent_msg = await message.channel.send(embed=embed_pg)
                    else:
                        if not re.search(r"fanfiction.net/u/", url):
                            # Check if the URL is in the FICHUB_SITES list
                            if any(
                                site.strip() in url.strip() for site in FICHUB_SITES
                            ):
                                logger.info("URL was passed. Searching Fichub")
                                embed_pg = fichub_metadata(url)

                                logger.info(
                                    f"Sending embed to Channel-> {message.channel.guild}:{message.channel.name}"
                                )
                                try:
                                    sent_msg = await message.reply(
                                        embed=embed_pg, mention_author=False
                                    )
                                except Exception as err:
                                    logger.error(err)
                                    sent_msg = await message.channel.send(
                                        embed=embed_pg
                                    )

        except Exception:
            logger.error(traceback.format_exc())

        finally:
            try:

                def check(reaction, user):
                    return (
                        str(reaction.emoji) == "👎"
                        and not user.bot
                        and reaction.message.id == sent_msg.id
                        and user.id == message.author.id
                    )

                await self.wait_for("reaction_add", check=check, timeout=30.0)
                await sent_msg.delete()

            except Exception:
                pass


# start_server()
if __name__ == "__main__":
    client = FicFinder()
    client.run(TOKEN)
