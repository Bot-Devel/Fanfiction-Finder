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
        return  # None

    msg = list(message.content.lower())

    with open('data/live_channels.txt', 'r') as f:
        channels = f.read().splitlines()

    query = message.content.lower().splitlines()
    query = ' '.join(query)

    if str(message.channel.id) in channels:

        if re.search(r"^ao3\b", query) is not None:
            msg = query.replace("ao3", "")
            msg = msg.replace("ffn", "")
            embed_pg = ao3_metadata(msg)

            if embed_pg is None:  # if not found in ao3, search in ffn
                embed_pg = ffn_metadata(msg)

            await message.channel.send(embed=embed_pg)

        elif re.search(r"^ffn\b", query) is not None:
            msg = query.replace("ffn", "")
            msg = msg.replace("ao3", "")
            embed_pg = ffn_metadata(msg)

            if embed_pg is None:  # if not found in ffn, search in ao3
                embed_pg = ao3_metadata(msg)

            await message.channel.send(embed=embed_pg)

        # if in code blocks
        elif re.search(r"`(.*?)`", query) is not None:

            msg_found = re.findall(
                r"`(.*?)`", query.lower(), re.MULTILINE)

            for msg in msg_found:
                embed_pg = ffn_metadata(msg)

                if embed_pg is None:  # if not found in ffn, search in ao3
                    msg2 = msg.replace("ao3", "")
                    embed_pg = ao3_metadata(msg2)

                await message.channel.send(embed=embed_pg)

        elif re.search(r"https?:\/\/(www.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b[-a-zA-Z0-9()@:%_\+.~#\?&=]*", query) is not None:

            if re.search(r"fanfiction.net\b",  query) is not None:
                msg_found = re.findall(
                    r"(?:http|https)://(?:[\w_-]+(?:(?:\.[\w_-]+)+))(?:[\w.,@?^=%&:/~+#-]*[\w@?^=%&/~+#-])?",  query, re.M)

                for msg in msg_found:
                    embed_pg = ffn_metadata(msg)
                    await message.channel.send(embed=embed_pg)

            elif re.search(r"archiveofourown.org\b", query) is not None:
                # if not found in ffn, search in ao3
                msg_found = re.findall(
                    r"(?:http|https)://(?:[\w_-]+(?:(?:\.[\w_-]+)+))(?:[\w.,@?^=%&:/~+#-]*[\w@?^=%&/~+#-])?",  query, re.M)

                for msg in msg_found:
                    embed_pg = ao3_metadata(msg)
                    await message.channel.send(embed=embed_pg)

start_server()
client.load_extension("cogs.settings")
client.load_extension("cogs.help")
client.run(TOKEN)
