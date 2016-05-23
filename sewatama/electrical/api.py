# http://eli.thegreenplace.net/2009/11/28/python-internals-working-with-python-asts

import simplejson as json
import pymongo
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, Http404, HttpResponseServerError
from pymongo import MongoClient

from bson.json_util import dumps

import os

db = MongoClient().inetscada


def modify_datetime(dt):
    dt = dt.replace(microsecond=0)
    return dt.isoformat()


def get_page_schema(page_id):
    f = open('electrical/conf/schema.json')
    schema = json.loads(f.read())
    return schema[page_id]


def grammar_sum(detail, row):
    total_value = 0
    for tag_name in detail['value']:
        if tag_name not in row['Tags']:
            continue
        total_value += float(row['Tags'][tag_name]['Value'])

    return total_value


def grammar_mean(detail, row):
    total_value = grammar_sum(detail, row)
    return "{:,.2f}".format(total_value / len(detail['value']))


def create_response(page):
    # query latest row from mongodb. there is only one row in a list
    row = db.ss.find().sort("_id", -1).limit(1)[0]

    response = list()
    for tag_id, detail in page.iteritems():
        if detail['type'] == 'gauge':
            # no grammar means no computation to yield the value. easy
            # and ensure tag_name exists in the latest mongodb document
            if 'grammar' not in detail and detail['value'] in row['Tags']:
                # set value
                tag_name = detail['value']
                if tag_name not in row['Tags']:
                    continue
                detail['value'] = row['Tags'][tag_name]['Value']

                # TODO just for temporary
                if tag_id == 'gauge-outgoing-power':
                    detail['value'] = detail['value'] / 1000

            # sum value from several tag names
            if 'grammar' in detail and detail['grammar'] == 'sum':
                detail['value'] = grammar_sum(detail, row)
                
            # set tag_id inside detail
            detail['tagId'] = tag_id

            response.append(detail)

        if detail['type'] == 'chart':
            # get a list of tag name
            tag_names = map(lambda i: i['data'], detail['series'])

            # get the latest 60 rows
            rows = list(db.ss.find().sort("_id", -1).limit(10))

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
                    
                    print r['SentDatetime'], dt
                    value = float("{:.2f}".format(r['Tags'][tag_name]['Value']))

                    # if key is not in dictionary, create key with list as value
                    # append a pair of (datetime, value) to list based on tag
                    result.setdefault(tag_name, []).append([dt, value])

            # replace value with an array of highchart series (datetime, value)
            for d in detail['series']:
                d['data'] = result[d['data']]

            # set tag_id inside detail
            detail['tagId'] = tag_id

            response.append(detail)
            
        if detail['type'] == 'oneColumnTable':
            final_data = list()
            # loop through data to render row in one column table
            for d in detail['data']:
                # default row. just value
                if d['type'] == 'default':
                    tag_name = d['value']
                    d['value'] = '#NA'
                    if tag_name in row['Tags']:
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
            
        if detail['type'] == 'threeColumnsTable':
            final_data = list()
            # iterate each row
            for d in detail['data']:
                if d['type'] == 'default':
                    if 'grammar' not in d:
                        tag_name = d['value']
                        d['value'] = '#NA'
                        if tag_name in row['Tags']:
                            d['value'] = \
                                "{:,.2f}".format(row['Tags'][tag_name]['Value'])
                        final_data.append(d)

                    # get sum value from several tag names
                    if 'grammar' in d and d['grammar'] == 'sum':
                        d['value'] = grammar_sum(d, row)
                        final_data.append(d)

                    # get mean value from several tag names
                    if 'grammar' in d and d['grammar'] == 'mean':
                        d['value'] = grammar_mean(d, row)
                        final_data.append(d)

                if d['type'] == 'image':
                    final_data.append(d)

            # set tag_id inside detail
            detail['tagId'] = tag_id
            detail['data'] = final_data

            response.append(detail)

        if detail['type'] == 'image':
            response.append(detail)
    return response


@login_required
def electrical_overview_outgoing_1(request):
    page_id = 'electrical-overview-outgoing-1'

    page_schema = get_page_schema(page_id)
    response = create_response(page_schema)

    return HttpResponse(json.dumps(response), content_type='application/json') 


@login_required
def electrical_sld_outgoing_1(request):
    page_id = 'electrical-sld-outgoing-1'

    page_schema = get_page_schema(page_id)
    response = create_response(page_schema)

    return HttpResponse(json.dumps(response), content_type='application/json') 


@login_required
def genset_overview_outgoing_1(request):
    page_id = 'genset-overview-outgoing-1'

    page_schema = get_page_schema(page_id)
    response = create_response(page_schema)

    return HttpResponse(json.dumps(response), content_type='application/json') 


