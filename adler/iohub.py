# http://stackoverflow.com/questions/31344127/how-to-process-multiple-commands-to-read-from-socket-at-the-same-time-in-tornado

"""
For development:
    - to run, use this command:
      $ python iohub.py inetscada localhost 5757 
"""

import simplejson as json
import sys

import redis

import tornado.ioloop
from tornado import gen
from tornado.tcpclient import TCPClient

IOSTREAM_IP = '10.212.0.10'
IOSTREAM_PORT = 5757
QUEUE = 'inetscada'


class IOStreamClient(TCPClient):
    def __init__(self, io=None, queue='', ip='localhost', port=None):
        super(IOStreamClient, self).__init__()
        self.ip = ip
        self.port = port
        self.queue = queue

        self.r = redis.Redis()

    @gen.coroutine
    def handle(self, stream):
        line = yield stream.read_until('\n')
        line = line.rstrip('\n')
        print line
        self.r.publish(self.queue, line)

    @gen.coroutine
    def main(self):
        stream = yield self.connect(self.ip, self.port)
        print 'stream:', stream

        try:
            while True:
                yield self.handle(stream)
        except KeyboardInterrupt:
            print "Ctrl+C has been pressed."
            stream.close()


if __name__ == '__main__':
    ioloop = tornado.ioloop.IOLoop.current()

    if len(sys.argv) > 1:
        queue = sys.argv[1]
        ip = sys.argv[2]
        port = sys.argv[3]

        client = IOStreamClient(io=ioloop, queue=queue, ip=ip, port=port)
    else:
        client = IOStreamClient(io=ioloop, queue=QUEUE, ip=IOSTREAM_IP,
                                port=IOSTREAM_PORT)

    ioloop.run_sync(client.main)
