import json
import requests

def createPoll(api, question, options, group_id):
    res = api.polls.create(question=question, owner_id=-group_id, add_answers=str(json.dumps(options)))
    return '{}_{}'.format(res['owner_id'], res['id'])

def sendDoc(api, file):
    resp = api.docs.getUploadServer()
    print(file)
    r = requests.post(resp['upload_url'], files=file)
    resp = r.json()
    resp = api.docs.save(file=resp['file'])
    return 'doc'+str(resp[0]['owner_id']) + '_' + str(resp[0]['id'])

def sendImage(api, group_id, file):
    resp = api.photos.getWallUploadServer(group_id=group_id)
    r = requests.post(resp['upload_url'], files={'file': open(file, 'rb')})
    resp = r.json()

    resp = api.photos.saveWallPhoto(group_id=group_id, server=resp['server'], photo=resp['photo'], hash=resp['hash'])
    return 'photo'+str(resp[0]['owner_id']) + '_' + str(resp[0]['id'])