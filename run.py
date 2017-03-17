import rutor
import saver
import vk_requests
import sender
import os
import time
import random

app_id = 5037590
group_id = 116093640

last_post = saver.openPref('me', 'post_id', 0)
if not os.path.exists('data'):
    os.mkdir('data/'.format(last_post))
if not os.path.exists('data/{}'.format(last_post)):
    os.mkdir('data/{}'.format(last_post))
permissions = ['offline', 'wall', 'docs', 'photos']

page = rutor.grabPage('http://rutor.is/torrent/556422/codex-of-victory-2017-pc-repack-ot-qoob')

torrent_file = {'file':
                    open(rutor.downloadFile('data/{}'.format(last_post), 'torrent_1.torrent', page.torrent_url), 'rb')}
if len(page.images_urls) > 4:
    page.images_urls = page.images_urls[:3]
img_id = 0
images = [rutor.downloadFile('data/{}'.format(last_post), 'cover.jpeg', page.post_cover)]

for image in page.images_urls:
    images.append(rutor.downloadFile('data/{}'.format(last_post), '{}.jpeg'.format(img_id), image))
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

attachments = ''

attachments += sender.sendDoc(api, torrent_file) + ', '
for image in images:
    attachments += sender.sendImage(api, group_id, image) + ', '
attachments += 'poll' + sender.createPoll(api, 'Оцени игру', ['5', '4', '3', '2', '1', 'Результат'], group_id)
saver.savePref('me', 'post_id', last_post + 1)

posts = api.wall.get(owner_id=-group_id, count=100, filter='postponed')
postphone = random.randint(60 * 60 * 18, 60 * 60 * 31)
if len(posts['items']) > 0:
    postphone += posts['items'][-1]['date'] - time.time()

api.wall.post(owner_id=-group_id, signed=1, attachments=attachments, message=page.title + '\n' + page.description,
              publish_date=int(time.time() + postphone))
