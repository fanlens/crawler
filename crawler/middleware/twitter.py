#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tweepy

from scrapy.http import Request, Response


# based on: https://github.com/yall/scrapy-twitter
# no license

# for other functionality revisit the original github


class TwitterStreamFilterRequest(Request):
    def __init__(self, *args, **kwargs):
        self.track = kwargs.pop('track', None)
        super(TwitterStreamFilterRequest, self).__init__('http://twitter.com',
                                                         dont_filter=True,
                                                         **kwargs)


class TwitterSearchRequest(Request):
    def __init__(self, *args, **kwargs):
        self.q = kwargs.pop('q', None)
        self.max_id = kwargs.pop('max_id', None)
        super(TwitterSearchRequest, self).__init__('http://twitter.com',
                                                   dont_filter=True,
                                                   **kwargs)


class TwitterResponse(Response):
    def __init__(self, *args, **kwargs):
        self.tweets = kwargs.pop('tweets', None)
        super(TwitterResponse, self).__init__('http://twitter.com',
                                              *args,
                                              **kwargs)


class TwitterDownloaderMiddleware(object):
    def __init__(self,
                 consumer_key, consumer_secret,
                 access_token_key, access_token_secret):
        self.auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        self.auth.secure = True
        self.auth.set_access_token(access_token_key, access_token_secret)

        self.api = tweepy.API(self.auth,
                              wait_on_rate_limit=True,
                              wait_on_rate_limit_notify=True,
                              retry_count=5,
                              retry_delay=2)

    @classmethod
    def from_crawler(cls, crawler):
        settings = crawler.settings
        consumer_key = settings['TWITTER_CONSUMER_KEY']
        consumer_secret = settings['TWITTER_CONSUMER_SECRET']
        access_token_key = settings['TWITTER_ACCESS_TOKEN_KEY']
        access_token_secret = settings['TWITTER_ACCESS_TOKEN_SECRET']
        return cls(consumer_key,
                   consumer_secret,
                   access_token_key,
                   access_token_secret)

    def process_request(self, request, spider):
        if isinstance(request, TwitterSearchRequest):
            tweets = self.api.search(q=request.q,
                                     count=100,
                                     result_type='recent',
                                     include_entities=True,
                                     max_id=request.max_id)
            return TwitterResponse(tweets=[tweet._json for tweet in tweets])

            # if isinstance(request, TwitterStreamFilterRequest):
            #     tweets = self.api.GetStreamFilter(track=request.track)
            #     return TwitterResponse(tweets=tweets)

    def process_response(self, request, response, spider):
        return response
