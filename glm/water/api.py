import csv
from datetime import datetime
import math
import os
import os.path

from django.http import HttpResponse, Http404, HttpResponseServerError
from django.contrib.auth.decorators import login_required
from django.utils import timezone

import simplejson as json
import pymongo
from pymongo import MongoClient
import pytz

from bson import Binary, Code
from bson.json_util import dumps


db = MongoClient().inetscada

SCHEMA = 'water/conf/schema.json'
COLL = 'glm'
COLL_REPORT = 'glm_report'


def modify_datetime(dt):
    dt = dt.replace(microsecond=0)
    return dt.isoformat()


def get_page_schema(page_id):
    f = open(SCHEMA)
    schema = json.loads(f.read())
    return schema[page_id]


def grammar_sum(detail, row):
    total_value = 0
    for tag_name in detail['value']:
        if tag_name not in row['Tags']:
            continue
        total_value += float(row['Tags'][tag_name]['Value'])
    return total_value


def grammar_substract(detail, row):
    a = detail['value'][0]
    b = detail['value'][1]

    return float(row['Tags'][a]['Value']) - float(row['Tags'][b]['Value'])


def grammar_div(detail, row):
    try:
        a = detail['value'][0]
        b = detail['value'][1]

        return float(row['Tags'][a]['Value']) / float(row['Tags'][b]['Value'])
    except ZeroDivisionError:
        return 'NaN'


def grammar_percentage(detail, row):
    try:
        a = detail['value'][0]
        b = detail['value'][1]

        return float(row['Tags'][a]['Value']) / float(row['Tags'][b]['Value']) * 100.0
    except ZeroDivisionError:
        return 0 


def grammar_mean(detail, row):
    total_value = grammar_sum(detail, row)
    return total_value / len(detail['value'])
    # return "{:,.2f}".format(total_value / len(detail['value']))


def get_chart_data(detail, tag_id, start=0, rows=60, first=False):
    # get a list of tag name
    tag_names = map(lambda i: i['data'], detail['series'])

    if first == True:
        # get the earliest 60 rows
        rows = list(db[COLL].find().skip(start).limit(rows))
    else:
        # get the latest 60 rows
        rows = list(db[COLL].find().sort("_id", -1).skip(start).limit(rows))

        # sort ascending based so that the oldest time in the first element
        # this is important so that highchart can render x-axis label
        rows.reverse()

    # collect 60 value for each tag name in temporary dictionary
    result = dict()
    for r in rows:
        for tag_name in tag_names:
            # prepare datetime and value
            # dt = r['SentTimestamp']
            dt = modify_datetime(r['SentDatetime'])
            
            value = float("{:.2f}".format(r['Tags'][tag_name]['Value']))

            # if key is not in dictionary, create key with list as value
            # append a pair of (datetime, value) to list based on tag
            result.setdefault(tag_name, []).append([dt, value])

    # replace value with an array of highchart series (datetime, value)
    for d in detail['series']:
        d['data'] = result[d['data']]

    # set tag_id inside detail
    detail['tagId'] = tag_id

    return detail


