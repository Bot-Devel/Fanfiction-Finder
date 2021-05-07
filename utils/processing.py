from dateutil.relativedelta import relativedelta
from datetime import datetime
from bs4 import BeautifulSoup
import re


def story_last_up_clean(story_last_up, _type):

    curr_time = datetime.now()
    if _type == 1:  # ffn last updated
        datetimeFormat = '%Y-%m-%d %H:%M:%S'
        story_last_up = datetime.strptime(
            story_last_up, datetimeFormat)
        story_last_updated = story_last_up.strftime(r'%-d %b, %Y ')

    elif _type == 2:  # ao3 last updated
        datetimeFormat = '%Y-%m-%d'
        story_last_up = datetime.strptime(
            story_last_up, datetimeFormat)
        story_last_updated = story_last_up.strftime(r'%-d %b, %Y ')

    diff_in_time = relativedelta(curr_time, story_last_up)

    # only amend hours & minutes diff
    if diff_in_time.years:
        pass

    elif diff_in_time.months:
        pass

    elif diff_in_time.days:
        pass

    elif diff_in_time.hours:
        if diff_in_time.hours == 1:
            story_last_updated += "☘︎ " + str(diff_in_time.hours)+" hour ago"
        else:
            story_last_updated += "☘︎ " + str(diff_in_time.hours)+" hours ago"

    elif diff_in_time.minutes:
        if diff_in_time.minutes == 1:
            story_last_updated += "☘︎ " + \
                str(diff_in_time.minutes)+" minute ago"
        else:
            story_last_updated += "☘︎ " + \
                str(diff_in_time.minutes)+" minutes ago"

    return str(story_last_updated)


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

    if re.search(r'\d', str(ffn_story_genre)) is not None:
        ffn_story_genre = None

    if re.search(r'\d', str(ffn_story_characters)) is not None:
        ffn_story_characters = None

    ffn_story_metainfo = ''
    for i in range(0, len(details)):
        if details[i].startswith('Reviews'):
            ffn_story_metainfo += details[i].replace(
                'Reviews:', '**Reviews:**').strip()
            ffn_story_metainfo += " ☘︎ "

        if details[i].startswith('Favs'):
            ffn_story_metainfo += details[i].replace(
                'Favs:', '**Favs:**').strip()
            ffn_story_metainfo += " ☘︎ "

        if details[i].startswith('Follows'):
            ffn_story_metainfo += details[i].replace(
                'Follows:', '**Follows:**').strip()

    ffn_story_length = get_ffn_word_cnt(details)
    ffn_story_length = "{:,}".format(int(ffn_story_length))
    ffn_story_chapters = get_ffn_chapters_cnt(details)

    return ffn_story_status, ffn_story_last_up, ffn_story_length, ffn_story_chapters, ffn_story_rating, ffn_story_genre, ffn_story_characters, ffn_story_metainfo


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
            cnt = 1
            ffn_story_last_up = str(datetime.fromtimestamp(
                int(dates[0]['data-xutime'])))  # Published date

    for i in range(0, len(details)):
        if details[i].startswith('Status: Complete'):
            cnt = 2

    if cnt == 1:
        return "Updated", ffn_story_last_up
    elif cnt == 2:
        return "Complete", ffn_story_last_up


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
