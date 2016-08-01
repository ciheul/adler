import ast
import urllib

import tornado.ioloop
import tornado.web

import dateutil.parser
import motor
import tornadoredis
import simplejson as json

from mixins import MongoConnectorMixin


PORT = 12000
QUEUE = 'inetscada'

GLM = 'GLM'
SEWATAMA = 'SS'
REPORT = 'REPORT'

class INetSCADASubscriber(MongoConnectorMixin):
    def __init__(self):
        super(INetSCADASubscriber, self).__init__()

        # connect to redis using non-blocking way
        self.nbr = tornadoredis.Client()
        self.nbr.connect()
        self.nbr.subscribe(QUEUE, callback=self.on_connect)

        # connect to mongodb using motor (not pymongo)
        self.db = motor.motor_tornado.MotorClient().inetscada

    def on_connect(self, data):
        self.nbr.listen(self.on_data)

    def on_data(self, data):
        # remove first response when tornado connecting with redis
        # or remove empty data that piggyback subscribed data
        if data.body == 1 or data.body == '':
            return

        # add new field 'SentDatetime' that has datetime format
        # so that, one can query document using datetime directly
        d = json.loads(data.body)
        d[u'SentDatetime'] = dateutil.parser.parse(d['SentTimestamp'])

        if d['Name'].split('\\')[0] == GLM and d['Name'].split('\\')[2] != REPORT:
            # insert to mongodb. success or error calls on_response callback
            self.db.glm.insert(d, callback=self.on_response)

        if d['Name'].split('\\')[0] == GLM and d['Name'].split('\\')[2] == REPORT:
            # insert to mongodb. success or error calls on_response callback
            self.db.glm_report.insert(d, callback=self.on_response)

        if d['Name'].split('\\')[0] == SEWATAMA and d['Name'].split('\\')[2] != REPORT:
            # insert to mongodb. success or error calls on_response callback
            self.db.ss.insert(d, callback=self.on_response)

        if d['Name'].split('\\')[0] == SEWATAMA and d['Name'].split('\\')[2] == REPORT:
            # insert to mongodb. success or error calls on_response callback
            self.db.ss_report.insert(d, callback=self.on_response)

    def on_response(self, result, error):
        print 'result:', result
        print 'error :', error
        
    def send_to_mongomanager(self, data):
        """Called this method in on_data callback function when inserting
           data through mongomanager is preferred."""
        headers = {'Content-type': 'application/json'}
        self.send('/glm/create', method='POST', headers=headers,
                  body=json.dumps(data.body))


if __name__ == '__main__':
    print "Core server on port {0}".format(PORT)

    s = INetSCADASubscriber()

    io_loop = tornado.ioloop.IOLoop.current()
    io_loop.start()
