from django.shortcuts import render
from django.http import HttpResponse
from django.core.files.storage import FileSystemStorage
from django.views.decorators.csrf import csrf_exempt
import os
import json
import requests
import base64
import grequests
import time

@csrf_exempt
def uploadImage(request):
    name = request.POST.get('name')
    url = 'https://api.kairos.com/enroll'
    headers = {'Content-Type': 'application/json', 'app_id': '9577a7cf',
               'app_key': 'bb4b12aca6697ff8db9daebc9c7a2967'}  # TODO Change Keys
    myfile = request.FILES.get('image')
    fs = FileSystemStorage()
    filename = fs.save("media/" + myfile.name, myfile)
    with open(filename, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
        payload = {"image": encoded_string, "gallery_name": "Gallery3", "subject_id": name} #TODO Change gallery name
        requests.post(url, data=json.dumps(payload), headers=headers)
    return HttpResponse(json.dumps({'statusCode': 200, 'message': 'Success'}))

@csrf_exempt
def ping(request):
    return HttpResponse(json.dumps({'statusCode': 200, 'message': 'Success'}))


@csrf_exempt
def uploadImages(request):
    async_list = []

    name = request.POST.get('name')

    url = 'https://api.kairos.com/enroll'
    headers = {'Content-Type': 'application/json', 'app_id': '9577a7cf',
               'app_key': 'bb4b12aca6697ff8db9daebc9c7a2967'}  # TODO Change Keys


    # start = time.time()
    for i in range(1, 7):
        # print request
        if request.FILES.has_key('image'+str(i)):
            myfile = request.FILES.get('image'+ str(i))
            print myfile
            fs = FileSystemStorage()
            filename = fs.save("media/"+ myfile.name, myfile)
            with open(filename, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read())
                payload = {"image": encoded_string, "gallery_name": "Gallery3", "subject_id": name}
                action_item = grequests.post(url, data=json.dumps(payload), headers=headers)
                async_list.append(action_item)
    # end = time.time()
    # print end-start
    start = time.time()
    grequests.map(async_list)
    end = time.time()
    print end-start
    return HttpResponse("success")


@csrf_exempt
def getImageCaption(request):
    myfile = request.FILES.get('image')
    fs = FileSystemStorage()
    filename = fs.save("media/aj.jpeg", myfile)
    captionDict = sendResponseFromImage(filename)
    if captionDict.has_key('person'):
        person_response = sendImage(filename)
        person_response_dict = json.loads(person_response.text)
        print person_response_dict
        if 'candidates' in person_response.text:
            # candidates = person_response_dict['images'][0]['candidates']
            transactions = person_response_dict['images']
            for transaction in transactions:
                if transaction.has_key('candidates'):
                    candidates = transaction['candidates']
                    for candidate in candidates:
                        if candidate['confidence'] > 0.65:
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

    print captions
    return HttpResponse(json.dumps(captions), content_type='application/json')



def sendImage(image):

    with open(image, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
        print 'sending File'
        url = 'https://api.kairos.com/recognize'
        payload = {"image": encoded_string, "gallery_name": "Gallery3"} #TODO Change gallery name before demo
        headers = {'Content-Type': 'application/json', 'app_id': '9577a7cf',
                   'app_key': 'bb4b12aca6697ff8db9daebc9c7a2967'}   #TODO Change Keys
        # POST with JSON
        r = requests.post(url, data=json.dumps(payload), headers=headers)
        return r

def sendResponseFromImage(imgFilePath):
    command = 'cd Script/ && ./darknet detect cfg/yolo.cfg yolo.weights ' + '../'+imgFilePath + ' > ../OutputDump/out.txt'
    print command
    # Uncomment to Get Working Copy TODO
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

    print captionDict
    return captionDict

# Create your views here.