@login_required
def genset_outgoing_1_unit_1(request):
    x = [
        # ('obj1', ''),
        ('obj2', 'SS\HSD_NPN0\RT4\GEN01\AVG_A'),
        ('obj3', 'SS\HSD_NPN0\RT4\GEN01\F'),
        ('obj4', 'SS\HSD_NPN0\RT4\GEN01\P_TOT'),
        ('obj5', 'SS\HSD_NPN0\RT4\GEN01\PF'),
        ('obj6', 'SS\HSD_NPN0\RT4\GEN01\RPM'),
        ('obj7', 'SS\HSD_NPN0\RT4\GEN01\CYL_EXH_TMP_001'),
        ('obj8', 'SS\HSD_NPN0\RT4\GEN01\CYL_EXH_TMP_002'),
        ('obj9', 'SS\HSD_NPN0\RT4\GEN01\CYL_EXH_TMP_003'),
        ('obj10', 'SS\HSD_NPN0\RT4\GEN01\CYL_EXH_TMP_004'),
        ('obj11', 'SS\HSD_NPN0\RT4\GEN01\CYL_EXH_TMP_005'),
        ('obj12', 'SS\HSD_NPN0\RT4\GEN01\CYL_EXH_TMP_006'),
        ('obj13', 'SS\HSD_NPN0\RT4\GEN01\CYL_EXH_TMP_007'),
        ('obj14', 'SS\HSD_NPN0\RT4\GEN01\CYL_EXH_TMP_008'),
        ('obj15', 'SS\HSD_NPN0\RT4\GEN01\CYL_EXH_TMP_009'),
        ('obj16', 'SS\HSD_NPN0\RT4\GEN01\CYL_EXH_TMP_010'),
        ('obj17', 'SS\HSD_NPN0\RT4\GEN01\CYL_EXH_TMP_011'),
        ('obj18', 'SS\HSD_NPN0\RT4\GEN01\CYL_EXH_TMP_012'),
        ('obj19', 'SS\HSD_NPN0\RT4\GEN01\CYL_EXH_TMP_013'),
        ('obj20', 'SS\HSD_NPN0\RT4\GEN01\CYL_EXH_TMP_014'),
        ('obj21', 'SS\HSD_NPN0\RT4\GEN01\CYL_EXH_TMP_015'),
        ('obj22', 'SS\HSD_NPN0\RT4\GEN01\CYL_EXH_TMP_016'),

        ('obj24', 'SS\HSD_NPN0\RT4\GEN01\ENG_OIL_PRS'),
        ('obj25', 'SS\HSD_NPN0\RT4\GEN01\ENG_OIL_TMP'),
        ('obj26', 'SS\HSD_NPN0\RT4\GEN01\FUL_PRS'),
        ('obj27', 'SS\HSD_NPN0\RT4\GEN01\ENG_COL_TMP'),
        ('obj28', 'SS\HSD_NPN0\RT4\GEN01\WH'),
        ('obj29', 'SS\HSD_NPN0\RT4\GEN01\FUL_CONS'),
        ('obj30', 'SS\HSD_NPN0\RT4\GEN01\FUL_CONS_RAT'),
        ('obj31', 'SS\HSD_NPN0\RT4\GEN01\FUL_PRS'),
        ('obj32', 'SS\HSD_NPN0\RT4\GEN01\OPR_HRS'),
        ('obj33', 'SS\HSD_NPN0\RT4\GEN01\BAT_V_001'),
        ('obj34', 'SS\HSD_NPN0\RT4\GEN01\R_TOT'),
        ('obj35', 'SS\HSD_NPN0\RT4\GEN01\S_TOT'),
        ('obj36', 'SS\HSD_NPN0\RT4\GEN01\AVG_A'),
        ('obj37', 'SS\HSD_NPN0\RT4\GEN01\CAL_GND_A'),
        ('obj38', 'SS\HSD_NPN0\RT4\GEN01\L1_L2_V'),
        ('obj39', 'SS\HSD_NPN0\RT4\GEN01\L2_L3_V'),
        ('obj40', 'SS\HSD_NPN0\RT4\GEN01\L3_L1_V'),
        ('obj41', 'SS\HSD_NPN0\RT4\GEN01\L1_N_V'),
        ('obj42', 'SS\HSD_NPN0\RT4\GEN01\L2_N_V'),
        ('obj43', 'SS\HSD_NPN0\RT4\GEN01\L3_N_V'),
        ('obj44', 'SS\HSD_NPN0\RT4\GEN01\WDG_PHSA_TMP'),
        ('obj45', 'SS\HSD_NPN0\RT4\GEN01\WDG_PHSB_TMP'),
        ('obj46', 'SS\HSD_NPN0\RT4\GEN01\WDG_PHSC_TMP'),
        ('obj47', 'SS\HSD_NPN0\RT4\GEN01\RER_BRG_TMP'),
        ('obj48', 'SS\HSD_NPN0\RT4\GEN01\AIR_FIL_DP'),
        ('obj49', 'SS\HSD_NPN0\RT4\GEN01\FUL_FIL_DP'),
        ('obj50', 'SS\HSD_NPN0\RT4\GEN01\OIL_FIL_DP'),
        ('obj51', 'SS\HSD_NPN0\RT4\GEN01\EXH_MAN_TMP_001'),
        ('obj52', 'SS\HSD_NPN0\RT4\GEN01\EXH_MAN_TMP_002'),
        ('obj53', 'SS\HSD_NPN0\RT4\GEN01\CRC_PRS'),
        ('obj54', 'SS\HSD_NPN0\RT4\GEN01\BST_PRS'),
    ]

    # query latest row from mongodb. there is only one row in a list
    row = db.ss.find().sort("_id", -1).limit(1)[0]

    # replace tag name with tag id for security reason
    data = dict()
    for i in x:
        tag_id, tag_name = i[0], i[1]
        data[tag_id] = row['Tags'][tag_name]

        # remove for security reason
        if 'Name' in data[tag_id]:
            del data[tag_id]['Name']

    # TODO special cases because they have more than one tag name
    # and need sum operation

    # obj1
    value1 = float(row['Tags']['SS\HSD_NPN0\RT4\GEN01\L1_L2_V']['Value'])
    value2 = float(row['Tags']['SS\HSD_NPN0\RT4\GEN01\L2_L3_V']['Value']) 
    value3 = float(row['Tags']['SS\HSD_NPN0\RT4\GEN01\L3_L1_V']['Value'])

    data['obj1'] = dict()
    data['obj1']['Value'] = (value1 + value2 + value3) / 3

    value1 = float(row['Tags']['SS\HSD_NPN0\RT4\GEN01\CYL_EXH_TMP_001']['Value']) 
    value2 = float(row['Tags']['SS\HSD_NPN0\RT4\GEN01\CYL_EXH_TMP_002']['Value'])
    value3 = float(row['Tags']['SS\HSD_NPN0\RT4\GEN01\CYL_EXH_TMP_003']['Value'])
    value4 = float(row['Tags']['SS\HSD_NPN0\RT4\GEN01\CYL_EXH_TMP_004']['Value'])
    value5 = float(row['Tags']['SS\HSD_NPN0\RT4\GEN01\CYL_EXH_TMP_005']['Value'])
    value6 = float(row['Tags']['SS\HSD_NPN0\RT4\GEN01\CYL_EXH_TMP_006']['Value'])
    value7 = float(row['Tags']['SS\HSD_NPN0\RT4\GEN01\CYL_EXH_TMP_007']['Value'])
    value8 = float(row['Tags']['SS\HSD_NPN0\RT4\GEN01\CYL_EXH_TMP_008']['Value'])
    value9 = float(row['Tags']['SS\HSD_NPN0\RT4\GEN01\CYL_EXH_TMP_009']['Value'])
    value10 = float(row['Tags']['SS\HSD_NPN0\RT4\GEN01\CYL_EXH_TMP_010']['Value']) 
    value11 = float(row['Tags']['SS\HSD_NPN0\RT4\GEN01\CYL_EXH_TMP_011']['Value'])
    value12 = float(row['Tags']['SS\HSD_NPN0\RT4\GEN01\CYL_EXH_TMP_012']['Value'])
    value13 = float(row['Tags']['SS\HSD_NPN0\RT4\GEN01\CYL_EXH_TMP_013']['Value'])
    value14 = float(row['Tags']['SS\HSD_NPN0\RT4\GEN01\CYL_EXH_TMP_014']['Value'])
    value15 = float(row['Tags']['SS\HSD_NPN0\RT4\GEN01\CYL_EXH_TMP_015']['Value'])
    value16 = float(row['Tags']['SS\HSD_NPN0\RT4\GEN01\CYL_EXH_TMP_016']['Value'])

    data['obj23'] = dict()
    data['obj23']['Value'] = (value1 + value2 + value3 + value4 + value5 \
                             + value6 + value7 + value8 + value9 + value10 \
                             + value11 + value12 + value13 + value14 + value15 \
                             + value16) / 16

    message = { 'success': 0, 'data': data }
    return HttpResponse(dumps(message), content_type='application/json') 
    

