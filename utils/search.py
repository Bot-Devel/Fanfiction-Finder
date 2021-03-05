import requests
from bs4 import BeautifulSoup
import re


def get_ao3_url(query):
    ao3_list = []
    href = []

    url = 'https://www.google.com/search?q=' + \
        query+"+ao3"

    page = requests.get(url)

    soup = BeautifulSoup(page.content, 'html.parser')
    found = soup.findAll('a')
    for link in found:
        href.append(link['href'])

    if re.search(r"\bseries\b", url) is not None:  # if the query has series
        for i in range(len(href)):
            if re.search(r"\barchiveofourown.org/series/\b", href[i]) is not None:
                ao3_list.append(href[i])

    else:
        for i in range(len(href)):
            if re.search(r"\barchiveofourown.org/works/\b", href[i]) is not None:
                ao3_list.append(href[i])
            if re.search(r"\barchiveofourown.org/chapters/\b", href[i]) is not None:
                ao3_list.append(href[i])
    if not ao3_list:
        return None

    # extract the https url from the the string since it contains /url?q=
    ao3_url = re.search(
        r"https?:\/\/(www/.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b[-a-zA-Z0-9()@:%_\+.~#?&//=]*", ao3_list[0])

    return ao3_url.group(0)


def get_ffn_url(query):
    ffn_list = []
    href = []

    url = 'https://www.google.com/search?q=' + \
        query+"+fanfiction"

    page = requests.get(url)

    soup = BeautifulSoup(page.content, 'html.parser')
    found = soup.findAll('a')

    for link in found:
        href.append(link['href'])

    for i in range(len(href)):
        if re.search(r"fanfiction.net\W", href[i]) is not None:
            ffn_list.append(href[i])

    if not ffn_list:
        return

    ffn_url = re.search(
        r"https?:\/\/(www/.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b[-a-zA-Z0-9()@:%_\+.~#?&//=]*", ffn_list[0])

    return ffn_url.group(0)