# please check schema.json
# key: page_name (ex: trend-unit-1)
# value: detail (ex: {tag_name: subdetail}
def create_response(page):
    # query latest row from mongodb. there is only one row in a list
    row = db[COLL].find().sort("_id", -1).limit(1)[0]

    response = list()
    for tag_id, detail in page.iteritems():
        if detail['type'] == 'gauge':
            tag_name = detail['value']

            # no grammar means no computation to yield the value. easy
            # and ensure tag_name exists in the latest mongodb document
            if 'grammar' not in detail and detail['value'] in row['Tags']:
                # set value
                if tag_name not in row['Tags']:
                    continue
                detail['value'] = row['Tags'][tag_name]['Value']

                # TODO just for temporary
                if tag_id == 'gauge-outgoing-power':
                    detail['value'] = detail['value'] / 1000.0
                elif tag_id == 'active-power':
                    detail['value'] = detail['value'] / 10.0
                elif tag_id == 'product-ph' or tag_id == 'ph-product':
                    detail['value'] = detail['value'] / 10.0

            # sum value from several tag names
            if 'grammar' in detail and detail['grammar'] == 'sum':
                detail['value'] = grammar_sum(detail, row)

                if tag_id == 'active-current':
                    detail['value'] = detail['value'] / 1000.0

            # sum value from several tag names
            if 'grammar' in detail and detail['grammar'] == 'mean':
                detail['value'] = grammar_mean(detail, row)
                
            if 'grammar' in detail and detail['grammar'] == 'percentage':
                detail['value'] = grammar_percentage(detail, row)

            # set tag_id inside detail
            detail['tagId'] = tag_id

            response.append(detail)

        if detail['type'] == 'chart':
            detail = get_chart_data(detail, tag_id)
            response.append(detail)
            
        # TODO merge with twoColumnsTable and threeColumnsTable
        if detail['type'] == 'oneColumnTable':
            final_data = list()
            # loop through data to render row in one column table
            for d in detail['data']:
                # default row. just value
                if d['type'] == 'default':
                    tag_name = d['value']
                    d['value'] = '#NA'
                    if tag_name in row['Tags']:
                        # TODO just for temporary
                        if tag_id == 'outgoing-1' and d['name'] == 'Power':
                            d['value'] = \
                                "{:,.2f}".format(row['Tags'][tag_name]['Value'] / 1000.0)
                        else:
                            d['value'] = \
                                "{:,.2f}".format(row['Tags'][tag_name]['Value'])
                    final_data.append(d)

                # row with general status (it consists of run and fault)
                if d['type'] == 'general':
                    tag_name = d['run']
                    if tag_name not in row['Tags']:
                        # the row is still rendered without value (NA) because
                        # value is undefined. logic is in template
                        del d['run']
                    else:
                        d['run'] = \
                            "{:,.2f}".format(row['Tags'][tag_name]['Value'])

                    tag_name = d['fault']
                    if tag_name not in row['Tags']:
                        # the row is still rendered without value (NA) because
                        # value is undefined. logic is in template
                        del d['fault']
                    else:
                        d['fault'] = row['Tags'][tag_name]['Value']

                    final_data.append(d)

                if d['type'] == 'indicator' or d['type'] == 'indicatorInverse':
                    tag_name = d['value']
                    if tag_name not in row['Tags']:
                        # the row is still rendered without value (NA) because
                        # value is undefined. logic is in template
                        del d['value']
                    else:
                        d['value'] = row['Tags'][tag_name]['Value']

                    final_data.append(d)

            # set tag_id inside detail
            detail['tagId'] = tag_id
            detail['data'] = final_data

            response.append(detail)
            
        if detail['type'] == 'twoColumnsTable' \
                or detail['type'] == 'threeColumnsTable':
            final_data = list()
            # iterate each row
            for d in detail['data']:
                if d['type'] == 'default':
                    if 'grammar' not in d:
                        tag_name = d['value']
                        d['value'] = '#NA'
                        if tag_name in row['Tags']:
                            d['value'] = row['Tags'][tag_name]['Value']

                            # TODO temporary adjustment
                            if tag_id == 'power-plant-info' \
                                    and d['name'] == 'TOTAL POWER':
                                d['value'] = "{:,.2f}".format(d['value'] / 1000.0)
                            elif tag_id == 'total-power' \
                                    and d['name'] == 'TOTAL':
                                d['value'] = "{:,.2f}".format(d['value'] / 1000.0)
                            elif tag_id == 'information-left' \
                                    and d['name'] != 'REACTIVE POWER':
                                d['value'] = "{:,.2f}".format(d['value'] / 10.0)
                            elif tag_id == 'information-left' \
                                    and d['name'] == 'REACTIVE POWER':
                                d['value'] = "{:,.2f}".format(d['value'] / 100.0)

                        final_data.append(d)

                    # get sum value from several tag names
                    if 'grammar' in d and d['grammar'] == 'sum':
                        d['value'] = grammar_sum(d, row)
                        final_data.append(d)

                    # get mean value from several tag names
                    if 'grammar' in d and d['grammar'] == 'div':
                        d['value'] = grammar_div(d, row)
                        if d['value'] != 'NaN':
                            d['value'] = "{:,.3f}".format(d['value'])
                        final_data.append(d)

                    # get mean value from several tag names
                    if 'grammar' in d and d['grammar'] == 'mean':
                        d['value'] = grammar_mean(d, row)
                        if d['value'] != 'NaN':
                            # # TODO temporary
                            if tag_id == 'information-right':
                                d['value'] = \
                                    "{:,.2f}".format(d['value'] / 100.0)
                            else:
                                d['value'] = "{:,.2f}".format(d['value'])
                        final_data.append(d)

                # row with general status (it consists of run and fault)
                if d['type'] == 'general':
                    tag_name = d['run']
                    if tag_name not in row['Tags']:
                        # the row is still rendered without value (NA) because
                        # value is undefined. logic is in template
                        del d['run']
                    else:
                        d['run'] = \
                            "{:,.2f}".format(row['Tags'][tag_name]['Value'])

                    tag_name = d['fault']
                    if tag_name not in row['Tags']:
                        # the row is still rendered without value (NA) because
                        # value is undefined. logic is in template
                        del d['fault']
                    else:
                        d['fault'] = row['Tags'][tag_name]['Value']

                    final_data.append(d)

                if d['type'] == 'running' \
                        or d['type'] == 'indicator' \
                        or d['type'] == 'indicatorInverse':
                    tag_name = d['value']
                    if tag_name not in row['Tags']:
                        # the row is still rendered without value (NA) because
                        # value is undefined. logic is in template
                        del d['value']
                    else:
                        d['value'] = row['Tags'][tag_name]['Value']

                    final_data.append(d)

                if d['type'] == 'image':
                    final_data.append(d)

                if d['type'] == 'report':
                    tag_name = d['value']
                    d['value'] = '#NA'

                    try:
                        row_report = db[COLL_REPORT].find().sort("_id", -1).limit(1)[0]
                        if tag_name in row_report['Tags']:
                            d['value'] = \
                                "{:,.2f}".format(row_report['Tags'][tag_name]['Value'])
                            if d['value'] == 'nan':
                                d['value'] = '#NA'
                    except Exception:
                        pass
                    final_data.append(d)

            # set tag_id inside detail
            detail['tagId'] = tag_id
            detail['data'] = final_data

            response.append(detail)

        if detail['type'] == 'bars':
            final_data = list()
            for d in detail['data']:
                tag_name = d['value']
                # d['value'] = '#NA'

                if 'grammar' not in d:
                    if tag_name in row['Tags']:
                        # TODO just for temporary
                        if tag_id == 'voltage':
                            if d['text'] in ['L1-L2', 'L2-L3', 'L3-L1']:
                                d['valueStr'] = \
                                    "{:,.2f}".format((row['Tags'][tag_name]['Value'] + 65536) / 100.0)

                                d['value'] = (row['Tags'][tag_name]['Value'] + 65536) / 100.0
                            else:
                                d['valueStr'] = \
                                    "{:,.2f}".format(row['Tags'][tag_name]['Value'] / 100.0)

                                d['value'] = row['Tags'][tag_name]['Value'] / 100.0
                        elif tag_id == 'current':
                            d['valueStr'] = \
                                "{:,.2f}".format(row['Tags'][tag_name]['Value'] / 1000.0)

                            d['value'] = row['Tags'][tag_name]['Value'] / 1000.0
                        else:
                            d['valueStr'] = \
                                "{:,.2f}".format(row['Tags'][tag_name]['Value'])

                            d['value'] = row['Tags'][tag_name]['Value']
                    final_data.append(d)

                if 'grammar' in d and d['grammar'] == 'substract':
                    d['valueStr'] = "{:,.2f}".format(grammar_substract(d, row))
                    d['value'] = grammar_substract(d, row)
                    final_data.append(d)

            detail['tagId'] = tag_id
            detail['data'] = final_data

            # print detail
            response.append(detail)

        if detail['type'] == 'fourIndicators':
            final_data = list()
            for d in detail['data']:
                tag_name = d['value']
                d['value'] = '#NA'
                if tag_name in row['Tags']:
                    d['value'] = row['Tags'][tag_name]['Value']
                final_data.append(d)

            detail['tagId'] = tag_id
            detail['data'] = final_data

            response.append(detail)

        if detail['type'] == 'image':
            response.append(detail)

        if detail['type'] == 'title':
            response.append(detail)

        if detail['type'] == 'spacer':
            detail['tagId'] = tag_id
            response.append(detail)
    return response


