from bs4 import BeautifulSoup
import bs4
import re
import pandas as pd
from os import walk
import requests
import tempfile
import csv
import tabula.io as tb


# ************************************************************************************
def corrector2(item):
    ems = []
    for em in [item.find_all("em")]:
        ems.append((' '.join([e.get_text().strip() for e in em])))
    bth = [[z.replace('(', '') for z in x if z != ''] for x in [y.split(')') for y in ems]][0]
    bag = ['вносится на нулевое чтение',
           'инициатор – нет, вх. № 0 от 00.00.0000',
           'Комитет нет']
    if len(bth) == 0:
        bth = bag
    if len(bth) == 1:
        if "инициатор" in bth[0]:
            bth.append(bth[0])
            bth[0] = bag[0]
            bth.append(bag[2])
        elif "чтение" in bth[0]:
            bth.append(bag[1])
            bth.append(bag[2])
        else:
            bth.append(bag[1])
            bth.append(bth[0])
            bth[0] = bag[0]
    if len(bth) == 2:
        if "чтение" in bth[0]:
            if "инициатор" in bth[1]:
                bth.append(bag[2])
            else:
                bth.append(bth[1])
                bth[1] = bag[2]
        elif "инициатор" in bth[0]:
            bth.append(bth[1])
            bth[1] = bth[0]
            bth[0] = bag[0]
    return bth


def corrector(item):
    ems = []
    for em in [em.find('em') for em in item.find_all("strong") if em.find('em') is not None]:
        ems.append(em.string)

    bth = [sent.replace('(', '') for sent in
           ''.join(filter(lambda x: x if x is not None else '', [em for em in ems])).split(')') if sent != '']
    bag = ['вносится на нулевое чтение',
           'инициатор – нет, вх. № 0 от 00.00.0000',
           'Комитет нет']
    if len(bth) == 0:
        bth = bag
    if len(bth) == 1:
        if "инициатор" in bth[0]:
            bth.append(bth[0])
            bth[0] = bag[0]
            bth.append(bag[2])
        elif "чтение" in bth[0]:
            bth.append(bag[1])
            bth.append(bag[2])
        else:
            bth.append(bag[1])
            bth.append(bth[0])
            bth[0] = bag[0]
    if len(bth) == 2:
        if "чтение" in bth[0]:
            if "инициатор" in bth[1]:
                bth.append(bag[2])
            else:
                bth.append(bth[1])
                bth[1] = bag[2]
        elif "инициатор" in bth[0]:
            bth.append(bth[1])
            bth[1] = bth[0]
            bth[0] = bag[0]
    return bth


# ************************************************************************************
def divider_law(for_df):
    for item in for_df:
        a = item[0].split('«')
        size_of_item = len(a)
        if size_of_item == 3:
            item[0] = a[2].replace('»', '').strip()
            item.append(a[1].strip())
            item.append(a[0].strip())
            break
        elif size_of_item == 2:
            item[0] = a[1].replace('»', '').strip()
            item.append(a[0].strip())
            item.append("Empty")
            break
        else:
            break
# ************************************************************************************
def divider_law2(text):
    arr = ['','','']
    a = text.split('«')
    size_of_item = len(a)
    if size_of_item == 3:
        arr[0] = a[2].replace('»', '').strip()
        arr[1] = a[1].strip()
        arr[2] =  a[0].strip()
    elif size_of_item == 2:
        arr[0] = a[1].replace('»', '').strip()
        arr[1] = a[0].strip()
        arr[2] =  "Empty"
    elif size_of_item == 1:
        arr[0] = a[0].strip()
        arr[1] = "Empty"
        arr[2] = "Empty"
    elif size_of_item > 3:
        arr[0] = ''.join([x for x in a[2:]]).strip()
        arr[1] = a[0].strip()
        arr[2] = a[1].strip()
    return arr
# ************************************************************************************
def pure_law(item):
    law = []
    for content in item.contents:
        if type(content) == bs4.element.NavigableString:
            law.append(re.sub(r"\n", "", content))
        if content.name == 'em':
            if content.find('strong') is None:
                law.append(content.text)
    return ''.join([x for x in law if x != ' '])


# ************************************************************************************
# processes file
def file_proccessor(html):
    with open(html) as file:
        src = file.read()
    for_df = []
    soup = BeautifulSoup(src, "lxml")
    page_all_a = soup.find_all("a")
    for item in page_all_a:
        row = []
        row.append(pure_law(item))
        [row.append(x) for x in corrector(item)]
        row.append("http://kenesh.kg/" + item.get("href"))
        for_df.append(row)
    divider_law(for_df)
    return for_df


