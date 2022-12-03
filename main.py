import os
import re
import random
import string
import asyncio
from itertools import cycle
import traceback
from loguru import logger

import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv

from utils.metadata import ao3_metadata, ffn_metadata

# to use repl+uptime monitor
# from utils.bot_uptime import start_server

client = commands.Bot(command_prefix=',', help_command=None)

load_dotenv()
TOKEN = os.getenv('DISCORD_CANARY_TOKEN')
OWNER_ID = os.getenv('OWNER_ID')
URL_VALIDATE = r"(?:(?:https?|ftp)://)(?:\S+(?::\S*)?@)?(?:(?:[1-9]\d?|1\d\d|2[01]\d|22[0-3])(?:\.(?:1?\d{1,2}|2[0-4]\d|25[0-5])){2}(?:\.(?:[1-9]\d?|1\d\d|2[0-4]\d|25[0-4]))|(?:(?:[a-z\u00a1-\uffff0-9]+-?)*[a-z\u00a1-\uffff0-9]+)(?:\.(?:[a-z\u00a1-\uffff0-9]+-?)*[a-z\u00a1-\uffff0-9]+)*(?:\.(?:[a-z\u00a1-\uffff]{2,})))(?::\d{2,5})?(?:/[^\s]*)?"

with open("data/status_quotes.txt", "r") as file:
    quotes = cycle(file.readlines())


@tasks.loop(seconds=1)
async def bot_status():
    """
    An activity status which cycles through the
    status_quotes.txt every 15s
    """

    await client.wait_until_ready()

    await client.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name=(next(quotes)).strip()
        )
    )

    await asyncio.sleep(15)

