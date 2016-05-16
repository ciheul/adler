# http://eli.thegreenplace.net/2009/11/28/python-internals-working-with-python-asts

import simplejson as json
import pymongo
from django.http import HttpResponse, Http404, HttpResponseServerError
from pymongo import MongoClient

from bson.json_util import dumps

import os

db = MongoClient().inetscada


def electrical_overview_outgoing_1(request):
    f = open('electrical/conf/schema.json')
    schema = json.loads(f.read())
    page = schema['page-overview-outgoing-1']

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

            # sum value from several tag names
            if 'grammar' in detail and detail['grammar'] == 'sum':
                total_value = 0
                for tag_name in detail['value']:
                    if tag_name not in row['Tags']:
                        continue
                    total_value += float(row['Tags'][tag_name]['Value'])
                detail['value'] = total_value
                
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

                # row with general status (it consists of run and fault
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

            # set tag_id inside detail
            detail['tagId'] = tag_id
            detail['data'] = final_data

            response.append(detail)
            
        if detail['type'] == 'threeColumnsTable':
            final_data = list()
            for d in detail['data']:
                if d['type'] == 'default':
                    tag_name = d['value']
                    d['value'] = '#NA'
                    if tag_name in row['Tags']:
                        d['value'] = \
                            "{:,.2f}".format(row['Tags'][tag_name]['Value'])
                    final_data.append(d)

            # set tag_id inside detail
            detail['tagId'] = tag_id
            detail['data'] = final_data

            response.append(detail)

    # TODO get page parameter and query to database which (tag_id, tag_name)
    # belongs to the page
    # x = [
    #     # ('obj1', 'SS\HSD_NPN0\RT4\OUT01\REAL_PWR_TOTAL'), # unavailable
    #     # ('obj2', 'SS\HSD_NPN0\RT4\GEN01\P_TOT'), # multivalue
    #     # ('obj3', 'SS\HSD_NPN0\RT2\OUT01\PF_TOTAL'), # unavailable
    #     # ('obj4', 'SS\HSD_NPN0\RT4\OUT01\FREQ'), # unavailable
    #     # ('obj5', 'SS\HSD_NPN0\RT4\OUT01\VOLTAGE_LL_AVG'), # unavailable 
    #     # ('obj14', 'SS\HSD_NPN0\RT4\OUT01\REAL_PWR_TOTAL'), # unavailable
    #
    #     ('obj19', 'SS\HSD_NPN0\RT4\GEN01\F'),
    #     # ('obj20', 'SS\HSD_NPN0\EVT\GEN01\DI11_EGF'), # unavailable
    #     ('obj21', 'SS\HSD_NPN0\RT4\GEN01\P_TOT'),
    #     ('obj22', 'SS\HSD_NPN0\RT4\GEN01\PF'),
    #     ('obj23', 'SS\HSD_NPN0\RT4\GEN01\OPR_HRS'),
    #
    #     ('obj24', 'SS\HSD_NPN0\RT4\GEN02\F'),
    #     # ('obj25', 'SS\HSD_NPN0\EVT\GEN02\DI11_EGF'), # unavailable
    #     ('obj26', 'SS\HSD_NPN0\RT4\GEN02\P_TOT'),
    #     ('obj27', 'SS\HSD_NPN0\RT4\GEN02\PF'),
    #     ('obj28', 'SS\HSD_NPN0\RT4\GEN02\OPR_HRS'),
    #
    #     ('obj29', 'SS\HSD_NPN0\RT4\GEN03\F'),
    #     # ('obj30', 'SS\HSD_NPN0\EVT\GEN03\DI11_EGF'), # unavailable
    #     ('obj31', 'SS\HSD_NPN0\RT4\GEN03\P_TOT'),
    #     ('obj32', 'SS\HSD_NPN0\RT4\GEN03\PF'),
    #     ('obj33', 'SS\HSD_NPN0\RT4\GEN03\OPR_HRS'),
    #
    #     ('obj34', 'SS\HSD_NPN0\RT4\GEN04\F'),
    #     # ('obj35', 'SS\HSD_NPN0\EVT\GEN04\DI11_EGF'), # unavailable
    #     ('obj36', 'SS\HSD_NPN0\RT4\GEN04\P_TOT'),
    #     ('obj37', 'SS\HSD_NPN0\RT4\GEN04\PF'),
    #     ('obj38', 'SS\HSD_NPN0\RT4\GEN04\OPR_HRS'),
    #
    #     # ('obj39', 'SS\HSD_NPN0\RT4\OUT01\REAL_PWR_TOTAL'), # unavailable
    #     # ('obj40', 'SS\HSD_NPN0\RT4\OUT01\PF_TOTAL'), # unavailable
    # ]
    #
    # # query latest row from mongodb. there is only one row in a list
    # row = db.ss.find().sort("_id", -1).limit(1)[0]
    #
    # # replace tag name with tag id for security reason
    # data = dict()
    # for i in x:
    #     tag_id, tag_name = i[0], i[1]
    #     data[tag_id] = row['Tags'][tag_name]
    #
    #     # remove for security reason
    #     del data[tag_id]['Name']
    #
    # # TODO special case for obj2 because it has more than one tag name
    # # and need sum operation
    # value1 = float(row['Tags']['SS\HSD_NPN0\RT4\GEN01\P_TOT']['Value'])
    # value2 = float(row['Tags']['SS\HSD_NPN0\RT4\GEN02\P_TOT']['Value']) 
    # value3 = float(row['Tags']['SS\HSD_NPN0\RT4\GEN03\P_TOT']['Value'])
    # value4 = float(row['Tags']['SS\HSD_NPN0\RT4\GEN04\P_TOT']['Value'])
    #
    # data['obj2'] = dict()
    # data['obj2']['Value'] = value1 + value2 + value3 + value4

    # data = list()
    # data.append({
    #     'type': 'gauge',
    #     'tagId': 'gauge-outgoing-power',
    #     'title': 'OUTGOING POWER',
    #     'minValue': 0,
    #     'maxValue': 3000,
    #     'value': 100,
    #     'label': 'kW'
    # });
    # message = { 'success': 0, 'data': data }
    
    return HttpResponse(json.dumps(response), content_type='application/json') 
    # return HttpResponse(json.dumps(message), content_type='application/json') 


