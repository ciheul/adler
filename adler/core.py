import urllib

import tornado.ioloop
import tornado.web

import tornadoredis
import simplejson as json

from mixins import MongoConnectorMixin


PORT = 12000
QUEUE = 'inetscada'

class INetSCADASubscriber(MongoConnectorMixin):
    def __init__(self):
        super(INetSCADASubscriber, self).__init__()

        self.nbr = tornadoredis.Client()
        self.nbr.connect()
        self.nbr.subscribe('inetscada', callback=self.on_connect)

    def on_connect(self, data):
        self.nbr.listen(self.on_data)

    def on_data(self, data):
        # remove first response when tornado connecting with redis
	if data.body == 1:
            return

        headers = {'Content-type': 'application/json'}
        self.send('/glm/create', method='POST', headers=headers,
                  body=json.dumps(data.body))


if __name__ == '__main__':
    print "Core server on port {0}".format(PORT)

    s = INetSCADASubscriber()

    io_loop = tornado.ioloop.IOLoop.current()
    io_loop.start()
