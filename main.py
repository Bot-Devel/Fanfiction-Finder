import os
import re

import discord
from discord.ext import commands
from dotenv import load_dotenv

from utils.metadata import ao3_metadata, ffn_metadata
from utils.bot_status import start_server

client = commands.Bot(command_prefix=',', help_command=None)

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
URL_VALIDATE = r"(?:(?:https?|ftp)://)(?:\S+(?::\S*)?@)?(?:(?:[1-9]\d?|1\d\d|2[01]\d|22[0-3])(?:\.(?:1?\d{1,2}|2[0-4]\d|25[0-5])){2}(?:\.(?:[1-9]\d?|1\d\d|2[0-4]\d|25[0-4]))|(?:(?:[a-z\u00a1-\uffff0-9]+-?)*[a-z\u00a1-\uffff0-9]+)(?:\.(?:[a-z\u00a1-\uffff0-9]+-?)*[a-z\u00a1-\uffff0-9]+)*(?:\.(?:[a-z\u00a1-\uffff]{2,})))(?::\d{2,5})?(?:/[^\s]*)?"


@client.event
async def on_ready():
    await client.change_presence(
        activity=discord.Game(name=",help")
    )


@client.event
async def on_message(message):
    """ Command to search and find the fanfiction by scraping google
    """
    # To run client.commands & client.event simultaneously
    await client.process_commands(message)

    if message.author == client.user:
        return  # Do not reply to yourself

    if message.author.bot:
        return  # Do not reply to other bots

    msg = list(message.content.lower())

    with open('data/live_channels.txt', 'r') as f:
        channels = f.read().splitlines()

    query = message.content.lower().splitlines()
    query = ' '.join(query)

    def check(reaction, user):
        return str(reaction.emoji) == '🗑️' and not user.bot and reaction.message.id == msg.id

    if str(message.channel.id) in channels:

        if re.search(r"^ao3\b", query) is not None:
            msg = query.replace("ao3", "")
            msg = msg.replace("ffn", "")
            embed_pg = ao3_metadata(msg)

            if embed_pg is None:  # if not found in ao3, search in ffn
                embed_pg = ffn_metadata(msg)

            msg = await message.channel.send(embed=embed_pg)
            await msg.add_reaction("🗑️")

            reaction, user = await client.wait_for('reaction_add', check=check)
            await msg.delete()

        elif re.search(r"^ffn\b", query) is not None:
            msg = query.replace("ffn", "")
            msg = msg.replace("ao3", "")
            embed_pg = ffn_metadata(msg)

            if embed_pg is None:  # if not found in ffn, search in ao3
                embed_pg = ao3_metadata(msg)

            msg = await message.channel.send(embed=embed_pg)
            await msg.add_reaction("🗑️")

            reaction, user = await client.wait_for('reaction_add',  check=check)
            await msg.delete()

        # if in code blocks
        elif re.search(r"`(.*?)`", query) is not None:

            url_found = re.findall(
                r"`(.*?)`", query.lower(), re.MULTILINE)

            url_found = url_found[:1]  # to limit the url to 1 only
            for i in url_found:
                embed_pg = ffn_metadata(i)

                if embed_pg is None:  # if not found in ffn, search in ao3
                    msg2 = i.replace("ao3", "")
                    embed_pg = ao3_metadata(msg2)

                msg = await message.channel.send(embed=embed_pg)
                await msg.add_reaction("🗑️")

                reaction, user = await client.wait_for('reaction_add', check=check)
                await msg.delete()

        elif re.search(URL_VALIDATE, query) is not None:
            url_found = re.findall(URL_VALIDATE, query.lower(), re.MULTILINE)
            url_found = url_found[:1]  # to limit the url to 1 only

            for i in url_found:
                if re.search(r"fanfiction.net\b",  i) is not None:
                    embed_pg = ffn_metadata(i)
                    msg = await message.channel.send(embed=embed_pg)
                    await msg.add_reaction("🗑️")

                    reaction, user = await client.wait_for('reaction_add', check=check)
                    await msg.delete()

                if re.search(r"archiveofourown.org\b", i) is not None:
                    embed_pg = ao3_metadata(i)
                    msg = await message.channel.send(embed=embed_pg)
                    await msg.add_reaction("🗑️")

                    reaction, user = await client.wait_for('reaction_add', check=check)
                    await msg.delete()

start_server()
client.load_extension("cogs.settings")
client.load_extension("cogs.help")
client.run(TOKEN)
