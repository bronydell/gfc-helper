import rutor
import rutracker
import saver
import vk_requests
import sender
import os
import time
import random
import argparse
import json
import requests
import zipfile
import sys
import io

app_id = 5931763

group_list = ['Игры для слабых ПК', 'Игры для мощных ПК']
group_ids = [53524685, 65820735]
__version__ = 2


def getSettings():
    with open('prefs.json', encoding='UTF-8') as data_file:
        data = json.load(data_file)
    return data


def getVersionsInfo():
    try:
        return requests.get(getSettings()['update_url']).json()
    except:
        return None


def extractZipFromURL(url):
    r = requests.get(url)
    z = zipfile.ZipFile(io.BytesIO(r.content))
    z.extractall()

def update():
    version_info = getVersionsInfo()
    if version_info is not None and version_info['versions'] is not None:
        version_info = version_info['versions'][-1]
        if version_info['version'] > __version__:
            print('Качаем обновление. Перезапустите скрипт')
            extractZipFromURL(version_info['url'])
            os.execl(sys.executable, sys.executable, *sys.argv)

def post(tracker_url, group_id):
    last_post = saver.openPref('me', 'post_id', 0)
    if not os.path.exists('data'):
        os.mkdir('data/'.format(last_post))
    if not os.path.exists('data/{}'.format(last_post)):
        os.mkdir('data/{}'.format(last_post))
    permissions = ['offline', 'wall', 'docs', 'photos']
    if 'rutracker' in tracker_url:
        page = rutracker.grabPage(tracker_url)
    elif 'rutor':
        page = rutor.grabPage(tracker_url)
    torrent_file = {'file':
                        open(rutracker.downloadFile('data/{}'.format(last_post), 'torrent_1.torrent', page.torrent_url),
                             'rb')}
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
                                     password=password, scope=permissions, api_version='5.62', interactive=True)
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
                  publish_date=time.time() + postphone)

if __name__ == "__main__":

    update()
    settings = getSettings()
    app_id = settings['app_id']
    parser = argparse.ArgumentParser()
    group_list = settings['group_list']
    group_ids = settings['group_ids']

    parser.add_argument("url", type=str,
                        help="URL on tracker", nargs='?', default=None)
    args = parser.parse_args()
    if args.url:
        url = args.url
    else:
        print(settings['messages']['paste_tip'])
        url = input(settings['messages']['enter_url'])

    print(settings['messages']['pick_a_group'])
    gid = 0
    for group in group_list:
        print('{}. {}'.format(gid+1, group))
        gid += 1
    group = -1

    group = int(input(settings['messages']['pick_a_number']))
    group -= 1
    post(url, group_ids[group])







