'''
The modules for eksisozluk are taken from the github repository
https://github.com/yusufusta/eksipy
Little modifications are made.
'''

import json
from requests_html import AsyncHTMLSession
from requests.models import PreparedRequest
from datetime import datetime
from time import mktime
import os
from typing import List
import re
import html
from typing import List
import asyncio
import functions_framework
import firebase_admin
from firebase_admin import firestore
from collections import defaultdict

app = firebase_admin.initialize_app()
db = firestore.client()

class Model(object):
    def __init__(self, client, **kwargs):
        self.client = client
        self.__dict__.update(kwargs)


class Message(Model):
    id = None
    from_user = None
    message = None
    preview = None
    date = None
    read = None
    unread = None
    thread_id = None

    def __init__(self, client, **kwargs):
        super().__init__(client, **kwargs)


class Entry(Model):
    id = None
    author = None
    topic = None
    entry = None
    date = None
    edited = None
    fav_count = None
    comment = None

    def dict(self):
        return self.__dict__

    def url(self):
        return f'https://eksisozluk.com/entry/{self.id}'

    def text(self):
        """
        Entry yazı haline çevirir.
        """

        _ = self.entry.html()
        linkler = self.entry("a")
        for link in linkler.items():
            if link.attr('class') == "b":
                _ = _.replace(html.unescape(link.outerHtml()),
                              f"`{link.text()}`")
                continue
            _ = _.replace(link.outerHtml(),
                          f"[{link.attr('href')} {link.text()}]")
            _ = html.unescape(_).replace("<br/>", "\n")
        return _

    def html(self):
        return self.entry.html()

    def __str__(self):
        return self.text()  # md(str(self.entry).strip())[1:]


class Topic(Model):
    id = None
    title = None
    giri = None
    current_page = None
    max_page = None
    slug = None
    url = None

    async def getUrl(self):
        """
        Başlığın adresini getirir.
        """

        if self.url == None:
            return (await self.client.convertToTopic(self.title))
        else:
            return self.url

    def dict(self):
        return self.__dict__

    def __str__(self):
        return self.title

    def __init__(self, client, **kwargs):
        super().__init__(client, **kwargs)

    def getEntrys(self, page=1, day=None, sukela=None) -> List[Entry]:
        """
        Başlığın entrylerini getirir.
        """

        return self.client.getEntrys(self, page, day, sukela)


class User(Model):
    id = None
    nick = None
    total_entry = None
    last_month = None
    last_week = None
    today = None
    last_entry = None
    pinned_entry = None
    badges = []

    def url(self):
        return f'https://eksisozluk.com/biri/{self.nick}'

    def __str__(self):
        return f'https://eksisozluk.com/biri/{self.nick}'