@login_required
def genset_outgoing_1_unit_2(request):
    x = [
        # ('obj1', ''),
        ('obj2', 'SS\HSD_NPN0\RT4\GEN02\AVG_A'),
        ('obj3', 'SS\HSD_NPN0\RT4\GEN02\F'),
        ('obj4', 'SS\HSD_NPN0\RT4\GEN02\P_TOT'),
        ('obj5', 'SS\HSD_NPN0\RT4\GEN02\PF'),
        ('obj6', 'SS\HSD_NPN0\RT4\GEN02\RPM'),
        ('obj7', 'SS\HSD_NPN0\RT4\GEN02\CYL_EXH_TMP_001'),
        ('obj8', 'SS\HSD_NPN0\RT4\GEN02\CYL_EXH_TMP_002'),
        ('obj9', 'SS\HSD_NPN0\RT4\GEN02\CYL_EXH_TMP_003'),
        ('obj10', 'SS\HSD_NPN0\RT4\GEN02\CYL_EXH_TMP_004'),
        ('obj11', 'SS\HSD_NPN0\RT4\GEN02\CYL_EXH_TMP_005'),
        ('obj12', 'SS\HSD_NPN0\RT4\GEN02\CYL_EXH_TMP_006'),
        ('obj13', 'SS\HSD_NPN0\RT4\GEN02\CYL_EXH_TMP_007'),
        ('obj14', 'SS\HSD_NPN0\RT4\GEN02\CYL_EXH_TMP_008'),
        ('obj15', 'SS\HSD_NPN0\RT4\GEN02\CYL_EXH_TMP_009'),
        ('obj16', 'SS\HSD_NPN0\RT4\GEN02\CYL_EXH_TMP_010'),
        ('obj17', 'SS\HSD_NPN0\RT4\GEN02\CYL_EXH_TMP_011'),
        ('obj18', 'SS\HSD_NPN0\RT4\GEN02\CYL_EXH_TMP_012'),
        ('obj19', 'SS\HSD_NPN0\RT4\GEN02\CYL_EXH_TMP_013'),
        ('obj20', 'SS\HSD_NPN0\RT4\GEN02\CYL_EXH_TMP_014'),
        ('obj21', 'SS\HSD_NPN0\RT4\GEN02\CYL_EXH_TMP_015'),
        ('obj22', 'SS\HSD_NPN0\RT4\GEN02\CYL_EXH_TMP_016'),

        ('obj24', 'SS\HSD_NPN0\RT4\GEN02\ENG_OIL_PRS'),
        ('obj25', 'SS\HSD_NPN0\RT4\GEN02\ENG_OIL_TMP'),
        ('obj26', 'SS\HSD_NPN0\RT4\GEN02\FUL_PRS'),
        ('obj27', 'SS\HSD_NPN0\RT4\GEN02\ENG_COL_TMP'),
        ('obj28', 'SS\HSD_NPN0\RT4\GEN02\WH'),
        ('obj29', 'SS\HSD_NPN0\RT4\GEN02\FUL_CONS'),
        ('obj30', 'SS\HSD_NPN0\RT4\GEN02\FUL_CONS_RAT'),
        ('obj31', 'SS\HSD_NPN0\RT4\GEN02\FUL_PRS'),
        ('obj32', 'SS\HSD_NPN0\RT4\GEN02\OPR_HRS'),
        ('obj33', 'SS\HSD_NPN0\RT4\GEN02\BAT_V_001'),
        ('obj34', 'SS\HSD_NPN0\RT4\GEN02\R_TOT'),
        ('obj35', 'SS\HSD_NPN0\RT4\GEN02\S_TOT'),
        ('obj36', 'SS\HSD_NPN0\RT4\GEN02\AVG_A'),
        ('obj37', 'SS\HSD_NPN0\RT4\GEN02\CAL_GND_A'),
        ('obj38', 'SS\HSD_NPN0\RT4\GEN02\L1_L2_V'),
        ('obj39', 'SS\HSD_NPN0\RT4\GEN02\L2_L3_V'),
        ('obj40', 'SS\HSD_NPN0\RT4\GEN02\L3_L1_V'),
        ('obj41', 'SS\HSD_NPN0\RT4\GEN02\L1_N_V'),
        ('obj42', 'SS\HSD_NPN0\RT4\GEN02\L2_N_V'),
        ('obj43', 'SS\HSD_NPN0\RT4\GEN02\L3_N_V'),
        ('obj44', 'SS\HSD_NPN0\RT4\GEN02\WDG_PHSA_TMP'),
        ('obj45', 'SS\HSD_NPN0\RT4\GEN02\WDG_PHSB_TMP'),
        ('obj46', 'SS\HSD_NPN0\RT4\GEN02\WDG_PHSC_TMP'),
        ('obj47', 'SS\HSD_NPN0\RT4\GEN02\RER_BRG_TMP'),
        ('obj48', 'SS\HSD_NPN0\RT4\GEN02\AIR_FIL_DP'),
        ('obj49', 'SS\HSD_NPN0\RT4\GEN02\FUL_FIL_DP'),
        ('obj50', 'SS\HSD_NPN0\RT4\GEN02\OIL_FIL_DP'),
        ('obj51', 'SS\HSD_NPN0\RT4\GEN02\EXH_MAN_TMP_001'),
        ('obj52', 'SS\HSD_NPN0\RT4\GEN02\EXH_MAN_TMP_002'),
        ('obj53', 'SS\HSD_NPN0\RT4\GEN02\CRC_PRS'),
        ('obj54', 'SS\HSD_NPN0\RT4\GEN02\BST_PRS'),
    ]

    # query latest row from mongodb. there is only one row in a list
    row = db.ss.find().sort("_id", -1).limit(1)[0]

    # replace tag name with tag id for security reason
    data = dict()
    for i in x:
        tag_id, tag_name = i[0], i[1]
        data[tag_id] = row['Tags'][tag_name]

        # remove for security reason
        if 'Name' in data[tag_id]:
            del data[tag_id]['Name']

    # TODO special cases because they have more than one tag name
    # and need sum operation

    # obj1
    value1 = float(row['Tags']['SS\HSD_NPN0\RT4\GEN02\L1_L2_V']['Value'])
    value2 = float(row['Tags']['SS\HSD_NPN0\RT4\GEN02\L2_L3_V']['Value']) 
    value3 = float(row['Tags']['SS\HSD_NPN0\RT4\GEN02\L3_L1_V']['Value'])

    data['obj1'] = dict()
    data['obj1']['Value'] = (value1 + value2 + value3) / 3

    value1 = float(row['Tags']['SS\HSD_NPN0\RT4\GEN02\CYL_EXH_TMP_001']['Value']) 
    value2 = float(row['Tags']['SS\HSD_NPN0\RT4\GEN02\CYL_EXH_TMP_002']['Value'])
    value3 = float(row['Tags']['SS\HSD_NPN0\RT4\GEN02\CYL_EXH_TMP_003']['Value'])
    value4 = float(row['Tags']['SS\HSD_NPN0\RT4\GEN02\CYL_EXH_TMP_004']['Value'])
    value5 = float(row['Tags']['SS\HSD_NPN0\RT4\GEN02\CYL_EXH_TMP_005']['Value'])
    value6 = float(row['Tags']['SS\HSD_NPN0\RT4\GEN02\CYL_EXH_TMP_006']['Value'])
    value7 = float(row['Tags']['SS\HSD_NPN0\RT4\GEN02\CYL_EXH_TMP_007']['Value'])
    value8 = float(row['Tags']['SS\HSD_NPN0\RT4\GEN02\CYL_EXH_TMP_008']['Value'])
    value9 = float(row['Tags']['SS\HSD_NPN0\RT4\GEN02\CYL_EXH_TMP_009']['Value'])
    value10 = float(row['Tags']['SS\HSD_NPN0\RT4\GEN02\CYL_EXH_TMP_010']['Value']) 
    value11 = float(row['Tags']['SS\HSD_NPN0\RT4\GEN02\CYL_EXH_TMP_011']['Value'])
    value12 = float(row['Tags']['SS\HSD_NPN0\RT4\GEN02\CYL_EXH_TMP_012']['Value'])
    value13 = float(row['Tags']['SS\HSD_NPN0\RT4\GEN02\CYL_EXH_TMP_013']['Value'])
    value14 = float(row['Tags']['SS\HSD_NPN0\RT4\GEN02\CYL_EXH_TMP_014']['Value'])
    value15 = float(row['Tags']['SS\HSD_NPN0\RT4\GEN02\CYL_EXH_TMP_015']['Value'])
    value16 = float(row['Tags']['SS\HSD_NPN0\RT4\GEN02\CYL_EXH_TMP_016']['Value'])

    data['obj23'] = dict()
    data['obj23']['Value'] = (value1 + value2 + value3 + value4 + value5 \
                             + value6 + value7 + value8 + value9 + value10 \
                             + value11 + value12 + value13 + value14 + value15 \
                             + value16) / 16

    message = { 'success': 0, 'data': data }
    return HttpResponse(dumps(message), content_type='application/json') 
    

