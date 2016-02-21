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
    #x = list(db.glm.find({},{}))
    #x = map(lambda i: i['Tags'], m)
    #y1 = map(lambda i: i[u'GLM\SWRO_001\RT01\MMF2A\DPRESS'], x)
    #y2 = map(lambda i: i[u'GLM\SWRO_001\RT01\MMF2B\DPRESS'], x)
    #y3 = map(lambda i: i[u'GLM\SWRO_001\RT01\PUMP_FEED03\FREQ'], x)
    
    #z1 = map(lambda i: i[u'Value'], y1)
    #z2 = map(lambda i: i[u'Value'], y2)
    #z3 = map(lambda i: i[u'Value'], y3)
    
    z1 = [233,221,131,212,192]
    z2 = [213,311,233,200,233]
    z3 = [221,333,312,333,222]
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

def trend_flowrates_api(request):
    #x = list(db.glm.find_one())
    #x = map(lambda i: i['Tags'], m)
    #y1 = map(lambda i: i[u'GLM\SWRO_001\RO_001\RT01\SWRO_FEED\FLOW'], x)
    #y2 = map(lambda i: i[u'GLM\SWRO_001\RT01\PX_RAW_IN\FLOW'], x)
    #y3 = map(lambda i: i[u'GLM\SWRO_001\RT01\MEMBRANE_FEED\PRESS'], x)
    
    #z1 = map(lambda i: i[u'Value'], y1)
    #z2 = map(lambda i: i[u'Value'], y2)
    #z3 = map(lambda i: i[u'Value'], y3)
    z1 = [12,23,44,12,11]
    z2 = [29,33,19,23,23]
    z3 = [33,22,11,40,39]
    x = {
        'timestamp': ['t0','t1','t2','t3','t4'],
        'value1': z1,
        'value2': z2,
        'value3': z3,
        'label1': 'F1 HP PUMP FLOW (CFH)',
        'label2': 'F1 CIRC PUMP FLOW (CFH)',
        'label3': 'P4 MEMBRANE INPUT PRESSURE (BAR)'
    }

    message = dumps(x)
    return HttpResponse(message, content_type='application/json')

def trend_pressures_api(request):
    #x = list(db.glm.find_one())
    #x = map(lambda i: i['Tags'], m)
    #y1 = map(lambda i: i[u'GLM\SWRO_001\RT01\PX_RAW_IN\PRESS'], x)
    #y2 = map(lambda i: i[u'GLM\SWRO_001\RT01\PX_RAW_OUT\PRESSIND'], x)
    #y3 = map(lambda i: i[u'GLM\SWRO_001\RT01\MEMBRANE_REJECT\PRESS'], x)
    #y4 = map(lambda i: i[u'GLM\SWRO_001\RT01\MEMBRANE_REJECT\PRESS'], x)
    
    #z1 = map(lambda i: i[u'Value'], y1)
    #z2 = map(lambda i: i[u'Value'], y2)
    #z3 = map(lambda i: i[u'Value'], y3)
    #z4 = map(lambda i: i[u'Value'], y4)
    
    z1 = [1,2,3,4]
    z2 = [4,3,1,2]
    z3 = [2,5,1,3]
    z4 = [3,2,5,1]

    x = {
        'timestamp': ['t0','t1','t2','...'],
        'value1': z1,
        'value2': z2,
        'value3': z3,
        'value4': z4,
        'label1': 'P1',
        'label2': 'P2',
        'label3': 'P3',
        'label4': 'P4'
    }

    message = dumps(x)
    return HttpResponse(message, content_type='application/json')

def trend_circulation_api(request):
    #x = list(db.glm.find_one())
    #x = map(lambda i: i['Tags'], m)
    #y1 = map(lambda i: i[u'GLM\SWRO_001\RT01\PUMP_HP\RUN'], x)
    #y2 = map(lambda i: i[u'GLM\SWRO_001\RT01\PUMP_CIRC\FREQ'], x)
    
    #z1 = map(lambda i: i[u'Value'], y1)
    #z2 = map(lambda i: i[u'Value'], y2)
    
    z1 = [11,23,33,12]
    z2 = [34,23,51,11]
    
    x = {
        'timestamp': ['t0','t1','t2','...'],
        'value1': z1,
        'value2': z2,
        'label1': 'HP PUMP SPEED (HZ)',
        'label2': 'CIRC PUMP SPEED (HZ)'
    }

    message = dumps(x)
    return HttpResponse(message, content_type='application/json')

