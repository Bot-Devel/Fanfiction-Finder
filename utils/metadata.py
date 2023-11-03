from __future__ import annotations

import re

from discord import Embed, Colour
from loguru import logger

from adapters.adapter_archiveofourown import ArchiveOfOurOwn
from adapters.adapter_fichub import FicHub
from utils.processing import timestamp_unix_to_local
from utils.search import get_ao3_url, get_fic_url


URL_VALIDATE = r"(?:(?:https?|ftp)://)(?:\S+(?::\S*)?@)?(?:(?:[1-9]\d?|1\d\d|2[01]\d|22[0-3])(?:\.(?:1?\d{1,2}|2[0-4]\d|25[0-5])){2}(?:\.(?:[1-9]\d?|1\d\d|2[0-4]\d|25[0-4]))|(?:(?:[a-z\u00a1-\uffff0-9]+-?)*[a-z\u00a1-\uffff0-9]+)(?:\.(?:[a-z\u00a1-\uffff0-9]+-?)*[a-z\u00a1-\uffff0-9]+)*(?:\.(?:[a-z\u00a1-\uffff]{2,})))(?::\d{2,5})?(?:/[^\s]*)?"


def ao3_metadata(query: str):

    query = query.strip()
    logger.info(f"QUERY: {query}")

    if re.search(URL_VALIDATE, query) is None:
        query = query.replace(" ", "+")

        logger.info("Query not an URL. Calling get_ao3_url()")
        ao3_url = get_ao3_url(query)

    else:  # extract the url from the query if it contains an url
        logger.info("Query is an URL")
        ao3_url = re.search(URL_VALIDATE, query).group(0)

    if ao3_url is None:
        logger.info("Fanfiction not found")
        return Embed(
            description="Fanfiction not found",
            colour=Colour.red())

    logger.info(f"Processing {ao3_url}")

    if re.search(r"/works/\b", ao3_url) is not None:

        # extract work id from the url
        ao3_works_id = str(re.search(r"\d+", ao3_url).group(0))
        ao3_url = "https://archiveofourown.org/works/"+ao3_works_id
        fic = ArchiveOfOurOwn(ao3_url)
        fic.get_ao3_works_metadata()
        fic.get_author_profile_image()
        if fic.ao3_works_name is None:
            return Embed(description="Fanfiction not found",
                         colour=Colour.red())

        embed = Embed(
            title=fic.ao3_works_name,
            url=fic.BaseUrl,
            description=fic.ao3_works_summary,
            colour=Colour(0x272b28))

        if fic.ao3_works_status == "Completed":

            embed.add_field(
                name='📜 Last Updated',
                value=fic.ao3_works_last_up +
                " ✓Complete", inline=True)

        elif fic.ao3_works_status == "Updated":

            embed.add_field(
                name='📜 Last Updated',
                value=fic.ao3_works_last_up, inline=True)

        elif fic.ao3_works_status is None:
            embed.add_field(
                name='📜 Last Updated',
                value=fic.ao3_works_last_up, inline=True)

        embed.add_field(
            name='📖 Length',
            value=fic.ao3_works_length +
            " words in "+fic.ao3_works_chapters+" chapter(s)", inline=True)

        other_info = [fic.ao3_works_fandom, "  ☘︎  "]

        for var in [fic.ao3_works_relationships, fic.ao3_works_characters]:
            if var is not None:
                other_info.append(str(var))
                other_info.append("  ☘︎  ")

        other_info = ''.join(other_info[:len(other_info)-1])
        if len(list(other_info)) > 100:
            other_info = other_info[:100] + "..."

        if other_info:
            embed.add_field(name=f":bookmark: Rating: {fic.ao3_works_rating}",
                            value=other_info, inline=False)

        if fic.ao3_works_metainfo:
            embed.add_field(name="📊 Stats",
                            value=fic.ao3_works_metainfo, inline=False)

        embed.add_field(name="\u200b",  # zero-width whitespace character
                        value="*If this content violates the server rules, react with 👎 and it will be removed.*", inline=False)

        embed.set_author(
            name=fic.ao3_author_name, url=fic.ao3_author_url,
            icon_url="https://archiveofourown.org/images/ao3_logos/logo_42.png")

    elif re.search(r"/series/\b", ao3_url) is not None:

        # extract series id from the url
        ao3_series_id = str(re.search(r"\d+", ao3_url).group(0))
        ao3_url = "https://archiveofourown.org/series/"+ao3_series_id

        fic = ArchiveOfOurOwn(ao3_url)
        fic.get_ao3_series_metadata()
        fic.get_author_profile_image()

        if fic.ao3_series_name is None:
            return Embed(description="Fanfiction not found",
                         colour=Colour.red())

        embed = Embed(
            title=fic.ao3_series_name,
            url=fic.BaseUrl,
            description=fic.ao3_series_summary,
            colour=Colour(0x272b28))

        if fic.ao3_series_status == "Completed":

            embed.add_field(
                name='📜 Last Updated',
                value=fic.ao3_series_last_up +
                " ✓Complete", inline=True)

        elif fic.ao3_series_status == "Updated":

            embed.add_field(
                name='📜 Last Updated',
                value=fic.ao3_series_last_up, inline=True)

        elif fic.ao3_series_status is None:
            embed.add_field(
                name='📜 Last Updated',
                value=fic.ao3_series_last_up, inline=True)

        embed.add_field(
            name='📖 Length',
            value=fic.ao3_series_length +
            " words in "+fic.ao3_series_works+" work(s)", inline=True)

        embed.add_field(name="\u200b",  # zero-width whitespace character
                        value="*If this content violates the server rules, react with 👎 and it will be removed.*", inline=False)

        embed.set_author(
            name=fic.ao3_author_name, url=fic.ao3_author_url,
            icon_url="https://archiveofourown.org/images/ao3_logos/logo_42.png")

    else:
        embed = Embed(
            description="Fanfiction not found",
            colour=Colour.red())

    if fic.ao3_author_img:
        embed.set_thumbnail(
            url=fic.ao3_author_img)

    return embed


