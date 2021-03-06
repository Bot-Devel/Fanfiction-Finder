import discord
import re
import time
from bs4 import BeautifulSoup
import cloudscraper

from utils.search import get_ao3_url, get_ffn_url
from utils.processing import story_last_up_clean, ffn_process_details, \
    ao3_convert_chapters_to_works
from utils.metadata_processing import ao3_metadata_works, ao3_metadata_series


def ao3_metadata(query):
    if re.search(r"https?:\/\/(www/.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b[-a-zA-Z0-9()@:%_\+.~#\?&//=]*", query) is None:

        query = query.replace(" ", "+")
        ao3_url = get_ao3_url(query)

    else:  # clean the url if the query was a url
        ao3_url = re.search(
            r"https?:\/\/(www/.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b[-a-zA-Z0-9()@:%_\+.~#\?&//=]*", query).group(0)

    if ao3_url is None:
        return None

    if re.search(r"/chapters/\b", ao3_url) is not None:
        ao3_url = ao3_convert_chapters_to_works(
            ao3_url)  # convert the url from /chapters/ to /works/

        ao3_story_name, ao3_author_name, ao3_author_url, ao3_story_summary, \
            ao3_story_status, ao3_story_last_up, ao3_story_length, \
            ao3_story_chapters, ao3_story_rating, ao3_story_relationships, \
            ao3_story_characters = ao3_metadata_works(
                ao3_url)

    elif re.search(r"/works/\b", ao3_url) is not None:
        ao3_story_name, ao3_author_name, ao3_author_url, ao3_story_summary, \
            ao3_story_status, ao3_story_last_up, ao3_story_length, \
            ao3_story_chapters, ao3_story_rating, ao3_story_relationships, \
            ao3_story_characters = ao3_metadata_works(
                ao3_url)

    elif re.search(r"/series/\b", ao3_url) is not None:
        ao3_series_name, ao3_author_name, ao3_author_url, ao3_series_summary, \
            ao3_series_status, ao3_series_last_up, ao3_series_length, \
            ao3_series_works = ao3_metadata_series(
                ao3_url)

        embed = discord.Embed(
            title=ao3_series_name,
            url=ao3_url,
            description=ao3_series_summary,
            colour=discord.Colour(0x272b28))

        if ao3_series_status == "Completed":

            embed.add_field(
                name='**📜 Last Updated**',
                value=ao3_series_last_up +
                " ✓Complete", inline=True)

        elif ao3_series_status == "Updated":

            embed.add_field(
                name='**📜 Last Updated**',
                value=ao3_series_last_up, inline=True)

        elif ao3_series_status is None:
            embed.add_field(
                name='**📜 Last Updated**',
                value=ao3_series_last_up, inline=True)

        embed.add_field(
            name='**📖 Length**',
            value=ao3_series_length +
            " words in "+ao3_series_works+" work(s)", inline=True)

        embed.set_author(
            name=ao3_author_name, url=ao3_author_url,
            icon_url="https://archiveofourown.org/images/ao3_logos/logo_42.png")

        return embed

    embed = discord.Embed(
        title=ao3_story_name,
        url=ao3_url,
        description=ao3_story_summary,
        colour=discord.Colour(0x272b28))

    if ao3_story_status == "Completed":

        embed.add_field(
            name='**📜 Last Updated**',
            value=ao3_story_last_up +
            " ✓Complete", inline=True)

    elif ao3_story_status == "Updated":

        embed.add_field(
            name='**📜 Last Updated**',
            value=ao3_story_last_up, inline=True)

    elif ao3_story_status is None:
        embed.add_field(
            name='**📜 Last Updated**',
            value=ao3_story_last_up, inline=True)

    embed.add_field(
        name='**📖 Length**',
        value=ao3_story_length +
        " words in "+ao3_story_chapters+" chapter(s)", inline=True)

    footer = []
    for var in [ao3_story_rating,
                ao3_story_relationships, ao3_story_characters]:
        if var is not None:
            footer.append(str(var))
            footer.append(" | ")

    footer = ''.join(footer[:len(footer)-1])
    if len(list(footer)) > 100:
        footer = footer[:100]

    embed.set_footer(text=footer)

    embed.set_author(
        name=ao3_author_name, url=ao3_author_url,
        icon_url="https://archiveofourown.org/images/ao3_logos/logo_42.png")

    return embed


