import dataframe_obtainer
from dataframe_obtainer import file_processor_html
import requests
from bs4 import BeautifulSoup
import pandas as pd

# this code gets all link to laws by pagination
def links_of_laws():
    big_url = 'http://kenesh.kg/ky/article/list/11'
    # 'http://kenesh.kg/ru/article/list/11?page=2'
    all_links = []
    r = requests.get('http://kenesh.kg/ru/article/list/11')
    soup = BeautifulSoup(r.text, "lxml")
    for link in [item.get("href") for item in soup.find_all("a", class_="news__item__title__link")]:
        all_links.append("http://kenesh.kg" + link)
    page_number = 2
    while page_number < 8:
        r = requests.get('http://kenesh.kg/ru/article/list/11?page=' + str(page_number))
        page_number += 1
        soup = BeautifulSoup(r.text, "lxml")
        for link in [item.get("href") for item in soup.find_all("a", class_="news__item__title__link")]:
            all_links.append("http://kenesh.kg" + link)
    dataframe = pd.DataFrame(all_links, columns=['page_links'])
    dataframe.to_csv('../pages/csv/links_to_laws_7th_JK.csv')
    return dataframe