def trend_analyzers_api(request):
    #x = list(db.glm.find_one())
    #x = map(lambda i: i['Tags'], m)
    #y1 = map(lambda i: i[u'GLM\SWRO_001\RT01\SWRO_FEED\TDS'], x)
    #y2 = map(lambda i: i[u'GLM\SWRO_001\RT01\MEMBRANE_PRODUCT\TDS'], x)
    #y3 = map(lambda i: i[u'GLM\SWRO_001\RT01\MEMBRANE_PRODUCT\PH'], x)
    
    #z1 = map(lambda i: i[u'Value'], y1)
    #z2 = map(lambda i: i[u'Value'], y2)
    #z3 = map(lambda i: i[u'Value'], y3)
    
    z1 = [1,2,3,4]
    z2 = [3,4,1,2]
    z3 = [2,3,4,1]

    x = {
        'timestamp': ['t0','t1','t2','...'],
        'value1': z1,
        'value2': z2,
        'value3': z3,
        'label1': 'TDS INPUT (PPM)',
        'label2': 'TDS PRODUCT (PPM)',
        'label3': '(PH)',
    }

    message = dumps(x)
    return HttpResponse(message, content_type='application/json')

def trend_transfer_api(request):
    #x = list(db.glm.find_one())
    #x = map(lambda i: i['Tags'], m)
    #y1 = map(lambda i: i[u'GLM\SWRO_001\RT01\MEMBRANE_PRODUCT\FLOW'], x)
    #y2 = map(lambda i: i[u''], x)
    #y3 = map(lambda i: i[u'GLM\SWRO_001\RT01\MEMBRANE_PRODUCT\PRESS'], x)
    
    #z1 = map(lambda i: i[u'Value'], y1)
    #z2 = map(lambda i: i[u'Value'], y2)
    #z3 = map(lambda i: i[u'Value'], y3)
    
    z1 = [1,3,1,3]
    z2 = [2,3,2,1]
    z3 = [2,3,1,2]

    x = {
        'timestamp': ['t0','t1','t2','...'],
        'value1': z1,
        'value2': z2,
        'value3': z3,
        'label1': 'TRANSFER FLOWRATE (CFH)',
        'label2': 'TRANSFER PUMP SPEED.. (?)',
        'label3': 'TRANSFER PRESSURE (BAR)'
    }
    
    message = dumps(x)
    return HttpResponse(message, content_type='application/json')

def trend_reject_api(request):
    #x = list(db.glm.find_one())
    #x = map(lambda i: i['Tags'], m)
    #y1 = map(lambda i: i[u'GLM\SWRO_001\RT01\PUMP_BRINE\FREQ'], x)
    
    z1 = map(lambda i: i[u'Value'], y1)

    x = {
        'timestamp': ['t0','t1','t2','...'],
        'value1': z1,
        'label': 'REJECT PUMP SPEED'
    }

    message = dumps(x)
    return HttpResponse(message, content_type='application/json') 

def trend_energy_api(request):
    #x = list(db.glm.find_one())
    #x = map(lambda i: i['Tags'], m)
    #y1 = map(lambda i: i[u'GLM\SWRO_001\RT01\MMF2A\DPRESS'], x)
    #y2 = map(lambda i: i[u'GLM\SWRO_001\RT01\MMF2B\DPRESS'], x)
    #y3 = map(lambda i: i[u'GLM\SWRO_001\RT01\PUMP_FEED03\FREQ'], x)
    
    #z1 = map(lambda i: i[u'Value'], y1)
    #z2 = map(lambda i: i[u'Value'], y2)
    #z3 = map(lambda i: i[u'Value'], y3)
    z1 = [1,3,1,4]
    z2 = [1,2,3,4]
    z4 = [3,1,2,3]
    x = {
        'timestamp': ['t0','t1','t2','...'],
        'value1': z1,
        'value2': z2,
        'value3': z3,
        'label1': 'POWER (W)',
        'label2': 'VOLTAGE (V)',
        'label3': 'COS (PHI)'
    }

    message = dumps(x)
    return HttpResponse(message, content_type='application/json')

def trend_reject_api(request):
    #m = list(db.glm.find())
    #x = map(lambda i: i['Tags'], m)
    #y = map(lambda i: i[u'GLM\SWRO_001\RT01\PUMP_BRINE\FREQ'], x)
    #z = map(lambda i: i[u'Value'], y)
    #print z
    x = [1,2,3]

    z = {
        'timestamp':['1','2','3'],
        'values': x
    }
    message = dumps(z)
    return HttpResponse(message, content_type='application/json') 
