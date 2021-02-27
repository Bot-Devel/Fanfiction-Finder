import os
import re
from discord.ext import commands
from dotenv import load_dotenv

from utils.metadata import ao3_metadata, ffn_metadata
from utils.bot_status import start_server

client = commands.Bot(command_prefix=',', help_command=None)
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')


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

    if str(message.channel.id) in channels:

        if re.search(r"^ao3\b", message.content.lower()) is not None:
            msg = message.content.replace("ao3", "")
            msg = message.content.replace("ffn", "")
            embed_pg = ao3_metadata(msg)

            if embed_pg is None:  # if not found in ao3, search in ffn
                embed_pg = ffn_metadata(msg)

            await message.channel.send(embed=embed_pg)

        elif re.search(r"^ffn\b", message.content.lower()) is not None:
            msg = message.content.replace("ffn", "")
            msg = message.content.replace("ao3", "")
            embed_pg = ffn_metadata(msg)

            if embed_pg is None:  # if not found in ffn, search in ao3
                embed_pg = ao3_metadata(msg)

            await message.channel.send(embed=embed_pg)

        # if in code blocks
        elif re.search(r"`(.*?)`", message.content.lower()) is not None:

            msg_found = re.findall(
                r"`(.*?)`", message.content.lower(), re.MULTILINE)

            for msg in msg_found:
                embed_pg = ffn_metadata(msg)

                if embed_pg is None:  # if not found in ffn, search in ao3
                    msg2 = msg.replace("ao3", "")
                    embed_pg = ao3_metadata(msg2)

                await message.channel.send(embed=embed_pg)

        elif re.search(r"https?:\/\/(www.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b[-a-zA-Z0-9()@:%_\+.~#\?&=]*", message.content.lower()) is not None:

            if re.search(r"fanfiction.net\b",  message.content) is not None:
                msg_found = re.findall(
                    r"(?:http|https)://(?:[\w_-]+(?:(?:\.[\w_-]+)+))(?:[\w.,@?^=%&:/~+#-]*[\w@?^=%&/~+#-])?",  message.content, re.M)

                for msg in msg_found:
                    embed_pg = ffn_metadata(msg)
                    await message.channel.send(embed=embed_pg)

            elif re.search(r"archiveofourown.org\b", message.content) is not None:
                # if not found in ffn, search in ao3
                msg_found = re.findall(
                    r"(?:http|https)://(?:[\w_-]+(?:(?:\.[\w_-]+)+))(?:[\w.,@?^=%&:/~+#-]*[\w@?^=%&/~+#-])?",  message.content, re.M)

                for msg in msg_found:
                    embed_pg = ao3_metadata(msg)
                    await message.channel.send(embed=embed_pg)

start_server()
client.load_extension("cogs.settings")
client.load_extension("cogs.help")
client.run(TOKEN)
