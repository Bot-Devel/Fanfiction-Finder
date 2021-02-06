import os
import re
import discord
from dotenv import load_dotenv
from utils.metadata import ao3_metadata, ffn_metadata
from utils.bot_status import keep_alive
client = discord.Client()
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')


@client.event
async def on_message(message):
    """ Command to search and find the fanfiction by scraping google
    """
    if message.author == client.user:
        return  # None
    msg = list(message.content.lower())
    msg_is_url = 0
    channel = ['803746153296429066', '752196383066554538',
               '801841616020570112', '801842614559047771']
    whitelist = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'é',
                 'v', 'w', 'x', 'y', 'z', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '!', '?', ' ', '.', ';', ',', '"', "'", '…', '*', '-', ':', '/', '%', '#']
    if str(message.channel.id) in channel:
        if all(elem in whitelist for elem in msg):  # if msg in whitelist
            if re.search(r"^ao3\b", message.content.lower()) is not None:
                msg = message.content.replace("ao3", "")
                embed_pg = ao3_metadata(msg)
            elif re.search(r"^ffn\b", message.content.lower()) is not None:
                msg = message.content.replace("ffn", "")
                embed_pg = ffn_metadata(msg)
            elif re.search(r"https?:\/\/(www.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b[-a-zA-Z0-9()@:%_\+.~#?&=]*", message.content.lower()) is not None:
                msg_is_url = 1
                if re.search(r"fanfiction.net\b",  message.content) is not None:
                    embed_pg = ffn_metadata(message.content)
                elif re.search(r"archiveofourown.org\b", message.content) is not None:
                    embed_pg = ao3_metadata(message.content)
            if embed_pg is None:
                if msg_is_url == 0:  # Delete msg only when the msg doesnt contain url
                    await message.delete()
            else:
                await message.channel.send("Searched by `"+str(message.author)+"`")
            await message.channel.send(embed=embed_pg)
            if msg_is_url == 0:  # Delete msg only when the msg doesnt contain url
                await message.delete()
keep_alive()
client.run(TOKEN)
