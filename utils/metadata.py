from discord import Embed, Colour
import re

from utils.search import get_ao3_url, get_ffn_url
from adapters.adapter_archiveofourown import ArchiveOfOurOwn
from adapters.adapter_fanfictionnet import FanFictionNet


URL_VALIDATE = r"(?:(?:https?|ftp)://)(?:\S+(?::\S*)?@)?(?:(?:[1-9]\d?|1\d\d|2[01]\d|22[0-3])(?:\.(?:1?\d{1,2}|2[0-4]\d|25[0-5])){2}(?:\.(?:[1-9]\d?|1\d\d|2[0-4]\d|25[0-4]))|(?:(?:[a-z\u00a1-\uffff0-9]+-?)*[a-z\u00a1-\uffff0-9]+)(?:\.(?:[a-z\u00a1-\uffff0-9]+-?)*[a-z\u00a1-\uffff0-9]+)*(?:\.(?:[a-z\u00a1-\uffff]{2,})))(?::\d{2,5})?(?:/[^\s]*)?"


def ao3_metadata(query, log):

    query = query.strip()
    log.info(f"QUERY: {query}")

    if re.search(URL_VALIDATE, query) is None:
        query = query.replace(" ", "+")

        log.info("query not an URL. Calling get_ao3_url()")
        ao3_url = get_ao3_url(query, log)

    else:  # extract the url from the query if it contains an url
        log.info("query is an URL")
        ao3_url = re.search(URL_VALIDATE, query).group(0)

    if ao3_url is None:
        log.info("Fanfiction not found")
        return Embed(
            description="Fanfiction not found",
            colour=Colour.red())

    log.info(f"Processing {ao3_url}")

    if re.search(r"/works/\b", ao3_url) is not None:

        # extract work id from the url
        ao3_works_id = str(re.search(r"\d+", ao3_url).group(0))
        ao3_url = "https://archiveofourown.org/works/"+ao3_works_id

        fic = ArchiveOfOurOwn(ao3_url, log)
        fic.get_ao3_works_metadata()
        fic.get_author_profile_image()

        if fic.ao3_works_name is None:
            return Embed(description="Fanfiction not found",
                         colour=Colour(0x272b28))

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

        other_info = [fic.ao3_works_fandom, " ☘︎ "]

        for var in [fic.ao3_works_relationships, fic.ao3_works_characters]:
            if var is not None:
                other_info.append(str(var))
                other_info.append(" ☘︎ ")

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
                        value="*If this content violates the server rules, reply to the bot message with `del` and it will be removed. Check `,help`.*", inline=False)

        embed.set_author(
            name=fic.ao3_author_name, url=fic.ao3_author_url,
            icon_url="https://archiveofourown.org/images/ao3_logos/logo_42.png")

    elif re.search(r"/series/\b", ao3_url) is not None:

        # extract series id from the url
        ao3_series_id = str(re.search(r"\d+", ao3_url).group(0))
        ao3_url = "https://archiveofourown.org/series/"+ao3_series_id

        fic = ArchiveOfOurOwn(ao3_url, log)
        fic.get_ao3_series_metadata()
        fic.get_author_profile_image()

        if fic.ao3_series_name is None:
            return Embed(description="Fanfiction not found",
                         colour=Colour(0x272b28))

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
                        value="*If this content violates the server rules, reply to the bot message with `del` and it will be removed. Check `,help`.*", inline=False)

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


def ffn_metadata(query, log):

    query = query.strip()
    log.info(f"QUERY: {query}")

    if re.search(URL_VALIDATE, query) is None:

        if re.search(r"ao3", query):
            embed = None
            return embed

        query = query.replace(" ", "+")

        log.info("query not an URL. Calling get_ffn_url()")
        ffn_url = get_ffn_url(query, log)

    else:  # extract the url from the query if it contains an url
        log.info("query is an URL")
        ffn_url = re.search(
            URL_VALIDATE, query).group(0)

    if ffn_url is None:
        log.info("Fanfiction not found")
        embed = Embed(
            description="Fanfiction not found",
            colour=Colour.red())
        return embed

    log.info(f"Processing {ffn_url}")

    # extract story id from the url
    ffn_story_id = str(re.search(r"\d+", ffn_url).group(0))
    ffn_url = "https://www.fanfiction.net/s/"+ffn_story_id

    fic = FanFictionNet(ffn_url, log)
    fic.get_ffn_story_metadata()

    if fic.ffn_story_name is None:
        return Embed(description="Fanfiction not found",
                     colour=Colour(0x272b28))

    embed = Embed(
        title=fic.ffn_story_name,
        url=fic.BaseUrl,
        description=fic.ffn_story_summary,
        colour=Colour(0x272b28))

    if fic.ffn_story_status == "Complete":

        embed.add_field(
            name='📜 Last Updated',
            value=fic.ffn_story_last_updated +
            " ✓"+fic.ffn_story_status, inline=True)

    elif fic.ffn_story_status == "Updated":

        embed.add_field(
            name='📜 Last Updated',
            value=fic.ffn_story_last_updated, inline=True)

    embed.add_field(
        name='📖 Length',
        value=str(fic.ffn_story_length) +
        " words in "+str(fic.ffn_story_chapters)+" chapter(s)", inline=True)

    other_info = [fic.ffn_story_fandom, " ☘︎ "]

    for var in [fic.ffn_story_genre,
                fic.ffn_story_characters]:
        if var is not None:
            other_info.append(str(var))
            other_info.append(" ☘︎ ")

    other_info = ''.join(other_info[:len(other_info)-1])

    if len(list(other_info)) > 100:
        other_info = other_info[:100] + "..."

    if other_info:
        embed.add_field(name=f":bookmark: Rating: {fic.ffn_story_rating}",
                        value=other_info, inline=False)

    if fic.ffn_story_metainfo:
        embed.add_field(name="📊 Stats",
                        value=fic.ffn_story_metainfo, inline=False)

    embed.add_field(name="\u200b",  # zero-width whitespace character
                    value="*If this content violates the server rules, reply to the bot message with `del` and it will be removed. Check `,help`.*", inline=False)

    embed.set_author(
        name=fic.ffn_author_name, url=fic.ffn_author_url,
        icon_url="https://pbs.twimg.com/profile_images/843841615122784256/WXbuqyjo_bigger.jpg")

    if fic.ffn_story_image:
        embed.set_thumbnail(
            url=f"https://www.fanfiction.net{fic.ffn_story_image}")

    return embed