# ************************************************************************************
# processes url
def file_processor_html_review(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "lxml")
    voted_links = soup.find("div", class_="ck-editor").find_all("a")
    for_df = []
    for item in voted_links:
        row = []
        row.append(pure_law(item))
        [row.append(x) for x in corrector(item)]
        row.append("http://kenesh.kg/" + str(item.get("href")))
        row.append(url)
        for_df.append(row)
    divider_law(for_df)
    return for_df


# ************************************************************************************
# files from dir, files html
def box_of_files():
    files = []
    for (dirpath, dirnames, filenames) in walk("../pages/html/"):
        files.extend(filenames)
        break
    return files


# ************************************************************************************
def data_df():
    files = box_of_files()
    columns = ['main_law', 'reading', 'initiators', 'committee', 'link_to_votes', 'draft', 'category_law']
    total = []
    for file in files:
        for d in file_proccessor("../pages/html/" + file):
            total.append(d)
    return pd.DataFrame(total, columns=columns)


# ************************************************************************************
def data_df_html_old(urls):
    columns = ['main_law', 'reading', 'initiators', 'committee', 'link_to_votes', 'url', 'draft', 'category_law']
    total = []
    for url in urls:
        for d in file_processor_html_review2(url):
            total.append(d)
    return total
    # return pd.DataFrame(total, columns=columns)
def data_df_html(urls):
    columns = ['main_law', 'draft', 'category_law','reading', 'initiators', 'committee', 'link_to_votes', 'url']
    total = []
    for url in urls:
        for d in file_processor_html_review3(url):
            total.append(d)
    return total
    # return pd.DataFrame(total, columns=columns)

# ************************************************************************************
def file_processor_html_review2(url):
    regex = r'\(.+?\)'
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "lxml")
    a_tags = soup.find("div", class_="ck-editor").find_all("a")
    for_df = []
    for a_tag in a_tags:
        row=[]
        parts = ''.join([re.sub(r'[\n\t]', '', x.text) for x in a_tag.find_all('strong')])
        container = feature_retriever(re.findall(regex, parts))
        # print("&"*100)
        # print(container)
        # print(len(container))
        # print("@"*100)
        if len(container) > 3:
            print("Ehuuu!")
            row.append(pure_law(a_tag)+container[3])
            container = container[:-1]
        elif len(container) == 3:
            row.append(pure_law(a_tag))
            print(pure_law(a_tag))
        [row.append(x) for x in container]
        row.append("http://kenesh.kg/" + str(a_tag.get("href")))
        row.append(url)
        for_df.append(row)
    divider_law(for_df)
    return for_df

def file_processor_html_review3(url):
    regex = r'\(.+?\)'
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "lxml")
    a_tags = soup.find("div", class_="ck-editor").find_all("a")
    for_df = []
    for a_tag in a_tags:
        row=[]
        parts = ''.join([re.sub(r'[\n\t]', '', x.text) for x in a_tag.find_all('strong')])
        container = feature_retriever(re.findall(regex, parts))
        if len(container) > 3:
            [row.append(i) for i in divider_law2(pure_law(pure_law(a_tag)+container[3]))]
            container = container[:-1]
        elif len(container) == 3:
            [row.append(i) for i in divider_law2(pure_law(a_tag))]
        [row.append(x) for x in container]
        row.append("http://kenesh.kg/" + str(a_tag.get("href")))
        row.append(url)
        for_df.append(row)
    return for_df

def feature_retriever(chunks):
    values = ["чтение", "инициатор", "Комитетом"]
    dics = {}
    orderer = []
    for chunk in chunks:
        if "чтение" in chunk:
            dics['чтение'] = re.sub(r'[\(\)]', '', chunk).strip()
        elif "инициатор" in chunk:
            dics['инициатор'] = re.sub(r'[\(\)]', '', chunk).strip()
        elif "Комитетом" in chunk:
            dics['Комитетом'] = re.sub(r'[\(\)]', '', chunk).strip()
        else :
            dics['разное'] = re.sub(r'[\(\)]', '', chunk).strip()
    for value in values:
        orderer.append(dics.get(value, "NO"))
    return orderer

def new_way(links):
    index = 0
    big_cont = []
    for link in links:
        response = requests.get(link)
        with tempfile.NamedTemporaryFile(delete = False) as fp:
            fp.write(response.content)
            fp.close()
            with open(fp.name, mode='rb') as f:
                csv_name = link.removeprefix('http://kenesh.kg//').replace('/','-')+'.csv'
                got_csv = tb.convert_into(f,csv_name, output_format="csv", pages=[1])
                dep_vtng = arrange_votings(csv_name)
                t1 = row_prep(dep_vtng,dataset[dataset['link_to_votes']== link].index[0])
                big_cont.append(t1)
    return pd.concat(big_cont)


