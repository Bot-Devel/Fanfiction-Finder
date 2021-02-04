import discord
import requests
import re
from bs4 import BeautifulSoup

from utils.search import get_fic_id
from utils.processing import ao3_story_chapter_clean, ao3_story_last_up_clean


def ao3_metadata(query):
    if re.search(r"https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)", query) is None:
        query = query.replace(" ", "+")
        ao3_id = get_fic_id(query)
        if not ao3_id:
            embed = discord.Embed(
                description="Fanfic not found!"
            )
            return embed
        ao3_url = "https://archiveofourown.org/works/"+''.join(ao3_id)
    else:  # if the query was ao3 url, not get_fic_id needed
        ao3_url = query
    ao3_page = requests.get(ao3_url)  # , headers)
    ao3_soup = BeautifulSoup(ao3_page.content, 'html.parser')
    ao3_story_name = (ao3_soup.find(
        'h2', attrs={'class': 'title heading'}).contents[0]).strip()
    ao3_author_name = (ao3_soup.find(
        'h3', attrs={'class': 'byline heading'}).find('a').contents[0]).strip()
    ao3_story_summary = (ao3_soup.find(
        'div', attrs={'class': 'summary module'}).find(
        'blockquote', attrs={'class': 'userstuff'}).find('p').contents[0]).strip()
    try:
        ao3_story_status = (ao3_soup.find(
            'dl', attrs={'class': 'stats'}).find(
            'dt', attrs={'class': 'status'}).contents[0]).strip()
        ao3_story_status = ao3_story_status.replace(":", "")
    except AttributeError:  # if story status not found
        ao3_story_status = "Complete"
    try:
        ao3_story_last_up = (ao3_soup.find(
            'dl', attrs={'class': 'stats'}).find(
            'dd', attrs={'class': 'status'}).contents[0]).strip()
    except AttributeError:  # if story last updated not found
        ao3_story_last_up = (ao3_soup.find(
            'dl', attrs={'class': 'stats'}).find(
            'dd', attrs={'class': 'published'}).contents[0]).strip()
    ao3_story_length = (ao3_soup.find(
        'dl', attrs={'class': 'stats'}).find(
        'dd', attrs={'class': 'words'}).contents[0]).strip()
    ao3_story_chapters = (ao3_soup.find(
        'dl', attrs={'class': 'stats'}).find(
        'dd', attrs={'class': 'chapters'}).contents[0]).strip()
    ao3_story_length = "{:,}".format(int(ao3_story_length))
    ao3_story_chapters = ao3_story_chapter_clean(ao3_story_chapters)
    ao3_story_last_up = ao3_story_last_up_clean(ao3_story_last_up)
    if len(list(ao3_story_summary)) > 2048:
        ao3_story_summary = ao3_story_summary[:2030] + "..."
    if ao3_story_status == "Complete":
        des = ao3_story_summary+"\n\n"+"**📜 Last Updated:** "+ao3_story_last_up +\
            " - "+ao3_story_status+"\n"+"**📖 Length:** " + ao3_story_length + \
            " words in "+ao3_story_chapters+" chapters"
    else:
        des = ao3_story_summary+"\n\n"+"**📜 Last Updated:** "+ao3_story_last_up +\
            "\n"+"**📖 Length:** " + ao3_story_length + \
            " words in "+ao3_story_chapters+" chapters"
    embed = discord.Embed(
        title=ao3_story_name+" by "+ao3_author_name,
        url=ao3_url,
        description=des,
        colour=discord.Colour(0x272b28))

    return embed
