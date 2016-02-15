from datetime import datetime
import random
import sys
import time

import pika
import simplejson as json


KEY = 'inetscada'
GLM_PREFIX = 'GLM\SWRO_001\RT01'
INTERVAL_TIME = 2

tag_names = [
    '\TANKFEED\LSH',
    '\TANKFEED\LSL',
    '\PUMP_FEED03\RUN',
    '\PUMP_FEED03\FAULT',
    '\MMF2A\PRESS',
    '\MMF2B\PRESS',
    '\DOSING_ANSCAL\AGT_RUN',
    '\TANK_BREAK\LSH',
    '\TANK_BREAK\LSL',
]


def create_message(tag_name):
    now = datetime.now()

    data = {
        'Name': GLM_PREFIX,
        'SenderIdentifier': 'INSE0F0000',
        'Tags': {
            GLM_PREFIX + tag_name: {
                'Name': GLM_PREFIX + tag_name,
                'LastChanged': now.isoformat(),
                'LastUpdated': now.isoformat(),
                'Value': random.randint(0, 100),
                'Type': 'Decimal',
                'Unit': 'bar',
                'Description': ''     
            }    
        }
    }

    return json.dumps(data)


def publish_message_from_array():
    for tag_name in tag_names:
        m = create_message(tag_name)
        channel.basic_publish(exchange='', routing_key=KEY, body=m)
        print m
    print


def publish_message_from_dump():
    f = open('dump/dump.json', 'r')
    m = f.read()
    channel.basic_publish(exchange='', routing_key=KEY, body=m)
    print m


if __name__ == '__main__':
    connection = pika.BlockingConnection(pika.ConnectionParameters(
        host='localhost'))
    channel = connection.channel()
    channel.queue_declare(queue=KEY)

    while True:
        try:
            # publish_message_from_array()
            publish_message_from_dump()
            time.sleep(INTERVAL_TIME)
            
        except KeyboardInterrupt:
            sys.exit()
            print "\nStop forcefully"
