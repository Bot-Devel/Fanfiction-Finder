import requests
import re
from bs4 import BeautifulSoup
from loguru import logger

from utils.processing import story_last_up_clean, get_ao3_series_works_index


URL_VALIDATE = r"(?:(?:https?|ftp)://)(?:\S+(?::\S*)?@)?(?:(?:[1-9]\d?|1\d\d|2[01]\d|22[0-3])(?:\.(?:1?\d{1,2}|2[0-4]\d|25[0-5])){2}(?:\.(?:[1-9]\d?|1\d\d|2[0-4]\d|25[0-4]))|(?:(?:[a-z\u00a1-\uffff0-9]+-?)*[a-z\u00a1-\uffff0-9]+)(?:\.(?:[a-z\u00a1-\uffff0-9]+-?)*[a-z\u00a1-\uffff0-9]+)*(?:\.(?:[a-z\u00a1-\uffff]{2,})))(?::\d{2,5})?(?:/[^\s]*)?"

params = {
    'view_adult': 'true',
    'view_full_work': 'true'
}


class ArchiveOfOurOwn:
    def __init__(self, BaseUrl):
        self.BaseUrl = BaseUrl
        self.session = requests.Session()

    def get_ao3_works_metadata(self):

        if re.search(URL_VALIDATE, self.BaseUrl):

            logger.info(
                f"Processing {self.BaseUrl} ")

            response = self.session.get(self.BaseUrl, params=params)

            logger.debug(f"GET: {response.status_code}: {response.url}")

            ao3_soup = BeautifulSoup(response.content, 'html.parser')

            try:
                self.ao3_works_name = (ao3_soup.find(
                    'h2', attrs={'class': 'title heading'}).contents[0]).strip()

            except AttributeError:
                logger.error(
                    "ao3_works_name is missing. Fanfiction not found")
                self.ao3_works_name = None
                return

            self.ao3_author_name_list = ao3_soup.find(
                'h3', attrs={'class': 'byline heading'}).find_all('a')

            try:
                self.ao3_author_url = ao3_soup.find(
                    'h3', attrs={'class': 'byline heading'}) \
                    .find('a', href=True)['href']
            except Exception:  # anon users
                logger.error("Author URL not found! Anonymous user")
                self.ao3_author_url = "/collections/anonymous"

            try:
                self.ao3_works_summary = ao3_soup.find(
                    'div', attrs={'class': 'summary module'}).find(
                    'blockquote', attrs={'class': 'userstuff'}).text

                self.ao3_works_summary = re.sub(
                    r'\s+', ' ', self.ao3_works_summary)  # removing whitespaces

            except AttributeError:  # if summary not found
                self.ao3_works_summary = ""

            try:
                self.ao3_works_status = (ao3_soup.find(
                    'dl', attrs={'class': 'stats'}).find(
                    'dt', attrs={'class': 'status'}).contents[0]).strip()

                self.ao3_works_status = self.ao3_works_status.replace(":", "")

            except AttributeError:  # if story status not found
                self.ao3_works_status = None

            try:
                self.ao3_works_last_up = (ao3_soup.find(
                    'dl', attrs={'class': 'stats'}).find(
                    'dd', attrs={'class': 'status'}).contents[0]).strip()

            except AttributeError:  # if story last updated not found
                self.ao3_works_last_up = (ao3_soup.find(
                    'dl', attrs={'class': 'stats'}).find(
                    'dd', attrs={'class': 'published'}).contents[0]).strip()

            try:
                self.ao3_works_length = (ao3_soup.find(
                    'dl', attrs={'class': 'stats'}).find(
                    'dd', attrs={'class': 'words'}).contents[0]).strip()

            except IndexError:  # Missing wordcount
                self.ao3_works_length = 0

            self.ao3_works_chapters = (ao3_soup.find(
                'dl', attrs={'class': 'stats'}).find(
                'dd', attrs={'class': 'chapters'}).contents[0]).strip()
            try:
                self.ao3_works_rating = (ao3_soup.find(
                    'dd', attrs={'class': 'rating tags'}).find('a').contents[0]).strip()

            except AttributeError:
                self.ao3_works_rating = None

            try:  # not found in every story
                self.ao3_works_relationships = [
                    a.contents[0].strip()
                    for a in ao3_soup.find(
                        'dd', attrs={'class': 'relationship tags'})
                    .find_all('a')
                ]
                self.ao3_works_relationships = ", ".join(
                    self.ao3_works_relationships)

            except AttributeError:
                self.ao3_works_relationships = None

            try:  # not found in every story
                self.ao3_works_characters = [
                    a.contents[0].strip()
                    for a in ao3_soup.find(
                        'dd', attrs={'class': 'character tags'}).find_all('a')
                ]

                self.ao3_works_characters = ", ".join(
                    self.ao3_works_characters)

            except AttributeError:
                self.ao3_works_characters = None

            self.ao3_works_fandom = (ao3_soup.find(
                'dd', attrs={'class': 'fandom tags'}).find('a').contents[0]).strip()

            try:
                self.ao3_works_kudos = '**Kudos:** '
                self.ao3_works_kudos += (ao3_soup.find(
                    'dl', attrs={'class': 'stats'}).find(
                    'dd', attrs={'class': 'kudos'}).contents[0]).strip()

            except AttributeError:
                self.ao3_works_kudos = '**Kudos:** 0 '

            try:
                self.ao3_works_bookmarks = '**Bookmarks:** '
                self.ao3_works_bookmarks += (ao3_soup.find(
                    'dl', attrs={'class': 'stats'}).find(
                    'dd', attrs={'class': 'bookmarks'}).find('a').contents[0]).strip()

            except AttributeError:
                self.ao3_works_bookmarks = '**Bookmarks:** 0'

            try:
                self.ao3_works_comments = '**Comments:** '
                self.ao3_works_comments += (ao3_soup.find(
                    'dl', attrs={'class': 'stats'}).find(
                    'dd', attrs={'class': 'comments'}).contents[0]).strip()

            except AttributeError:
                self.ao3_works_comments = '**Comments:** 0 '

            try:
                self.ao3_works_hits = '**Hits:** '
                self.ao3_works_hits += (ao3_soup.find(
                    'dl', attrs={'class': 'stats'}).find(
                    'dd', attrs={'class': 'hits'}).contents[0]).strip()

            except AttributeError:
                self.ao3_works_hits = '**Hits:** 0 '

            self.ao3_meta_info = [self.ao3_works_comments, self.ao3_works_kudos,
                                  self.ao3_works_bookmarks, self.ao3_works_hits]

            self.ao3_works_metainfo = ""
            for m in range(len(self.ao3_meta_info)):
                if self.ao3_meta_info[m]:
                    self.ao3_works_metainfo += self.ao3_meta_info[m]
                    if m < len(self.ao3_meta_info)-1:
                        self.ao3_works_metainfo += " ☘︎ "

            self.ao3_works_length = "{:,}".format(int(str(self.ao3_works_length).replace(",","")))
            self.ao3_works_chapters = re.search(
                r"\d+", self.ao3_works_chapters).group(0)
            self.ao3_works_last_up = story_last_up_clean(
                self.ao3_works_last_up, 2)
            self.ao3_author_url = "https://archiveofourown.org" \
                + self.ao3_author_url

            if self.ao3_author_name_list:
                self.ao3_author_name = []
                for author in self.ao3_author_name_list:
                    self.ao3_author_name.append(author.string.strip())
                self.ao3_author_name = ", ".join(self.ao3_author_name)
            else:  # username not found
                self.ao3_author_name = "Anonymous"

            if len(list(self.ao3_works_summary)) > 2048:
                self.ao3_works_summary = self.ao3_works_summary[:2030] + "..."

            # remove everything after &sa from the BaseUrl
            if re.search(r"^(.*?)&", self.BaseUrl) is not None:
                self.BaseUrl = re.search(
                    r"^(.*?)&", self.BaseUrl).group(1)

        else:
            logger.error("BaseUrl is invalid")

    def get_ao3_series_metadata(self):

        if re.search(URL_VALIDATE, self.BaseUrl):

            response = self.session.get(self.BaseUrl, params=params)

            logger.info(
                f"Processing {self.BaseUrl} ")

            logger.debug(f"GET: {response.status_code}: {response.url}")
            ao3_soup = BeautifulSoup(response.content, 'html.parser')

            try:
                self.ao3_series_name = (ao3_soup.find(
                    'div', attrs={'class': 'series-show region'}).find(
                    'h2', attrs={'class': 'heading'}).contents[0]).strip()

            except AttributeError:
                logger.error(
                    "ao3_series_name is missing. Fanfiction not found")
                self.ao3_series_name = None
                return

            self.ao3_author_name_list = ao3_soup.find(
                'dl', attrs={'class': 'series meta group'}) \
                .find('dd').find_all('a')

            try:
                self.ao3_series_summary = ao3_soup.find(
                    'div', attrs={'class': 'series-show region'}).find(
                    'blockquote', attrs={'class': 'userstuff'}).text

            except AttributeError:  # if summary not found
                self.ao3_series_summary = ""

            self.ao3_series_summary = re.sub(
                r'\s+', ' ', self.ao3_series_summary)  # removing whitespaces

            try:
                self.ao3_series_status = (ao3_soup.find(
                    'dl', attrs={'class': 'stats'}).find(
                    'dt', text='Complete:').findNext(
                    'dd')).string.strip()

                if self.ao3_series_status == "No":
                    self.ao3_series_status = "Updated"
                elif self.ao3_series_status == "Yes":
                    self.ao3_series_status = "Complete"

            except AttributeError:  # if story status not found
                self.ao3_series_status = None

            try:
                self.ao3_series_last_up = ao3_soup.find(
                    'div', attrs={'class': 'series-show region'}).find(
                    'dt', text='Series Updated:').findNext(
                    'dd').string.strip()

            except AttributeError:  # if story last updated not found
                self.ao3_series_last_up = ao3_soup.find(
                    'div', attrs={'class': 'series-show region'}).find(
                    'dt', text='Series Begun:').findNext(
                    'dd').string.strip()

            try:
                self.ao3_series_length = ao3_soup.find(
                    'dt', text='Words:').findNext(
                    'dd').string.strip()
            except IndexError:  # Missing wordcount
                self.ao3_series_length = 0

            self.ao3_series_works = ao3_soup.find(
                'dt', text='Works:').findNext(
                'dd').string.strip()

            self.ao3_series_works_index = get_ao3_series_works_index(ao3_soup)
            self.ao3_series_last_up = story_last_up_clean(
                self.ao3_series_last_up, 2)

            for author in self.ao3_author_name_list:
                self.ao3_author_url = author['href']
                break  # To only get the 1st author url

            self.ao3_author_url = "https://archiveofourown.org" \
                + self.ao3_author_url

            self.ao3_author_name = []
            for author in self.ao3_author_name_list:
                self.ao3_author_name.append(author.string.strip())
            self.ao3_author_name = ", ".join(self.ao3_author_name)

            if len(list(self.ao3_series_summary)) > 2048:
                self.ao3_series_summary = self.ao3_series_summary[:1930] \
                    + "..."
            else:
                self.ao3_series_summary = self.ao3_series_summary + \
                    '\n\n' + "📚 **Works**:\n" + self.ao3_series_works_index

            if len(list(self.ao3_series_summary)) > 2048:  # recheck the size of summary
                self.ao3_series_summary = self.ao3_series_summary[:1930]

                # if the line doesnt end with ")", remove the whole line.
                # this prevents brokens links to ao3 works
                self.ao3_series_summary_lines = self.ao3_series_summary.splitlines()
                if not self.ao3_series_summary_lines[-1].endswith(")"):
                    self.ao3_series_summary_lines.pop(-1)

                self.ao3_series_summary = "\n".join(
                    self.ao3_series_summary_lines)

            # remove everything after &sa from the BaseUrl
            if re.search(r"^(.*?)&", self.BaseUrl) is not None:
                self.BaseUrl = re.search(
                    r"^(.*?)&", self.BaseUrl).group(1)

        else:
            logger.error("BaseUrl is invalid")

    def get_author_profile_image(self):

        author_profile_url = f"https://archiveofourown.org/users/{self.ao3_author_name}/profile"
        response = self.session.get(author_profile_url)

        logger.debug(f"GET: {response.status_code}: {author_profile_url}")
        profile_soup = BeautifulSoup(response.content, 'html.parser')

        try:
            self.ao3_author_img = (profile_soup.find(
                'p', attrs={'class': 'icon'}).find('img'))['src']

        except AttributeError:
            logger.error(
                "ao3_author_img is missing.")
            self.ao3_author_img = None

        try:
            # if author image not found
            if not self.ao3_author_img.startswith("http"):
                self.ao3_author_img = None

        except AttributeError:  # if None
            pass
