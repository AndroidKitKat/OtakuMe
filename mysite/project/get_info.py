#!/usr/bin/env python2.7

import urllib
from bs4 import BeautifulSoup as soup
from bs4 import SoupStrainer as strain
import sqlite3
import string
import unicodedata
import requests

def remove_accents(data):
    # From https://stackoverflow.com/questions/8694815/removing-accent-and-special-characters#8695067
    line = data.split()
    for i, word in enumerate(line):
        line[i] = ''.join(x for x in unicodedata.normalize('NFKD', word) if x in
                string.ascii_letters).lower()
    return ' '.join(line)

def name_to_id(name):
    '''
    Currently not using...
    '''
    name1 = name.encode('utf-8')
    print type(name1)
    conn = sqlite3.connect('project/title_database.db')
    conn.text_factory = str

    c = conn.cursor()
    t = (name, )

def get_anime_info(name):
    name1 = name.encode('utf-8')
    name1 = name1.lower().strip()
    conn = sqlite3.connect('project/title_database.db')
    conn.text_factory = str
    descriptions = []
    c = conn.cursor()
    ids = []

    for row in c.execute('SELECT * FROM anime'):
        x = str(row[0])
        if (name1 in x) or name1 == x.lower():
            ids.append(str(row[1]))

    for _id in ids:
        bad = False
        url="https://www.animenewsnetwork.com/encyclopedia/api.xml?anime=" + _id

        client = urllib.urlopen(url)
        html = client.read()
        client.close()

        page_soup = soup(html, 'lxml')

        genres = []
        themes = []
        songs = [[],[]] # op, ed
        run_dates = [] # Start, end
        plot_summary = ""
        pic = ""
        score = None
        title = ""


        # TODO: Update this so that it does not search through the whole
        # document so many times
        for item in page_soup.findAll(type="Ending Theme"):
            songs[1].append(item.text.encode('utf-8'))
        for item in page_soup.findAll(type="Opening Theme"):
            songs[0].append(item.text.encode('utf-8'))
        for item in page_soup.findAll(type="Plot Summary"):
            plot_summary = item.text.encode('utf-8')
        for item in page_soup.findAll(type="Genres"):
            genres.append(item.text.encode('utf-8'))
        for item in page_soup.findAll(type="Themes"):
            themes.append(item.text.encode('utf-8'))
        for item in page_soup.findAll(type="Vintage"):
            run_dates.append(item.text.encode('utf-8'))
        for item in page_soup.findAll(type="Picture"):
            pic= item.find('img')['src']
        for item in page_soup.findAll(type="Main title"):
            title = remove_accents(title).strip()
            title = item.text.encode('utf-8')
        for item in page_soup.findAll("ratings"):
            score = item["weighted_score"].encode('utf-8')
        crunchy = "-".join(title.split())
        URL = "https://www.crunchyroll.com/" + crunchy
        r = requests.get(url = URL)

        genres = ', '.join(genres)
        themes = ', '.join(themes)

        run_dates = None # Rightnow these do not look good when displayed

        for show in descriptions: # Removes duplicate listings
            if show['title'] == title:
                bad = True

        if not bad:
            if not r.ok:
                crunchy = None
            descriptions.append({'crunchy': crunchy, 'image': pic,
                'title':title, 'genres': genres, 'themes': themes,
                'songs': songs, 'summary': plot_summary,
                'rundates': run_dates, 'score': score})

    print descriptions
    return descriptions

def get_manga_info(name):
    name1 = name.encode('utf-8')
    name1 = name1.lower().strip()
    conn = sqlite3.connect('project/manga_database.db')
    conn.text_factory = str
    descriptions = []
    c = conn.cursor()
    ids = []
    t = (name1, )
    for row in c.execute('SELECT * FROM manga'):
        x = str(row[0])
        if (name1 in x) or name1 == x.lower():
            ids.append(str(row[1]))

    for _id in ids:
        bad = False
        url="https://www.animenewsnetwork.com/encyclopedia/api.xml?manga=" + _id

    # TODO: MAKE IT POSSIBLE TO RETURN MULTIPLE THINGS PER search
    # search:your -> your lie in april, your xx yy zz, etc
        client = urllib.urlopen(url)
        html = client.read()
        client.close()

        page_soup = soup(html, 'lxml')

        page_num = 0
        books_num = 0
        genres = []
        themes = []
        run_dates = [] # Start, end
        plot_summary = ""
        pic = ""
        title = ""
        tank = None
        pages = None
        score = None

        strainer = strain('info',{})

        #TODO: Update this by using a strainer, so that we do not search
        # through the whole page so many freakin times
        for item in page_soup.findAll(type="Number of pages"):
            page_num = item.text.encode('utf-8')
        for item in page_soup.findAll(type="Number of tankoubon"):
            books_num =  item.text.encode('utf-8')
        for item in page_soup.findAll(type="Plot Summary"):
            plot_summary = item.text.encode('utf-8')
        for item in page_soup.findAll(type="Genres"):
            genres.append(item.text.encode('utf-8'))
        for item in page_soup.findAll(type="Themes"):
            themes.append(item.text.encode('utf-8'))
        for item in page_soup.findAll(type="Vintage"):
            run_dates.append(item.text.encode('utf-8'))
        for item in page_soup.findAll(type="Picture"):
            pic= item.find('img')['src']
        for item in page_soup.findAll(type="Main title"):
            title = remove_accents(title).strip()
            title = item.text.encode('utf-8')
        for item in page_soup.findAll("ratings"):
            score = item["weighted_score"].encode('utf-8')
        for item in page_soup.findAll(type="Number of tankoubon"):
            tank = item.text.encode('utf-8')
        for item in page_soup.findAll(type="Number of pages"):
            pages = item.text.encode('utf-8')

        genres = ', '.join(genres)
        themes = ', '.join(themes)

        if genres == "":
            genres = None
        if themes == "":
            themes = None
        for show in descriptions: # Removes duplicate listings
            if show['title'] == title:
                bad = True
        if not bad:

            descriptions.append({'image': pic, 'title':title, 'genres': genres,
            'themes': themes, 'summary': plot_summary, 'score': score,
            'pages': pages, 'tankou': tank})
    print descriptions
    return descriptions


if  __name__=='__main__':
    # get_anime_info("13")
    get_manga_info('13')