def electrical_sld_outgoing_1(request):
    # TODO get page parameter and query to database which (tag_id, tag_name)
    # belongs to the page
    x = [
        # ('obj1', 'SS\HSD_NPN0\EVT\GEN01\AUX_DI_6'), # unavailable
        # ('obj2', 'SS\HSD_NPN0\EVT\GEN01\ST_GCB_CLS'), # unavailable
        # ('obj3', 'SS\HSD_NPN0\EVT\GEN01\DI9_TRF'), # unavailable
        # ('obj4', 'SS\HSD_NPN0\EVT\GEN02\AUX_DI_6'), # unavailable
        # ('obj5', 'SS\HSD_NPN0\EVT\GEN02\ST_GCB_CLS'), # unavailable
        # ('obj6', 'SS\HSD_NPN0\EVT\GEN02\DI9_TRF'), # unavailable
        # ('obj7', 'SS\HSD_NPN0\EVT\GEN03\AUX_DI_6'), # unavailable
        # ('obj8', 'SS\HSD_NPN0\EVT\GEN03\ST_GCB_CLS'), # unavailable
        # ('obj9', 'SS\HSD_NPN0\EVT\GEN03\DI9_TRF'), # unavailable
        # ('obj10', 'SS\HSD_NPN0\EVT\GEN04\AUX_DI_6'), # unavailable
        # ('obj11', 'SS\HSD_NPN0\EVT\GEN04\ST_GCB_CLS'), # unavailable
        # ('obj12', 'SS\HSD_NPN0\EVT\GEN04\DI9_TRF'), # unavailable
        # ('obj13', 'SS\HSD_NPN0\EVT\OUT01\ST_CB_CLS'), # unavailable

        ('obj19', 'SS\HSD_NPN0\RT4\GEN01\F'),
        # ('obj20', 'SS\HSD_NPN0\EVT\GEN01\DI11_EGF'), # unavailable
        ('obj21', 'SS\HSD_NPN0\RT4\GEN01\P_TOT'),
        ('obj22', 'SS\HSD_NPN0\RT4\GEN01\PF'),
        ('obj23', 'SS\HSD_NPN0\RT4\GEN01\OPR_HRS'),

        ('obj24', 'SS\HSD_NPN0\RT4\GEN02\F'),
        # ('obj25', 'SS\HSD_NPN0\EVT\GEN02\DI11_EGF'), # unavailable
        ('obj26', 'SS\HSD_NPN0\RT4\GEN02\P_TOT'),
        ('obj27', 'SS\HSD_NPN0\RT4\GEN02\PF'),
        ('obj28', 'SS\HSD_NPN0\RT4\GEN02\OPR_HRS'),

        ('obj29', 'SS\HSD_NPN0\RT4\GEN03\F'),
        # ('obj30', 'SS\HSD_NPN0\EVT\GEN03\DI11_EGF'), # unavailable
        ('obj31', 'SS\HSD_NPN0\RT4\GEN03\P_TOT'),
        ('obj32', 'SS\HSD_NPN0\RT4\GEN03\PF'),
        ('obj33', 'SS\HSD_NPN0\RT4\GEN03\OPR_HRS'),

        ('obj34', 'SS\HSD_NPN0\RT4\GEN04\F'),
        # ('obj35', 'SS\HSD_NPN0\EVT\GEN04\DI11_EGF'), # unavailable
        ('obj36', 'SS\HSD_NPN0\RT4\GEN04\P_TOT'),
        ('obj37', 'SS\HSD_NPN0\RT4\GEN04\PF'),
        ('obj38', 'SS\HSD_NPN0\RT4\GEN04\OPR_HRS'),
    ]

    # query latest row from mongodb. there is only one row in a list
    row = db.ss.find().sort("_id", -1).limit(1)[0]
    
    # replace tag name with tag id for security reason
    data = dict()
    for i in x:
        tag_id, tag_name = i[0], i[1]
        data[tag_id] = row['Tags'][tag_name]

        # remove for security reason
        del data[tag_id]['Name']

    message = { 'success': 0, 'data': data }
    
    return HttpResponse(dumps(message), content_type='application/json') 


