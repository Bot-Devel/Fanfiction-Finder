from dateutil.relativedelta import relativedelta
from datetime import *


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


def ao3_story_last_up_clean(ao3_story_last_up):
    today = date.today()
    today_date = today.strftime('%Y-%m-%d')
    today_date = tuple(map(int, today_date.split('-')))
    last_updated = tuple(map(int, ao3_story_last_up.split('-')))
    diff_in_date = relativedelta(
        date(*today_date), date(*last_updated))
    if not diff_in_date.years:
        last_up = "Recently"
        return last_up
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
            last_up = str(diff_in_date.months)+" day ago"
        else:
            last_up = str(diff_in_date.days)+" days ago"

    return last_up
