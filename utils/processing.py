from dateutil.relativedelta import relativedelta
from datetime import *
from bs4 import BeautifulSoup
import requests
import re


def ao3_story_chapter_clean(ao3_story_chapters):
    pos_of_slash1 = []
    ao3_chapter = []
    ao3_chapter_list = list(ao3_story_chapters)

    for i in range(len(ao3_chapter_list)):
        if "/" in ao3_chapter_list[i]:
            pos_of_slash1.append(i)

    if pos_of_slash1 is not None:
        for i in range(0, pos_of_slash1[0]):
            ao3_chapter.append(ao3_chapter_list[i])

    ao3_chapter = ''.join(ao3_chapter)
    return ao3_chapter


def story_last_up_clean(story_last_up):
    today = date.today()
    today_date = today.strftime('%Y-%m-%d')
    today_date = tuple(map(int, today_date.split('-')))
    last_updated = tuple(map(int, story_last_up.split('-')))

    diff_in_date = relativedelta(
        date(*today_date), date(*last_updated))

    if diff_in_date.years:
        if diff_in_date.years == 1:
            last_up = str(diff_in_date.years)+" year ago"
        else:
            last_up = str(diff_in_date.years)+" years ago"

    elif diff_in_date.months:
        if diff_in_date.months == 1:
            last_up = str(diff_in_date.months)+" month ago"
        else:
            last_up = str(diff_in_date.months)+" months ago"

    elif diff_in_date.days:
        if diff_in_date.days == 1:
            last_up = str(diff_in_date.days)+" day ago"
        else:
            last_up = str(diff_in_date.days)+" days ago"

    return str(last_up)


def ffn_process_details(ffn_soup):
    details = ffn_soup.find_all('span', {
        'class': 'xgray xcontrast_txt'
    })[0].text.split(' - ')

    ffn_story_status, ffn_story_last_up = get_ffn_story_status(
        ffn_soup, details)

    ffn_story_length = get_ffn_word_cnt(details)
    ffn_story_length = "{:,}".format(int(ffn_story_length))
    ffn_story_chapters = get_ffn_chapters_cnt(details)
    return ffn_story_status, str(ffn_story_last_up), str(ffn_story_length), str(ffn_story_chapters)


def get_ffn_story_status(ffn_soup, details):
    dates = [date for date in ffn_soup.find_all(
        'span') if date.has_attr('data-xutime')]

    cnt = 0
    for i in range(0, len(details)):
        if details[i].startswith('Updated:'):
            cnt = 1
            ffn_story_last_up = str(date.fromtimestamp(
                int(dates[0]['data-xutime'])))

            break  # if found, exit the loop to prevent overwriting of the variable

        else:
            cnt = 2
            ffn_story_last_up = str(date.fromtimestamp(
                int(dates[1]['data-xutime'])))  # Published date

    if cnt == 1:
        return "Updated", ffn_story_last_up
    elif cnt == 2:
        return "Completed", ffn_story_last_up


def get_ffn_word_cnt(details):
    search = [x for x in details if x.startswith("Words:")]
    if len(search) == 0:
        return 0
    return int(search[0][len("Words:"):].replace(',', ''))


def get_ffn_chapters_cnt(details):
    search = [x for x in details if x.startswith("Chapters:")]
    if len(search) == 0:
        return 0
    return int(search[0][len("Chapters:"):].replace(',', ''))


def ao3_convert_chapters_to_works(ao3_url):
    ao3_id_cleaned = []
    pos_of_slash1 = []
    ao3_page = requests.get(ao3_url)
    ao3_soup = BeautifulSoup(ao3_page.content, 'html.parser')

    ao3_id = (ao3_soup.find(
        'li', attrs={'class': 'share'}).find('a', href=True))['href']  # to scrape the /works/ url
    ao3_id = list(ao3_id)

    for i in range(len(ao3_id)):
        if "/" in ao3_id[i]:
            pos_of_slash1.append(i)

    if pos_of_slash1 is not None:
        for i in range(pos_of_slash1[1]+1, pos_of_slash1[2]):
            ao3_id_cleaned.append(ao3_id[i])

    ao3_id_cleaned = ''.join(ao3_id_cleaned)  # got id from the /works/ url
    ao3_url_cleaned = "https://archiveofourown.org/works/" + ao3_id_cleaned
    return ao3_url_cleaned


def get_ao3_series_works_index(ao3_soup):
    ao3_series_works_html = []
    ao3_series_works_index = []

    ao3_series_works_html_h4 = ao3_soup.findAll(
        'h4', attrs={'class': 'heading'})

    for i in ao3_series_works_html_h4:
        ao3_series_works_html.append(i)
    ao3_series_works_html = ""

    for i in ao3_series_works_html_h4:
        ao3_series_works_html += str(i)

    soup_work = BeautifulSoup(ao3_series_works_html, 'html.parser')
    for tag in soup_work.findAll('a', {'href': re.compile('/works/')}):
        ao3_series_works_index.append(
            "["+tag.text+"](https://archiveofourown.org"+tag['href']+")")  # inline html tag for embed

    ao3_series_works_index = '\n'.join(ao3_series_works_index)
    return ao3_series_works_index
