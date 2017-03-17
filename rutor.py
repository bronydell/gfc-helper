from bs4 import BeautifulSoup
import requests
import image_hosts
import shutil
import vk_requests
import saver
import sender

app_id = 5037590

permissions = ['offline', 'wall', 'docs', 'photos']

hosts = [
    "fastpic.ru",
    "radikal.ru"
]
not_hosts = [
    "http://fastpic.ru/",
    "http://radikal.ru/"
]

class Page:
    description = ''
    torrent_url = ''
    images_urls = []

    def __init__(self, url):
        self.url = url

def grabPage(url):

    pg = Page(url)

    html = requests.get(url).content
    soup = BeautifulSoup(html, "html.parser")
    description = soup.find('table', {'id': 'details'})
    description = description.find('tr')

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


def downloadFile(filename, url):
    response = requests.get(url, stream=True)
    with open(filename, 'wb') as out_file:
        shutil.copyfileobj(response.raw, out_file)
    del response


page = grabPage('http://rutor.is/torrent/554071/under-zero-2016-pc-repack-ot-qoob')
downloadFile('torrent_1.torrent', page.torrent_url)
if len(page.images_urls) > 4:
    page.images_urls = page.images_urls[:3]
img_id = 0
for image in page.images_urls:
    downloadFile('{}.jpeg'.format(img_id), image)
    img_id += 1

if saver.openPref('me', 'login', None) is None:
    login = input('Number or email: ')
    password = input('Password: ')
else:
    login = saver.openPref('me', 'login', None)
    password = saver.openPref('me', 'password', None)

try:
    api = vk_requests.create_api(app_id=app_id, login=login,
                                 password=password, scope=permissions, api_version='5.62')
    if saver.openPref('me', 'login', None) is None:
        saver.savePref('me', 'login', login)
        saver.savePref('me', 'password', password)
except Exception as ex:
    print(ex.__str__())

group_id = 116093640

doc_1 = sender.sendDoc(api, 'torrent_1.torrent')
photo_1 = sender.sendImage(api, group_id, '0.jpeg')
photo_2 = sender.sendImage(api, group_id, '1.jpeg')
photo_3 = sender.sendImage(api, group_id, '2.jpeg')

api.wall.post(owner_id=-group_id, message = page.description,
              attachments = 'doc{}, photo{}, photo{}, photo{}'.format(doc_1, photo_1, photo_2, photo_3))



