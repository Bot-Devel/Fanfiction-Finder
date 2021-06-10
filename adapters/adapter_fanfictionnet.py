import re
from datetime import datetime
from bs4 import BeautifulSoup
import cloudscraper

from utils.processing import story_last_up_clean

URL_VALIDATE = r"(?:(?:https?|ftp)://)(?:\S+(?::\S*)?@)?(?:(?:[1-9]\d?|1\d\d|2[01]\d|22[0-3])(?:\.(?:1?\d{1,2}|2[0-4]\d|25[0-5])){2}(?:\.(?:[1-9]\d?|1\d\d|2[0-4]\d|25[0-4]))|(?:(?:[a-z\u00a1-\uffff0-9]+-?)*[a-z\u00a1-\uffff0-9]+)(?:\.(?:[a-z\u00a1-\uffff0-9]+-?)*[a-z\u00a1-\uffff0-9]+)*(?:\.(?:[a-z\u00a1-\uffff]{2,})))(?::\d{2,5})?(?:/[^\s]*)?"


class FanFictionNet:
    def __init__(self, BaseUrl, log):
        self.BaseUrl = BaseUrl
        self.log = log

    def get_ffn_story_metadata(self):

        if re.search(URL_VALIDATE, self.BaseUrl):

            self.log.info(
                f"Processing {self.BaseUrl} ")

            self.scraper = cloudscraper.CloudScraper(
                delay=2, browser={
                    'browser': 'chrome',
                    'platform': 'windows',
                    'mobile': False,
                    'desktop': True,
                }
            )

            response = self.scraper.get(self.BaseUrl)
            # response = self.session.get(
            #     f"https://cloudscraper-proxy.roguedev1.repl.co/v1?q={self.BaseUrl}")

            self.log.info(f"GET: {response.status_code}: {self.BaseUrl}")

            ffn_soup = BeautifulSoup(response.content, 'html.parser')

            try:
                self.ffn_story_name = ffn_soup.find_all('b', 'xcontrast_txt')[
                    0].string.strip()

            except IndexError:  # Story Not Found
                self.log.error(
                    "ffn_story_name is missing. Fanfiction not found")
                self.ffn_story_name = None
                return

            self.ffn_story_id = (re.search(r"\d+", self.BaseUrl)).group(0)

            self.ffn_author_name = ffn_soup.find_all(
                'a', {'href': re.compile(r'^/u/\d+/.')})[0].string.strip()

            self.ffn_author_url = (ffn_soup.find(
                'div', attrs={'id': 'profile_top'}).find('a', href=True))['href']

            self.ffn_author_id = (
                re.search(r"\d+", self.ffn_author_url)).group(0)

            try:
                self.ffn_story_summary = ffn_soup.find_all('div', {
                    'style': 'margin-top:2px',
                    'class': 'xcontrast_txt'})[0].string.strip()

            except IndexError:  # Missing summary
                self.log.error("ffn_story_summary is missing.")
                self.ffn_story_summary = ""

            self.ffn_story_fandom = ffn_soup.find(
                'span', attrs={'class': 'lc-left'}).find(
                'a', attrs={'class': 'xcontrast_txt'}).text

            self.has_img = False
            try:
                self.has_img = True
                self.ffn_story_image = (ffn_soup.find(
                    'div', attrs={'id': 'profile_top'}).find(
                    'img', attrs={'class': 'cimage'}))['src']

            except TypeError:
                self.has_img = False

            # if the fandom isnt crossover, then go to the next <a>
            if not re.search(r"\bcrossover\b", self.ffn_story_fandom, re.IGNORECASE):
                self.ffn_story_fandom = ffn_soup.find(
                    'span', attrs={'class': 'lc-left'}).find(
                    'a', attrs={'class': 'xcontrast_txt'}).findNext('a').text

            self.details = ffn_soup.find_all(
                'span', {'class': 'xgray xcontrast_txt'}
            )[0].text.split(' - ')

            self.dates = [date for date in ffn_soup.find_all(
                'span') if date.has_attr('data-xutime')]

            for i in range(0, len(self.details)):

                if self.details[i].startswith('Updated:'):

                    self.ffn_story_status = "Updated"

                    self.ffn_story_last_updated = datetime.fromtimestamp(
                        int(self.dates[0]['data-xutime']))

                    self.ffn_story_published = datetime.fromtimestamp(
                        int(self.dates[1]['data-xutime']))  # Published date

                    # change formatting
                    self.ffn_story_published = datetime.strptime(
                        str(self.ffn_story_published), '%Y-%m-%d %H:%M:%S')

                    self.ffn_story_published = self.ffn_story_published.strftime(
                        r'%-d %b, %Y ')

                    break  # if found, exit the loop to prevent overwriting of the variable

                elif self.details[i].startswith('Published:'):

                    self.ffn_story_status = "Complete"

                    # if Updated not found, pub & last_up will be same
                    self.ffn_story_last_updated = str(datetime.fromtimestamp(
                        int(self.dates[0]['data-xutime'])))  # Published date

                    self.ffn_story_published = str(datetime.fromtimestamp(
                        int(self.dates[0]['data-xutime'])))  # Published dat

                    # change formatting
                    self.ffn_story_published = datetime.strptime(
                        str(self.ffn_story_published), '%Y-%m-%d %H:%M:%S')

                    self.ffn_story_published = self.ffn_story_published.strftime(
                        r'%-d %b, %Y ')

            for i in range(0, len(self.details)):

                if self.details[i].startswith('Reviews:'):

                    self.ffn_story_reviews = self.details[i].replace(
                        'Reviews:', '').strip()

                    break  # if found, exit the loop to prevent overwriting of the variable

                else:
                    self.ffn_story_reviews = 'Not found'

            for i in range(0, len(self.details)):
                if self.details[i].startswith('Favs:'):

                    self.ffn_story_favs = self.details[i].replace(
                        'Favs:', '').strip()

                    break  # if found, exit the loop to prevent overwriting of the variable

                else:
                    self.ffn_story_favs = 'Not found'

            for i in range(0, len(self.details)):
                if self.details[i].startswith('Follows:'):

                    self.ffn_story_follows = self.details[i].replace(
                        'Follows:', '').strip()

                    break  # if found, exit the loop to prevent overwriting of the variable

                else:
                    self.ffn_story_follows = 'Not found'

            for i in range(0, len(self.details)):
                if self.details[i].startswith('Rated:'):

                    self.ffn_story_rating = self.details[i].replace(
                        'Rated:', '').strip()

                    break  # if found, exit the loop to prevent overwriting of the variable

                else:
                    self.ffn_story_rating = 'Not found'

            self.ffn_story_lang = self.details[1]
            self.ffn_story_genre = self.details[2]
            self.ffn_story_characters = self.details[3]

            if re.search(r'\d', str(self.ffn_story_genre)) is not None:
                self.ffn_story_genre = None

            if re.search(r'\d', str(self.ffn_story_characters)):
                self.ffn_story_characters = None

            self.ffn_story_metainfo = ''
            for i in range(0, len(self.details)):
                if self.details[i].startswith('Reviews'):
                    self.ffn_story_metainfo += self.details[i].replace(
                        'Reviews:', '**Reviews:**').strip()
                    self.ffn_story_metainfo += " ☘︎ "

                if self.details[i].startswith('Favs'):
                    self.ffn_story_metainfo += self.details[i].replace(
                        'Favs:', '**Favs:**').strip()
                    self.ffn_story_metainfo += " ☘︎ "

                if self.details[i].startswith('Follows'):
                    self.ffn_story_metainfo += self.details[i].replace(
                        'Follows:', '**Follows:**').strip()

            search = [x for x in self.details if x.startswith("Words:")]
            if len(search) == 0:
                self.ffn_story_length = 0
            else:
                self.ffn_story_length = int(
                    search[0][len("Words:"):].replace(',', ''))

                self.ffn_story_length = "{:,}".format(
                    int(self.ffn_story_length))

            search = [x for x in self.details if x.startswith("Chapters:")]
            if len(search) == 0:
                self.ffn_story_chapters = 1  # 1 as the default chapter number
            else:
                self.ffn_story_chapters = str(
                    int(search[0][len("Chapters:"):].replace(',', ''))).strip()

            self.ffn_author_url = "https://www.fanfiction.net" + self.ffn_author_url

            self.ffn_story_last_updated = story_last_up_clean(
                self.ffn_story_last_updated, 1)

            # remove everything after &sa from the BaseUrl
            if re.search(r"^(.*?)&", self.BaseUrl) is not None:
                self.BaseUrl = re.search(
                    r"^(.*?)&", self.BaseUrl).group(1)

        else:
            self.log.error("BaseUrl is invalid")
