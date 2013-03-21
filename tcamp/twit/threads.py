import datetime
import threading
from time import sleep

import twitter
from django.conf import settings


class SendTweetThread(threading.Thread):
    def __init__(self, initial_tweet, **kwargs):
        self.class_instance = initial_tweet.__class__
        self.initial_tweet = self.current_tweet = initial_tweet
        self.api = twitter.Api(consumer_key=settings.TWITTER_CONSUMER_KEY,
                               consumer_secret=settings.TWITTER_CONSUMER_SECRET,
                               access_token_key=settings.TWITTER_ACCESS_KEY,
                               access_token_secret=settings.TWITTER_ACCESS_SECRET)
        return super(SendTweetThread, self).__init__(**kwargs)

    def run(self):
        while True:
            self.api.PostUpdate(self.current_tweet.text)
            self.current_tweet.sent_at = datetime.datetime.now()
            self.current_tweet.save()

            try:
                self.current_tweet = self.current_tweet.next
            except:
                break

            sleep(1)
