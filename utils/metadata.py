import discord
import re
from bs4 import BeautifulSoup
import cloudscraper

from utils.search import get_ao3_id, get_ffn_id
from utils.processing import story_last_up_clean, ffn_process_details, ao3_convert_chapters_to_works
from utils.metadata_processing import ao3_metadata_works, ao3_metadata_series


def ao3_metadata(query):
    if re.search(r"https?:\/\/(www/.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b[-a-zA-Z0-9()@:%_\+.~#?&//=]*", query) is None:

        query = query.replace(" ", "+")
        ao3_id = get_ao3_id(query)

        if not ao3_id:
            embed = None
            return embed

        if ao3_id == 1:
            embed = None
            return embed

        # its an ao3 series, get_ao3_id will return the ao3 series url
        if re.search(r"https?:\/\/(www/.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b[-a-zA-Z0-9()@:%_\+.~#?&//=]*", ao3_id) is not None:
            ao3_url = ao3_id  # ao3_url was returned inplace of ao3_id
            ao3_series_name, ao3_author_name, ao3_author_url, ao3_series_summary, ao3_series_status, ao3_series_last_up, ao3_series_length, ao3_series_works = ao3_metadata_series(
                ao3_url)

            if ao3_series_status == "Completed":
                des = ao3_series_summary+"\n\n"+"**📜 Last Updated:** "+ao3_series_last_up +\
                    "\n"+"**📖 Length:** " + ao3_series_length + \
                    " words in "+ao3_series_works+" works"

            elif ao3_series_status == "Updated":
                des = ao3_series_summary+"\n\n"+"**📜 Last Updated:** "+ao3_series_last_up +\
                    "\n"+"**📖 Length:** " + ao3_series_length + \
                    " words in "+ao3_series_works+" works"
            embed = discord.Embed(
                title=ao3_series_name,
                url=ao3_url,
                description=des,
                colour=discord.Colour(0x272b28))

            embed.set_author(name=ao3_author_name, url=ao3_author_url,
                             icon_url="https://archiveofourown.org/images/ao3_logos/logo_42.png")

            return embed
        else:
            ao3_url = "https://archiveofourown.org/works/"+''.join(ao3_id)
    else:  # if the query was ao3 url, not get_fic_id needed
        ao3_url = re.search(
            r"((http|https)\:\/\/)?[a-zA-Z0-9\.\/\?\:@\-_=#]+\.([a-zA-Z]){2,6}([a-zA-Z0-9\.\&\/\?\:@\-_=#])*\b", query)
        ao3_url = ao3_url.group()

    if re.search(r"archiveofourown.org/works/\b", ao3_url) is not None:
        ao3_story_name, ao3_author_name, ao3_author_url, ao3_story_summary, ao3_story_status, ao3_story_last_up, ao3_story_length, ao3_story_chapters = ao3_metadata_works(
            ao3_url)

    elif re.search(r"archiveofourown.org/chapters/\b", ao3_url) is not None:
        ao3_url = ao3_convert_chapters_to_works(
            ao3_url)  # convert the url from /chapters/ to /works/

        ao3_story_name, ao3_author_name, ao3_author_url, ao3_story_summary, ao3_story_status, ao3_story_last_up, ao3_story_length, ao3_story_chapters = ao3_metadata_works(
            ao3_url)

    elif re.search(r"archiveofourown.org/series/\b", ao3_url) is not None:
        ao3_series_name, ao3_author_name, ao3_author_url, ao3_series_summary, ao3_series_status, ao3_series_last_up, ao3_series_length, ao3_series_works = ao3_metadata_series(
            ao3_url)

        if ao3_series_status == "Completed":
            des = ao3_series_summary+"\n\n"+"**📜 Last Updated:** "+ao3_series_last_up +\
                "\n"+"**📖 Length:** " + ao3_series_length + \
                " words in "+ao3_series_works+" works"

        elif ao3_series_status == "Updated":
            des = ao3_series_summary+"\n\n"+"**📜 Last Updated:** "+ao3_series_last_up +\
                "\n"+"**📖 Length:** " + ao3_series_length + \
                " words in "+ao3_series_works+" works"

        embed = discord.Embed(
            title=ao3_series_name,
            url=ao3_url,
            description=des,
            colour=discord.Colour(0x272b28))

        embed.set_author(name=ao3_author_name, url=ao3_author_url,
                         icon_url="https://archiveofourown.org/images/ao3_logos/logo_42.png")

        return embed

    if ao3_story_status == "Completed":
        des = ao3_story_summary+"\n\n"+"**📜 Last Updated:** "+ao3_story_last_up +\
            " - "+ao3_story_status+"\n"+"**📖 Length:** " + ao3_story_length +\
            " words in "+ao3_story_chapters+" chapters"

    elif ao3_story_status == "Updated":
        des = ao3_story_summary+"\n\n"+"**📜 Last Updated:** "+ao3_story_last_up +\
            "\n"+"**📖 Length:** " + ao3_story_length +\
            " words in "+ao3_story_chapters+" chapters"

    embed = discord.Embed(
        title=ao3_story_name,
        url=ao3_url,
        description=des,
        colour=discord.Colour(0x272b28))

    embed.set_author(name=ao3_author_name, url=ao3_author_url,
                     icon_url="https://archiveofourown.org/images/ao3_logos/logo_42.png")

    return embed


def ffn_metadata(query):
    if re.search(r"https?:\/\/(www/.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b[-a-zA-Z0-9()@:%_\+.~#?&//=]*", query) is None:

        if re.search(r"ao3\b", query):
            embed = None
            return embed

        query = query.replace(" ", "+")
        ffn_id = get_ffn_id(query)

        if not ffn_id:
            embed = None
            return embed

        if ffn_id == 1:
            embed = None
            return embed

        ffn_url = "https://www.fanfiction.net/s/"+''.join(ffn_id)
    else:  # if the query was ffn url, not get_fic_id needed
        ffn_url = query

    scraper = cloudscraper.create_scraper()
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

        ffn_story_status, ffn_story_last_up, ffn_story_length, ffn_story_chapters = ffn_process_details(
            ffn_soup)

        ffn_story_last_up = story_last_up_clean(ffn_story_last_up)
        ffn_author_url = "https://www.fanfiction.net"+ffn_author_url

        if len(list(ffn_story_summary)) > 2048:
            ffn_story_summary = ffn_story_summary[:2030] + "..."

        if ffn_story_status == "Complete":
            des = ffn_story_summary+"\n\n"+"**📜 Last Updated:** "+ffn_story_last_up +\
                " - "+ffn_story_status+"\n"+"**📖 Length:** " + ffn_story_length + \
                " words in "+ffn_story_chapters+" chapters"
        elif ffn_story_status == "Updated":
            des = ffn_story_summary+"\n\n"+"**📜 Last Updated:** "+ffn_story_last_up +\
                "\n"+"**📖 Length:** " + ffn_story_length +\
                " words in "+ffn_story_chapters+" chapters"

        embed = discord.Embed(
            title=ffn_story_name,
            url=ffn_url,
            description=des,
            colour=discord.Colour(0x272b28))
        embed.set_author(name=ffn_author_name, url=ffn_author_url,
                         icon_url="https://pbs.twimg.com/profile_images/843841615122784256/WXbuqyjo_bigger.jpg")

    except IndexError:
        embed = None

    return embed