def ffn_metadata(query):
    if re.search(r"https?:\/\/(www/.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b[-a-zA-Z0-9()@:%_\+.~#\?&//=]*", query) is None:
        if re.search(r"ao3\b", query):
            embed = None
            return embed
        query = query.replace(" ", "+")
        ffn_url = get_ffn_url(query)

    else:  # clean the url if the query was a url
        ffn_url = re.search(
            r"https?:\/\/(www/.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b[-a-zA-Z0-9()@:%_\+.~#\?&//=]*", query).group(0)

    if ffn_url is None:
        return None

    # convert m.fanfiction.net to www.fanfiction.net
    ffn_url = ffn_url.replace(r"/m.", r"/www.")

    scraper = cloudscraper.CloudScraper(
        delay=3, browser={
            'browser': 'chrome',
            'platform': 'windows',
            'mobile': False,
            'desktop': True,
        }
    )

    time.sleep(3)
    ffn_page = scraper.get(ffn_url).text
    ffn_soup = BeautifulSoup(ffn_page, 'html.parser')

    try:
        ffn_story_name = ffn_soup.find_all('b', 'xcontrast_txt')[
            0].string.strip()

        ffn_author_name = ffn_soup.find_all(
            'a', {'href': re.compile('^/u/\d+/.')})[0].string.strip()

        ffn_author_url = (ffn_soup.find(
            'div', attrs={'id': 'profile_top'}).find('a', href=True))['href']

        ffn_story_summary = ffn_soup.find_all('div', {
            'style': 'margin-top:2px',
            'class': 'xcontrast_txt'})[0].string.strip()

        ffn_story_status, ffn_story_last_up, ffn_story_length, \
            ffn_story_chapters, ffn_story_rating, ffn_story_genre, \
            ffn_story_characters = ffn_process_details(
                ffn_soup)

        ffn_story_last_up = story_last_up_clean(ffn_story_last_up, 1)
        ffn_author_url = "https://www.fanfiction.net"+ffn_author_url

        if len(list(ffn_story_summary)) > 2048:
            ffn_story_summary = ffn_story_summary[:2030] + "..."

        embed = discord.Embed(
            title=ffn_story_name,
            url=ffn_url,
            description=ffn_story_summary,
            colour=discord.Colour(0x272b28))

        if ffn_story_status == "Complete":

            embed.add_field(
                name='**📜 Last Updated**',
                value=ffn_story_last_up +
                " ✓"+ffn_story_status, inline=True)

        elif ffn_story_status == "Updated":

            embed.add_field(
                name='**📜 Last Updated**',
                value=ffn_story_last_up, inline=True)

        embed.add_field(
            name='**📖 Length**',
            value=str(ffn_story_length) +
            " words in "+str(ffn_story_chapters)+" chapter(s)", inline=True)

        footer = []
        for var in [ffn_story_rating, ffn_story_genre,
                    ffn_story_characters]:
            if var is not None:
                footer.append(str(var))
                footer.append(" | ")

        footer = ''.join(footer[:len(footer)-1])
        if len(list(footer)) > 100:
            footer = footer[:100]

        if footer is not None:
            embed.set_footer(text=footer)

        embed.set_author(
            name=ffn_author_name, url=ffn_author_url,
            icon_url="https://pbs.twimg.com/profile_images/843841615122784256/WXbuqyjo_bigger.jpg")

    except IndexError:
        embed = None

    return embed
