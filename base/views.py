from django.shortcuts import render
from django.http import HttpResponse
from django.core.files.storage import FileSystemStorage
from django.views.decorators.csrf import csrf_exempt
import os
import json
import requests
import base64
from sets import Set

@csrf_exempt
def getImageCaption(request):
    myfile = request.FILES.get('image')
    fs = FileSystemStorage()
    filename = fs.save("media/aj.jpeg", myfile)
    captionDict = sendResponseFromImage(filename)
    if captionDict.has_key('person'):
        person_response = sendImage(filename)
        if person_response.status_code is 200:
            candidates = person_response.text['images']['candidates']
            for candidate in candidates:
                captionDict[candidate['subject_id']] = 100
            del captionDict['person']
    captions = []
    for key, value in captionDict.iteritems():
        captions.append({'caption':key, 'confidenceScore':value})
    # for c in captions:
    #     if c['caption'] is 'person':
    #         person_response = sendImage(filename)
    #         if person_response.status_code is 200:
    #             candidates = person_response.text['images']['candidates']
    #             persons = Set([])
    #             for candidate in candidates:
    #                 persons.add(candidate['subject_id'])
    #             for person in persons:
    #                 captions.append({'caption': person, 'confidenceScore': 100})
    #     del captions[c]


    return HttpResponse(json.dumps(captions), content_type='application/json')



def sendImage(image):

    with open(image, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
        print 'sending File'
        url = 'https://api.kairos.com/recognize'
        payload = {"image": encoded_string, "gallery_name": "Gallery1"} #TODO Change gallery name before demo
        headers = {'Content-Type': 'application/json', 'app_id': '9577a7cf',
                   'app_key': 'bb4b12aca6697ff8db9daebc9c7a2967'}   #TODO Change Keys
        # POST with JSON
        r = requests.post(url, data=json.dumps(payload), headers=headers)
        print r.text

def sendResponseFromImage(imgFilePath):
    command = 'cd Script/ && ./darknet detect cfg/yolo.cfg yolo.weights ' + '../'+imgFilePath + ' > ../OutputDump/out.txt'
    print command
    # Uncomment to Get Working Copy TODO
    # os.system(command)

    f = open('OutputDump/out.txt', 'r')
    content = f.readlines()
    content = [c.strip() for c in content]
    del content[0]

    captions = []
    captionDict = {}

    for caption in content:
        list = caption.split(": ")
        percent = list[1]
        percent = int(percent[:-1])

        # list[1] = int(str(list[1:-1]))
        if captionDict.has_key(list[0]):
            if captionDict[list[0]] < percent:
                captionDict[list[0]] = percent
        else:
            captionDict[list[0]] = percent

    print captionDict
    return captionDict

# Create your views here.
