from bs4 import BeautifulSoup
import requests
import image_hosts
import shutil
import re
import saver
import sender

hosts = [
    "fastpic.ru",
    "radikal.ru"
]
not_hosts = [
    "http://fastpic.ru/",
    "http://radikal.ru/"
]


class Page:
    title = ''
    description = ''
    torrent_url = ''
    post_cover = ''
    images_urls = []

    def __init__(self, url):
        self.url = url


def grabPage(url):
    pg = Page(url)

    html = requests.get(url).content
    soup = BeautifulSoup(html, "html.parser")
    description = soup.find('table', {'id': 'details'})
    description = description.find('tr')
    pg.title = soup.find('div', {'id':'all'}).find('h1').text
    pg.post_cover = description.find('img')['src']
    for link in description.findAll('a'):
        if any(x in link['href'] for x in hosts) and all(x != link['href'] for x in not_hosts) and link.find('img'):
            img_url = image_hosts.parse(link['href'])
            if img_url:
                pg.images_urls.append(img_url)

    for match in description.findAll('div', {'class': 'hidewrap'}):
        match.replaceWith('')

    for url in soup.find('div', {'id': 'download'}).findAll('a'):
        if url['href'].startswith('/download'):
            pg.torrent_url = 'http://rutor.is{}'.format(url['href'])
    pg.description = description.text
    return pg


def downloadFile(path, filename, url):
    response = requests.get(url, stream=True)
    if 'content-disposition' in response.headers:
        d = response.headers['content-disposition']
        filename = re.findall("filename=(.+)", d)[0][1:-1]
    filename = path + '/' + filename
    with open(filename, 'wb') as out_file:
        shutil.copyfileobj(response.raw, out_file)
    del response
    return filename

