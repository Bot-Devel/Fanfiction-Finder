from bs4 import BeautifulSoup
from discord import Embed, Colour
import requests
import time
import re

from utils.processing import story_last_up_clean, get_ao3_series_works_index


def ao3_metadata_works(ao3_url):

    time.sleep(2)
    ao3_page = requests.get(ao3_url)
    ao3_soup = BeautifulSoup(ao3_page.content, 'html.parser')

    try:
        ao3_work_name = (ao3_soup.find(
            'h2', attrs={'class': 'title heading'}).contents[0]).strip()

    except AttributeError:
        return Embed(
            description="Fanfiction not found",
            colour=Colour(0x272b28))

    ao3_author_name_list = ao3_soup.find(
        'h3', attrs={'class': 'byline heading'}).find_all('a')

    ao3_author_url = ao3_soup.find(
        'h3', attrs={'class': 'byline heading'}).find('a', href=True)['href']

    try:
        ao3_work_summary = ao3_soup.find(
            'div', attrs={'class': 'summary module'}).find(
            'blockquote', attrs={'class': 'userstuff'}).text

    except AttributeError:  # if summary not found
        ao3_work_summary = ""

    ao3_work_summary = re.sub(
        r'\s+', ' ', ao3_work_summary)  # removing whitespaces

    try:
        ao3_work_status = (ao3_soup.find(
            'dl', attrs={'class': 'stats'}).find(
            'dt', attrs={'class': 'status'}).contents[0]).strip()
        ao3_work_status = ao3_work_status.replace(":", "")

    except AttributeError:  # if story status not found
        ao3_work_status = None

    try:
        ao3_work_last_up = (ao3_soup.find(
            'dl', attrs={'class': 'stats'}).find(
            'dd', attrs={'class': 'status'}).contents[0]).strip()

    except AttributeError:  # if story last updated not found
        ao3_work_last_up = (ao3_soup.find(
            'dl', attrs={'class': 'stats'}).find(
            'dd', attrs={'class': 'published'}).contents[0]).strip()

    try:
        ao3_work_length = (ao3_soup.find(
            'dl', attrs={'class': 'stats'}).find(
            'dd', attrs={'class': 'words'}).contents[0]).strip()

    except IndexError:  # Missing wordcount
        ao3_work_length = 0

    ao3_work_chapters = (ao3_soup.find(
        'dl', attrs={'class': 'stats'}).find(
        'dd', attrs={'class': 'chapters'}).contents[0]).strip()

    try:
        ao3_work_rating = (ao3_soup.find(
            'dd', attrs={'class': 'rating tags'}).find('a').contents[0]).strip()

    except AttributeError:
        ao3_work_rating = None

    try:  # not found in every story
        ao3_work_relationships = [
            a.contents[0].strip()
            for a in ao3_soup.find(
                'dd', attrs={'class': 'relationship tags'}).find_all('a')
        ]
        ao3_work_relationships = ", ".join(ao3_work_relationships)

    except AttributeError:
        ao3_work_relationships = None

    try:  # not found in every story
        ao3_work_characters = [
            a.contents[0].strip()
            for a in ao3_soup.find(
                'dd', attrs={'class': 'character tags'}).find_all('a')
        ]

        ao3_work_characters = ", ".join(ao3_work_characters)

    except AttributeError:
        ao3_work_characters = None

    ao3_work_fandom = (ao3_soup.find(
        'dd', attrs={'class': 'fandom tags'}).find('a').contents[0]).strip()

    try:
        ao3_work_kudos = '**Kudos:** '
        ao3_work_kudos += (ao3_soup.find(
            'dl', attrs={'class': 'stats'}).find(
            'dd', attrs={'class': 'kudos'}).contents[0]).strip()

    except AttributeError:
        ao3_work_kudos = '**Kudos:** 0 '

    try:
        ao3_work_bookmarks = '**Bookmarks:** '
        ao3_work_bookmarks += (ao3_soup.find(
            'dl', attrs={'class': 'stats'}).find(
            'dd', attrs={'class': 'bookmarks'}).find('a').contents[0]).strip()

    except AttributeError:
        ao3_work_bookmarks = '**Bookmarks:** 0'

    try:
        ao3_work_comments = '**Comments:** '
        ao3_work_comments += (ao3_soup.find(
            'dl', attrs={'class': 'stats'}).find(
            'dd', attrs={'class': 'comments'}).contents[0]).strip()

    except AttributeError:
        ao3_work_comments = '**Comments:** 0 '

    try:
        ao3_work_hits = '**Hits:** '
        ao3_work_hits += (ao3_soup.find(
            'dl', attrs={'class': 'stats'}).find(
            'dd', attrs={'class': 'hits'}).contents[0]).strip()

    except AttributeError:
        ao3_work_hits = '**Hits:** 0 '

    ao3_meta_info = [ao3_work_comments, ao3_work_kudos,
                     ao3_work_bookmarks, ao3_work_hits]

    ao3_work_metainfo = ""
    for m in range(len(ao3_meta_info)):
        if ao3_meta_info[m]:
            ao3_work_metainfo += ao3_meta_info[m]
            if m < len(ao3_meta_info)-1:
                ao3_work_metainfo += " ☘︎ "

    ao3_work_length = "{:,}".format(int(ao3_work_length))
    ao3_work_chapters = re.search(r"\d+", ao3_work_chapters).group(0)
    ao3_work_last_up = story_last_up_clean(ao3_work_last_up, 2)
    ao3_author_url = "https://archiveofourown.org"+ao3_author_url

    ao3_author_name = []
    for author in ao3_author_name_list:
        ao3_author_name.append(author.string.strip())
    ao3_author_name = ", ".join(ao3_author_name)

    if len(list(ao3_work_summary)) > 2048:
        ao3_work_summary = ao3_work_summary[:2030] + "..."

    # remove everything after &sa from the url
    if re.search(r"^(.*?)&", ao3_url) is not None:
        ao3_url = re.search(
            r"^(.*?)&", ao3_url).group(1)

    embed = Embed(
        title=ao3_work_name,
        url=ao3_url,
        description=ao3_work_summary,
        colour=Colour(0x272b28))

    if ao3_work_status == "Completed":

        embed.add_field(
            name='📜 Last Updated',
            value=ao3_work_last_up +
            " ✓Complete", inline=True)

    elif ao3_work_status == "Updated":

        embed.add_field(
            name='📜 Last Updated',
            value=ao3_work_last_up, inline=True)

    elif ao3_work_status is None:
        embed.add_field(
            name='📜 Last Updated',
            value=ao3_work_last_up, inline=True)

    embed.add_field(
        name='📖 Length',
        value=ao3_work_length +
        " words in "+ao3_work_chapters+" chapter(s)", inline=True)

    other_info = [ao3_work_fandom, " ☘︎ "]

    for var in [ao3_work_relationships, ao3_work_characters]:
        if var is not None:
            other_info.append(str(var))
            other_info.append(" ☘︎ ")

    other_info = ''.join(other_info[:len(other_info)-1])
    if len(list(other_info)) > 100:
        other_info = other_info[:100] + "..."

    if other_info:
        embed.add_field(name=f":bookmark: Rating: {ao3_work_rating}",
                        value=other_info, inline=False)

    if ao3_work_metainfo:
        embed.add_field(name="📊 Stats",
                        value=ao3_work_metainfo, inline=False)

    embed.add_field(name="\u200b",  # zero-width whitespace character
                    value="*If this content violates the server rules, reply to the bot message with `del` and it will be removed. Check `,help`.*", inline=False)

    embed.set_author(
        name=ao3_author_name, url=ao3_author_url,
        icon_url="https://archiveofourown.org/images/ao3_logos/logo_42.png")

    return embed