class Eksi:
    def __init__(self, session: AsyncHTMLSession = None, config={"EKSI_URL": "https://eksisozluk.com/"}):
        """
        Sinifi başlatir.
        """

        if session == None:
            self.session = AsyncHTMLSession()
        else:
            if isinstance(session, AsyncHTMLSession):
                self.session = session
            else:
                self.session = AsyncHTMLSession()
        self.config = config
        self.eksi = self.config["EKSI_URL"]

    def addParamsToUrl(self, url: str, params: dict) -> str:
        """
        Belirtilen parametreleri adrese ekler.
        """

        req = PreparedRequest()
        req.prepare_url(url, params)
        return req.url

    async def bugun(self, page=1) -> List[Topic]:
        """
        Ekşi Sözlükteki bugün bölümü çeker.
        """

        bugun = await self.session.get(
            f'{self.eksi}basliklar/bugun/{page}&_=0'
        )

        topics = bugun.html.find(
            '#content-body > ul', first=True).find("a")
        basliklar = []

        for topic in topics:
            topic_id = topic.find('a', first=True).pq
            if not topic_id == None:
                if topic_id.find('small'):
                    giri_sayi = topic_id('small').text()
                    topic_id('small').remove()
                else:
                    giri_sayi = None
                baslik = topic_id.text()
                topic_id = int(topic_id("a").attr("href").split(
                    '?day=')[0].split('--')[1])
            else:
                continue

            basliklar.append(
                Topic(
                    self,
                    id=topic_id,
                    title=baslik,
                    giri=giri_sayi
                )
            )
        return basliklar

    async def convertToTopic(self, title) -> str:
        """
        Yazdığınız kelimeleri başlığa çevirir.
        """

        istek = await self.session.get(self.eksi + "?q=" + title)
        if istek.status_code != 404:
            return istek.url
        else:
            return False

    async def getEntrys(self, baslik: Topic, page=1, day=None, sukela=None) -> List[Entry]:
        """
        Verdiğiniz başlığın entrylerini çeker.
        """

        url = await baslik.getUrl()
        if(url == False):
            return []
        url = self.addParamsToUrl(url, {"p": page})
        if not day == None:
            url = self.addParamsToUrl(url, {"day": day})
        if not sukela == None:
            url = self.addParamsToUrl(url, {"a": sukela})

        topic = await self.session.get(
            url
        )

        topic = topic.html.find("#topic", first=True)
        if(topic == None):
            return []
        giriler = []

        entrys = topic.find("#entry-item-list", first=True)
        if entrys == None:
            return []
        entrys = entrys.find("li")
        for entry in entrys:
            giriler.append(
                Entry(
                    self,
                    id=entry.attrs['data-id'],
                    author=User(
                        self,
                        id=entry.attrs['data-author-id'], nick=entry.attrs['data-author']),
                    entry=entry.pq(".content"),
                    topic=baslik,
                    date="",
                    edited=False,
                    fav_count=entry.attrs['data-favorite-count'],
                    comment=entry.attrs['data-comment-count'],
                )
            )
        return giriler

    async def getEntry(self, entry: int) -> Entry:
        """
        Belirli bir entry çeker.
        """

        url = self.eksi + "entry/" + str(entry)
        topic = await self.session.get(
            url
        )

        topic = topic.html.find("#topic", first=True)
        entry = topic.find("#entry-item-list", first=True).find("li")[0]
        tarih = entry.find(
            "footer > div.info > a.entry-date.permalink", first=True).text
        duzenleme, tarih = self.convertToDate(tarih)
        return Entry(
            self,
            id=entry.attrs['data-id'],
            author=User(
                self,
                id=entry.attrs['data-author-id'], nick=entry.attrs['data-author']),
            entry=entry.pq(".content"),
            date=tarih,
            edited=duzenleme,
            fav_count=entry.attrs['data-favorite-count'],
            comment=entry.attrs['data-comment-count'],
        )

    def convertToDate(self, date: str) -> str:
        """
        Ekşi Sözlük zamanını unix time çevirir.
        """

        if '~' in date:
            parcalama = date.split('~')
            parcalama[0] = parcalama[0].strip()
            parcalama[1] = parcalama[1].strip()

            tarih = round(
                mktime(datetime.strptime(
                       parcalama[0], "%d.%m.%Y %H:%M" if ':' in parcalama[0] else "%d.%m.%Y").timetuple())
            )

            if '.' in parcalama[1]:
                duzenleme = round(
                    mktime(datetime.strptime(
                        parcalama[1], "%d.%m.%Y %H:%M" if ':' in parcalama[1] else "%d.%m.%Y").timetuple())
                )
            else:
                duzenleme = round(
                    mktime(datetime.strptime(
                        f"{parcalama[0].split(' ')[0]} {parcalama[1]}", "%d.%m.%Y %H:%M").timetuple())
                )
        else:
            duzenleme = False
            tarih = mktime(datetime.strptime(
                date, "%d.%m.%Y %H:%M" if ':' in date else "%d.%m.%Y").timetuple())
        return duzenleme, tarih

    async def gundem(self, page=1) -> List[Topic]:
        """
        Gündem feedini çeker
        """

        gundem = await self.session.get(
            f'{self.eksi}basliklar/gundem?p={page}'
        )

        topics = gundem.html.find('#partial-index > ul', first=True).find('a')
        basliklar = []

        for topic in topics:
            topic_id = topic.find('a', first=True).pq
            if not topic_id == None:
                if topic_id.find('small'):
                    giri_sayi = topic_id('small').text()
                    topic_id('small').remove()
                else:
                    giri_sayi = None
                baslik = topic_id.text()
                topic_id = int(topic_id("a").attr("href").split(
                    '?a=')[0].split('--')[1])
            else:
                continue

            basliklar.append(
                Topic(
                    self,
                    id=topic_id,
                    title=baslik,
                    giri=giri_sayi
                )
            )
        return basliklar

    async def getTopic(self, title) -> Topic:
        """
        Başlık getirir.
        """

        adres = await self.convertToTopic(title)
        if adres != False:
            baslik = await self.session.get(adres)
            title = baslik.html.find("#title", first=True)
            pager = baslik.html.find("div[class='pager']", first=True)

            return Topic(
                self,
                id=int(title.attrs['data-id']),
                title=title.attrs['data-title'],
                max_page=int(pager.attrs['data-pagecount']),
                current_page=int(pager.attrs['data-currentpage']),
                slug=title.attrs['data-slug'],
                url=adres
            )
        else:
            raise Exception("404: böyle bir başlık yok.")

def remove_html_tags(data):
    p = re.compile(r'<.*?>')
    return p.sub(' ', data)

def remove_not_supported_chars(data):
    p = re.compile(r'&#\d+;')
    return p.sub('', data)

def fix_quote(data):
    p = re.compile(r'`')
    return p.sub('\'', data)

def format_string(data):
    return fix_quote(remove_not_supported_chars(remove_html_tags(data)))

async def main(page):
    eksi = Eksi()
    gundem = (await eksi.gundem(page))
    # return str('\n'.join(list(map(lambda x: x.__str__(), gundem))))
    mp_gundem = defaultdict(list)
    print("gundem cekiliyor")
    for baslik in gundem:
        url = await baslik.getUrl()
        if(url == False):
            continue
        entries = (await eksi.getEntrys(baslik))
        for entry in entries[:3]:
            e = entry.__str__()
            if(len(e) < 80):
                continue
            if(len(e) > 300):
                e = e[:300]
            formatted = format_string(e)
            mp_gundem[baslik.__str__()].append(formatted)
    print("gundem cekildi")
    db.collection("gundem").add(mp_gundem)
    return mp_gundem

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "*",
    "Access-Control-Allow-Headers": "*",
    "Access-Control-Max-Age": "3600",
}        

@functions_framework.http
def get_topics(request):
    request_json = request.get_json(silent=True)
    request_args = request.args
    page = 1
    if request_json and 'page' in request_json:
        page = request_json['page']
    elif request_args and 'page' in request_args:
        page = request_args['page']
    return (asyncio.run(main(page)),200,CORS_HEADERS)