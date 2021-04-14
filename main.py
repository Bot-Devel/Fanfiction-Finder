import os
import re
import asyncio

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

    query = message.content.lower().splitlines()
    query = ' '.join(query)

    if re.search(r"^ao3\b", query) is not None:
        await message.channel.trigger_typing()
        msg = query.replace("ao3", "")
        msg = msg.replace("ffn", "")
        embed_pg = ao3_metadata(msg)

        if embed_pg is None:  # if not found in ao3, search in ffn
            embed_pg = ffn_metadata(msg)

        embed_pg.set_footer(text="User ID: "+str(message.author.id))
        await message.channel.send(embed=embed_pg)

    elif re.search(r"^ffn\b", query) is not None:
        await message.channel.trigger_typing()
        msg = query.replace("ffn", "")
        msg = msg.replace("ao3", "")
        embed_pg = ffn_metadata(msg)

        if embed_pg is None:  # if not found in ffn, search in ao3
            embed_pg = ao3_metadata(msg)

        embed_pg.set_footer(text="User ID: "+str(message.author.id))
        await message.channel.send(embed=embed_pg)

    # if in code blocks
    elif re.search(r"`(.*?)`", query) is not None:

        str_found = re.findall(r"`(.*?)`", query.lower(), re.MULTILINE)
        str_found = str_found[:2]  # to limit the url to 2 only

        for i in str_found:
            await message.channel.trigger_typing()
            embed_pg = ffn_metadata(i)

            # if not found in ffn, search in ao3
            if embed_pg is None or embed_pg.description.startswith("Fanfiction not found"):
                msg2 = i.replace("ao3", "")
                embed_pg = ao3_metadata(msg2)

            embed_pg.set_footer(text="User ID: "+str(message.author.id))
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

        for i in supported_url:
            await message.channel.trigger_typing()
            if re.search(r"fanfiction.net\b",  i) is not None:
                embed_pg = ffn_metadata(i)

                embed_pg.set_footer(
                    text="User ID: "+str(message.author.id))

                await message.channel.send(embed=embed_pg)

            if re.search(r"archiveofourown.org\b", i) is not None:
                embed_pg = ao3_metadata(i)

                embed_pg.set_footer(
                    text="User ID: "+str(message.author.id))
                await message.channel.send(embed=embed_pg)

    elif re.search(r"^del\b", query) and message.reference is not None:

        message_ref = message.reference  # message id of reply
        message_to_delete = await message.channel.fetch_message(message_ref.message_id)

        # if the messsage was created by a bot
        if message_to_delete.author.bot:
            embeds = message_to_delete.embeds
            for embed in embeds:
                try:
                    author_id = embed.to_dict()['footer']['text']
                    author_id = author_id.replace("User ID: ", "")

                    # only server admins & user of the message to be deleted can use this command
                    if int(message.author.id) == int(author_id) or message.author.guild_permissions.administrator:
                        await message_to_delete.delete()
                        await message.delete()

                    else:
                        await message.delete()
                        msg = await message.channel.send(
                            embed=discord.Embed(
                                description="You are not allowed to delete someone else's message. \
                                Only the message author can delete this message."))
                        await asyncio.sleep(5)
                        await msg.delete()

                except (KeyError, ValueError):
                    await message.delete()
                    msg = await message.channel.send(
                        embed=discord.Embed(
                            description="This message cannot be deleted because the  \
                            message was created before the new `del` feature was added."))
                    await asyncio.sleep(5)
                    await msg.delete()
        else:
            await message.delete()
            msg = await message.channel.send(
                embed=discord.Embed(
                    description="I am not allowed to do that. I can only delete my messages."))
            await asyncio.sleep(5)
            await msg.delete()


start_server()
client.load_extension("cogs.settings")
client.load_extension("cogs.help")
client.run(TOKEN)