@login_required
def genset_outgoing_1_unit_3(request):
    x = [
        # ('obj1', ''),
        ('obj2', 'SS\HSD_NPN0\RT4\GEN03\AVG_A'),
        ('obj3', 'SS\HSD_NPN0\RT4\GEN03\F'),
        ('obj4', 'SS\HSD_NPN0\RT4\GEN03\P_TOT'),
        ('obj5', 'SS\HSD_NPN0\RT4\GEN03\PF'),
        ('obj6', 'SS\HSD_NPN0\RT4\GEN03\RPM'),
        ('obj7', 'SS\HSD_NPN0\RT4\GEN03\CYL_EXH_TMP_001'),
        ('obj8', 'SS\HSD_NPN0\RT4\GEN03\CYL_EXH_TMP_002'),
        ('obj9', 'SS\HSD_NPN0\RT4\GEN03\CYL_EXH_TMP_003'),
        ('obj10', 'SS\HSD_NPN0\RT4\GEN03\CYL_EXH_TMP_004'),
        ('obj11', 'SS\HSD_NPN0\RT4\GEN03\CYL_EXH_TMP_005'),
        ('obj12', 'SS\HSD_NPN0\RT4\GEN03\CYL_EXH_TMP_006'),
        ('obj13', 'SS\HSD_NPN0\RT4\GEN03\CYL_EXH_TMP_007'),
        ('obj14', 'SS\HSD_NPN0\RT4\GEN03\CYL_EXH_TMP_008'),
        ('obj15', 'SS\HSD_NPN0\RT4\GEN03\CYL_EXH_TMP_009'),
        ('obj16', 'SS\HSD_NPN0\RT4\GEN03\CYL_EXH_TMP_010'),
        ('obj17', 'SS\HSD_NPN0\RT4\GEN03\CYL_EXH_TMP_011'),
        ('obj18', 'SS\HSD_NPN0\RT4\GEN03\CYL_EXH_TMP_012'),
        ('obj19', 'SS\HSD_NPN0\RT4\GEN03\CYL_EXH_TMP_013'),
        ('obj20', 'SS\HSD_NPN0\RT4\GEN03\CYL_EXH_TMP_014'),
        ('obj21', 'SS\HSD_NPN0\RT4\GEN03\CYL_EXH_TMP_015'),
        ('obj22', 'SS\HSD_NPN0\RT4\GEN03\CYL_EXH_TMP_016'),

        ('obj24', 'SS\HSD_NPN0\RT4\GEN03\ENG_OIL_PRS'),
        ('obj25', 'SS\HSD_NPN0\RT4\GEN03\ENG_OIL_TMP'),
        ('obj26', 'SS\HSD_NPN0\RT4\GEN03\FUL_PRS'),
        ('obj27', 'SS\HSD_NPN0\RT4\GEN03\ENG_COL_TMP'),
        ('obj28', 'SS\HSD_NPN0\RT4\GEN03\WH'),
        ('obj29', 'SS\HSD_NPN0\RT4\GEN03\FUL_CONS'),
        ('obj30', 'SS\HSD_NPN0\RT4\GEN03\FUL_CONS_RAT'),
        ('obj31', 'SS\HSD_NPN0\RT4\GEN03\FUL_PRS'),
        ('obj32', 'SS\HSD_NPN0\RT4\GEN03\OPR_HRS'),
        ('obj33', 'SS\HSD_NPN0\RT4\GEN03\BAT_V_001'),
        ('obj34', 'SS\HSD_NPN0\RT4\GEN03\R_TOT'),
        ('obj35', 'SS\HSD_NPN0\RT4\GEN03\S_TOT'),
        ('obj36', 'SS\HSD_NPN0\RT4\GEN03\AVG_A'),
        ('obj37', 'SS\HSD_NPN0\RT4\GEN03\CAL_GND_A'),
        ('obj38', 'SS\HSD_NPN0\RT4\GEN03\L1_L2_V'),
        ('obj39', 'SS\HSD_NPN0\RT4\GEN03\L2_L3_V'),
        ('obj40', 'SS\HSD_NPN0\RT4\GEN03\L3_L1_V'),
        ('obj41', 'SS\HSD_NPN0\RT4\GEN03\L1_N_V'),
        ('obj42', 'SS\HSD_NPN0\RT4\GEN03\L2_N_V'),
        ('obj43', 'SS\HSD_NPN0\RT4\GEN03\L3_N_V'),
        ('obj44', 'SS\HSD_NPN0\RT4\GEN03\WDG_PHSA_TMP'),
        ('obj45', 'SS\HSD_NPN0\RT4\GEN03\WDG_PHSB_TMP'),
        ('obj46', 'SS\HSD_NPN0\RT4\GEN03\WDG_PHSC_TMP'),
        ('obj47', 'SS\HSD_NPN0\RT4\GEN03\RER_BRG_TMP'),
        ('obj48', 'SS\HSD_NPN0\RT4\GEN03\AIR_FIL_DP'),
        ('obj49', 'SS\HSD_NPN0\RT4\GEN03\FUL_FIL_DP'),
        ('obj50', 'SS\HSD_NPN0\RT4\GEN03\OIL_FIL_DP'),
        ('obj51', 'SS\HSD_NPN0\RT4\GEN03\EXH_MAN_TMP_001'),
        ('obj52', 'SS\HSD_NPN0\RT4\GEN03\EXH_MAN_TMP_002'),
        ('obj53', 'SS\HSD_NPN0\RT4\GEN03\CRC_PRS'),
        ('obj54', 'SS\HSD_NPN0\RT4\GEN03\BST_PRS'),
    ]

    # query latest row from mongodb. there is only one row in a list
    row = db.ss.find().sort("_id", -1).limit(1)[0]

    # replace tag name with tag id for security reason
    data = dict()
    for i in x:
        tag_id, tag_name = i[0], i[1]
        data[tag_id] = row['Tags'][tag_name]

        # remove for security reason
        if 'Name' in data[tag_id]:
            del data[tag_id]['Name']

    # TODO special cases because they have more than one tag name
    # and need sum operation

    # obj1
    value1 = float(row['Tags']['SS\HSD_NPN0\RT4\GEN03\L1_L2_V']['Value'])
    value2 = float(row['Tags']['SS\HSD_NPN0\RT4\GEN03\L2_L3_V']['Value']) 
    value3 = float(row['Tags']['SS\HSD_NPN0\RT4\GEN03\L3_L1_V']['Value'])

    data['obj1'] = dict()
    data['obj1']['Value'] = (value1 + value2 + value3) / 3

    value1 = float(row['Tags']['SS\HSD_NPN0\RT4\GEN03\CYL_EXH_TMP_001']['Value']) 
    value2 = float(row['Tags']['SS\HSD_NPN0\RT4\GEN03\CYL_EXH_TMP_002']['Value'])
    value3 = float(row['Tags']['SS\HSD_NPN0\RT4\GEN03\CYL_EXH_TMP_003']['Value'])
    value4 = float(row['Tags']['SS\HSD_NPN0\RT4\GEN03\CYL_EXH_TMP_004']['Value'])
    value5 = float(row['Tags']['SS\HSD_NPN0\RT4\GEN03\CYL_EXH_TMP_005']['Value'])
    value6 = float(row['Tags']['SS\HSD_NPN0\RT4\GEN03\CYL_EXH_TMP_006']['Value'])
    value7 = float(row['Tags']['SS\HSD_NPN0\RT4\GEN03\CYL_EXH_TMP_007']['Value'])
    value8 = float(row['Tags']['SS\HSD_NPN0\RT4\GEN03\CYL_EXH_TMP_008']['Value'])
    value9 = float(row['Tags']['SS\HSD_NPN0\RT4\GEN03\CYL_EXH_TMP_009']['Value'])
    value10 = float(row['Tags']['SS\HSD_NPN0\RT4\GEN03\CYL_EXH_TMP_010']['Value']) 
    value11 = float(row['Tags']['SS\HSD_NPN0\RT4\GEN03\CYL_EXH_TMP_011']['Value'])
    value12 = float(row['Tags']['SS\HSD_NPN0\RT4\GEN03\CYL_EXH_TMP_012']['Value'])
    value13 = float(row['Tags']['SS\HSD_NPN0\RT4\GEN03\CYL_EXH_TMP_013']['Value'])
    value14 = float(row['Tags']['SS\HSD_NPN0\RT4\GEN03\CYL_EXH_TMP_014']['Value'])
    value15 = float(row['Tags']['SS\HSD_NPN0\RT4\GEN03\CYL_EXH_TMP_015']['Value'])
    value16 = float(row['Tags']['SS\HSD_NPN0\RT4\GEN03\CYL_EXH_TMP_016']['Value'])

    data['obj23'] = dict()
    data['obj23']['Value'] = (value1 + value2 + value3 + value4 + value5 \
                             + value6 + value7 + value8 + value9 + value10 \
                             + value11 + value12 + value13 + value14 + value15 \
                             + value16) / 16

    message = { 'success': 0, 'data': data }
    return HttpResponse(dumps(message), content_type='application/json') 
    

