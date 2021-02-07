from bs4 import BeautifulSoup
import requests
import re
from utils.processing import story_last_up_clean, ao3_story_chapter_clean, ao3_convert_chapters_to_works, get_ao3_series_works_index


def ao3_metadata_works(ao3_url):
    ao3_page = requests.get(ao3_url)
    ao3_soup = BeautifulSoup(ao3_page.content, 'html.parser')

    ao3_story_name = (ao3_soup.find(
        'h2', attrs={'class': 'title heading'}).contents[0]).strip()

    ao3_author_name = (ao3_soup.find(
        'h3', attrs={'class': 'byline heading'}).find('a').contents[0]).strip()

    ao3_story_summary = ao3_soup.find(
        'div', attrs={'class': 'summary module'}).find(
        'blockquote', attrs={'class': 'userstuff'}).text

    ao3_story_summary = re.sub(
        r'\s+', ' ', ao3_story_summary)  # removing whitespaces

    try:
        ao3_story_status = (ao3_soup.find(
            'dl', attrs={'class': 'stats'}).find(
            'dt', attrs={'class': 'status'}).contents[0]).strip()
        ao3_story_status = ao3_story_status.replace(":", "")

    except AttributeError:  # if story status not found
        ao3_story_status = "Completed"

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
    ao3_story_last_up = story_last_up_clean(ao3_story_last_up)

    if len(list(ao3_story_summary)) > 2048:
        ao3_story_summary = ao3_story_summary[:2030] + "..."

    return ao3_story_name, ao3_author_name, ao3_story_summary, ao3_story_status, ao3_story_last_up, ao3_story_length, ao3_story_chapters


def ao3_metadata_series(ao3_url):
    ao3_page = requests.get(ao3_url)
    ao3_soup = BeautifulSoup(ao3_page.content, 'html.parser')

    ao3_series_name = (ao3_soup.find(
        'div', attrs={'class': 'series-show region'}).find(
        'h2', attrs={'class': 'heading'}).contents[0]).strip()

    ao3_author_name = (ao3_soup.find(
        'div', attrs={'class': 'series-show region'}).find(
        'a', attrs={'rel': 'author'}).contents[0]).strip()

    ao3_series_summary = ao3_soup.find(
        'div', attrs={'class': 'series-show region'}).find(
        'blockquote', attrs={'class': 'userstuff'}).text

    ao3_series_summary = re.sub(
        r'\s+', ' ', ao3_series_summary)  # removing whitespaces

    try:
        ao3_series_status = (ao3_soup.find(
            'dl', attrs={'class': 'stats'}).find(
            'dt', text='Complete:').findNext(
            'dd')).string.strip()
        if ao3_series_status == "No":
            ao3_series_status = "Updated"

    except AttributeError:  # if story status not found
        ao3_series_status = "Completed"

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
    ao3_series_last_up = story_last_up_clean(ao3_series_last_up)

    if len(list(ao3_series_summary)) > 2048:
        ao3_series_summary = ao3_series_summary[:1930] + "..."
    else:
        ao3_series_summary = ao3_series_summary + \
            '\n\n'+"📚 **Works**:\n"+ao3_series_works_index

    if len(list(ao3_series_summary)) > 2048:  # recheck the size of summary
        ao3_series_summary = ao3_series_summary[:1930] + "..."

    return ao3_series_name, ao3_author_name, ao3_series_summary, ao3_series_status, ao3_series_last_up, ao3_series_length, ao3_series_works