@client.event
async def on_message(message):
    """ Command to search and find the fanfiction by scraping google
    """

    try:
        query = message.content.lower()

        log_flag = False
        if re.search("-log", query, re.IGNORECASE) \
                and int(message.author.id) == int(OWNER_ID):

            log_flag = True

        # unique id for each request
        request_id = ''.join(random.choice(string.ascii_lowercase)
                             for i in range(10))

        if log_flag:
            # create log directory
            if not os.path.exists('data/logs'):
                os.makedirs('data/logs')

            logger.add(
                f"data/logs/{request_id}.log",
                format="{time:YYYY-MM-DD HH:mm:ss!UTC} | {level} | {file}:{function}:{line} - {message}")

        # To run client.commands & client.event simultaneously
        await client.process_commands(message)

        if message.author == client.user:
            return  # Do not reply to yourself

        if message.author.bot:
            return  # Do not reply to other bots

        msg = list(message.content.lower())

        if message.guild is None:
            logger.info("Not allowed to reply to DMs.")
            return  # Do not reply to DMs

        elif re.search(r"^linkao3\b", query) is not None:

            logger.info("linkao3 command was used. Searching ao3")
            await message.channel.trigger_typing()
            logger.info("Sleeping for 1s to avoid ratelimit")
            await asyncio.sleep(1)

            msg = query.replace("linkao3", "")
            msg = msg.replace("linkffn", "")
            msg = msg.replace("-log", "")

            embed_pg = ao3_metadata(msg)

            if embed_pg is None:  # if not found in AO3, search in FFN
                logger.info(
                    "Fanfiction not found in AO3, trying to search FFN")
                embed_pg = ffn_metadata(msg)

            logger.info(
                f"Sending embed to Channel-> {message.channel.guild}:{message.channel.name}")
            try:
                sent_msg = await message.reply(embed=embed_pg, mention_author=False)
            except Exception as err:
                logger.error(err)
                sent_msg = await message.channel.send(embed=embed_pg)

        elif re.search(r"^linkffn\b", query) is not None:

            logger.info("linkffn command was used. Searching ffn")
            await message.channel.trigger_typing()
            logger.info("Sleeping for 1s to avoid ratelimit")
            await asyncio.sleep(1)

            msg = query.replace("linkffn", "")
            msg = msg.replace("linkao3", "")
            msg = msg.replace("-log", "")

            embed_pg = ffn_metadata(msg)

            if embed_pg is None:  # if not found in FFN, search in AO3
                logger.info(
                    "Fanfiction not found in FFN, trying to search AO3")
                embed_pg = ao3_metadata(msg)

            logger.info(
                f"Sending embed to Channel-> {message.channel.guild}:{message.channel.name}")
            try:
                sent_msg = await message.reply(embed=embed_pg, mention_author=False)
            except Exception as err:
                logger.error(err)
                sent_msg = await message.channel.send(embed=embed_pg)

        # if in code blocks
        elif re.search(r"`(.*?)`", query) is not None:

            logger.info("The backquote search was used. Searching ffn")
            str_found = re.findall(r"`(.*?)`", query.lower(), re.MULTILINE)
            str_found = str_found[:1]  # to limit the search query to 1 only

            for i in str_found:
                await message.channel.trigger_typing()
                logger.info("Sleeping for 1s to avoid ratelimit")
                await asyncio.sleep(1)

                i = i.replace("-log", "")
                embed_pg = ffn_metadata(i)

                # if not found in FFN, search in AO3
                if embed_pg is None or embed_pg.description.startswith("Fanfiction not found"):
                    logger.info(
                        "Fanfiction not found on FFN. Trying to search AO3")

                    msg = i.replace("ao3", "")
                    msg = msg.replace("-log", "")

                    embed_pg = ao3_metadata(msg)

                logger.info(
                    f"Sending embed to Channel-> {message.channel.guild}:{message.channel.name}")
                try:
                    sent_msg = await message.reply(
                        embed=embed_pg, mention_author=False)
                except Exception as err:
                    logger.error(err)
                    sent_msg = await message.channel.send(embed=embed_pg)

        elif re.search(URL_VALIDATE, query) is not None:

            logger.info("URL was passed. Verifying if URL is supported")
            url_found = re.findall(URL_VALIDATE, query.lower(), re.MULTILINE)

            supported_url = []
            for i in url_found:

                # check if the url is ffn or ao3
                if re.search(r"fanfiction.net\b",  i) or \
                        re.search(r"archiveofourown.org\b", i):
                    supported_url.append(i)

            # to limit the url to 1 only
            supported_url = supported_url[:1]

            for url in supported_url:
                await message.channel.trigger_typing()
                logger.info("Sleeping for 2s to avoid ratelimit")
                await asyncio.sleep(2)

                if re.search(r"fanfiction.net\b",  url) is not None:

                    # ignore /u/ endpoint
                    if not re.search(r"/u/", url):

                        logger.info(
                            "fanfiction.net URL was passed. Searching ffn")
                        embed_pg = ffn_metadata(url)

                        logger.info(
                            f"Sending embed to Channel-> {message.channel.guild}:{message.channel.name}")
                        try:
                            sent_msg = await message.reply(
                                embed=embed_pg, mention_author=False)
                        except Exception as err:
                            logger.error(err)
                            sent_msg = await message.channel.send(embed=embed_pg)
                            sent_msg = await message.channel.send(embed=embed_pg)

                if re.search(r"archiveofourown.org\b", url) is not None:

                    # ignore /users/ endpoint
                    if not re.search(r"/users/", url):
                        logger.info(
                            "archiveofourown.org URL was passed. Searching ao3")

                        embed_pg = ao3_metadata(url)

                        logger.info(
                            f"Sending embed to Channel-> {message.channel.guild}:{message.channel.name}")

                        try:
                            sent_msg = await message.reply(
                                embed=embed_pg, mention_author=False)
                        except Exception as err:
                            logger.error(err)
                            sent_msg = await message.channel.send(embed=embed_pg)

        if log_flag:
            try:
                await message.reply(file=discord.File(
                    f"data/logs/{request_id}.log"
                ), mention_author=False)

            except Exception as err:
                logger.error(err)
                await message.channel.send(file=discord.File(
                    f"data/logs/{request_id}.log"
                ))

            # delete the log
            os.remove(f"data/logs/{request_id}.log")

    except Exception as err:
        logger.error(traceback.format_exc())
        if log_flag:
            # remove log if the bot is not allowed to send msgs to this channel
            os.remove(f"data/logs/{request_id}.log")

    finally:
        try:
            def check(reaction, user):
                return str(reaction.emoji) == '👎' and \
                    not user.bot and reaction.message.id == sent_msg.id and \
                    user.id == message.author.id

            await client.wait_for('reaction_add',
                                  check=check, timeout=30.0)
            await sent_msg.delete()

        except Exception:
            pass

bot_status.start()
# start_server()
client.load_extension("cogs.settings")
client.load_extension("cogs.help")
client.run(TOKEN)