@login_required
def genset_outgoing_1_unit_4(request):
    x = [
        # ('obj1', ''),
        ('obj2', 'SS\HSD_NPN0\RT4\GEN04\AVG_A'),
        ('obj3', 'SS\HSD_NPN0\RT4\GEN04\F'),
        ('obj4', 'SS\HSD_NPN0\RT4\GEN04\P_TOT'),
        ('obj5', 'SS\HSD_NPN0\RT4\GEN04\PF'),
        ('obj6', 'SS\HSD_NPN0\RT4\GEN04\RPM'),
        ('obj7', 'SS\HSD_NPN0\RT4\GEN04\CYL_EXH_TMP_001'),
        ('obj8', 'SS\HSD_NPN0\RT4\GEN04\CYL_EXH_TMP_002'),
        ('obj9', 'SS\HSD_NPN0\RT4\GEN04\CYL_EXH_TMP_003'),
        ('obj10', 'SS\HSD_NPN0\RT4\GEN04\CYL_EXH_TMP_004'),
        ('obj11', 'SS\HSD_NPN0\RT4\GEN04\CYL_EXH_TMP_005'),
        ('obj12', 'SS\HSD_NPN0\RT4\GEN04\CYL_EXH_TMP_006'),
        ('obj13', 'SS\HSD_NPN0\RT4\GEN04\CYL_EXH_TMP_007'),
        ('obj14', 'SS\HSD_NPN0\RT4\GEN04\CYL_EXH_TMP_008'),
        ('obj15', 'SS\HSD_NPN0\RT4\GEN04\CYL_EXH_TMP_009'),
        ('obj16', 'SS\HSD_NPN0\RT4\GEN04\CYL_EXH_TMP_010'),
        ('obj17', 'SS\HSD_NPN0\RT4\GEN04\CYL_EXH_TMP_011'),
        ('obj18', 'SS\HSD_NPN0\RT4\GEN04\CYL_EXH_TMP_012'),
        ('obj19', 'SS\HSD_NPN0\RT4\GEN04\CYL_EXH_TMP_013'),
        ('obj20', 'SS\HSD_NPN0\RT4\GEN04\CYL_EXH_TMP_014'),
        ('obj21', 'SS\HSD_NPN0\RT4\GEN04\CYL_EXH_TMP_015'),
        ('obj22', 'SS\HSD_NPN0\RT4\GEN04\CYL_EXH_TMP_016'),

        ('obj24', 'SS\HSD_NPN0\RT4\GEN04\ENG_OIL_PRS'),
        ('obj25', 'SS\HSD_NPN0\RT4\GEN04\ENG_OIL_TMP'),
        ('obj26', 'SS\HSD_NPN0\RT4\GEN04\FUL_PRS'),
        ('obj27', 'SS\HSD_NPN0\RT4\GEN04\ENG_COL_TMP'),
        ('obj28', 'SS\HSD_NPN0\RT4\GEN04\WH'),
        ('obj29', 'SS\HSD_NPN0\RT4\GEN04\FUL_CONS'),
        ('obj30', 'SS\HSD_NPN0\RT4\GEN04\FUL_CONS_RAT'),
        ('obj31', 'SS\HSD_NPN0\RT4\GEN04\FUL_PRS'),
        ('obj32', 'SS\HSD_NPN0\RT4\GEN04\OPR_HRS'),
        ('obj33', 'SS\HSD_NPN0\RT4\GEN04\BAT_V_001'),
        ('obj34', 'SS\HSD_NPN0\RT4\GEN04\R_TOT'),
        ('obj35', 'SS\HSD_NPN0\RT4\GEN04\S_TOT'),
        ('obj36', 'SS\HSD_NPN0\RT4\GEN04\AVG_A'),
        ('obj37', 'SS\HSD_NPN0\RT4\GEN04\CAL_GND_A'),
        ('obj38', 'SS\HSD_NPN0\RT4\GEN04\L1_L2_V'),
        ('obj39', 'SS\HSD_NPN0\RT4\GEN04\L2_L3_V'),
        ('obj40', 'SS\HSD_NPN0\RT4\GEN04\L3_L1_V'),
        ('obj41', 'SS\HSD_NPN0\RT4\GEN04\L1_N_V'),
        ('obj42', 'SS\HSD_NPN0\RT4\GEN04\L2_N_V'),
        ('obj43', 'SS\HSD_NPN0\RT4\GEN04\L3_N_V'),
        ('obj44', 'SS\HSD_NPN0\RT4\GEN04\WDG_PHSA_TMP'),
        ('obj45', 'SS\HSD_NPN0\RT4\GEN04\WDG_PHSB_TMP'),
        ('obj46', 'SS\HSD_NPN0\RT4\GEN04\WDG_PHSC_TMP'),
        ('obj47', 'SS\HSD_NPN0\RT4\GEN04\RER_BRG_TMP'),
        ('obj48', 'SS\HSD_NPN0\RT4\GEN04\AIR_FIL_DP'),
        ('obj49', 'SS\HSD_NPN0\RT4\GEN04\FUL_FIL_DP'),
        ('obj50', 'SS\HSD_NPN0\RT4\GEN04\OIL_FIL_DP'),
        ('obj51', 'SS\HSD_NPN0\RT4\GEN04\EXH_MAN_TMP_001'),
        ('obj52', 'SS\HSD_NPN0\RT4\GEN04\EXH_MAN_TMP_002'),
        ('obj53', 'SS\HSD_NPN0\RT4\GEN04\CRC_PRS'),
        ('obj54', 'SS\HSD_NPN0\RT4\GEN04\BST_PRS'),
    ]

    # query latest row from mongodb. there is only one row in a list
    row = db.ss.find().sort("_id", -1).limit(1)[0]

    # replace tag name with tag id for security reason
    data = dict()
    for i in x:
        tag_id, tag_name = i[0], i[1]
        data[tag_id] = row['Tags'][tag_name]

        # remove for security reason
        if 'Name' in data[tag_id]:
            del data[tag_id]['Name']

    # TODO special cases because they have more than one tag name
    # and need sum operation

    # obj1
    value1 = float(row['Tags']['SS\HSD_NPN0\RT4\GEN04\L1_L2_V']['Value'])
    value2 = float(row['Tags']['SS\HSD_NPN0\RT4\GEN04\L2_L3_V']['Value']) 
    value3 = float(row['Tags']['SS\HSD_NPN0\RT4\GEN04\L3_L1_V']['Value'])

    data['obj1'] = dict()
    data['obj1']['Value'] = (value1 + value2 + value3) / 3

    value1 = float(row['Tags']['SS\HSD_NPN0\RT4\GEN04\CYL_EXH_TMP_001']['Value']) 
    value2 = float(row['Tags']['SS\HSD_NPN0\RT4\GEN04\CYL_EXH_TMP_002']['Value'])
    value3 = float(row['Tags']['SS\HSD_NPN0\RT4\GEN04\CYL_EXH_TMP_003']['Value'])
    value4 = float(row['Tags']['SS\HSD_NPN0\RT4\GEN04\CYL_EXH_TMP_004']['Value'])
    value5 = float(row['Tags']['SS\HSD_NPN0\RT4\GEN04\CYL_EXH_TMP_005']['Value'])
    value6 = float(row['Tags']['SS\HSD_NPN0\RT4\GEN04\CYL_EXH_TMP_006']['Value'])
    value7 = float(row['Tags']['SS\HSD_NPN0\RT4\GEN04\CYL_EXH_TMP_007']['Value'])
    value8 = float(row['Tags']['SS\HSD_NPN0\RT4\GEN04\CYL_EXH_TMP_008']['Value'])
    value9 = float(row['Tags']['SS\HSD_NPN0\RT4\GEN04\CYL_EXH_TMP_009']['Value'])
    value10 = float(row['Tags']['SS\HSD_NPN0\RT4\GEN04\CYL_EXH_TMP_010']['Value']) 
    value11 = float(row['Tags']['SS\HSD_NPN0\RT4\GEN04\CYL_EXH_TMP_011']['Value'])
    value12 = float(row['Tags']['SS\HSD_NPN0\RT4\GEN04\CYL_EXH_TMP_012']['Value'])
    value13 = float(row['Tags']['SS\HSD_NPN0\RT4\GEN04\CYL_EXH_TMP_013']['Value'])
    value14 = float(row['Tags']['SS\HSD_NPN0\RT4\GEN04\CYL_EXH_TMP_014']['Value'])
    value15 = float(row['Tags']['SS\HSD_NPN0\RT4\GEN04\CYL_EXH_TMP_015']['Value'])
    value16 = float(row['Tags']['SS\HSD_NPN0\RT4\GEN04\CYL_EXH_TMP_016']['Value'])

    data['obj23'] = dict()
    data['obj23']['Value'] = (value1 + value2 + value3 + value4 + value5 \
                             + value6 + value7 + value8 + value9 + value10 \
                             + value11 + value12 + value13 + value14 + value15 \
                             + value16) / 16

    message = { 'success': 0, 'data': data }
    return HttpResponse(dumps(message), content_type='application/json') 


