#!/usr/bin/python

from datetime import timedelta
import settings
import time
import tweepy
import sys

import pika


auth = tweepy.OAuthHandler(settings.CONSUMER_KEY, settings.CONSUMER_SECRET)
auth.set_access_token(settings.ACCESS_KEY, settings.ACCESS_SECRET)
api = tweepy.API(auth)

key = 'tweets'

class CustomStreamListener(tweepy.StreamListener):
    def on_connect(self):
        print 'on_connect'
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(
            host='localhost'))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=key)

    def on_status(self, tweet):
        created_at = tweet.created_at + timedelta(hours=7)

        # print created_at
        # print tweet.user.screen_name, tweet.user.location
        # print tweet.text
        # print

        tweet_model = (
            tweet.id_str,
            tweet.user.screen_name,
            created_at.isoformat(' '),
            str(tweet.text.encode('utf-8')),
            None,
            None
        )

        self.channel.basic_publish(exchange='',
                                   routing_key=key,
                                   body=tweet.text.encode('utf-8'))

        print tweet_model

    def on_error(self, status_code):
        print >> sys.stderr, 'Encountered error with status code:', \
            status_code + ": Not Acceptable Response. One or more \
            inputs are wrong."
        return True

    def on_timeout(self):
        print >> sys.stderr, 'Timeout...'
        return True


if __name__ == '__main__':
    while True:
        try:
            stream_api = tweepy.streaming.Stream(auth, CustomStreamListener(),
                                                 timeout=60)
            # fetch 'lewatmana', 'TMCPoldaMetro', 'NTMCLantasPolri',
            # 'RTMC_Jatim', 'RadioElShinta'
            #stream_api.filter(follow=['18795386', '76647722', '130169009'])
            stream_api.filter(track=['bandung'])
        except IOError, e:
            print e
        except KeyboardInterrupt:
            print "Stop the tweet streaming"
            quit()
        finally:
            print
            print "Twitter has resetted the connection. Wait for a while and" \
                "let's reconnect! >:)"
            time.sleep(5)

