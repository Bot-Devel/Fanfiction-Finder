import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import traceback
import time
from loguru import logger

headers = {
    'User-Agent': 'Fanfiction-Finder-Bot/RogueOne'
}

retry_strategy = Retry(
    total=3,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504]
)


class FicHub:
    def __init__(self):
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.http = requests.Session()
        self.http.mount("https://", adapter)
        self.http.mount("http://", adapter)

    def get_fic_metadata(self, url: str):
        """
        Sends GET request to Fichub API to fetch the metadata
        """
        params = {'q': url}

        for _ in range(2):
            try:
                response = self.http.get(
                    "https://fichub.net/api/v0/epub", params=params,
                    allow_redirects=True, headers=headers, timeout=(6.1, 300)
                )
                logger.debug(
                        f"GET: {response.status_code}: {response.url}")

                break
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
                logger.error(str(traceback.format_exc()))

        try:
            self.response = response.json()
            self.file_format = []
            self.cache_hash = {}
            cache_urls = {}
            for format in range(4):
                if format == 0:
                    cache_urls['epub'] = self.response['urls']['epub']
                    self.cache_hash['epub'] = self.response['hashes']['epub']
                    self.file_format.append(".epub")

                elif format == 1:
                    cache_urls['mobi'] = self.response['urls']['mobi']
                    self.cache_hash['mobi'] = self.response['hashes']['epub']
                    self.file_format.append(".mobi")

                elif format == 2:
                    cache_urls['pdf'] = self.response['urls']['pdf']
                    self.cache_hash['pdf'] = self.response['hashes']['epub']
                    self.file_format.append(".pdf")

                elif format == 3:
                    cache_urls['zip'] = self.response['urls']['html']
                    self.cache_hash['zip'] = self.response['hashes']['epub']
                    self.file_format.append(".zip")

            self.files = {}
            for file_format in self.file_format:
                self.files[self.response['urls']['epub'].split(
                    "/")[4].split("?")[0].replace(".epub", file_format)] = {
                    "hash": self.cache_hash[file_format.replace(".", "")],
                    "download_url": "https://fichub.net" + cache_urls[file_format.replace(".", "")]
                }
        # Error: 'epub_url'
        # Reason: Unsupported URL
        except (KeyError, UnboundLocalError) as e:
            print("str(e)",str(e))
            logger.error(f"Error: {str(e)} not found!")
            logger.error(f"GET:Response: {str(self.response)}")
            logger.error(
                f"Skipping unsupported URL: {url}")

            self.exit_status = 1

    def get_fic_data(self, download_url: str):
        """
        Sends GET request to Fichub API to fetch the cache for the ebook
        """

        params = {}

        for _ in range(2):
            try:
                self.response_data = self.http.get(
                    download_url, allow_redirects=True, headers=headers,
                    params=params, timeout=(6.1, 300))
                logger.debug(
                        f"GET: {self.response_data.status_code}: {self.response_data.url}")
                break
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
                logger.error(str(traceback.format_exc()))
                time.sleep(3)