def genset_overview_outgoing_1(request):
    # TODO get page parameter and query to database which (tag_id, tag_name)
    # belongs to the page
    x = [
        # ('obj1', ''),
        # ('obj2', ''),
        ('obj3', 'SS\HSD_NPN0\RT4\GEN01\AVG_A'),
        ('obj4', 'SS\HSD_NPN0\RT4\GEN01\F'),
        ('obj5', 'SS\HSD_NPN0\RT4\GEN01\PF'),
        ('obj6', 'SS\HSD_NPN0\RT4\GEN01\P_TOT'),
        ('obj7', 'SS\HSD_NPN0\RT4\GEN01\WH'),
        ('obj8', 'SS\HSD_NPN0\RT4\GEN01\BAT_V_001'), # TODO verify

        # ('obj9', ''),
        # ('obj10', ''),
        ('obj11', 'SS\HSD_NPN0\RT4\GEN02\AVG_A'),
        ('obj12', 'SS\HSD_NPN0\RT4\GEN02\F'),
        ('obj13', 'SS\HSD_NPN0\RT4\GEN02\PF'),
        ('obj14', 'SS\HSD_NPN0\RT4\GEN02\P_TOT'),
        ('obj15', 'SS\HSD_NPN0\RT4\GEN02\WH'),
        ('obj16', 'SS\HSD_NPN0\RT4\GEN02\BAT_V_001'),

        # ('obj17', ''),
        # ('obj18', ''),
        ('obj19', 'SS\HSD_NPN0\RT4\GEN03\AVG_A'),
        ('obj20', 'SS\HSD_NPN0\RT4\GEN03\F'),
        ('obj21', 'SS\HSD_NPN0\RT4\GEN03\PF'),
        ('obj22', 'SS\HSD_NPN0\RT4\GEN03\P_TOT'),
        ('obj23', 'SS\HSD_NPN0\RT4\GEN03\WH'),
        ('obj24', 'SS\HSD_NPN0\RT4\GEN03\BAT_V_001'),

        # ('obj25', ''),
        # ('obj26', ''),
        ('obj27', 'SS\HSD_NPN0\RT4\GEN04\AVG_A'),
        ('obj28', 'SS\HSD_NPN0\RT4\GEN04\F'),
        ('obj29', 'SS\HSD_NPN0\RT4\GEN04\PF'),
        ('obj30', 'SS\HSD_NPN0\RT4\GEN04\P_TOT'),
        ('obj31', 'SS\HSD_NPN0\RT4\GEN04\WH'),
        ('obj32', 'SS\HSD_NPN0\RT4\GEN04\BAT_V_001'),

    ]

    # query latest row from mongodb. there is only one row in a list
    row = db.ss.find().sort("_id", -1).limit(1)[0]

    # replace tag name with tag id for security reason
    data = dict()
    for i in x:
        tag_id, tag_name = i[0], i[1]
        data[tag_id] = row['Tags'][tag_name]

        # remove for security reason
        del data[tag_id]['Name']

    # TODO special cases because they have more than one tag name
    # and need sum operation

    # obj1
    value1 = float(row['Tags']['SS\HSD_NPN0\RT4\GEN01\L1_L2_V']['Value'])
    value2 = float(row['Tags']['SS\HSD_NPN0\RT4\GEN01\L2_L3_V']['Value']) 
    value3 = float(row['Tags']['SS\HSD_NPN0\RT4\GEN01\L3_L1_V']['Value'])

    data['obj1'] = dict()
    data['obj1']['Value'] = value1 + value2 + value3

    # obj2
    value1 = float(row['Tags']['SS\HSD_NPN0\RT4\GEN01\L1_N_V']['Value'])
    value2 = float(row['Tags']['SS\HSD_NPN0\RT4\GEN01\L2_N_V']['Value']) 
    value3 = float(row['Tags']['SS\HSD_NPN0\RT4\GEN01\L3_N_V']['Value'])

    data['obj2'] = dict()
    data['obj2']['Value'] = value1 + value2 + value3

    # obj9
    value1 = float(row['Tags']['SS\HSD_NPN0\RT4\GEN02\L1_L2_V']['Value'])
    value2 = float(row['Tags']['SS\HSD_NPN0\RT4\GEN02\L2_L3_V']['Value']) 
    value3 = float(row['Tags']['SS\HSD_NPN0\RT4\GEN02\L3_L1_V']['Value'])

    data['obj9'] = dict()
    data['obj9']['Value'] = value1 + value2 + value3

    # obj10
    value1 = float(row['Tags']['SS\HSD_NPN0\RT4\GEN02\L1_N_V']['Value'])
    value2 = float(row['Tags']['SS\HSD_NPN0\RT4\GEN02\L2_N_V']['Value']) 
    value3 = float(row['Tags']['SS\HSD_NPN0\RT4\GEN02\L3_N_V']['Value'])

    data['obj10'] = dict()
    data['obj10']['Value'] = value1 + value2 + value3

    # obj17
    value1 = float(row['Tags']['SS\HSD_NPN0\RT4\GEN03\L1_L2_V']['Value'])
    value2 = float(row['Tags']['SS\HSD_NPN0\RT4\GEN03\L2_L3_V']['Value']) 
    value3 = float(row['Tags']['SS\HSD_NPN0\RT4\GEN03\L3_L1_V']['Value'])

    data['obj17'] = dict()
    data['obj17']['Value'] = value1 + value2 + value3

    # obj18
    value1 = float(row['Tags']['SS\HSD_NPN0\RT4\GEN03\L1_N_V']['Value'])
    value2 = float(row['Tags']['SS\HSD_NPN0\RT4\GEN03\L2_N_V']['Value']) 
    value3 = float(row['Tags']['SS\HSD_NPN0\RT4\GEN03\L3_N_V']['Value'])

    data['obj18'] = dict()
    data['obj18']['Value'] = value1 + value2 + value3

    # obj25
    value1 = float(row['Tags']['SS\HSD_NPN0\RT4\GEN04\L1_L2_V']['Value'])
    value2 = float(row['Tags']['SS\HSD_NPN0\RT4\GEN04\L2_L3_V']['Value']) 
    value3 = float(row['Tags']['SS\HSD_NPN0\RT4\GEN04\L3_L1_V']['Value'])

    data['obj25'] = dict()
    data['obj25']['Value'] = value1 + value2 + value3

    # obj26
    value1 = float(row['Tags']['SS\HSD_NPN0\RT4\GEN04\L1_N_V']['Value'])
    value2 = float(row['Tags']['SS\HSD_NPN0\RT4\GEN04\L2_N_V']['Value']) 
    value3 = float(row['Tags']['SS\HSD_NPN0\RT4\GEN04\L3_N_V']['Value'])

    data['obj26'] = dict()
    data['obj26']['Value'] = value1 + value2 + value3

    message = { 'success': 0, 'data': data }

    return HttpResponse(dumps(message), content_type='application/json') 
    
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

def trend_unit_1(request):
    message = dumps(list(db.ss.find().sort("_id",-1).limit(1)))
    return HttpResponse(message, content_type='application/json') 

def trend_unit_2(request):
    message = dumps(list(db.ss.find().sort("_id",-1).limit(1)))
    return HttpResponse(message, content_type='application/json') 

def trend_unit_3(request):
    message = dumps(list(db.ss.find().sort("_id",-1).limit(1)))
    return HttpResponse(message, content_type='application/json') 

def trend_unit_4(request):
    message = dumps(list(db.ss.find().sort("_id",-1).limit(1)))
    return HttpResponse(message, content_type='application/json') 
