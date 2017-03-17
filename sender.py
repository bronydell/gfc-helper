import requests

def sendDoc(api, filename):
    resp = api.docs.getUploadServer()
    r = requests.post(resp['upload_url'], files={'file': open(filename, 'rb')})
    resp = r.json()
    resp = api.docs.save(file=resp['file'])
    return str(resp[0]['owner_id']) + '_' + str(resp[0]['id'])

def sendImage(api, group_id ,filename):
    resp = api.photos.getWallUploadServer(group_id=group_id)
    r = requests.post(resp['upload_url'], files={'file': open(filename, 'rb')})
    resp = r.json()

    resp = api.photos.saveWallPhoto(group_id=group_id, server=resp['server'], photo=resp['photo'], hash=resp['hash'])
    return str(resp[0]['owner_id']) + '_' + str(resp[0]['id'])