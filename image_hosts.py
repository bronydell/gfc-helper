import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin

hosts = [
    "fastpic.ru",
    "radikal.ru",
    "lostpic.net",
    "scrin.org"
]
not_hosts = [
    "http://fastpic.ru/",
    "http://radikal.ru/",
    "http://lostpic.net/",
    "http://scrin.org"
]

def find_between( s, first, last ):
    try:
        end = s.rfind(last, 0)
        s = s[:end]
        start = s.rfind( first ) + len( first )

        return s[start:end]
    except ValueError:
        return ""

def parse(link):
    req = requests.get(link)
    if req.headers['Content-Type'] == 'image/jpeg':
        return req.url
    html = req.content
    soup = BeautifulSoup(html, "html.parser")
    name = find_between(link, '/', '.')
    for img in soup.find_all('img'):
        if name in find_between(img['src'], '/', '.'):
            return img['src']
    img = soup.find("div", {"class": "image-viewer-image"})
    if img is not None:
        return img.a['href']
    img = soup.find("div", {"id": "view-full-image"})
    if img is not None:
        return urljoin(link, img.a['href'])
    return None