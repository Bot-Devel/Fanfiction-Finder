from dateutil.relativedelta import relativedelta
from datetime import datetime
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


def story_last_up_clean(story_last_up, _type):

    curr_time = datetime.now()

    if _type == 1:  # ffn & ao3 works
        datetimeFormat = '%Y-%m-%d %H:%M:%S'
    elif _type == 2:  # ao3 series
        datetimeFormat = '%Y-%m-%d'

    story_last_up = datetime.strptime(story_last_up, datetimeFormat)

    diff_in_time = relativedelta(curr_time, story_last_up)

    if diff_in_time.years:

        if diff_in_time.years == 1:
            last_up = str(diff_in_time.years)+" year ago"
        else:
            last_up = str(diff_in_time.years)+" years ago"

    elif diff_in_time.months:

        if diff_in_time.months == 1:
            last_up = str(diff_in_time.months)+" month ago"
        else:
            last_up = str(diff_in_time.months)+" months ago"

    elif diff_in_time.days:
        if diff_in_time.days == 1:
            last_up = str(diff_in_time.days)+" day ago"
        else:
            last_up = str(diff_in_time.days)+" days ago"

    elif diff_in_time.hours:
        if diff_in_time.hours == 1:
            last_up = str(diff_in_time.hours)+" hour ago"
        else:
            last_up = str(diff_in_time.hours)+" hours ago"

    elif diff_in_time.minutes:
        if diff_in_time.minutes == 1:
            last_up = str(diff_in_time.minutes)+" minute ago"
        else:
            last_up = str(diff_in_time.minutes)+" minutes ago"

    return str(last_up)


def ffn_process_details(ffn_soup):
    details = ffn_soup.find_all('span', {
        'class': 'xgray xcontrast_txt'
    })[0].text.split(' - ')

    ffn_story_status, ffn_story_last_up = get_ffn_story_status(
        ffn_soup, details)

    for i in range(0, len(details)):
        if details[i].startswith('Rated:'):

            ffn_story_rating = details[i].replace('Rated:', '').strip()

            break  # if found, exit the loop to prevent overwriting of the variable

        else:
            ffn_story_rating = None

    ffn_story_genre = details[2]
    ffn_story_characters = details[3]

    if re.search(r'\d', str(ffn_story_characters)) is not None:
        ffn_story_characters = None

    ffn_story_length = get_ffn_word_cnt(details)
    ffn_story_length = "{:,}".format(int(ffn_story_length))
    ffn_story_chapters = get_ffn_chapters_cnt(details)

    return ffn_story_status, ffn_story_last_up, ffn_story_length, ffn_story_chapters, ffn_story_rating, ffn_story_genre, ffn_story_characters


def get_ffn_story_status(ffn_soup, details):
    dates = [date for date in ffn_soup.find_all(
        'span') if date.has_attr('data-xutime')]

    cnt = 0
    for i in range(0, len(details)):
        if details[i].startswith('Updated:'):
            cnt = 1
            ffn_story_last_up = str(datetime.fromtimestamp(
                int(dates[0]['data-xutime'])))

            break  # if found, exit the loop to prevent overwriting of the variable

        elif details[i].startswith('Published:'):
            cnt = 2
            ffn_story_last_up = str(datetime.fromtimestamp(
                int(dates[0]['data-xutime'])))  # Published date

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
        return 1  # 1 as the default chapter number
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


def get_ffn_footer(ffn_story_characters, ffn_story_genre, ffn_story_rating):

    if all(v is not None for v in [
            ffn_story_characters,
            ffn_story_genre, ffn_story_rating]):

        footer = str(ffn_story_rating)+" | " + \
            str(ffn_story_genre)+" | "+str(ffn_story_characters)

    elif all(v is not None for v in [
            ffn_story_characters,
            ffn_story_genre]):
        footer = str(ffn_story_genre)+" | "+str(ffn_story_characters)

    elif all(v is not None for v in [
            ffn_story_characters,
            ffn_story_rating]):
        footer = str(ffn_story_rating)+" | "+str(ffn_story_characters)

    elif all(v is not None for v in [
            ffn_story_genre,
            ffn_story_rating]):
        footer = str(ffn_story_rating)+" | "+str(ffn_story_genre)

    elif all(v is not None for v in [
            ffn_story_characters]):
        footer = str(ffn_story_characters)

    elif all(v is not None for v in [
            ffn_story_rating]):
        footer = str(ffn_story_rating)

    elif all(v is not None for v in [
            ffn_story_genre]):
        footer = str(ffn_story_genre)

    if len(list(footer)) > 100:
        footer = footer[:100]

    return footer
