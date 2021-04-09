import discord
import re
import time
from bs4 import BeautifulSoup
import cloudscraper

from utils.search import get_ao3_url, get_ffn_url
from utils.processing import story_last_up_clean, ffn_process_details, \
    ao3_convert_chapters_to_works
from utils.metadata_processing import ao3_metadata_works, ao3_metadata_series

URL_VALIDATE = r"(?:(?:https?|ftp)://)(?:\S+(?::\S*)?@)?(?:(?:[1-9]\d?|1\d\d|2[01]\d|22[0-3])(?:\.(?:1?\d{1,2}|2[0-4]\d|25[0-5])){2}(?:\.(?:[1-9]\d?|1\d\d|2[0-4]\d|25[0-4]))|(?:(?:[a-z\u00a1-\uffff0-9]+-?)*[a-z\u00a1-\uffff0-9]+)(?:\.(?:[a-z\u00a1-\uffff0-9]+-?)*[a-z\u00a1-\uffff0-9]+)*(?:\.(?:[a-z\u00a1-\uffff]{2,})))(?::\d{2,5})?(?:/[^\s]*)?"


def ao3_metadata(query):
    if re.search(URL_VALIDATE, query) is None:

        query = query.replace(" ", "+")
        ao3_url = get_ao3_url(query)

    else:  # clean the url if the query contains a url
        ao3_url = re.search(URL_VALIDATE, query).group(0)

    if ao3_url is None:
        embed = discord.Embed(
            description="Fanfiction not found.",
            colour=discord.Colour(0x272b28))
        return embed

    if re.search(r"/chapters/\b", ao3_url) is not None:
        ao3_url = ao3_convert_chapters_to_works(
            ao3_url)  # convert the url from /chapters/ to /works/

        ao3_story_name, ao3_author_name, ao3_author_url, ao3_story_summary, \
            ao3_story_status, ao3_story_last_up, ao3_story_length, \
            ao3_story_chapters, ao3_story_rating, ao3_story_relationships, \
            ao3_story_characters, ao3_story_fandom = ao3_metadata_works(
                ao3_url)

    elif re.search(r"/works/\b", ao3_url) is not None:
        ao3_story_name, ao3_author_name, ao3_author_url, ao3_story_summary, \
            ao3_story_status, ao3_story_last_up, ao3_story_length, \
            ao3_story_chapters, ao3_story_rating, ao3_story_relationships, \
            ao3_story_characters, ao3_story_fandom = ao3_metadata_works(
                ao3_url)

    elif re.search(r"/series/\b", ao3_url) is not None:
        ao3_series_name, ao3_author_name, ao3_author_url, ao3_series_summary, \
            ao3_series_status, ao3_series_last_up, ao3_series_length, \
            ao3_series_works = ao3_metadata_series(
                ao3_url)

        # remove everything after &sa from the url
        if re.search(r"^(.*?)&", ao3_url) is not None:
            ao3_url = re.search(
                r"^(.*?)&", ao3_url).group(1)

        embed = discord.Embed(
            title=ao3_series_name,
            url=ao3_url,
            description=ao3_series_summary,
            colour=discord.Colour(0x272b28))

        if ao3_series_status == "Completed":

            embed.add_field(
                name='📜 Last Updated',
                value=ao3_series_last_up +
                " ✓Complete", inline=True)

        elif ao3_series_status == "Updated":

            embed.add_field(
                name='📜 Last Updated',
                value=ao3_series_last_up, inline=True)

        elif ao3_series_status is None:
            embed.add_field(
                name='📜 Last Updated',
                value=ao3_series_last_up, inline=True)

        embed.add_field(
            name='📖 Length',
            value=ao3_series_length +
            " words in "+ao3_series_works+" work(s)", inline=True)

        embed.add_field(name="\u200b",  # zero-width whitespace character
                        value="*If this content violates the server rules, reply to the bot message with `del` and it will be removed.*", inline=False)

        embed.set_author(
            name=ao3_author_name, url=ao3_author_url,
            icon_url="https://archiveofourown.org/images/ao3_logos/logo_42.png")

        return embed

    # remove everything after &sa from the url
    if re.search(r"^(.*?)&", ao3_url) is not None:
        ao3_url = re.search(
            r"^(.*?)&", ao3_url).group(1)

    embed = discord.Embed(
        title=ao3_story_name,
        url=ao3_url,
        description=ao3_story_summary,
        colour=discord.Colour(0x272b28))

    if ao3_story_status == "Completed":

        embed.add_field(
            name='📜 Last Updated',
            value=ao3_story_last_up +
            " ✓Complete", inline=True)

    elif ao3_story_status == "Updated":

        embed.add_field(
            name='📜 Last Updated',
            value=ao3_story_last_up, inline=True)

    elif ao3_story_status is None:
        embed.add_field(
            name='📜 Last Updated',
            value=ao3_story_last_up, inline=True)

    embed.add_field(
        name='📖 Length',
        value=ao3_story_length +
        " words in "+ao3_story_chapters+" chapter(s)", inline=True)

    other_info = [ao3_story_fandom, " **|** "]

    for var in [ao3_story_relationships, ao3_story_characters]:
        if var is not None:
            other_info.append(str(var))
            other_info.append(" **|** ")

    other_info = ''.join(other_info[:len(other_info)-1])
    if len(list(other_info)) > 100:
        other_info = other_info[:100] + "..."

    if other_info:
        embed.add_field(name=f":bookmark: Rating: {ao3_story_rating}",
                        value=other_info, inline=False)

    embed.add_field(name="\u200b",  # zero-width whitespace character
                    value="*If this content violates the server rules, reply to the bot message with `del` and it will be removed.*", inline=False)

    embed.set_author(
        name=ao3_author_name, url=ao3_author_url,
        icon_url="https://archiveofourown.org/images/ao3_logos/logo_42.png")

    return embed


