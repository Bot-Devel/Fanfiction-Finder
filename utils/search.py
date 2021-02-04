import requests
from bs4 import BeautifulSoup
import re

def get_fic_id(query):
    ao3_list = []
    pos_of_slash1 = []
    ao3_id_list1 = []
    pos_of_qmark = None
    url = 'https://www.google.com/search?q=' + \
        query+"+ao3"
    page = requests.get(url) 
    soup = BeautifulSoup(page.content, 'html.parser')
    found = soup.findAll('a')
    hrefs = []
    for link in found:
        hrefs.append(link['href'])
    for i in range(len(hrefs)):
        if re.search(r"\barchiveofourown.org/works\W", hrefs[i]) is not None:
            ao3_list.append(hrefs[i])
    for i in range(len(hrefs)):
        if re.search(r"\barchiveofourown.org/chapters\W", hrefs[i]) is not None:
            ao3_list.append(hrefs[i])
    if not ao3_list:
        return None
    ao3_url = re.search(
        r"https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)", ao3_list[0])
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
    else: # extract the story id by appending the characters between 2nd and 3rd /
        for i in range(pos_of_slash1[1]+1, pos_of_slash1[2]):
            ao3_id_list1.append(ao3_list_clean[i])
    ao3_id = ''.join(ao3_id_list1)
    return ao3_id
