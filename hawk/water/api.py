import simplejson as json
import pymongo
from django.http import HttpResponse, Http404, HttpResponseServerError
from pymongo import MongoClient

from bson import Binary, Code
from bson.json_util import dumps


client = MongoClient()
db = client.inetscada

#live pages
def live_pretreatment_api(request):
    message = dumps(list(db.glm.find().sort("_id",-1).limit(1)))
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

#trend page
def trend_pretreatment_api(request):
    x = list(db.glm.find())
    #x = map(lambda i: i['Tags'], m)
    y1 = map(lambda i: i[u'GLM\SWRO_001\RT01\MMF2A\DPRESS'], x)
    y2 = map(lambda i: i[u'GLM\SWRO_001\RT01\MMF2B\DPRESS'], x)
    y3 = map(lambda i: i[u'GLM\SWRO_001\RT01\PUMP_FEED03\FREQ'], x)
    
    z1 = map(lambda i: i[u'Value'], y1)
    z2 = map(lambda i: i[u'Value'], y2)
    z3 = map(lambda i: i[u'Value'], y3)

    x = {
        'timestamp': ['t0','t1','t2','...'],
        'value1': z1,
        'value2': z2,
        'value3': z3
    }

    message = dumps(z)
    return HttpResponse(message, content_type='application/json')

def trend_flowrates_api(request):
    x = list(db.glm.find_one())
    #x = map(lambda i: i['Tags'], m)
    y1 = map(lambda i: i[u'GLM\SWRO_001\RO_001\RT01\SWRO_FEED\FLOW'], x)
    y2 = map(lambda i: i[u'GLM\SWRO_001\RT01\PX_RAW_IN\FLOW'], x)
    y3 = map(lambda i: i[u'GLM\SWRO_001\RT01\MEMBRANE_FEED\PRESS'], x)
    
    z1 = map(lambda i: i[u'Value'], y1)
    z2 = map(lambda i: i[u'Value'], y2)
    z3 = map(lambda i: i[u'Value'], y3)

    x = {
        'timestamp': ['t0','t1','t2','...'],
        'value1': z1,
        'value2': z2,
        'value3': z3
    }

    message = dumps(z)
    return HttpResponse(message, content_type='application/json')

def trend_pressures_api(request):
    m = list(db.glm.find_one())
    x = map(lambda i: i['Tags'], m)
    y1 = map(lambda i: i[u'GLM\SWRO_001\RT01\PX_RAW_IN\PRESS'], x)
    y2 = map(lambda i: i[u'GLM\SWRO_001\RT01\PX_RAW_OUT\PRESSIND'], x)
    y3 = map(lambda i: i[u'GLM\SWRO_001\RT01\MEMBRANE_REJECT\PRESS'], x)
    y4 = map(lambda i: i[u'GLM\SWRO_001\RT01\MEMBRANE_REJECT\PRESS'], x)
    
    z1 = map(lambda i: i[u'Value'], y1)
    z2 = map(lambda i: i[u'Value'], y2)
    z3 = map(lambda i: i[u'Value'], y3)
    z4 = map(lambda i: i[u'Value'], y4)

    x = {
        'timestamp': ['t0','t1','t2','...'],
        'value1': z1,
        'value2': z2,
        'value3': z3,
        'value4': z4
    }

    message = dumps(z)
    return HttpResponse(message, content_type='application/json')

def trend_circulation_api(request):
    m = list(db.glm.find_one())
    x = map(lambda i: i['Tags'], m)
    y1 = map(lambda i: i[u'GLM\SWRO_001\RT01\PUMP_HP\RUN'], x)
    y2 = map(lambda i: i[u'GLM\SWRO_001\RT01\PUMP_CIRC\FREQ'], x)
    
    z1 = map(lambda i: i[u'Value'], y1)
    z2 = map(lambda i: i[u'Value'], y2)

    x = {
        'timestamp': ['t0','t1','t2','...'],
        'value1': z1,
        'value2': z2
    }

    message = dumps(z)
    return HttpResponse(message, content_type='application/json')

def trend_analyzers_api(request):
    m = list(db.glm.find_one())
    x = map(lambda i: i['Tags'], m)
    y1 = map(lambda i: i[u'GLM\SWRO_001\RT01\SWRO_FEED\TDS'], x)
    y2 = map(lambda i: i[u'GLM\SWRO_001\RT01\MEMBRANE_PRODUCT\TDS'], x)
    y3 = map(lambda i: i[u'GLM\SWRO_001\RT01\MEMBRANE_PRODUCT\PH'], x)
    
    z1 = map(lambda i: i[u'Value'], y1)
    z2 = map(lambda i: i[u'Value'], y2)
    z3 = map(lambda i: i[u'Value'], y3)

    x = {
        'timestamp': ['t0','t1','t2','...'],
        'value1': z1,
        'value2': z2,
        'value3': z3
    }

    message = dumps(z)
    return HttpResponse(message, content_type='application/json')

def trend_transfer_api(request):
    m = list(db.glm.find_one())
    x = map(lambda i: i['Tags'], m)
    y1 = map(lambda i: i[u'GLM\SWRO_001\RT01\MEMBRANE_PRODUCT\FLOW'], x)
    y2 = map(lambda i: i[u''], x)
    y3 = map(lambda i: i[u'GLM\SWRO_001\RT01\MEMBRANE_PRODUCT\PRESS'], x)
    
    z1 = map(lambda i: i[u'Value'], y1)
    z2 = map(lambda i: i[u'Value'], y2)
    z3 = map(lambda i: i[u'Value'], y3)

    x = {
        'timestamp': ['t0','t1','t2','...'],
        'value1': z1,
        'value2': z2,
        'value3': z3
    }

    message = dumps(z)
    return HttpResponse(message, content_type='application/json')

def trend_reject_api(request):
    m = list(db.glm.find_one())
    x = map(lambda i: i['Tags'], m)
    y1 = map(lambda i: i[u'GLM\SWRO_001\RT01\PUMP_BRINE\FREQ'], x)
    
    z1 = map(lambda i: i[u'Value'], y1)

    x = {
        'timestamp': ['t0','t1','t2','...'],
        'value1': z1,
    }

    message = dumps(z)
    return HttpResponse(message, content_type='application/json') 

def trend_energy_api(request):
    m = list(db.glm.find_one())
    x = map(lambda i: i['Tags'], m)
    y1 = map(lambda i: i[u'GLM\SWRO_001\RT01\MMF2A\DPRESS'], x)
    y2 = map(lambda i: i[u'GLM\SWRO_001\RT01\MMF2B\DPRESS'], x)
    y3 = map(lambda i: i[u'GLM\SWRO_001\RT01\PUMP_FEED03\FREQ'], x)
    
    z1 = map(lambda i: i[u'Value'], y1)
    z2 = map(lambda i: i[u'Value'], y2)
    z3 = map(lambda i: i[u'Value'], y3)

    x = {
        'timestamp': ['t0','t1','t2','...'],
        'value1': z1,
        'value2': z2,
        'value3': z3
    }

    message = dumps(z)
    return HttpResponse(message, content_type='application/json')