#live pages
# def live_pretreatment_api(request):
#     message = dumps(list(db.glm.find().sort("_id",-1).limit(1)))
#     return HttpResponse(message, content_type='application/json') 
   

@login_required
def live_overview_api(request):
    page_id = 'live-overview'

    page_schema = get_page_schema(page_id)
    response = create_response(page_schema)

    return HttpResponse(json.dumps(response), content_type='application/json') 


@login_required
def live_intake_api(request):
    page_id = 'live-intake'

    page_schema = get_page_schema(page_id)
    response = create_response(page_schema)

    return HttpResponse(json.dumps(response), content_type='application/json') 


@login_required
def live_pretreatment_api(request):
    page_id = 'live-pretreatment'

    page_schema = get_page_schema(page_id)
    response = create_response(page_schema)

    return HttpResponse(json.dumps(response), content_type='application/json') 


@login_required
def live_osmosis_api(request):
    page_id = 'live-osmosis'

    page_schema = get_page_schema(page_id)
    response = create_response(page_schema)

    return HttpResponse(json.dumps(response), content_type='application/json') 


@login_required
def live_product_api(request):
    page_id = 'live-product'

    page_schema = get_page_schema(page_id)
    response = create_response(page_schema)

    return HttpResponse(json.dumps(response), content_type='application/json') 


