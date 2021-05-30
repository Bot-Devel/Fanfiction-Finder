import os
import re
import asyncio
import random
import string
import requests

import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv

from utils.metadata import ao3_metadata, ffn_metadata
from utils.logging import create_logger

# to use repl+uptime monitor
from utils.bot_uptime import start_server

client = commands.Bot(command_prefix=',', help_command=None)

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
OWNER_ID = os.getenv('OWNER_ID')
URL_VALIDATE = r"(?:(?:https?|ftp)://)(?:\S+(?::\S*)?@)?(?:(?:[1-9]\d?|1\d\d|2[01]\d|22[0-3])(?:\.(?:1?\d{1,2}|2[0-4]\d|25[0-5])){2}(?:\.(?:[1-9]\d?|1\d\d|2[0-4]\d|25[0-4]))|(?:(?:[a-z\u00a1-\uffff0-9]+-?)*[a-z\u00a1-\uffff0-9]+)(?:\.(?:[a-z\u00a1-\uffff0-9]+-?)*[a-z\u00a1-\uffff0-9]+)*(?:\.(?:[a-z\u00a1-\uffff]{2,})))(?::\d{2,5})?(?:/[^\s]*)?"


@client.event
async def on_ready():
    await client.change_presence(
        activity=discord.Game(name=",help")
    )


@tasks.loop(seconds=10.0)
async def bot_uptime():

    await client.wait_until_ready()

    while not client.is_closed():

        requests.get("https://fanfiction-finder-bot.roguedev1.repl.co/")
        await asyncio.sleep(30)


