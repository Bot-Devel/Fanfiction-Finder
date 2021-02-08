import requests
from bs4 import BeautifulSoup
import re


def get_ao3_id(query):
    ao3_list = []
    pos_of_slash1 = []
    ao3_id_list1 = []
    hrefs = []
    pos_of_qmark = None

    url = 'https://www.google.com/search?q=' + \
        query+"+ao3"
    try:
        page = requests.get(url)
    except Exception:
        ao3_id = 1
        return ao3_id

    soup = BeautifulSoup(page.content, 'html.parser')
    found = soup.findAll('a')
    for link in found:
        hrefs.append(link['href'])

    if re.search(r"\bseries\b", url) is not None:  # if the query has series
        for i in range(len(hrefs)):
            if re.search(r"\barchiveofourown.org/series/\b", hrefs[i]) is not None:
                ao3_list.append(hrefs[i])

    else:
        for i in range(len(hrefs)):
            if re.search(r"\barchiveofourown.org/works/\b", hrefs[i]) is not None:
                ao3_list.append(hrefs[i])
            if re.search(r"\barchiveofourown.org/chapters/\b", hrefs[i]) is not None:
                ao3_list.append(hrefs[i])
    if not ao3_list:
        return None

    # extract the https url from the the string since it contains /url?q=
    ao3_url = re.search(
        r"https?:\/\/(www/.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b[-a-zA-Z0-9()@:%_\+.~#?&//=]*", ao3_list[0])

    if re.search(r"archiveofourown.org/series/\b", ao3_url.group(0)) is None:  # if not an ao3 series
        ao3_page = requests.get(ao3_url.group(0))
        ao3_soup = BeautifulSoup(ao3_page.content, 'html.parser')

        ao3_list_clean = (ao3_soup.find(
            'li', attrs={'class': 'share'}).find('a', href=True))['href']

        for i in range(len(ao3_list_clean)):
            if "/" in ao3_list_clean[i]:
                pos_of_slash1.append(i)

        for i in range(len(ao3_list_clean)):
            if "?" in ao3_list_clean[i]:
                pos_of_qmark = i

        if pos_of_qmark is not None:
            # if ? is found in the ao3 url, extract the story id by appending the characters between 2nd / and ?
            for i in range(pos_of_slash1[1]+1, pos_of_qmark):
                ao3_id_list1.append(ao3_list_clean[i])

        else:  # extract the story id by appending the characters between 2nd and 3rd /
            for i in range(pos_of_slash1[1]+1, pos_of_slash1[2]):
                ao3_id_list1.append(ao3_list_clean[i])
        ao3_id = ''.join(ao3_id_list1)

    else:
        # if its an ao3 series, the url can be used directly in ao3_metadata_series()
        ao3_id = ao3_url.group(0)
    return ao3_id


def get_ffn_id(query):
    ffn_list = []
    pos_of_slash1 = []
    ffn_id_list1 = []
    hrefs = []

    url = 'https://www.google.com/search?q=' + \
        query+"+fanfiction"

    try:
        page = requests.get(url)
    except Exception:
        ffn_id = 1
    soup = BeautifulSoup(page.content, 'html.parser')
    found = soup.findAll('a')

    for link in found:
        hrefs.append(link['href'])

    for i in range(len(hrefs)):
        if re.search(r"fanfiction.net\W", hrefs[i]) is not None:
            ffn_list.append(hrefs[i])

    if not ffn_list:
        return

    ffn_url = re.search(
        r"https?:\/\/(www/.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b[-a-zA-Z0-9()@:%_\+.~#?&//=]*", ffn_list[0])
    ffn_list_clean = list(ffn_url.group(0))

    for i in range(len(ffn_list_clean)):
        if "/" in ffn_list_clean[i]:
            pos_of_slash1.append(i)

    for i in range(pos_of_slash1[3]+1, pos_of_slash1[4]):
        ffn_id_list1.append(ffn_list_clean[i])

    ffn_id = ''.join(ffn_id_list1)
    return ffn_id