@login_required
def live_reject_api(request):
    page_id = 'live-reject'

    page_schema = get_page_schema(page_id)
    response = create_response(page_schema)

    return HttpResponse(json.dumps(response), content_type='application/json') 


@login_required
def live_energy_api(request):
    page_id = 'live-energy'

    page_schema = get_page_schema(page_id)
    response = create_response(page_schema)

    return HttpResponse(json.dumps(response), content_type='application/json') 


@login_required
def report_api(request):
    page_id = 'report'

    page_schema = get_page_schema(page_id)
    response = create_response(page_schema)

    return HttpResponse(json.dumps(response), content_type='application/json') 


@login_required
def trend_api(request):
    page_id = 'trend'

    page_schema = get_page_schema(page_id)
    response = create_response(page_schema)

    return HttpResponse(json.dumps(response), content_type='application/json') 


@login_required
def get_historical_trend(request):
    # parameters validation
    if 'page' not in request.GET or 'eq' not in request.GET \
            or 'rows' not in request.GET or 'start' not in request.GET:
        response = {
            'success': -1,
            'error_message': 'Parameters are not complete.'
        }
        return HttpResponse(json.dumps(response),
                            content_type='application/json')

    first = False
    if 'first' in request.GET and request.GET['first'] == 'true':
        first = True

    page = request.GET['page']
    tag_id = request.GET['eq']
    rows = int(request.GET['rows'])

    # start of query from the latest rows, not from the earliest rows
    # later, query row using sort and reverse
    start = int(request.GET['start'])
    
    page_schema = get_page_schema(page)

    detail = get_chart_data(page_schema[tag_id], tag_id, start, rows, first)

    response = list()
    response.append(detail)

    return HttpResponse(json.dumps(response), content_type='application/json')
    

@login_required
def download_trend_csv(request):
    if 'page' not in request.GET and 'eq' not in request.GET:
        return HttpResponse('No parameter')

    page = request.GET['page']
    equipment = request.GET['eq']

    # TODO need to review
    dt = timezone.localtime(timezone.make_aware(datetime.now()))
    dt_str = dt.strftime('%Y%m%d-%H%M%S')

    filename = '%s-%s-%s.csv' % (page, equipment, dt_str)

    # prepare header response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="%s"' % filename

    # create the csv writer
    writer = csv.writer(response)

    # get the latest n rows
    total_data = 60
    rows = db[COLL].find().sort("_id",-1).limit(total_data)
    if rows.count() == 0:
        return HttpResponse('Fail to retrieve csv data. No data.')

    # get tags
    schema = get_page_schema(page)
    tags = map(lambda i: i['data'], schema[equipment]['series'])

    # write to csv in response with ascending time
    rows = list(rows)
    rows.reverse()
    for row in rows:
        # line = [row['SentTimestamp']]
        date = row['SentDatetime'].strftime('%Y-%m-%d')
        time = row['SentDatetime'].strftime('%H:%M:%S')
        line = [date, time]
        for tag in tags:
            line.append(row['Tags'][tag]['Value'])

        writer.writerow(line)

    return response


# def live_osmosis_api(request):
#     message =  dumps(list(db.glm.find().sort("_id",-1).limit(1)))
#     return HttpResponse(message, content_type='application/json') 
#


# def live_product_api(request):
#     message =  dumps(list(db.glm.find().sort("_id",-1).limit(1)))
#     return HttpResponse(message, content_type='application/json') 

# def live_reject_api(request):
#     message =  dumps(list(db.glm.find().sort("_id",-1).limit(1)))
#     return HttpResponse(message, content_type='application/json') 
#
# def live_energy_api(request):
#     message =  dumps(list(db.glm.find().sort("_id",-1).limit(1)))
#     return HttpResponse(message, content_type='application/json') 


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


@login_required
def latest(request):
    message = dumps(list(db.glm.find().sort("_id",-1).limit(1)))
    return HttpResponse(message, content_type='application/json') 
