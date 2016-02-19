import simplejson as json
import pymongo
from django.http import HttpResponse, Http404, HttpResponseServerError
from pymongo import MongoClient

from bson import Binary, Code
from bson.json_util import dumps


client = MongoClient()
db = client.inetscada

def live_pretreatment_api(request):
    message = dumps(list(db.glm.find().sort("_id",-1).limit(1)))
    return HttpResponse(message, content_type='application/json') 


def trend_pretreatment_api(request):
    message = {'success': 0}
    return HttpResponse(message, content_type='application/json') 

def live_osmosis_api(request):
    message =  dumps(list(db.glm.find().sort("_id",-1).limit(1)))
    return HttpResponse(message, content_type='application/json') 

def live_product_api(request):
    message =  dumps(list(db.glm.find().sort("_id",-1).limit(1)))
    return HttpResponse(message, content_type='application/json') 

def live_reject_api(request):
    message =  dumps(list(db.glm.find().sort("_id",-1).limit(1)))
    return HttpResponse(message, content_type='application/json') 

def live_energy_api(request):
    message =  dumps(list(db.glm.find().sort("_id",-1).limit(1)))
    return HttpResponse(message, content_type='application/json') 


def trend_reject_api(request):
    m = list(db.glm.find())
    x = map(lambda i: i['Tags'], m)
    y = map(lambda i: i[u'GLM\SWRO_001\RT01\PUMP_BRINE\FREQ'], x)
    z = map(lambda i: i[u'Value'], y)
    print z

    message = dumps(z)
    return HttpResponse(message, content_type='application/json') 
