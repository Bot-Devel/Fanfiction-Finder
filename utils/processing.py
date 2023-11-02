from __future__ import annotations

from datetime import datetime

import re

from bs4 import BeautifulSoup


def story_last_up_clean(story_last_up, _type):
    curr_time = datetime.now()
    if _type == 1:  # ffn last updated
        datetimeFormat = '%Y-%m-%d %H:%M:%S'
        story_last_up = datetime.strptime(str(story_last_up), datetimeFormat)
        story_last_updated = story_last_up.strftime(r'%d %b, %Y').lstrip('0')

    elif _type == 2:  # ao3 last updated
        datetimeFormat = '%Y-%m-%d'
        story_last_up = datetime.strptime(str(story_last_up), datetimeFormat)
        story_last_updated = story_last_up.strftime(r'%d %b, %Y').lstrip('0')

    diff_in_time = curr_time - story_last_up

    # only amend hours & minutes diff
    if diff_in_time.days:
        pass
    elif hours := (diff_in_time.seconds // 3600):
        if hours == 1:
            story_last_updated += f"☘︎ {hours} hour ago"
        else:
            story_last_updated += f"☘︎ {hours} hours ago"

    elif minutes := (diff_in_time.seconds // 60):
        if minutes == 1:
            story_last_updated += f"☘︎ {minutes} minute ago"
        else:
            story_last_updated += f"☘︎ {minutes} minutes ago"

    return str(story_last_updated)


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

def timestamp_unix_to_local(unix_time):
    utc_time = datetime.utcfromtimestamp(int(unix_time))
    return utc_time.strftime(r'%d %b, %Y').lstrip('0')

