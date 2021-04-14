from bs4 import BeautifulSoup
import requests
import time
import re
from utils.processing import story_last_up_clean, get_ao3_series_works_index


def ao3_metadata_works(ao3_url):

    time.sleep(2)
    ao3_page = requests.get(ao3_url)
    ao3_soup = BeautifulSoup(ao3_page.content, 'html.parser')

    ao3_story_name = (ao3_soup.find(
        'h2', attrs={'class': 'title heading'}).contents[0]).strip()

    ao3_author_name_list = ao3_soup.find(
        'h3', attrs={'class': 'byline heading'}).find_all('a')

    ao3_author_url = ao3_soup.find(
        'h3', attrs={'class': 'byline heading'}).find('a', href=True)['href']

    try:
        ao3_story_summary = ao3_soup.find(
            'div', attrs={'class': 'summary module'}).find(
            'blockquote', attrs={'class': 'userstuff'}).text

    except AttributeError:  # if summary not found
        ao3_story_summary = ""

    ao3_story_summary = re.sub(
        r'\s+', ' ', ao3_story_summary)  # removing whitespaces

    try:
        ao3_story_status = (ao3_soup.find(
            'dl', attrs={'class': 'stats'}).find(
            'dt', attrs={'class': 'status'}).contents[0]).strip()
        ao3_story_status = ao3_story_status.replace(":", "")

    except AttributeError:  # if story status not found
        ao3_story_status = None

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

    ao3_story_rating = (ao3_soup.find(
        'dd', attrs={'class': 'rating tags'}).find('a').contents[0]).strip()

    try:  # not found in every story
        ao3_story_relationships = [
            a.contents[0].strip()
            for a in ao3_soup.find(
                'dd', attrs={'class': 'relationship tags'}).find_all('a')
        ]
        ao3_story_relationships = ", ".join(ao3_story_relationships)

    except AttributeError:
        ao3_story_relationships = None

    try:  # not found in every story
        ao3_story_characters = [
            a.contents[0].strip()
            for a in ao3_soup.find(
                'dd', attrs={'class': 'character tags'}).find_all('a')
        ]

        ao3_story_characters = ", ".join(ao3_story_characters)

    except AttributeError:
        ao3_story_characters = None

    ao3_story_fandom = (ao3_soup.find(
        'dd', attrs={'class': 'fandom tags'}).find('a').contents[0]).strip()

    try:
        ao3_story_kudos = '**Kudos:** '
        ao3_story_kudos += (ao3_soup.find(
            'dl', attrs={'class': 'stats'}).find(
            'dd', attrs={'class': 'kudos'}).contents[0]).strip()

    except AttributeError:
        ao3_story_bookmarks = None

    try:
        ao3_story_bookmarks = '**Bookmarks:** '
        ao3_story_bookmarks += (ao3_soup.find(
            'dl', attrs={'class': 'stats'}).find(
            'dd', attrs={'class': 'bookmarks'}).find('a').contents[0]).strip()

    except AttributeError:
        ao3_story_bookmarks = None

    try:
        ao3_story_comments = '**Comments:** '
        ao3_story_comments += (ao3_soup.find(
            'dl', attrs={'class': 'stats'}).find(
            'dd', attrs={'class': 'comments'}).contents[0]).strip()

    except AttributeError:
        ao3_story_bookmarks = None

    try:
        ao3_story_hits = '**Hits:** '
        ao3_story_hits += (ao3_soup.find(
            'dl', attrs={'class': 'stats'}).find(
            'dd', attrs={'class': 'hits'}).contents[0]).strip()

    except AttributeError:
        ao3_story_bookmarks = None

    ao3_meta_info = [ao3_story_comments, ao3_story_kudos,
                     ao3_story_bookmarks, ao3_story_hits]
    ao3_story_metainfo = ""
    for m in range(len(ao3_meta_info)):
        if ao3_meta_info[m]:
            ao3_story_metainfo += ao3_meta_info[m]
            if m < len(ao3_meta_info)-1:
                ao3_story_metainfo += ' - '

    ao3_story_length = "{:,}".format(int(ao3_story_length))
    ao3_story_chapters = re.search(r"\d+", ao3_story_chapters).group(0)
    ao3_story_last_up = story_last_up_clean(ao3_story_last_up, 2)
    ao3_author_url = "https://archiveofourown.org"+ao3_author_url

    ao3_author_name = []
    for author in ao3_author_name_list:
        ao3_author_name.append(author.string.strip())
    ao3_author_name = ", ".join(ao3_author_name)

    if len(list(ao3_story_summary)) > 2048:
        ao3_story_summary = ao3_story_summary[:2030] + "..."

    return ao3_story_name, ao3_author_name, ao3_author_url, \
        ao3_story_summary, ao3_story_status, ao3_story_last_up, \
        ao3_story_length, ao3_story_chapters, ao3_story_rating, \
        ao3_story_relationships, ao3_story_characters, ao3_story_fandom, \
        ao3_story_metainfo


def ao3_metadata_series(ao3_url):

    time.sleep(2)

    ao3_page = requests.get(ao3_url)
    ao3_soup = BeautifulSoup(ao3_page.content, 'html.parser')

    ao3_series_name = (ao3_soup.find(
        'div', attrs={'class': 'series-show region'}).find(
        'h2', attrs={'class': 'heading'}).contents[0]).strip()

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

    ao3_series_length = ao3_soup.find(
        'dt', text='Words:').findNext(
        'dd').string.strip()

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
        ao3_series_summary = ao3_series_summary[:1930] + "..."

    return ao3_series_name, ao3_author_name, ao3_author_url, \
        ao3_series_summary, ao3_series_status, ao3_series_last_up,\
        ao3_series_length, ao3_series_works
