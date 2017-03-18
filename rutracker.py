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

auth_cookie = {
    "bb_session": "0-11316112-LRS6cAJJBrudES3zPyMm",
    "bb_t": "a%3A17%3A%7Bi%3A4948966%3Bi%3A1485429224%3Bi%3A5326952%3Bi%3A1485718899%3Bi%3A5174311%3Bi%3A1484701525%3Bi%3A5334252%3Bi%3A1484981204%3Bi%3A5341831%3Bi%3A1486157664%3Bi%3A5035604%3Bi%3A1486211478%3Bi%3A5154734%3Bi%3A1485965222%3Bi%3A5245966%3Bi%3A1487325959%3Bi%3A5347855%3Bi%3A1487262997%3Bi%3A5343252%3Bi%3A1487256097%3Bi%3A5347868%3Bi%3A1486652771%3Bi%3A5353618%3Bi%3A1487826880%3Bi%3A5360509%3Bi%3A1488218244%3Bi%3A5363523%3Bi%3A1488474485%3Bi%3A5363327%3Bi%3A1488050792%3Bi%3A5361385%3Bi%3A1488189701%3Bi%3A5205599%3Bi%3A1489756742%3B%7D"
}
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
    html = requests.get(url, cookies=auth_cookie).content
    soup = BeautifulSoup(html, "html.parser")

    description = soup.find('div', {'class': 'post_body'})

    pg.title = ''
    for link in description.findAll('a', {'class': 'postLink'}):
        if any(x in link['href'] for x in hosts) and all(x != link['href'] for x in not_hosts) and link.find('var'):
            img_url = image_hosts.parse(link['href'])
            if img_url:
                pg.images_urls.append(img_url)

    for match in description.findAll('div', {'class': 'sp-wrap'}):
        match.replaceWith('')
    url = soup.find('a', {'class': 'dl-stub'})
    if url['href'].startswith('dl.php?t='):
        pg.torrent_url = 'https://rutracker.org/forum/{}'.format(url['href'])

    description.find('div', {'id': 'tor-reged'}).replaceWith('')

    pg.post_cover = description.find('var')['title']
    pg.description = description.text
    return pg


def downloadFile(path, filename, url):
    response = requests.get(url, stream=True, cookies=auth_cookie)
    if 'content-disposition' in response.headers:
        d = response.headers['content-disposition']
        print(d)
        filename = re.findall("filename=(.+)", d)[0][1:-1]
    filename = path + '/' + filename
    with open(filename, 'wb') as out_file:
        shutil.copyfileobj(response.raw, out_file)
    del response
    return filename