@client.event
async def on_message(message):
    """ Command to search and find the fanfiction by scraping google
    """

    query = message.content.lower()

    log_flag = False
    if re.search("-log", query, re.IGNORECASE) \
            and int(message.author.id) == int(OWNER_ID):

        log_flag = True

    # unique id for each request
    request_id = ''.join(random.choice(string.ascii_lowercase)
                         for i in range(10))

    log = create_logger(log_flag, request_id)

    # To run client.commands & client.event simultaneously
    await client.process_commands(message)

    if message.author == client.user:
        return  # Do not reply to yourself

    if message.author.bot:
        return  # Do not reply to other bots

    msg = list(message.content.lower())

    if re.search(r"^del\b", query) and message.reference is not None:

        log.info("del command was used!")
        message_ref = message.reference  # message id of reply
        message_to_delete = await message.channel.fetch_message(message_ref.message_id)

        # if the messsage was created by a bot
        if message_to_delete.author.bot:
            embeds = message_to_delete.embeds
            for embed in embeds:
                try:
                    footer = embed.to_dict()['footer']['text']

                    author_id = (re.search(r"(User ID:)(.*)",
                                           footer)).group(2).strip()

                    # only server admins & user of the message to be deleted can use this command
                    if int(message.author.id) == int(author_id) or message.author.guild_permissions.administrator:
                        await message_to_delete.delete()
                        await message.delete()

                    else:
                        log.info("User not authorized to delete the message")
                        await message.delete()
                        msg = await message.reply(
                            embed=discord.Embed(
                                description="You are not allowed to delete someone else's message. \
                                Only the message author can delete this message."), mention_author=False)
                        await asyncio.sleep(5)
                        await msg.delete()

                except (KeyError, ValueError):
                    log.info(
                        "Message cannot be deleted since it doesn't contain the User ID in the footer. Can't verify messsage author.")
                    await message.delete()
                    msg = await message.reply(
                        embed=discord.Embed(
                            description="This message cannot be deleted because the  \
                            message doesn't contain the User id at the footer. Can't verify messsage author."), mention_author=False)
                    await asyncio.sleep(5)
                    await msg.delete()
        else:
            log.info("Bot is only allowed to delete its own messages.")
            await message.delete()
            msg = await message.reply(
                embed=discord.Embed(
                    description="I am not allowed to do that. I can only delete my messages."), mention_author=False)
            await asyncio.sleep(5)
            await msg.delete()

    if message.guild is None:
        log.info("Not allowed to reply to DMs.")
        return  # Do not reply to DMs

    elif re.search(r"^linkao3\b", query) is not None:

        log.info("linkao3 command was used. Searching ao3")
        await message.channel.trigger_typing()

        msg = query.replace("linkao3", "")
        msg = msg.replace("linkffn", "")
        msg = msg.replace("-log", "")

        embed_pg = ao3_metadata(msg, log)

        if embed_pg is None:  # if not found in ao3, search in ffn
            log.info("Fanfiction not found in ao3, trying to search ffn")
            embed_pg = ffn_metadata(msg, log)

        embed_pg.set_footer(text="User ID: "+str(message.author.id))

        log.info(f"Sending embed to Channel: {message.channel.name}")
        try:
            await message.reply(embed=embed_pg, mention_author=False)
        except Exception:
            await message.channel.send(embed=embed_pg)

    elif re.search(r"^linkffn\b", query) is not None:

        log.info("linkffn command was used. Searching ffn")
        await message.channel.trigger_typing()

        msg = query.replace("linkffn", "")
        msg = msg.replace("linkao3", "")
        msg = msg.replace("-log", "")

        embed_pg = ffn_metadata(msg, log)

        if embed_pg is None:  # if not found in ffn, search in ao3
            log.info("Fanfiction not found in ffn, trying to search ao3")
            embed_pg = ao3_metadata(msg, log)

        embed_pg.set_footer(text="User ID: "+str(message.author.id))

        log.info(f"Sending embed to Channel: {message.channel.name}")
        try:
            await message.reply(embed=embed_pg, mention_author=False)
        except Exception:
            await message.channel.send(embed=embed_pg)

    # if in code blocks
    elif re.search(r"`(.*?)`", query) is not None:

        str_found = re.findall(r"`(.*?)`", query.lower(), re.MULTILINE)
        str_found = str_found[:2]  # to limit the search query to 2 only

        for i in str_found:
            await message.channel.trigger_typing()
            log.info("The backquote search was used. Searching ffn")
            i = i.replace("-log", "")

            embed_pg = ffn_metadata(i, log)

            # if not found in ffn, search in ao3
            if embed_pg is None or embed_pg.description.startswith("Fanfiction not found"):
                log.info("Fanfiction not found on ao3. Trying to search ao3")

                msg = i.replace("ao3", "")
                msg = msg.replace("-log", "")

                embed_pg = ao3_metadata(msg, log)

            embed_pg.set_footer(text="User ID: "+str(message.author.id))

            log.info(f"Sending embed to Channel: {message.channel.name}")
            try:
                await message.reply(embed=embed_pg, mention_author=False)
            except Exception:
                await message.channel.send(embed=embed_pg)

    elif re.search(URL_VALIDATE, query) is not None:

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
            await asyncio.sleep(2)

            if re.search(r"fanfiction.net\b",  url) is not None:

                # ignore /u/ endpoint
                if not re.search(r"/u/", url):

                    log.info("fanfiction.net URL was passed. Searching ffn")
                    embed_pg = ffn_metadata(url, log)

                    embed_pg.set_footer(
                        text="User ID: "+str(message.author.id))

                    log.info(
                        f"Sending embed to Channel: {message.channel.name}")
                    try:
                        await message.reply(embed=embed_pg, mention_author=False)
                    except Exception:
                        await message.channel.send(embed=embed_pg)

            if re.search(r"archiveofourown.org\b", url) is not None:

                # ignore /users/ endpoint
                if not re.search(r"/users/", url):
                    log.info("archiveofourown.org URL was passed. Searching ao3")

                    embed_pg = ao3_metadata(url, log)

                    embed_pg.set_footer(
                        text="User ID: "+str(message.author.id))

                    log.info(
                        f"Sending embed to Channel: {message.channel.name}")
                    try:
                        await message.reply(embed=embed_pg, mention_author=False)
                    except Exception:
                        await message.channel.send(embed=embed_pg)

    if log_flag:
        await message.reply(file=discord.File(
            f"data/logs/{request_id}.log"
        ), mention_author=False)
        # delete the log
        os.remove(f"data/logs/{request_id}.log")

bot_uptime.start()
start_server()
client.load_extension("cogs.settings")
client.load_extension("cogs.help")
client.run(TOKEN)