def ao3_metadata_series(ao3_url):

    time.sleep(2)

    ao3_page = requests.get(ao3_url)
    ao3_soup = BeautifulSoup(ao3_page.content, 'html.parser')

    try:
        ao3_series_name = (ao3_soup.find(
            'div', attrs={'class': 'series-show region'}).find(
            'h2', attrs={'class': 'heading'}).contents[0]).strip()

    except AttributeError:
        return Embed(
            description="Fanfiction not found",
            colour=Colour.red())

    ao3_author_name_list = ao3_soup.find(
        'dl', attrs={'class': 'series meta group'}).find('dd').find_all('a')

    try:
        ao3_series_summary = ao3_soup.find(
            'div', attrs={'class': 'series-show region'}).find(
            'blockquote', attrs={'class': 'userstuff'}).text

    except AttributeError:  # if summary not found
        ao3_series_summary = ""

    ao3_series_summary = re.sub(
        r'\s+', ' ', ao3_series_summary)  # removing whitespaces

    try:
        ao3_series_status = (ao3_soup.find(
            'dl', attrs={'class': 'stats'}).find(
            'dt', text='Complete:').findNext(
            'dd')).string.strip()
        if ao3_series_status == "No":
            ao3_series_status = "Updated"
        elif ao3_series_status == "Yes":
            ao3_series_status = "Complete"

    except AttributeError:  # if story status not found
        ao3_series_status = None

    try:
        ao3_series_last_up = ao3_soup.find(
            'div', attrs={'class': 'series-show region'}).find(
            'dt', text='Series Updated:').findNext(
            'dd').string.strip()

    except AttributeError:  # if story last updated not found
        ao3_series_last_up = ao3_soup.find(
            'div', attrs={'class': 'series-show region'}).find(
            'dt', text='Series Begun:').findNext(
            'dd').string.strip()

    try:
        ao3_series_length = ao3_soup.find(
            'dt', text='Words:').findNext(
            'dd').string.strip()
    except IndexError:  # Missing wordcount
        ao3_series_length = 0

    ao3_series_works = ao3_soup.find(
        'dt', text='Works:').findNext(
        'dd').string.strip()

    ao3_series_works_index = get_ao3_series_works_index(ao3_soup)
    ao3_series_last_up = story_last_up_clean(ao3_series_last_up, 2)

    for author in ao3_author_name_list:
        ao3_author_url = author['href']
        break  # To only get the 1st author url

    ao3_author_url = "https://archiveofourown.org"+ao3_author_url

    ao3_author_name = []
    for author in ao3_author_name_list:
        ao3_author_name.append(author.string.strip())
    ao3_author_name = ", ".join(ao3_author_name)

    if len(list(ao3_series_summary)) > 2048:
        ao3_series_summary = ao3_series_summary[:1930] + "..."
    else:
        ao3_series_summary = ao3_series_summary + \
            '\n\n'+"📚 **Works**:\n"+ao3_series_works_index

    if len(list(ao3_series_summary)) > 2048:  # recheck the size of summary
        ao3_series_summary = ao3_series_summary[:1930]

        # if the line doesnt end with ")", remove the whole line.
        # this prevents brokens links to ao3 works
        ao3_series_summary_lines = ao3_series_summary.splitlines()
        if not ao3_series_summary_lines[-1].endswith(")"):
            ao3_series_summary_lines.pop(-1)

        ao3_series_summary = "\n".join(ao3_series_summary_lines)

    # remove everything after &sa from the url
    if re.search(r"^(.*?)&", ao3_url) is not None:
        ao3_url = re.search(
            r"^(.*?)&", ao3_url).group(1)

    embed = Embed(
        title=ao3_series_name,
        url=ao3_url,
        description=ao3_series_summary,
        colour=Colour(0x272b28))

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
                    value="*If this content violates the server rules, reply to the bot message with `del` and it will be removed. Check `,help`.*", inline=False)

    embed.set_author(
        name=ao3_author_name, url=ao3_author_url,
        icon_url="https://archiveofourown.org/images/ao3_logos/logo_42.png")

    return embed
