import re

import requests
from bs4 import BeautifulSoup
from loguru import logger

from config import FICHUB_SITES


URL_VALIDATE = r"(?:(?:https?|ftp)://)(?:\S+(?::\S*)?@)?(?:(?:[1-9]\d?|1\d\d|2[01]\d|22[0-3])(?:\.(?:1?\d{1,2}|2[0-4]\d|25[0-5])){2}(?:\.(?:[1-9]\d?|1\d\d|2[0-4]\d|25[0-4]))|(?:(?:[a-z\u00a1-\uffff0-9]+-?)*[a-z\u00a1-\uffff0-9]+)(?:\.(?:[a-z\u00a1-\uffff0-9]+-?)*[a-z\u00a1-\uffff0-9]+)*(?:\.(?:[a-z\u00a1-\uffff]{2,})))(?::\d{2,5})?(?:/[^\s]*)?"
search_engines = ['google', 'bing']


def get_ao3_url(query: str):
    ao3_list = []
    href = []

    for engine in search_engines:
        url = f'https://www.{engine}.com/search?q={query}+ao3'

        page = requests.get(url)
        logger.debug(f"GET: {page.status_code}: {url}")

        if page.status_code == 200:
            soup = BeautifulSoup(page.content, 'html.parser')
            found = soup.findAll('a')
            for link in found:
                href.append(link['href'])

            if re.search(r"\bseries\b", url):  # if the query has series
                for i in range(len(href)):
                    if (
                        re.search(r"\barchiveofourown.org/series/\b", href[i])
                        is not None
                    ):
                        logger.info(f"URL FOUND: {href[i]}")
                        ao3_list.append(href[i])

            else:  # if query is unspecified
                for i in range(len(href)):
                    # append /works/ first
                    if (
                        re.search(r"\barchiveofourown.org/works/\b", href[i])
                        is not None
                    ):
                        logger.info(f"URL FOUND: {href[i]}")
                        ao3_list.append(href[i])

                    # append /chapters/ next
                    # if re.search(r"\barchiveofourown.org/chapters/\b", href[i]) is not None:
                    #     logger.info(f"URL FOUND: {href[i]}")
                    #     ao3_list.append(href[i])

                    # append /series/ next
                    if (
                        re.search(r"\barchiveofourown.org/series/\b", href[i])
                        is not None
                    ):
                        logger.info(f"URL FOUND: {href[i]}")
                        ao3_list.append(href[i])

            if not ao3_list:
                logger.error(f"URL NOT FOUND using {engine}")
                continue
            else:
                break
        else:
            continue

    # extract the https url from the the string since it contains /url?q=
    ao3_url = re.search(URL_VALIDATE, ao3_list[0])

    return ao3_url.group(0)


def get_ffn_url(query: str):
    ffn_list = []
    href = []
    try:
        for engine in search_engines:
            url = f'https://www.{engine}.com/search?q={query}+fanfiction'
            page = requests.get(url)
            logger.debug(f"GET: {page.status_code}: {url}")

            if page.status_code == 200:
                soup = BeautifulSoup(page.content, 'html.parser')
                found = soup.findAll('a')

                for link in found:
                    href.append(link['href'])

                for i in range(len(href)):
                    if re.search(r"fanfiction.net/s/", href[i]) is not None:
                        logger.info(f"URL FOUND: {href[i]}")
                        ffn_list.append(href[i])
                if not ffn_list:
                    logger.error(f"URL NOT FOUND using {engine}")
                    continue
                else:
                    break
            else:
                continue
    except Exception:
        pass

    if ffn_list:
        ffn_url = re.search(URL_VALIDATE, ffn_list[0])
        return ffn_url.group(0)
    else:
        return None


def get_fic_url(query: str):
    fic_list = []
    href = []
    try:
        for engine in search_engines:
            url = f'https://www.{engine}.com/search?q={query}+fanfiction'
            page = requests.get(url)
            logger.debug(f"GET: {page.status_code}: {url}")

            if page.status_code == 200:
                soup = BeautifulSoup(page.content, 'html.parser')
                found = soup.findAll('a')

                for link in found:
                    href.append(link['href'])
                print(href)
                for i in range(len(href)):
                    logger.info(f"URL FOUND: {href[i]}")
                    fic_list.append(href[i])
                if not fic_list:
                    logger.error(f"URL NOT FOUND using {engine}")
                    continue
                else:
                    break
            else:
                continue
    except Exception:
        pass

    if fic_list:
        # Check if any of the found URLs match the FICHUB_SITES list
        for url in fic_list:
            if any(site.strip() in url.strip() for site in FICHUB_SITES):
                fic_list = re.search(URL_VALIDATE, url)
                return fic_list.group(0)
    else:
        return None