@login_required
def trend_unit_1(request):
    page_id = 'trend-unit-1'

    page_schema = get_page_schema(page_id)
    response = create_response(page_schema)

    return HttpResponse(json.dumps(response), content_type='application/json') 

    # rows = dumps(list(db.ss.find().sort("_id",-1).limit(60)))
    # return HttpResponse(rows, content_type='application/json') 


@login_required
def trend_unit_chart(request):
    page_id = 'trend-unit-1'
    page_schema = get_page_schema(page_id)
    i = request.GET['id']
    tag_name = page_schema['cylinder-exhause-temperature']['series'][i]['data']

    row = db.ss.find().sort("_id", -1).limit(1)[0]

    dt = modify_datetime(row['SentDatetime'])
    value = row['Tags'][tag_name]['Value']

    response = [dt, value]

    return HttpResponse(json.dumps(response), content_type='application/json')


@login_required
def trend_unit_2(request):
    page_id = 'trend-unit-2'

    page_schema = get_page_schema(page_id)
    response = create_response(page_schema)

    return HttpResponse(json.dumps(response), content_type='application/json') 


@login_required
def trend_unit_3(request):
    page_id = 'trend-unit-3'

    page_schema = get_page_schema(page_id)
    response = create_response(page_schema)

    return HttpResponse(json.dumps(response), content_type='application/json') 


@login_required
def trend_unit_4(request):
    page_id = 'trend-unit-4'

    page_schema = get_page_schema(page_id)
    response = create_response(page_schema)

    return HttpResponse(json.dumps(response), content_type='application/json') 


# @login_required
# def trend_unit_4(request):
#     message = dumps(list(db.ss.find().sort("_id",-1).limit(1)))
#     return HttpResponse(message, content_type='application/json') 
