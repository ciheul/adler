import simplejson as json
import pymongo
from django.http import HttpResponse, Http404, HttpResponseServerError
from pymongo import MongoClient

from bson import Binary, Code
from bson.json_util import dumps


client = MongoClient()
db = client.inetscada

def tag_update_api(request):
    message =  dumps(list(db.glm.find().sort("_id",-1).limit(1)))
    return HttpResponse(message, content_type='application/json') 

def tag_update_1_api(request):
    message = dumps(list(db.tagSettler.find()))
    return HttpResponse(message, content_type='application/json')

def tags_api(request):
    #x = list(db.glm.find({},{}))
    #y2 = map(lambda i: i[u'GLM\SWRO_001\RT01\MMF2B\DPRESS'], x)
    
    z1 = {
         "dateupdated":"date",
         "tagname": "",
         "tag": "GLM\\SWRO_001\\RT2\\PUMP_FEED03\\RUN"
    }
    z2 = {
         "dateupdated":"date",
         "tagname": "",
         "tag": "GLM\\SWRO_001\\RT2\\PUMP_FEED03\\FAULT"
    }
    z3 = {   
         "dateupdated":"date",
         "tagname": "",
         "tag": "GLM\\SWRO_001\\RT2\\PUMP_FEED03\\FREQ"
    }
    x = {
        'timestamp': ['t0','t1','t2','t3','t4'],
        'value1': z1,
        'value2': z2,
        'value3': z3,
        'label1': 'MM FILTER 2A DP (BAR)',
        'label2': 'MM FILTER 2B DP (BAR)',
        'label3': 'FEED PUMP FLOW (HZ)'
    }
    message = dumps(x)
    return HttpResponse(message, content_type='application/json')