def ffn_metadata(query):
    if re.search(URL_VALIDATE, query) is None:
        if re.search(r"ao3\b", query):
            embed = None
            return embed
        query = query.replace(" ", "+")
        ffn_url = get_ffn_url(query)

    else:  # clean the url if the query contains a url
        ffn_url = re.search(
            URL_VALIDATE, query).group(0)

    if ffn_url is None:
        return None

    # convert m.fanfiction.net to www.fanfiction.net
    ffn_url = ffn_url.replace(r"/m.", r"/www.")

    scraper = cloudscraper.CloudScraper(
        delay=2, browser={
            'browser': 'chrome',
            'platform': 'windows',
            'mobile': False,
            'desktop': True,
        }
    )
    time.sleep(2)
    ffn_page = scraper.get(ffn_url).text
    ffn_soup = BeautifulSoup(ffn_page, 'html.parser')

    try:
        ffn_story_name = ffn_soup.find_all('b', 'xcontrast_txt')[
            0].string.strip()

        ffn_author_name = ffn_soup.find_all(
            'a', {'href': re.compile(r'^/u/\d+/.')})[0].string.strip()

        ffn_author_url = (ffn_soup.find(
            'div', attrs={'id': 'profile_top'}).find('a', href=True))['href']

        ffn_story_summary = ffn_soup.find_all('div', {
            'style': 'margin-top:2px',
            'class': 'xcontrast_txt'})[0].string.strip()

        ffn_story_fandom = ffn_soup.find(
            'span', attrs={'class': 'lc-left'}).find(
            'a', attrs={'class': 'xcontrast_txt'}).text

        # if the fandom isnt crossover, then go to the next <a>
        if not re.search(r"\bcrossover\b", ffn_story_fandom, re.IGNORECASE):
            ffn_story_fandom = ffn_soup.find(
                'span', attrs={'class': 'lc-left'}).find(
                'a', attrs={'class': 'xcontrast_txt'}).findNext('a').text

        ffn_story_status, ffn_story_last_up, ffn_story_length, \
            ffn_story_chapters, ffn_story_rating, ffn_story_genre, \
            ffn_story_characters = ffn_process_details(
                ffn_soup)

        ffn_story_last_up = story_last_up_clean(ffn_story_last_up, 1)
        ffn_author_url = "https://www.fanfiction.net"+ffn_author_url

        # remove everything after &sa from the url
        if re.search(r"^(.*?)&", ffn_url) is not None:
            ffn_url = re.search(
                r"^(.*?)&", ffn_url).group(1)

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
                name='📜 Last Updated',
                value=ffn_story_last_up, inline=True)

        embed.add_field(
            name='📖 Length',
            value=str(ffn_story_length) +
            " words in "+str(ffn_story_chapters)+" chapter(s)", inline=True)

        other_info = [ffn_story_fandom, " **|** "]

        for var in [ffn_story_genre,
                    ffn_story_characters]:
            if var is not None:
                other_info.append(str(var))
                other_info.append(" **|** ")

        other_info = ''.join(other_info[:len(other_info)-1])

        if len(list(other_info)) > 100:
            other_info = other_info[:100] + "..."

        if other_info:
            embed.add_field(name=f":bookmark: Rating: {ffn_story_rating}",
                            value=other_info, inline=False)

        embed.add_field(name="\u200b",  # zero-width whitespace character
                        value="*If this content violates the server rules, reply to the bot message with `del` and it will be removed.*", inline=False)

        embed.set_author(
            name=ffn_author_name, url=ffn_author_url,
            icon_url="https://pbs.twimg.com/profile_images/843841615122784256/WXbuqyjo_bigger.jpg")

    except IndexError:
        embed = discord.Embed(
            description="Fanfiction not found.",
            colour=discord.Colour(0x272b28))

    return embed