def fichub_metadata(query):

    query = query.strip()
    logger.info(f"QUERY: {query}")

    if re.search(URL_VALIDATE, query) is None:

        if re.search(r"ao3", query):
            embed = None
            return embed

        query = query.replace(" ", "+")

        logger.info("Query not an URL. Calling get_fic_url()")
        fic_url = get_fic_url(query)

    else:  # extract the url from the query if it contains an url
        logger.info("Query is an URL")
        fic_url = re.search(
            URL_VALIDATE, query).group(0)

    if fic_url is None:
        logger.info("Fanfiction not found")
        embed = Embed(
            description="Fanfiction not found",
            colour=Colour.red())
        return embed

    logger.info(f"Processing {fic_url}")

    fic = FicHub()
    fic.get_fic_metadata(fic_url)

    if str(fic.response['err']).strip() != "0":
        print("h1")
        return Embed(description="Fanfiction not found",
                     colour=Colour.red())

    embed = Embed(
        title=fic.response['meta']['title'],
        url=fic.response['meta']['source'],
        description=fic.response['meta']['description']
        .replace("<p>","").replace("</p>","").replace("<hr />","\n\n"),
        colour=Colour(0x272b28))

    if fic.response['meta']["status"] == "complete":
        fic_last_update = timestamp_unix_to_local(fic.response['meta']['rawExtendedMeta']['updated']) if 'updated' in fic.response['meta']['rawExtendedMeta'] else ""
        embed.add_field(
            name='📜 Last Updated',
            value= fic_last_update + "✓" + fic.response['meta']["status"], inline=True)

    elif fic.response['meta']["status"] == "ongoing":
        fic_last_update = timestamp_unix_to_local(fic.response['meta']['rawExtendedMeta']['updated']) if 'updated' in fic.response['meta']['rawExtendedMeta'] else ""
        embed.add_field(
            name='📜 Last Updated',
            value= fic_last_update + "✓" + fic.response['meta']["status"], inline=True)

    embed.add_field(
        name='📖 Length',
        value=str(fic.response['meta']['words']) +
        " words in "+str(fic.response['meta']['chapters'])+" chapter(s)", inline=True)
    if fic.response['meta']['rawExtendedMeta']:

        other_info = [fic.response['meta']['rawExtendedMeta']['raw_fandom'], "  ☘︎  "]

        for var in [fic.response['meta']['rawExtendedMeta']['genres'] if 'genres' in fic.response['meta']['rawExtendedMeta'] else "",
                    fic.response['meta']['rawExtendedMeta']['characters']]:
            if var is not None:
                other_info.append(str(var))
                other_info.append("  ☘︎  ")

        other_info = ''.join(other_info[:len(other_info)-1])

        if len(list(other_info)) > 100:
            other_info = other_info[:100] + "..."

        if other_info:
            embed.add_field(name=f":bookmark: Rating: {fic.response['meta']['rawExtendedMeta']['rated']}",
                            value=other_info, inline=False)

        fic_stats = f"**Reviews:** {fic.response['meta']['rawExtendedMeta']['reviews']}  ☘︎  **Favs:** {fic.response['meta']['rawExtendedMeta']['favorites']}  ☘︎  **Follows:** {fic.response['meta']['rawExtendedMeta']['follows']}"
        embed.add_field(name="📊 Stats",
                        value=fic_stats, inline=False)

    embed.add_field(name="\u200b",  # zero-width whitespace character
                    value="*If this content violates the server rules, react with 👎 and it will be removed.\nThe bot is using Fichub.net API's archive metadata. Latest data is not guaranteed!*", inline=False)

    embed.set_author(
        name=fic.response['meta']['author'], url=fic.response['meta']['authorUrl'],
        icon_url="https://pbs.twimg.com/profile_images/843841615122784256/WXbuqyjo_bigger.jpg")
    print("embed",embed)
    return embed

    