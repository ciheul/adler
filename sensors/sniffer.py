# http://askldjd.com/2014/01/15/a-reasonably-fast-python-ip-sniffer/
# https://thepacketgeek.com/scapy-sniffing-with-custom-actions-part-1/
# http://stackoverflow.com/questions/17314510/how-to-fix-scapy-warning-pcapy-api-does-not-permit-to-get-capure-file-descripto
# http://artwalk.github.io/2015/06/17/homebrew-cannot-run-C-compiled-programs/
# http://bt3gl.github.io/black-hat-python-infinite-possibilities-with-the-scapy-module.html

from scapy.all import *
import socket
import pika


key = 'sniff'
ip_src = '192.168.2.102'
# ip_src = '10.10.254.214'

class Sniffer:
    def __init__(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(
            host='localhost'))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=key)

    def packet_callback(self, packet):
        if packet['IP'].src == ip_src:
            try:
                hostname = socket.gethostbyaddr(packet['IP'].dst)[0]
                print "{0} => {1} [{2}]".format(packet['IP'].src,
                                                packet['IP'].dst,
                                                hostname)
            except socket.herror:
                print "{0} => {1}".format(packet['IP'].src, packet['IP'].dst)

            self.channel.basic_publish(exchange='',
                                       routing_key=key,
                                       body=packet['IP'].dst)
    
    def main(self):
        sniff(iface="en1", filter="ip", prn=self.packet_callback)


s = Sniffer()
s.main()
