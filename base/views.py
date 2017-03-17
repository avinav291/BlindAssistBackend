from django.shortcuts import render
from django.http import HttpResponse
from django.core.files.storage import FileSystemStorage
from django.views.decorators.csrf import csrf_exempt
import os
import json
import requests
import base64

@csrf_exempt
def getImageCaption(request):
    myfile = request.FILES.get('image')
    fs = FileSystemStorage()
    filename = fs.save("media/aj.jpeg", myfile)
    sendImage(filename)
    return HttpResponse(json.dumps(sendResponseFromImage(filename)), content_type='application/json')

def sendImage(image):

    with open(image, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
        print 'sending File'
        url = 'https://api.kairos.com/verify'
        payload = {"image": encoded_string,
                   "subject_id": "George Clooney", "gallery_name": "Gallery1"}
        headers = {'Content-Type': 'application/json', 'app_id': '9577a7cf',
                   'app_key': 'bb4b12aca6697ff8db9daebc9c7a2967'}
        # POST with JSON
        r = requests.post(url, data=json.dumps(payload), headers=headers)
        print r.text

def sendResponseFromImage(imgFilePath):
    command = 'cd Script/ && ./darknet detect cfg/yolo.cfg yolo.weights ' + '../'+imgFilePath + ' > ../OutputDump/out.txt'
    # command = 'cd Script/ && pwd'
    print command
    os.system(command)

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

    for key, value in captionDict.iteritems():
        captions.append({'caption':key, 'confidenceScore':value})
    print captions
    return captions

# Create your views here.
