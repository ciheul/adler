import tornado.ioloop
from tornado.tcpserver import TCPServer
from rabbitmqmanager import RabbitMQManager

# import message_pb2


SNIFF_QUEUE = 'sniff'
TWITTER_QUEUE = 'tweets'
INETSCADA_QUEUE = 'inetscada'

class IOStreamServer(TCPServer):
    def __init__(self, io=None, queue=''):
        super(IOStreamServer, self).__init__()
        self.rm = RabbitMQManager(io_loop=io, queue=queue)
        self.rm.add_event_listener(self)
        self.rm.connect()

        self.streams = list()

    def emit(self, data):
        # serialized_message = self.serialize_to_protobuf(data)
        # print "emit:{0} / {1}".format(data, len(serialized_message))
        print data
        for stream in self.streams:
            try:
                stream.write(data + '\n')
                # stream.write(serialized_message + '|')
            except tornado.iostream.StreamClosedError:
                print "remove stream:", stream
                self.streams.remove(stream)

    # def serialize_to_protobuf(self, data):
    #     m = message_pb2.GroupTag()
    #     m.JSONData = data
    #     return m.SerializeToString()

    def handle_stream(self, stream, address):
        print "stream :", stream
        print "address:", address

        self.streams.append(stream)

        # stream.write('Welcome to IO Stream Server|')


ioloop = tornado.ioloop.IOLoop.instance()

server0 = IOStreamServer(io=ioloop, queue=SNIFF_QUEUE)
server1 = IOStreamServer(io=ioloop, queue=TWITTER_QUEUE)
server2 = IOStreamServer(io=ioloop, queue=INETSCADA_QUEUE)

server0.listen(5758)
server1.listen(20001)
server2.listen(5757)

ioloop.start()
