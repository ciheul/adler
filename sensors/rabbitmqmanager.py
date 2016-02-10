import logging

from pika.adapters import TornadoConnection
import pika
import tornado.ioloop

# from singleton import Singleton


AMQP_URL = 'amqp://guest:guest@localhost:5672/%2F'

LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) '
              '-35s %(lineno) -5d: %(message)s')
logger = logging.getLogger(__name__)


class RabbitMQManager(object):
    # __metaclass__ = Singleton

    # QUEUE = 'hello'
    EXCHANGE = ''
    PUBLISH_INTERVAL = 1

    def __init__(self, io_loop=None, queue=None, amqp_url=AMQP_URL):
        self.io_loop = io_loop# or tornado.ioloop.IOLoop.current()
        self.url = amqp_url
        self.queue = queue

        self.is_connected = False
        self.is_connecting = False

        self.connection = None
        self.channel = None

        self.listeners = set([])

        # print '__init__'
        # print self.io_loop
        # if io_loop is None:
        #     tornado.ioloop.IOLoop.current().start()

    def connect(self):
        print "connect"
        if self.is_connecting:
            print "Already connecting to RabbitMQ"
            logger.info("PikaConnection: Already connecting to RabbitMQ")
            return

        logger.info("PikaConnection: Connecting to RabbitMQ")
        self.connecting = True

        self.connection = TornadoConnection(
            pika.URLParameters(self.url),
            on_open_callback=self.on_connected)

        self.connection.add_on_close_callback(self.on_closed)

    def on_connected(self, connection):
        print "on_connected"
        logger.info("PikaConnection: connected to RabbitMQ")
        self.connected = True
        self.connection = connection
        self.connection.channel(self.on_channel_open)
        self.connection.add_backpressure_callback(self.on_pressure)

    def on_closed(self, connection):
        print "on_closed"
        logger.info("PikaConnection: connection closed")
        if self.io_loop is not None:
            self.io_loop.stop()

    def on_channel_open(self, channel):
        print "on_channel_open:", channel
        self.channel = channel
        self.channel.add_on_close_callback(self.on_channel_closed)
        self.channel.queue_declare(queue=self.queue,
                                   callback=self.on_queue_declared)

    def on_channel_closed(self, channel, reply_code, reply_text):
        print "on_channel_closed"
        self.connection.close()

    def on_queue_declared(self, frame):
        print "subscribe frame:", frame
        self.channel.basic_consume(self.on_message,
                                   queue=self.queue,
                                   no_ack=False)

    def on_pressure(self):
        print "on_pressure"

    def on_message(self, channel, method, header, body):
        # logger.info(body)
        for listener in self.listeners:
            listener.emit(body)

    def add_event_listener(self, listener):
        self.listeners.add(listener)

    def publish_message(self, *args, **kwargs):
        print self.channel
        if self.channel and 'message' in kwargs:
            self.channel.basic_publish(exchange=self.EXCHANGE,
                                       routing_key=self.queue,
                                       body=kwargs['message'])
