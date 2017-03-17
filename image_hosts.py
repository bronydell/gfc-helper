import requests
from bs4 import BeautifulSoup
import re

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
    name = find_between(link, '/', '.jpg')
    for img in soup.find_all('img'):
        print(img['src'])
        if name in img['src']:
            return img['src']
    return None